#!/usr/bin/env python3
"""Remove an explicit idle-file list only after independent remote verification."""
import argparse,datetime,hashlib,json,os,resource
from pathlib import Path

ROOT=Path('/workspace/scratch/1389522c4edd')
def memory():
    p=Path('/sys/fs/cgroup');d={x.split()[0]:int(x.split()[1]) for x in (p/'memory.stat').read_text().splitlines()}
    return {'current':int((p/'memory.current').read_text()),'anonymous':d['anon'],'file_cache':d['file'],'shared_memory':d['shmem'],'events':(p/'memory.events').read_text()}
def allowed(p):
    if p.parent==Path('/tmp'):return p.name.startswith('pscs') and p.suffix=='.json'
    if p.parent==ROOT:return p.name.startswith('Planning_Search_Constraints_RSI_Simple_Checkpoint.zip')
    for n in ['cpu_runtime_exports','cpu_historical_import','cpu_historical_extra_import']:
        if p.is_relative_to(ROOT/n):return True
    for n in ['windows/W0001/vendor','windows/W0001/results','windows/W0001/data','windows/W0001/evidence','data']:
        if p.is_relative_to(ROOT/'planning_simple'/n):return True
    return False
def main():
    resource.setrlimit(resource.RLIMIT_AS,(256000000,256000000))
    a=argparse.ArgumentParser();a.add_argument('--verification-receipt',type=Path,required=True);a.add_argument('--candidates',type=Path,required=True);a.add_argument('--receipt',type=Path,required=True);a.add_argument('--execute',action='store_true');x=a.parse_args()
    proof=json.loads(x.verification_receipt.read_text());assert proof['status']=='verified' and proof['sqlite_integrity']=='ok'
    targets=json.loads(x.candidates.read_text())['candidates'];names={t['path'] for t in targets};busy=set();unreadable=0
    for d in Path('/proc').iterdir():
        if not d.name.isdigit():continue
        try:
            for fd in (d/'fd').iterdir():
                try:
                    p=os.readlink(fd)
                    if p in names:busy.add(p)
                except OSError:pass
            for line in (d/'maps').read_text().splitlines():
                cols=line.split(None,5)
                if len(cols)==6 and cols[5] in names:busy.add(cols[5])
        except (OSError,PermissionError):unreadable+=1
    receipt={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verified_commit':proof['commit'],'executed':x.execute,'memory_before':memory(),'filesystem_free_before':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize,'deleted':[],'skipped':[],'already_absent':[],'unique_unlinked_payload_bytes':0,'unique_unlinked_allocated_bytes':0,'process_inspection_unavailable':unreadable,'scope':'Only exact allowlisted byte-matching idle files; runner databases, controls, live supervisor logs, other projects and remote originals retained.'}
    for t in targets:
        p=Path(t['path']);assert allowed(p),str(p)
        if not p.exists():receipt['already_absent'].append(str(p));continue
        if p.is_symlink() or str(p) in busy:receipt['skipped'].append({'path':str(p),'reason':'symlink or open/mapped file'});continue
        before=p.stat()
        if before.st_size!=t['bytes']:receipt['skipped'].append({'path':str(p),'reason':'size changed'});continue
        h=hashlib.sha256()
        with p.open('rb') as f:
            while b:=f.read(1024*1024):h.update(b)
            os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
        after=p.stat()
        if h.hexdigest()!=t['sha256'] or (before.st_ino,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_mtime_ns,after.st_size):receipt['skipped'].append({'path':str(p),'reason':'hash or stat changed'});continue
        if x.execute:
            p.unlink()
            if after.st_nlink==1:
                receipt['unique_unlinked_payload_bytes']+=after.st_size;receipt['unique_unlinked_allocated_bytes']+=after.st_blocks*512
        receipt['deleted'].append({**t,'unlink_performed':x.execute,'prior_link_count':after.st_nlink})
    receipt['memory_after']=memory();receipt['filesystem_free_after']=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
    receipt['immediate_remaining']=[t['path'] for t in targets if Path(t['path']).exists()]
    receipt['cross_context_absence_verified']=False
    x.receipt.parent.mkdir(parents=True,exist_ok=True);x.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['executed','unique_unlinked_payload_bytes','unique_unlinked_allocated_bytes','memory_after','cross_context_absence_verified']}));print(json.dumps({'deleted_paths':len(receipt['deleted']),'skipped':len(receipt['skipped']),'remaining':len(receipt['immediate_remaining'])}))
if __name__=='__main__':main()
