import argparse,json
from pathlib import Path
from decontam_selector import import_blinded_confirmation_index,open_db,sha_file

def main():
    p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--target',required=True); p.add_argument('--protocol',required=True); p.add_argument('--contract',required=True); p.add_argument('--summary',required=True); a=p.parse_args()
    protocol_sha=sha_file(a.protocol); contract_sha=sha_file(a.contract); target=Path(a.target); target.parent.mkdir(parents=True,exist_ok=True)
    db=open_db(target)
    try:
        imported=import_blinded_confirmation_index(db,a.source,protocol_sha,contract_sha)
        meta=dict(db.execute('SELECT k,v FROM meta'))
        counts={'confirmation_records':db.execute('SELECT COUNT(*) FROM conf').fetchone()[0],'unique_url_hashes':db.execute('SELECT COUNT(*) FROM conf_url_hash').fetchone()[0],'unique_shingle_records':db.execute('SELECT COUNT(*) FROM grams').fetchone()[0],'shingle_mass':db.execute('SELECT COALESCE(SUM(n),0) FROM grams').fetchone()[0]}
        languages=dict(db.execute('SELECT lang,COUNT(*) FROM conf GROUP BY lang ORDER BY lang')); integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
    finally: db.close()
    result={'schema_version':1,'scope':'result-blind confirmation-hash adapter only; no raw confirmation text, development selection, tokenizer, or fairness result','source_index_sha256':sha_file(a.source),'target_selector_sha256':sha_file(target),'protocol_sha256':protocol_sha,'adapter_contract_sha256':contract_sha,'imported_this_call':imported,'counts':counts,'languages':languages,'integrity_check':integrity,'confirmation_complete':meta.get('confirmation_complete'),'confirmation_representation':meta.get('confirmation_representation'),'raw_confirmation_text_accessed':False,'tokenizer_or_fairness_output_computed':False}
    out=Path(a.summary); tmp=out.with_name(out.name+'.tmp'); tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); tmp.replace(out); print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
