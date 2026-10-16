#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, os, platform, resource, subprocess, tarfile, time
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, maximum_filter

ROOT=Path(__file__).resolve().parents[1]; ARCH=ROOT/'data/tum/rgbd_dataset_freiburg1_xyz.tgz'; PLAN=ROOT/'plans/gravity-pose-tum-fr1xyz-v3.md'
SRC=ROOT/'sources/GravityPose'; POSELIB=ROOT/'sources/PoseLib'; CPP=ROOT/'experiments/gravity_pose_tum_fr1xyz_v1.cpp'
OUTDIR=ROOT/'results/gravity-pose-tum-fr1xyz-v3'; OUT=ROOT/'results/gravity-pose-tum-fr1xyz-v3.json'; DATA=ROOT/'data/tum/gravity-fr1xyz-v2'
EIGEN=Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/casadi/include/eigen3')
K=np.array([[525.,0,319.5],[0,525.,239.5],[0,0,1.]])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(text,n):
 o=[]
 for l in text.splitlines():
  if not l.strip() or l.startswith('#'):continue
  a=l.split();o.append((float(a[0]),a[1:] if n<0 else [float(x) for x in a[1:]]))
 return o
def near(a,t):return min(a,key=lambda x:abs(x[0]-t))
def qR(q):
 x,y,z,w=np.asarray(q)/np.linalg.norm(q);return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def feat(p):
 im=np.asarray(Image.open(p).convert('L'),float)/255.;ix=gaussian_filter(im,1.2,order=(0,1));iy=gaussian_filter(im,1.2,order=(1,0));sxx=gaussian_filter(ix*ix,1.2);syy=gaussian_filter(iy*iy,1.2);sxy=gaussian_filter(ix*iy,1.2);r=sxx*syy-sxy*sxy-.04*(sxx+syy)**2
 local=r==maximum_filter(r,size=17,mode='constant',cval=-np.inf);local[:8]=False;local[-8:]=False;local[:,:8]=False;local[:,-8:]=False;local&=r>0;yy,xx=np.nonzero(local);order=np.argsort(r[yy,xx])[::-1][:512];P=[];D=[];A=[]
 for y,x in zip(yy[order],xx[order]):
  q=im[y-5:y+6,x-5:x+6].reshape(-1).copy();q-=q.mean();n=np.linalg.norm(q)
  if n<1e-10:continue
  ys=slice(y-8,y+9);xs=slice(x-8,x+9);ang=np.arctan2(iy[ys,xs],ix[ys,xs]);mag=np.hypot(ix[ys,xs],iy[ys,xs]);bins=np.floor((ang+math.pi)*(36/(2*math.pi))).astype(int)%36;hist=np.bincount(bins.ravel(),weights=mag.ravel(),minlength=36);A.append((np.argmax(hist)+.5)*(2*math.pi/36)-math.pi);P.append((x,y));D.append(q/n)
 return np.asarray(P,float),np.asarray(D,float),np.asarray(A,float)
def matches(a,b):
 p1,d1,o1=a;p2,d2,o2=b
 if len(d1)<2 or len(d2)<2:return []
 ds=np.maximum(0,2-2*d1@d2.T);n12=np.argmin(ds,axis=1);n21=np.argmin(ds,axis=0);out=[]
 for i,j in enumerate(n12):
  if n21[j]!=i:continue
  x=np.partition(ds[i],1)[:2];y=np.partition(ds[:,j],1)[:2];r1=math.sqrt(x[0]/max(x[1],1e-15));r2=math.sqrt(y[0]/max(y[1],1e-15))
  if r1<=.8 and r2<=.8:out.append((r1+r2,i,int(j),r1,r2))
 return sorted(out)[:256]
def xyz(depth,x,y):
 z=depth[y,x]/5000.;return np.array([(x-319.5)*z/525.,(y-239.5)*z/525.,z]) if z>0 else None
def normal(depth,x,y):
 if x<2 or y<2 or x>=depth.shape[1]-2 or y>=depth.shape[0]-2:return None
 pts=[xyz(depth,x-2,y),xyz(depth,x+2,y),xyz(depth,x,y-2),xyz(depth,x,y+2)]
 if any(p is None for p in pts):return None
 n=np.cross(pts[1]-pts[0],pts[3]-pts[2]);z=np.linalg.norm(n)
 if z<1e-8:return None
 n/=z;c=xyz(depth,x,y)
 if c is None:return None
 if n@c>0:n=-n
 return n
def rxz(R):
 cx=math.hypot(R[1,0],R[1,1]);x=math.atan2(-R[1,2],cx);z=math.atan2(R[1,0],R[1,1]);Rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]]);Rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]]);return Rx@Rz
def main():
 resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:4]);assert sha(ARCH)=='a0236d97b8c30cd93b653656d2b6c293ff7c982a4130ef2a1a8beecdb124ef98';DATA.mkdir(parents=True,exist_ok=True);OUTDIR.mkdir(parents=True,exist_ok=True)
 with tarfile.open(ARCH,'r:gz') as tf:
  names=tf.getnames();prefix=next(n.rsplit('/',1)[0] for n in names if n.endswith('/rgb.txt'))
  def text(n):return tf.extractfile(prefix+'/'+n).read().decode()
  rgb=rows(text('rgb.txt'),-1);dep=rows(text('depth.txt'),-1);gt=rows(text('groundtruth.txt'),7);exposed=set()
  old=json.loads((ROOT/'results/linear-fundamental-tum-fr1xyz-v1.json').read_text())
  for p in old['pairs']:
   exposed.update([p.get('anchor_path'),p.get('partner_path')])
  selected=[];t0=rgb[0][0]
  for k in range(8):
   ar=t0+15.25+1.0*k;r=near(rgb,ar);q=near(rgb,r[0]+.30);d=near(dep,r[0]);g1=near(gt,r[0]);g2=near(gt,q[0]);accepted=max(abs(r[0]-ar),abs(q[0]-(r[0]+.30)),abs(d[0]-r[0]),abs(g1[0]-r[0]),abs(g2[0]-q[0]))<=.02 and r[1][0] not in exposed and q[1][0] not in exposed
   rec={'pair':k,'accepted':accepted,'ref_t':r[0],'query_t':q[0],'depth_t':d[0],'ref_path':r[1][0],'query_path':q[1][0],'depth_path':d[1][0],'miss_max':max(abs(r[0]-ar),abs(q[0]-(r[0]+.30)),abs(d[0]-r[0]),abs(g1[0]-r[0]),abs(g2[0]-q[0])),'g1':g1,'g2':g2};selected.append(rec)
   if accepted:
    for rel in [r[1][0],q[1][0],d[1][0]]:
     dst=DATA/Path(rel).name
     if not dst.exists():dst.write_bytes(tf.extractfile(prefix+'/'+rel).read())
 pairmeta=[];matchrows=[];diag=[]
 for rec in selected:
  if not rec['accepted']:diag.append({k:v for k,v in rec.items() if k not in ['g1','g2']});continue
  p1=feat(DATA/Path(rec['ref_path']).name);p2=feat(DATA/Path(rec['query_path']).name);mm=matches(p1,p2);depth=np.asarray(Image.open(DATA/Path(rec['depth_path']).name),dtype=np.uint16);valid=[];rej={'zero_depth':0,'normal':0}
  for score,i,j,r1,r2 in mm:
   x,y=np.rint(p1[0][i]).astype(int);X=xyz(depth,x,y);n=normal(depth,x,y)
   if X is None:rej['zero_depth']+=1;continue
   if n is None:rej['normal']+=1;continue
   valid.append((score,X,p2[0][j]-[319.5,239.5],p1[2][i],p2[2][j],n))
  valid=valid[:128];g1,g2=rec['g1'],rec['g2'];R1,R2=qR(g1[1][3:]),qR(g2[1][3:]);t1,t2=np.array(g1[1][:3]),np.array(g2[1][:3]);R=R2.T@R1;t=R2.T@(t1-t2);G=rxz(R);pairmeta.append([rec['pair'],*R.ravel(),*t,*G.ravel()])
  for _,X,y,ar,aq,n in valid:matchrows.append([rec['pair'],*X,*y,ar,aq,*n])
  diag.append({**{k:v for k,v in rec.items() if k not in ['g1','g2']},'image_matches':len(mm),'valid_depth_normal_matches':len(valid),'rejections':rej,'rotation_deg':float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))),'translation_m':float(np.linalg.norm(t))})
 pairs=OUTDIR/'pairs.csv';mfile=OUTDIR/'matches.csv';
 with pairs.open('w',newline='') as f:w=csv.writer(f);w.writerow(['pair',*[f'R{i}' for i in range(9)],'tx','ty','tz',*[f'G{i}' for i in range(9)]]);w.writerows(pairmeta)
 with mfile.open('w',newline='') as f:w=csv.writer(f);w.writerow(['pair','X','Y','Z','u','v','angle_ref','angle_query','nx','ny','nz']);w.writerows(matchrows)
 binary=OUTDIR/'run';sources=[CPP,SRC/'src/solvers/solver_up2pf_ori.cpp',POSELIB/'PoseLib/solvers/p3p.cc',POSELIB/'PoseLib/misc/univariate.cc'];cmd=['g++','-std=c++17','-O3','-DNDEBUG','-I',str(EIGEN),'-I',str(SRC/'src/include'),'-I',str(POSELIB),*[str(x) for x in sources],'-o',str(binary)];t=time.monotonic();c=subprocess.run(cmd,capture_output=True,text=True,timeout=180);run=None;arms=[]
 if c.returncode==0:
  run=subprocess.run([str(binary),str(pairs),str(mfile)],capture_output=True,text=True,timeout=120)
  if run.returncode==0:arms=list(csv.DictReader(io.StringIO(run.stdout)));(OUTDIR/'raw.csv').write_text(run.stdout)
 by={}
 for a in arms:
  z={k:(float(v) if k not in ['pair','arm','valid','valid_hypotheses','inliers'] else v) for k,v in a.items()};z['pair']=int(z['pair']);z['valid']=z['valid']=='1';z['valid_hypotheses']=int(z['valid_hypotheses']);z['inliers']=int(z['inliers']);by.setdefault(z['arm'],[]).append(z)
 summary={k:{'pairs':len(v),'valid_pairs':sum(x['valid'] for x in v),'median_rotation_error_deg':float(np.median([x['rotation_error_deg'] for x in v if x['valid']])) if any(x['valid'] for x in v) else None,'median_center_error_m':float(np.median([x['center_error_m'] for x in v if x['valid']])) if any(x['valid'] for x in v) else None,'median_inliers':float(np.median([x['inliers'] for x in v])) if v else None} for k,v in by.items()}
 qualified=sum(d.get('valid_depth_normal_matches',0)>=24 for d in diag)>=6 and summary.get('up2pf_ori_ransac',{}).get('valid_pairs',0)>=4
 out={'scope':'Frozen public RGB-D source-model development diagnostic; not paper reproduction or benchmark','plan':{'path':str(PLAN.relative_to(ROOT)),'sha256':sha(PLAN)},'archive':{'path':str(ARCH.relative_to(ROOT)),'sha256':sha(ARCH)},'sources':{str(x.relative_to(ROOT)):sha(x) for x in sources},'selection_and_data':diag,'arms':arms,'summary':summary,'qualification':{'pairs_with_24_valid_matches':sum(d.get('valid_depth_normal_matches',0)>=24 for d in diag),'up2_valid_pairs':summary.get('up2pf_ori_ransac',{}).get('valid_pairs',0),'passed':qualified},'compile':{'returncode':c.returncode,'seconds':time.monotonic()-t,'stderr':c.stderr},'run':None if run is None else {'returncode':run.returncode,'stderr':run.stderr},'runtime':{'platform':platform.platform(),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'summary':summary,'qualification':out['qualification'],'peak_rss_kib':out['runtime']['peak_rss_kib'],'compile':c.returncode,'run':None if run is None else run.returncode}));return 0 if c.returncode==0 and run and run.returncode==0 else 1
if __name__=='__main__':raise SystemExit(main())
