"""Independent arithmetic reconstruction from stored integer aligned costs."""
import json,math
from pathlib import Path

def stats(costs):
    n=len(costs)
    assert n>0 and all(len(r)==2 and all(isinstance(x,int) and x>0 for x in r) for r in costs)
    a=sum(r[0] for r in costs);b=sum(r[1] for r in costs)
    return {'n':n,'mean_tokens':[a/n,b/n],'gini':abs(a-b)/(2*(a+b)),
            'worst_cost':max(a,b)/n,'sum_language_means':(a+b)/n,
            'mean_sentence_gini':sum(abs(x-y)/(2*(x+y)) for x,y in costs)/n}

def check(actual,expected):
    for k,value in actual.items():
        if k=='mean_tokens':
            assert all(math.isclose(x,y,abs_tol=1e-12,rel_tol=1e-12) for x,y in zip(value,expected[k]))
        else:assert math.isclose(value,expected[k],abs_tol=1e-12,rel_tol=1e-12),(k,value,expected[k])

new=json.loads(Path('output/efficiency_candidate_evaluation.json').read_text())
old=json.loads(Path('inputs/multibook_raw_evaluation.json').read_text())
full=json.loads(Path('inputs/full_candidate_evaluation.json').read_text())
checked=0
for name,record in new['arms'].items():
    for row in list(record['books'].values())+list(record['tico'].values()):
        check(stats(row['paired_costs']),row);checked+=1
    aggregate={
      'mean_book_gini':sum(r['gini'] for r in record['books'].values())/10,
      'mean_book_worst':sum(r['worst_cost'] for r in record['books'].values())/10,
      'mean_book_total':sum(r['sum_language_means'] for r in record['books'].values())/10}
    for k,v in aggregate.items():assert math.isclose(v,record['aggregate'][k],abs_tol=1e-12)
    bases={b:old['arms'][b] for b in ['classical','pooled','robust_domain']}
    bases.update({b:full['arms'][b]['books'] for b in ['full_minmax','full_pooled']})
    for base,contrasts in record['contrasts'].items():
        for metric,reported in contrasts.items():
            diff=[record['books'][w][metric]-bases[base][w][metric] for w in record['books']]
            assert math.isclose(sum(diff)/10,reported['mean_delta'],abs_tol=1e-12)
            assert sum(x<0 for x in diff)==reported['better_books']
            assert sum(x>0 for x in diff)==reported['worse_books']

def delta(a,b):
    return {k:new['arms'][a]['aggregate'][k]-b[k] for k in ['mean_book_gini','mean_book_worst','mean_book_total']}

result={'integer_cost_tables_checked':checked,'arithmetic_passed':True,
  'eff_minmax_minus_full_minmax':delta('eff_minmax',full['arms']['full_minmax']['aggregate']),
  'eff_minmax_minus_full_pooled':delta('eff_minmax',full['arms']['full_pooled']['aggregate']),
  'eff_minmax_minus_exact_train':delta('eff_minmax',new['arms']['exact_train']['aggregate']),
  'eff_minmax_minus_classical':delta('eff_minmax',new['existing_books_summary']['classical']),
  'prediction_checks':{
    'cost_lower_than_full_minmax':new['arms']['eff_minmax']['aggregate']['mean_book_total']<full['arms']['full_minmax']['aggregate']['mean_book_total'],
    'gini_lower_than_full_pooled':new['arms']['eff_minmax']['aggregate']['mean_book_gini']<full['arms']['full_pooled']['aggregate']['mean_book_gini']},
  'claim_scope':'All evaluated Books/TICO rows are exposed diagnostics; arithmetic verification is not independent scientific confirmation.'}
Path('output/efficiency_table_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
