#!/usr/bin/env python3
"""Verify an independently fetched immutable commit before local eviction."""
import argparse,datetime,hashlib,importlib.util,json,os,resource,sqlite3,subprocess
from pathlib import Path

def hash_file(path):
    h=hashlib.sha256();size=0
    with path.open('rb') as f:
        while b:=f.read(1024*1024):h.update(b);size+=len(b)
        os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
    return h.hexdigest(),size

def main():
    resource.setrlimit(resource.RLIMIT_AS,(768000000,768000000))
    if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--commit',required=True);p.add_argument('--expected-queue',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--restore-dir',type=Path,required=True);a=p.parse_args()
    r=a.repo.resolve();head=subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip();assert head==a.commit
    tree={}
    for line in subprocess.check_output(['git','-C',str(r),'ls-tree','-rz','HEAD']).split(b'\0'):
        if not line:continue
        info,path=line.split(b'\t',1);mode,kind,sha=info.decode().split();tree[path.decode()]=(kind,sha)
    q=json.loads(a.expected_queue.read_text());verified_bytes=0
    for x in q:
        assert tree.get(x['path'])==('blob',x['git_sha']),x['path']
        sha,size=hash_file(r/x['path']);assert (sha,size)==(x['sha256'],x['size']),x['path'];verified_bytes+=size
    ns='projects/planning-search-constraints-simple-20261011';spec=importlib.util.spec_from_file_location('archive',r/ns/'archive_store.py');archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
    objects=0;object_bytes=0
    for prefix in ['historical/objects',ns+'/original-packages',ns+'/packs','projects/planning-status-exports/packs']:
        for ip in (r/prefix).rglob('index.json'):
            d=json.loads(ip.read_text());h=hashlib.sha256();size=0
            for part in d['parts']:
                path=ip.parent/part['path'];ph,ps=hash_file(path);assert (ph,ps)==(part['sha256'],part['bytes'])
                with path.open('rb') as f:
                    while b:=f.read(1024*1024):h.update(b);size+=len(b)
                    os.posix_fadvise(f.fileno(),0,0,os.POSIX_FADV_DONTNEED)
            assert (h.hexdigest(),size)==(d['sha256'],d['bytes']),str(ip);objects+=1;object_bytes+=size
    member_counts={}
    for project in ['planning-search-constraints-simple-20261011','planning-status-exports']:
        member_counts[project]=archive.restore(r,project,None,verify=True)
    controls=['CHECKPOINT.json','CURRENT_WINDOW.json','RESUME.md','AUTHORIZATION.json','runtime','windows/W0001/.research-autopilot/simple-loop.sqlite3']
    for prefix in controls:archive.restore(r,'planning-search-constraints-simple-20261011',a.restore_dir,prefix=prefix)
    db=a.restore_dir/'windows/W0001/.research-autopilot/simple-loop.sqlite3'
    with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as conn:integrity=conn.execute('pragma integrity_check').fetchall()
    assert integrity==[('ok',)],integrity
    receipt={'schema_version':1,'status':'verified','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'https://github.com/Yunbo-max/cpu','commit':head,'independent_checkout':str(r),'expected_queue_sha256':hash_file(a.expected_queue)[0],'git_paths_and_sha256_verified':len(q),'downloaded_path_bytes':verified_bytes,'reconstructed_object_count':objects,'reconstructed_object_bytes':object_bytes,'verified_original_members':member_counts,'restored_controls':controls,'sqlite_integrity':'ok','deletion_performed':False,'scope':'Only the three namespaces in expected_queue. Does not certify another project or prove a supervisor stopped.'}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
