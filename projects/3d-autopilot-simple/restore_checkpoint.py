#!/usr/bin/env python3
"""Restore an immutable GitHub checkpoint, optionally only selected project paths.

Pass an actual commit SHA, never a guessed or moving branch. Extraction refuses
nonempty targets, path traversal, symlinks and every hash/length mismatch.
"""
import argparse,concurrent.futures,hashlib,io,json,os,pathlib,tempfile,urllib.request,zipfile
BASE='https://raw.githubusercontent.com/Yunbo-max/cpu/'
PREFIX='projects/3d-autopilot-simple/'
def download(url):
    with urllib.request.urlopen(url,timeout=60) as r:return r.read()
def main():
    p=argparse.ArgumentParser();p.add_argument('--commit',required=True)
    p.add_argument('--destination',required=True);p.add_argument('--include',action='append',default=[])
    p.add_argument('--manifest',default=PREFIX+'snapshots/2026-10-12-wake16/manifest.json')
    args=p.parse_args()
    if len(args.commit)!=40 or any(c not in '0123456789abcdef' for c in args.commit):raise ValueError('exact commit required')
    dest=pathlib.Path(args.destination).resolve()
    if dest.exists() and any(dest.iterdir()):raise ValueError('destination must be empty; never overwrite live state')
    manifest=json.loads(download(BASE+args.commit+'/'+args.manifest))
    with tempfile.TemporaryDirectory(prefix='3d-checkpoint-') as tmp:
        tmp=pathlib.Path(tmp)
        downloaded=set()
        def fetch(part):
            f=tmp/str(part['index'])
            if f.exists():return f
            raw=download(BASE+args.commit+'/'+part['path'])
            assert len(raw)==part['bytes'] and hashlib.sha256(raw).hexdigest()==part['sha256']
            f.write_bytes(raw);downloaded.add(part['index']);return f
        class SparseArchive(io.RawIOBase):
            def __init__(self):self.pos=0
            def seekable(self):return True
            def readable(self):return True
            def tell(self):return self.pos
            def seek(self,offset,whence=0):
                self.pos=offset if whence==0 else self.pos+offset if whence==1 else manifest['archive_bytes']+offset
                if self.pos<0:raise ValueError('negative seek')
                return self.pos
            def read(self,n=-1):
                if n<0:n=manifest['archive_bytes']-self.pos
                end=min(self.pos+n,manifest['archive_bytes']);chunks=[]
                while self.pos<end:
                    idx=self.pos//manifest['part_bytes'];part=manifest['parts'][idx]
                    offset=self.pos-idx*manifest['part_bytes'];count=min(end-self.pos,part['bytes']-offset)
                    with fetch(part).open('rb') as f:f.seek(offset);chunks.append(f.read(count))
                    self.pos+=count
                return b''.join(chunks)
        full_hash=None
        if args.include:
            archive=SparseArchive()
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,manifest['parts']))
            archive=tmp/'checkpoint.zip';h=hashlib.sha256()
            with archive.open('wb') as out:
                for part in manifest['parts']:
                    f=tmp/str(part['index']);raw=f.read_bytes();out.write(raw);h.update(raw);f.unlink()
            assert archive.stat().st_size==manifest['archive_bytes'] and h.hexdigest()==manifest['archive_sha256']
            full_hash=h.hexdigest()
        with zipfile.ZipFile(archive) as z:
            index=json.loads(z.read('CHECKPOINT_MANIFEST.json'))
            selected=[r for r in index['files'] if not args.include or any(r['path']==s or r['path'].startswith(s.rstrip('/')+'/') for s in args.include)]
            # Validate every selected member before writing anything.
            for r in selected:
                rel=pathlib.PurePosixPath(r['path'])
                assert not rel.is_absolute() and '..' not in rel.parts
                assert (z.getinfo('3d_autopilot_simple/'+str(rel)).external_attr>>16)&0o170000 != 0o120000
                raw=z.read('3d_autopilot_simple/'+str(rel))
                assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
            dest.mkdir(parents=True,exist_ok=True)
            for r in selected:
                target=dest/r['path'];target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as f:
                    f.write(z.read('3d_autopilot_simple/'+r['path']))
                    f.flush()
                    if hasattr(os,'posix_fadvise'):os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
        print(json.dumps({'restored_files':len(selected),'full_archive_sha256_verified':full_hash,'parts_downloaded':len(downloaded),'downloaded_bytes':sum(manifest['parts'][i]['bytes'] for i in downloaded),'commit':args.commit,'destination':str(dest),'includes':args.include}))
if __name__=='__main__':main()
