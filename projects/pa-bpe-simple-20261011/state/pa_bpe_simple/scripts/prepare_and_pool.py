import sys,runpy
runpy.run_path('scripts/prepare_candidate.py',run_name='__main__')
sys.argv=['author_source/parity_aware_bpe/parity_aware_learn_bpe.py','--input','data/train.en','data/train.fr','--dev','data/dev2.pooled.en','data/dev2.pooled.fr','--symbols','1000','--min-frequency','2','--num-workers','1','--verbose','--output','runs/pooled.merges']
runpy.run_path(sys.argv[0],run_name='__main__')
