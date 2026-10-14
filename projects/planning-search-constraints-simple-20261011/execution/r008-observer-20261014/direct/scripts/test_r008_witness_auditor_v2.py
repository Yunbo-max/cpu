"""Independent small evaluator fixtures; these are not planning benchmarks."""
import tempfile,pathlib,json,copy
from audit_r008_split_witness_v2 import audit
initial='''BEGIN initial 1 -1 -1 -1 -1
META 1 0 0 1 18446744073709551615
C 0 1
M
G 0
E 0 0
V 0 0 2 0 1
L 0 0 0
END initial 1
'''
base='''META 2 0 1 1 18446744073709551615
C 0 1
M 0
G 1
E 0 0
V 0 0 2 0
O 0 0 1 0
E 1 0
V 1 0 2 1
I 1 0 0 0
L 1 0 0
'''
post='BEGIN post_refine 2 0 0 1 0\n'+base+'END post_refine 2\n'
def settled(kind):return f'BEGIN {kind} 2 -1 -1 -1 -1\n'+base+'D 0 0 1\nD 1 1 0\n'+f'END {kind} 2\n'
good=initial+post+settled('sp_updated')+settled('final')
cases={'missing-split':initial+settled('final'),'mirror-multiplicity':good.replace('I 1 0 0 0\n','',1),'bad-order-position':good.replace('O 0 0 1 0','O 0 0 1 2',1),'child-outside-parent':good.replace('V 1 0 2 1','V 1 0 2 2',1),'overlap-split-coordinate':good.replace('V 1 0 2 1','V 1 0 2 0',1),'omitted-changed-var':good.replace('M 0','M',1),'stale-native-distance':good.replace('D 0 0 1','D 0 0 0',1),'stale-phase-native-distance':good.replace('END post_refine','D 0 0 1\nEND post_refine',1),'truncated':good[:-10]}
cases['missing-SP-milestone']=initial+post+settled('final')
cases['cost-drift']=initial+post.replace('C 0 1','C 0 2')+settled('sp_updated').replace('C 0 1','C 0 2').replace('D 0 0 1','D 0 0 2').replace('D 1 1 0','D 1 2 0')+settled('final').replace('C 0 1','C 0 2').replace('D 0 0 1','D 0 0 2').replace('D 1 1 0','D 1 2 0')
cases['INF-drift']=initial+(post+settled('sp_updated')+settled('final')).replace('18446744073709551615','999999')
rows=[]
with tempfile.TemporaryDirectory() as t:
 p=pathlib.Path(t)/'w.tsv';p.write_text(good);a=audit(p,2,1);assert a['post_refine_count']==1 and a['sp_updated_count']==1;rows.append({'fixture':'valid-two-state','accepted':True})
 zero=good.replace('C 0 1','C 0 0\nC 1 2').replace('O 0 0 1 0','O 0 1 1 0').replace('I 1 0 0 0','I 1 1 0 0').replace('D 0 0 1','D 0 0 8589934592').replace('D 1 1 0','D 1 8589934592 0');p.write_text(zero);audit(p,2,1);rows.append({'fixture':'zero-cost-lexicographic-positive-shift','accepted':True})
 unreachable=good.replace('META 2 0 1 1','META 2 0 0 1').replace('O 0 0 1 0\n','').replace('I 1 0 0 0\n','').replace('D 0 0 1','D 0 0 18446744073709551615').replace('D 1 1 0','D 1 18446744073709551615 0');p.write_text(unreachable);audit(p,2,1);rows.append({'fixture':'unreachable-init-and-goal','accepted':True})
 for name,text in cases.items():
  p.write_text(text)
  try:audit(p,2,1)
  except (AssertionError,ValueError,KeyError,IndexError) as e:rows.append({'fixture':name,'rejected':True,'message':str(e)})
  else:raise AssertionError('Failed to reject '+name)
r=pathlib.Path(__file__).resolve().parents[1];o=r/'evidence/R008-witness-auditor-fixtures-v2.json';o.write_text(json.dumps({'scope':'Evaluator fixtures only; no native run or scientific cycle','results':rows},indent=2)+'\n');print(json.dumps(rows))
