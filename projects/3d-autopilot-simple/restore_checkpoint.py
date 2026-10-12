#!/usr/bin/env python3
"""Verified sparse restoration of a base archive plus immutable additive overlays.

Use --commit EXACT_LATEST_COMMIT --destination EMPTY_DIR [--include PREFIX].
Existing differing files are never overwritten. Overlay replacement occurs in
the virtual index before extraction, not by mutating an existing live database.
"""
import argparse, hashlib, io, json, os, pathlib, tempfile, urllib.request, zipfile
BASE='https://raw.githubusercontent.com/Yunbo-max/cpu/'
PREFIX='projects/3d-autopilot-simple/'

def download(commit,path):
    assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
    assert path.startswith(PREFIX) and '..' not in pathlib.PurePosixPath(path).parts
    with urllib.request.urlopen(BASE+commit+'/'+path,timeout=60) as r:return r.read()

class Archive(io.RawIOBase):
    def __init__(self,commit,path,cache):
        self.commit=commit;self.manifest=json.loads(download(commit,path))
        self.pos=0;self.cache=pathlib.Path(cache);self.cache.mkdir(parents=True)
        self.downloaded=set()
        self.zip=zipfile.ZipFile(self)
        self.index=json.loads(self.zip.read('CHECKPOINT_MANIFEST.json'))
    def fetch(self,i):
        p=self.cache/str(i);r=self.manifest['parts'][i]
        if not p.exists():
            b=download(self.commit,r['path'])
            assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
            p.write_bytes(b);self.downloaded.add(i)
        return p
    def tell(self):return self.pos
    def seekable(self):return True
    def readable(self):return True
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.manifest['archive_bytes']+offset
        if self.pos<0:raise ValueError('negative seek')
        return self.pos
    def read(self,n=-1):
        if n<0:n=self.manifest['archive_bytes']-self.pos
        end=min(self.pos+n,self.manifest['archive_bytes']);chunks=[]
        while self.pos<end:
            i=self.pos//self.manifest['part_bytes'];r=self.manifest['parts'][i]
            off=self.pos-i*self.manifest['part_bytes'];count=min(end-self.pos,r['bytes']-off)
            assert count>0
            with self.fetch(i).open('rb') as f:f.seek(off);chunks.append(f.read(count))
            self.pos+=count
        return b''.join(chunks)
    def file(self,row):
        name='3d_autopilot_simple/'+row['path'];info=self.zip.getinfo(name)
        assert (info.external_attr>>16)&0o170000 != 0o120000
        b=self.zip.read(name)
        assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        return b

def load(commit,cache):
    latest=json.loads(download(commit,PREFIX+'latest.json'))
    descriptors=[{'commit':latest['archive_commit'],'manifest_path':latest['manifest_path']}]+latest.get('overlays',[])
    archives=[];index={}
    for i,d in enumerate(descriptors):
        a=Archive(d['commit'],d['manifest_path'],pathlib.Path(cache)/str(i));archives.append(a)
        if 'archive_sha256' in d:assert a.manifest['archive_sha256']==d['archive_sha256']
        for row in a.index['files']:
            p=pathlib.PurePosixPath(row['path'])
            assert not p.is_absolute() and '..' not in p.parts
            index[row['path']]=(a,row)
    return latest,archives,index

def main():
    p=argparse.ArgumentParser();p.add_argument('--commit',required=True)
    p.add_argument('--destination',required=True);p.add_argument('--include',action='append',default=[])
    p.add_argument('--allow-identical',action='store_true');args=p.parse_args()
    dest=pathlib.Path(args.destination).resolve()
    if dest.exists() and any(dest.iterdir()) and not args.allow_identical:raise ValueError('destination must be empty')
    with tempfile.TemporaryDirectory(prefix='3d-github-restore-') as tmp:
        latest,archives,index=load(args.commit,tmp)
        selected=[v for k,v in sorted(index.items()) if not args.include or any(k==s or k.startswith(s.rstrip('/')+'/') for s in args.include)]
        # Validate all selected remote content before writing any target.
        for a,row in selected:
            target=dest/row['path'];assert not target.is_symlink() and not any(q.is_symlink() for q in target.parents)
            b=a.file(row)
            if target.exists():assert args.allow_identical and target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256'], str(target)+' differs'
        for a,row in selected:
            target=dest/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():continue
            with target.open('xb') as f:
                f.write(a.file(row));f.flush()
                if hasattr(os,'posix_fadvise'):os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
        whole=[]
        for a in archives:
            if len(a.downloaded)==len(a.manifest['parts']):
                h=hashlib.sha256()
                for i in range(len(a.manifest['parts'])):h.update(a.fetch(i).read_bytes())
                assert h.hexdigest()==a.manifest['archive_sha256'];whole.append(h.hexdigest())
        print(json.dumps({'commit':args.commit,'restored_files':len(selected),'total_index_files':len(index),'archive_count':len(archives),'downloaded_bytes':sum(sum(a.manifest['parts'][i]['bytes'] for i in a.downloaded) for a in archives),'whole_archive_hashes_verified':whole,'all_selected_file_hashes_verified':True,'destination':str(dest)}))
if __name__=='__main__':main()
