"""Single-threaded source-isolated diagnostic build; no solver or source upgrade."""
import pathlib,json,hashlib,subprocess,sys,os
r=pathlib.Path(__file__).resolve().parents[1];mp=r/'data/R008-observer-source-manifest-v1.json';m=json.loads(mp.read_text());tree=r/m['source_tree'];out=r/'results/R008-observer-build-W5-v2';out.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
for f in m['files']:assert sha(r/f['path'])==f['sha256'],f['path']
cmake=str(r/'vendor/cmake-3.31.6/cmake/data/bin/cmake');versions={c:subprocess.run([c,'--version'],capture_output=True,text=True,check=True).stdout for c in [cmake,'c++','make']};(out/'toolchain.json').write_text(json.dumps(versions,indent=2)+'\n')
build=out/'build';env=dict(os.environ);env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',CMAKE_BUILD_PARALLEL_LEVEL='1')
commands=[[cmake,'-S',str(tree/'src'),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DUSE_LP=NO'],[cmake,'--build',str(build),'--parallel','1']]
for i,cmd in enumerate(commands):
 (out/f'command-{i}.json').write_text(json.dumps(cmd)+'\n')
 with (out/f'build-{i}.stdout.log').open('wb') as so,(out/f'build-{i}.stderr.log').open('wb') as se:
  p=subprocess.run(cmd,env=env,stdout=so,stderr=se)
 if p.returncode:raise SystemExit(p.returncode)
binary=build/'bin/downward';assert binary.exists()
identity={'binary':str(binary.relative_to(r)),'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'source_manifest':str(mp.relative_to(r)),'source_manifest_sha256':sha(mp),'toolchain_sha256':sha(out/'toolchain.json'),'compile_threads':1,'scope':'Build only, native observer not yet qualified','parent_source':'Scorpion c4d2c76d4a28bd36c594f7c6318edc5c5f0d2398 coarse CPU/export fork; all input files separately SHA-bound'}
(out/'build_identity.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity))
