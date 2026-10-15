"""Immutable-buffer lossless encoding; final ZIP member AND every raw decode checked."""
import pathlib,json,hashlib,zipfile,subprocess,shutil,copy,sys,datetime
C=pathlib.Path(__file__).resolve().parent;B=C/'planning-resume-20261014';V=B/'r011-terminal-publication';O=B/'r011-terminal-compact-publication';O.mkdir(exist_ok=False);M=json.loads((V/'manifest.json').read_text());basis=V/'consistent-W5.sqlite3'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while q:=f.read(1048576):h.update(q)
    return h.hexdigest()
def write(p,x):
    with p.open('w') as f:print(json.dumps(x,indent=2),file=f)
assert sha(basis)==M['members']['windows/W0005/.research-autopilot/simple-loop.sqlite3']['sha256']
derived={n:x for n,x in M['members'].items() if '/.simple-loop.sqlite3.' in n}
assert derived
members={};rows=[];archive=O/'terminal-lossless-overlay.zip'
def buffer_member(z,n,raw,mode=0o644):
    info=zipfile.ZipInfo(n);info.external_attr=(0o100000|mode)<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,raw)
    members[n]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'mode':mode}
with zipfile.ZipFile(V/'terminal-supplement.zip') as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
    for n,x in M['members'].items():
        if n in derived:continue
        with src.open(n) as f,dst.open(copy.copy(src.getinfo(n)),'w',force_zip64=True) as out:shutil.copyfileobj(f,out,1048576)
        members[n]=x
    for n,x in derived.items():
        raw=B/'project'/n;assert sha(raw)==x['sha256'] and raw.stat().st_size==x['bytes']
        member=f'forensic-deltas/temporary-{len(rows):02d}.zst';cmd=['zstd','-T1','-3','--patch-from='+str(basis),str(raw),'-c']
        with (O/f'encode-{len(rows):02d}.stderr.log').open('wb') as se:result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=se,timeout=180)
        assert result.returncode==0;encoded=bytes(result.stdout);assert sha(raw)==x['sha256']
        buffer_member(dst,member,encoded)
        rows.append({'path':n,**x,'basis_member':'windows/W0005/.research-autopilot/simple-loop.sqlite3','basis_sha256':sha(basis),'encoding':'zstd-patch-from','encoded_member':member,'encoded_bytes':len(encoded),'encoded_sha256':hashlib.sha256(encoded).hexdigest(),'captured_from_immutable_buffer':True,'encode_argv':cmd})
        print(json.dumps({'encoded':n,'raw_bytes':x['bytes'],'encoded_bytes':len(encoded)}),flush=True)
    mapping={'format':'lossless-forensic-raw-recovery-map-v2','meaning':'Temporary idle raw bytes, cause unknown, not valid-DB/repair claim. Exact included current canonical backup basis, never liveDB. Immutable encoding buffers captured directly; finalmember join and fullraw decode required. Original localV1 wholeZIP retained, no deletions.','derived_objects':rows}
    buffer_member(dst,'recovery/derived-raw-map.json',(json.dumps(mapping,indent=2)+'\n').encode())
    for p in [pathlib.Path(__file__),C/'verify_r011_terminal_v2.py']+list(O.glob('*.log')):buffer_member(dst,'recovery/'+p.name,p.read_bytes(),p.stat().st_mode&0o777)
# Crucial final join: final captured member bytes, not an earlier mutable file.
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(members)
    for n,x in members.items():
        h=hashlib.sha256();count=0
        with z.open(n) as f:
            while q:=f.read(1048576):h.update(q);count+=len(q)
        assert (h.hexdigest(),count)==(x['sha256'],x['bytes']),n
        assert ((z.getinfo(n).external_attr>>16)&0o777)==x['mode']
    for i,x in enumerate(rows):
        enc=z.read(x['encoded_member']);assert (len(enc),hashlib.sha256(enc).hexdigest())==(x['encoded_bytes'],x['encoded_sha256'])
        assert members[x['encoded_member']]['sha256']==x['encoded_sha256'] and members[x['encoded_member']]['bytes']==x['encoded_bytes']
        # Feed exact final ZIP bytes through a file-backed stdin, bounded output streaming.
        import tempfile
        with tempfile.TemporaryFile() as inp,(O/f'decode-{i:02d}.stderr.log').open('wb') as se:
            inp.write(enc);inp.seek(0);p=subprocess.Popen(['zstd','-d','-M2048MB','--patch-from='+str(basis),'-c'],stdin=inp,stdout=subprocess.PIPE,stderr=se);h=hashlib.sha256();count=0
            while q:=p.stdout.read(1048576):h.update(q);count+=len(q)
            assert p.wait(timeout=180)==0
        assert (h.hexdigest(),count)==(x['sha256'],x['bytes']),x['path']
parts=[]
with archive.open('rb') as f:
    while q:=f.read(8388608):
        p=O/f'part-{len(parts):03d}.bin';p.write_bytes(q);parts.append({'path':p.name,'bytes':len(q),'sha256':sha(p)})
m={**M,'format':'explicit-additive-terminal-lossless-overlay-v2','parts':parts,'members':members,'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'derived_raw_objects':rows,'new_forensic_raw_bytes':sum(x['bytes'] for x in rows),'final_zip_member_mapping_join_and_all_raw_decodes_verified_locally':True,'superseded_local_v1_manifest_sha256':sha(V/'manifest.json'),'superseded_local_v1_archive_sha256':M['archive_sha256'],'superseded_local_v1_archive_bytes':M['archive_bytes'],'object_scope':M['object_scope']+' New rawforensic temporary copies represented by exact basis-bound lossless patches, not ordinary rawZIP members. Every finalencoded member joined SHA/bytes to map and all rawbytes decoded/hash-verified before upload; originalV1 rawZIP retained locally.'};write(O/'manifest.json',m);write(O/'derived-raw-map.json',mapping);shutil.copyfile(V/'capture-state.json',O/'capture-state.json')
prefix='projects/planning-search-constraints-simple-20261011/';folder=prefix+'execution/r011-p06-20261015/completed-v2/'
files=[(O/'manifest.json',folder+'manifest.json'),(O/'derived-raw-map.json',folder+'derived-raw-map.json'),(V/'manifest.json',folder+'superseded-local-v1-manifest.json'),(O/'capture-state.json',folder+'capture-state.json'),(pathlib.Path(__file__),folder+'compact_v2.py'),(C/'verify_r011_terminal_v2.py',folder+'verify_remote_v2.py')]+[(O/x['path'],folder+x['path']) for x in parts]
for x in json.loads((V/'uploads.json').read_text()):
    if x['path'].endswith(('manifest.json','capture-state.json','verify_remote_v1.py')) or '/part-' in x['path']:continue
    files.append((pathlib.Path(x['local']),x['path'].replace('/completed-v1/','/completed-v2/')))
uploads=[]
for p,n in files:
    raw=p.read_bytes();uploads.append({'local':str(p),'path':n,'bytes':len(raw),'sha256':sha(p),'git_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()})
write(O/'uploads.json',uploads);print(json.dumps({'parts':len(parts),'bytes':m['archive_bytes'],'members':len(members),'derived_objects':len(rows),'derived_raw_bytes':m['new_forensic_raw_bytes'],'new_final_member_join_and_raw_decode_verified':True}))
