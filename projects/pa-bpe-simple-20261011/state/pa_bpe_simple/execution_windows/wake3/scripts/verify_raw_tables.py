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

old=json.loads(Path('output/multibook_raw_evaluation.json').read_text())
aggregate=json.loads(Path('output/multibook_analysis.json').read_text())
new=json.loads(Path('output/pair_candidate_evaluation.json').read_text())
paired=json.loads(Path('output/paired_raw_rescore.json').read_text())
checked=0
for name,books in old['arms'].items():
    assert set(books)==set(old['sampling'])
    for work,row in books.items():check(stats(row['paired_costs']),row);checked+=1
    assert len(books)==10 and sum(x['n'] for x in books.values())==5120
    assert math.isclose(sum(row['gini'] for row in books.values())/10,aggregate['aggregate'][name]['mean_book_gini'],abs_tol=1e-12)
for name,record in new['arms'].items():
    for row in list(record['books'].values())+list(record['tico'].values()):check(stats(row['paired_costs']),row);checked+=1
    for base,contrasts in record['contrasts'].items():
        for metric,reported in contrasts.items():
            diff=[record['books'][w][metric]-old['arms'][base][w][metric] for w in record['books']]
            assert math.isclose(sum(diff)/len(diff),reported['mean_delta'],abs_tol=1e-12)
            assert sum(x<0 for x in diff)==reported['better_books']
            assert sum(x>0 for x in diff)==reported['worse_books']
for name,record in paired['arms'].items():
    for split,row in record.items():check(stats(row['raw_paired_costs']),row['raw']);checked+=1

interactions={}
for split in paired['datasets']:
    r=paired['arms']['robust_domain'][split];b=paired['arms']['classical'][split]
    a=r['annotated']['gini']-b['annotated']['gini'];raw=r['raw']['gini']-b['raw']['gini']
    interactions[split]={'annotated_candidate_minus_classical':a,'raw_candidate_minus_classical':raw,'interaction':raw-a,'direction_reversed':a*raw<0}
method_comparison={k:new['arms']['pair_minmax']['aggregate'][k]-new['arms']['pair_pooled']['aggregate'][k] for k in ['mean_book_gini','mean_book_worst','mean_book_total']}
old_dev=json.loads(Path('output/merge_descent_audit.json').read_text())['arms']['robust_domain']['summary']['final_max_domain_gini']
new_dev=new['arms']['pair_minmax']['training']['final_objective']
verdict={'integer_cost_tables_checked':checked,'pairing':'Same stored512 units for every method in each of10works; all raw-ID pairs fixed for two-work sensitivity','arithmetic_passed':True,'preprocessing_interactions':interactions,'pair_minmax_minus_pair_pooled_book_macro':method_comparison,'development_prediction':{'old_robust_max_gini':old_dev,'new_pair_minmax_max_gini':new_dev,'lower_is_better_prediction_met':new_dev<old_dev},'uncertainty':'All candidate-evaluation datasets are exposed development diagnostics; no new independent confirmation. Multiple books from same authors. No causal/novelty certification.'}
Path('output/independent_table_verification.json').write_text(json.dumps(verdict,indent=2)+'\n')
print(json.dumps(verdict))
