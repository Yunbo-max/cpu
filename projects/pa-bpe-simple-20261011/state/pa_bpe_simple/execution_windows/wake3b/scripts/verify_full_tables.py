"""Independent arithmetic reconstruction from stored integer cost pairs."""
import json,math
from pathlib import Path

def stats(costs):
    n=len(costs);assert n>0 and all(len(r)==2 and all(isinstance(x,int) and x>0 for x in r) for r in costs)
    a=sum(r[0] for r in costs);b=sum(r[1] for r in costs)
    # Exact two-language reduction, directly on integer sums (not scorer implementation).
    return {'n':n,'mean_tokens':[a/n,b/n],'gini':abs(a-b)/(2*(a+b)),
            'worst_cost':max(a,b)/n,'sum_language_means':(a+b)/n,
            'mean_sentence_gini':sum(abs(a-b)/(2*(a+b)) for a,b in costs)/n}

def check(actual,expected):
    for k,value in actual.items():
        if k=='mean_tokens':assert all(math.isclose(x,y,abs_tol=1e-12,rel_tol=1e-12) for x,y in zip(value,expected[k]))
        else:assert math.isclose(value,expected[k],abs_tol=1e-12,rel_tol=1e-12),(k,value,expected[k])


new=json.loads(Path('output/full_candidate_evaluation.json').read_text());old=json.loads(Path('output/multibook_raw_evaluation.json').read_text());checked=0
for name,record in new['arms'].items():
    for row in list(record['books'].values())+list(record['tico'].values()):check(stats(row['paired_costs']),row);checked+=1
    for base,contrasts in record['contrasts'].items():
        for metric,reported in contrasts.items():
            diff=[record['books'][w][metric]-old['arms'][base][w][metric] for w in record['books']]
            assert math.isclose(sum(diff)/len(diff),reported['mean_delta'],abs_tol=1e-12)
            assert sum(x<0 for x in diff)==reported['better_books']
            assert sum(x>0 for x in diff)==reported['worse_books']
    assert math.isclose(sum(r['gini'] for r in record['books'].values())/10,record['aggregate']['mean_book_gini'],abs_tol=1e-12)
contrast={k:new['arms']['full_minmax']['aggregate'][k]-new['arms']['full_pooled']['aggregate'][k] for k in ['mean_book_gini','mean_book_worst','mean_book_total']}
result={'integer_cost_tables_checked':checked,'arithmetic_passed':True,'full_minmax_minus_full_pooled_book_macro':contrast,'dev_max_gini':new['arms']['full_minmax']['training']['final_objective'],'claim_scope':'Development/exploratory only; no independent confirmation or causal guarantee'}
Path('output/full_table_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
