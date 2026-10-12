#!/usr/bin/env python3
"""Streaming, incremental ZIP snapshots with SHA256 and selective restoration.

Publication and remote verification must finish before any local eviction.
Only stdlib; no changes to scientific runtime or its private ledger.
"""
import argparse,contextlib,datetime,hashlib,io,json,os,resource,shutil,sqlite3,stat,subprocess,tempfile,zipfile
from pathlib import Path,PurePosixPath

CHUNK=8*1024*1024
EXCLUDE={'.git','__pycache__','tooling','node_modules','.venv','venv','env','env-daac'}
def safe(s):
    p=PurePosixPath(s)
    if not s or p.is_absolute() or '..' in p.parts or '\\' in s: raise ValueError('Unsafe path: '+s)
    return str(p)
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        off=0
        while b:=f.read(1024*1024):
            h.update(b);os.posix_fadvise(f.fileno(),off,len(b),os.POSIX_FADV_DONTNEED);off+=len(b)
    return h.hexdigest()
def write_json(p,j):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n')
def evictions(root):
    p=root/'GITHUB_EVICTED_FILES.json'
    return {x['path']:x for x in json.loads(p.read_text())['files']} if p.exists() else {}
def split_file(source,dest):
    dest.mkdir(parents=True,exist_ok=False); parts=[];h=hashlib.sha256();size=0
    with source.open('rb') as f:
        while True:
            chunk=bytearray();remaining=CHUNK
            while remaining and (b:=f.read(min(1024*1024,remaining))):
                chunk.extend(b);h.update(b);size+=len(b);remaining-=len(b)
                os.posix_fadvise(f.fileno(),size-len(b),len(b),os.POSIX_FADV_DONTNEED)
            if not chunk:break
            name='part-%05d.bin'%len(parts);p=dest/name
            with p.open('wb') as o:
                o.write(chunk);o.flush();os.fsync(o.fileno());os.posix_fadvise(o.fileno(),0,0,os.POSIX_FADV_DONTNEED)
            parts.append({'path':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
    meta={'sha256':h.hexdigest(),'bytes':size,'part_size':CHUNK,'parts':parts};write_json(dest/'index.json',meta);return meta

class PartsReader(io.RawIOBase):
    def __init__(self,repo,pack):
        self.repo=repo;self.pack=safe(pack);self.meta=json.loads(self._path(self.pack+'/index.json').read_text());self.pos=0;self.checked=set()
    def _path(self,rel):
        rel=safe(rel);p=self.repo/rel
        if not p.exists():
            p.parent.mkdir(parents=True,exist_ok=True)
            tmp=p.with_name(p.name+'.fetching')
            try:
                with tmp.open('xb') as f:
                    subprocess.run(['git','-C',str(self.repo),'show','HEAD:'+rel],stdout=f,check=True)
                    f.flush();os.fsync(f.fileno())
                os.replace(tmp,p)
            except BaseException:
                tmp.unlink(missing_ok=True);raise
        return p
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        self.pos=n if whence==0 else self.pos+n if whence==1 else self.meta['bytes']+n
        if self.pos<0:raise ValueError('negative seek')
        return self.pos
    def read(self,n=-1):
        if n<0:n=self.meta['bytes']-self.pos
        n=min(n,self.meta['bytes']-self.pos);out=bytearray()
        while n>0:
            i,offset=divmod(self.pos,self.meta['part_size']);part=self.meta['parts'][i];p=self._path(self.pack+'/'+part['path'])
            if i not in self.checked:
                if p.stat().st_size!=part['bytes'] or digest(p)!=part['sha256']:raise ValueError('Corrupt part')
                self.checked.add(i)
            with p.open('rb') as f:
                f.seek(offset);b=f.read(min(n,part['bytes']-offset));os.posix_fadvise(f.fileno(),offset,len(b),os.POSIX_FADV_DONTNEED)
            if not b:raise ValueError('Truncated part')
            out.extend(b);self.pos+=len(b);n-=len(b)
        return bytes(out)

def snapshot(repo,root,project,tag,overlay=False):
    ns='projects/'+safe(project);base=repo/ns;latest=base/'LATEST.json';prior={};evicted=evictions(root)
    if latest.exists():
        last=json.loads(latest.read_text());old=base/safe(last['manifest'])
        if digest(old)!=last['sha256']:raise ValueError('Bad previous manifest')
        prior={x['path']:x for x in json.loads(old.read_text())['files']}
    manifest={'schema_version':1,'project_id':project,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_root':str(root),'files':[],'excluded':[],'unstable':[],'overlay':overlay,'sqlite_note':'Each database is a separate read-only online backup; multiple databases are not a cross-database atomic transaction. Reconcile runtime receipts before resume.'}
    pack=ns+'/packs/'+safe(tag); staging=repo/'.staging';staging.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=staging) as td:
        td=Path(td);zpath=td/'payload.zip'
        with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for here,ds,fs in os.walk(root,followlinks=False):
                for d in list(ds):
                    if d in EXCLUDE or (Path(here)/d).is_symlink():
                        manifest['excluded'].append({'path':str((Path(here)/d).relative_to(root)),'reason':'reproducible environment, Git internals, cache, or directory symlink'});ds.remove(d)
                for name in sorted(fs):
                    p=Path(here)/name;rel=safe(str(p.relative_to(root)))
                    if p.is_symlink() or name.endswith(('-wal','-shm','.pyc','.o','.a')) or name in {'.env','.credentials','id_rsa','id_ed25519'}:
                        manifest['excluded'].append({'path':rel,'reason':'symlink, credential file, SQLite transient sidecar, or reproducible intermediate'});continue
                    before=p.stat();source=p;is_db=False
                    marker=evicted.get(rel);old=prior.get(rel)
                    if before.st_size==0 and marker and old and marker['sha256']==old['sha256'] and marker['bytes']==old['bytes']:
                        if not overlay:raise ValueError('Evicted placeholders require --overlay')
                        manifest['excluded'].append({'path':rel,'reason':'Verified eviction placeholder; retain prior original bytes'});continue
                    with p.open('rb') as f:is_db=f.read(16)==b'SQLite format 3\0'
                    if is_db:
                        source=td/'sqlite-copy'
                        if source.exists():source.unlink()
                        with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True,timeout=15) as src,sqlite3.connect(source) as dst:
                            src.backup(dst,pages=128,sleep=.01)
                    sha=digest(source);size=source.stat().st_size
                    if not is_db and (p.stat().st_size!=before.st_size or p.stat().st_mtime_ns!=before.st_mtime_ns):
                        manifest['unstable'].append(rel);continue
                    old=prior.get(rel)
                    if old and old['sha256']==sha and old['bytes']==size:
                        item=dict(old)
                    else:
                        info=zipfile.ZipInfo(rel);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(before.st_mode&0xffff)<<16
                        check=hashlib.sha256()
                        with source.open('rb') as f,z.open(info,'w',force_zip64=True) as o:
                            pos=0
                            while b:=f.read(1024*1024):
                                o.write(b);check.update(b);os.posix_fadvise(f.fileno(),pos,len(b),os.POSIX_FADV_DONTNEED);pos+=len(b)
                                if pos%(4*1024*1024)==0:
                                    z.fp.flush();os.fsync(z.fp.fileno());os.posix_fadvise(z.fp.fileno(),0,0,os.POSIX_FADV_DONTNEED)
                        if check.hexdigest()!=sha:raise ValueError('Source changed during archive: '+rel)
                        item={'path':rel,'sha256':sha,'bytes':size,'pack':pack,'member':rel}
                    item.update(mode=stat.S_IMODE(before.st_mode),source_mtime_ns=before.st_mtime_ns,sqlite_backup=is_db)
                    manifest['files'].append(item)
                z.fp.flush();os.fsync(z.fp.fileno());os.posix_fadvise(z.fp.fileno(),0,0,os.POSIX_FADV_DONTNEED)
        meta=split_file(zpath,repo/pack)
    if overlay:
        present={x['path'] for x in manifest['files']}
        manifest['files'].extend(dict(x) for rel,x in prior.items() if rel not in present)
        manifest['files'].sort(key=lambda x:x['path'])
        manifest['overlay_note']='Missing local files retain their previous verified manifest entries; no implicit deletion.'
    target=base/'snapshots'/(safe(tag)+'.json');write_json(target,manifest)
    out={'project_id':project,'manifest':str(target.relative_to(base)),'sha256':digest(target),'files':len(manifest['files']),'raw_bytes':sum(x['bytes'] for x in manifest['files']),'new_pack_bytes':meta['bytes'],'unstable':manifest['unstable'],'publication':'requires remote commit verification'}
    write_json(latest,out);print(json.dumps(out));return out

def restore(repo,project,dest,prefix=None,verify=False):
    base=repo/'projects'/safe(project);latest=json.loads((base/'LATEST.json').read_text());mp=base/safe(latest['manifest'])
    if digest(mp)!=latest['sha256']:raise ValueError('Manifest hash mismatch')
    m=json.loads(mp.read_text());packs={};count=0;evicted=evictions(dest) if dest else {}
    for x in m['files']:
        rel=safe(x['path'])
        if prefix and not (rel==prefix or rel.startswith(prefix.rstrip('/')+'/')):continue
        if x['pack'] not in packs:packs[x['pack']]=zipfile.ZipFile(PartsReader(repo,x['pack']))
        h=hashlib.sha256();size=0;target=dest/rel if dest else None
        if target:
            parent=target.parent.resolve()
            if not parent.is_relative_to(dest.resolve()):raise ValueError('Destination symlink escape')
            if target.exists() or target.is_symlink():
                marker=evicted.get(rel)
                placeholder=not target.is_symlink() and target.stat().st_size==0 and marker and marker['sha256']==x['sha256'] and marker['bytes']==x['bytes']
                if not placeholder:
                    if target.is_symlink() or digest(target)!=x['sha256']:raise ValueError('Refuse overwrite')
                    count+=1;continue
            target.parent.mkdir(parents=True,exist_ok=True)
        output=contextlib.nullcontext(None) if not target else (target.with_name(target.name+'.restoring')).open('xb')
        with packs[x['pack']].open(x['member']) as f,output as o:
            while b:=f.read(1024*1024):
                h.update(b);size+=len(b)
                if o:
                    o.write(b)
                    if size%(4*1024*1024)==0:o.flush();os.fsync(o.fileno());os.posix_fadvise(o.fileno(),0,0,os.POSIX_FADV_DONTNEED)
            if o:o.flush();os.fsync(o.fileno());os.posix_fadvise(o.fileno(),0,0,os.POSIX_FADV_DONTNEED)
        if h.hexdigest()!=x['sha256'] or size!=x['bytes']:raise ValueError('Member hash mismatch')
        if target:
            tmp=target.with_name(target.name+'.restoring');tmp.chmod(x['mode']);os.replace(tmp,target)
        count+=1
    for z in packs.values():z.close()
    print(json.dumps({'verified_files':count,'restored':not verify}));return count

def main():
    resource.setrlimit(resource.RLIMIT_AS,(384_000_000,384_000_000))
    a=argparse.ArgumentParser();a.add_argument('command',choices=['snapshot','verify','restore','split']);a.add_argument('--repo',type=Path,default=Path.cwd());a.add_argument('--project');a.add_argument('--root',type=Path);a.add_argument('--tag');a.add_argument('--dest',type=Path);a.add_argument('--prefix');a.add_argument('--overlay',action='store_true');x=a.parse_args()
    if x.command=='snapshot':snapshot(x.repo.resolve(),x.root.resolve(),x.project,x.tag,x.overlay)
    elif x.command=='split':print(json.dumps(split_file(x.root,x.dest)))
    else:restore(x.repo.resolve(),x.project,x.dest,x.prefix,x.command=='verify')
if __name__=='__main__':main()
