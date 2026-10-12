from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1];plan=json.loads((p/'experiment_plan_v1.json').read_text());m=json.loads((p/'data/manifest.json').read_text())
files=['experiment_plan_v1.json','data/manifest.json','review/wake1_metric_protocol.md']+[str(f.relative_to(p)) for f in (p/'data').glob('*') if f.is_file()]+['author_source/parity_aware_bpe/learn_bpe.py','author_source/parity_aware_bpe/parity_aware_learn_bpe.py']
refs=[{'path':f,'sha256':hashlib.sha256((p/f).read_bytes()).hexdigest()} for f in dict.fromkeys(files)]
env=['/usr/bin/env','PYTHONPATH=/workspace/scratch/42f1128b703b/pa_bpe_deps','OPENBLAS_NUM_THREADS=1','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','TOKENIZERS_PARALLELISM=false','python3'];tasks=[]
for arm in plan['arms']:
 if arm in ['classical','balanced']:argv=['author_source/parity_aware_bpe/learn_bpe.py','--input','data/train.joint' if arm=='classical' else 'data/train.balanced.dict']+(['--dict-input'] if arm=='balanced' else [])
 else:
  argv=['author_source/parity_aware_bpe/parity_aware_learn_bpe.py','--input','data/train.en','data/train.fr']
  if arm.startswith('ratio'):argv+=['--ratio']+[str(v) for v in (m['ratio_dev'] if arm=='ratio_dev' else [1,1])]
  else:argv+=['--dev','data/dev.en','data/dev.fr']
  if arm=='window_a1':argv+=['--variant','window','--window-size','100','--alpha','1']
  if arm=='hybrid500':argv+=['--global-merges','500']
 argv+=['--symbols','1000','--min-frequency','2','--num-workers','1','--verbose','--output',f'runs/{arm}.merges']
 tasks.append({'task_id':arm+'-w1','argv':env+argv,'phase':'experiment','purpose':'Frozen native arm '+arm,'timeout_seconds':70,'cwd':'.','depends_on':[],'input_refs':refs,'outputs':[f'runs/{arm}.merges']})
f='scripts/evaluate_pilot.py';tasks.append({'task_id':'evaluate-w1','argv':env+[f],'phase':'verify','purpose':'Independent replay and Gini gates, aligned cross-domain pilot scores','timeout_seconds':90,'cwd':'.','depends_on':[t['task_id'] for t in tasks],'input_refs':refs+[{'path':f,'sha256':hashlib.sha256((p/f).read_bytes()).hexdigest()}],'outputs':['runs/evaluation_v1.json']})
inbox=json.loads((p/'evidence/inbox_prepare.json').read_text())[0]
response={'response_id':'native-pilot-response-w1','request_id':inbox['request_id'],'idea':plan['idea'],'revision':1,'goal_contract_version':1,'reason':'Real aligned data prepared and native source independently reviewed; frozen prospective seven-arm pilot with encoding and metric gates','tasks':tasks}
(p/'response_native_w1.json').write_text(json.dumps(response,indent=2))
