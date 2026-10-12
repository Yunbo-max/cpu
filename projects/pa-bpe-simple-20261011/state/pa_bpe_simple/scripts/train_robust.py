"""Pilot hypothesis: select worst normalized domain, then its costly language.
This is a greedy selection heuristic, NOT a proof of minimax descent.
For two languages max_l cost_l/mean(cost) = 1+2*Gini.
"""
import sys,types,json,hashlib,runpy
from pathlib import Path
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/workspace/scratch/42f1128b703b/pa_bpe_deps')
from tokenizers.pre_tokenizers import Sequence,Whitespace,ByteLevel
src=(P/'author_source/parity_aware_bpe/parity_aware_learn_bpe.py').read_text()
old='max_index, max_value = max(enumerate(lengths), key=operator.itemgetter(1))'
new='matrix = lengths.reshape(2, 2)\n                    relative = matrix / matrix.mean(axis=1, keepdims=True)\n                    domain_index, max_index = numpy.unravel_index(numpy.argmax(relative), relative.shape)\n                    max_value = lengths[2*domain_index + max_index]'
assert src.count(old)==1
src=src.replace(old,new)
(P/'runs/robust_domain_source.py').write_text(src)
mod=types.ModuleType('robust_domain_native');exec(compile(src,'robust_domain_native','exec'),mod.__dict__)
mod.pre_tokenizer=Sequence([Whitespace(),ByteLevel(use_regex=False)])
with open(P/'data/train.en') as a,open(P/'data/train.fr') as b,open(P/'data/dev2.tico.en') as c,open(P/'data/dev2.tico.fr') as d,open(P/'data/dev2.books.en') as e,open(P/'data/dev2.books.fr') as f,open(P/'runs/robust_domain.merges','w') as out:
 mod.learn_bpe([a,b],out,[c,d,e,f],1000,min_frequency=2,verbose=True,num_workers=1)
runpy.run_path(str(P/'scripts/evaluate_candidate.py'),run_name='__main__')
