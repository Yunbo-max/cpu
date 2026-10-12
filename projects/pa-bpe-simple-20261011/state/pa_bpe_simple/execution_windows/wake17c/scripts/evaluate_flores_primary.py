import hashlib, json, math, random, re, tarfile, datetime
from pathlib import Path

LANGS = ["en", "fr", "es"]
MEMBERS = {
    "en": "./flores200_dataset/devtest/eng_Latn.devtest",
    "fr": "./flores200_dataset/devtest/fra_Latn.devtest",
    "es": "./flores200_dataset/devtest/spa_Latn.devtest",
}
EXPECTED_ARCHIVE = "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6"
EXPECTED_CODES = {
    "classical": "cc0a8b1e68d0116eddeb7c3617a1e5793c875708e684484bb8da6a67eca749d2",
    "hybrid": "682c21b7ba516834c682a66113eac163da85d3407087f19e80aba193f4ee81a8",
}
TOKEN_RE = re.compile(r"\w+|[^\w\s]+", re.UNICODE)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def byte_encoder():
    base = list(range(ord("!"), ord("~")+1)) + list(range(0xA1,0xAD)) + list(range(0xAE,0x100))
    values=base[:]; extra=0
    for value in range(256):
        if value not in base: base.append(value); values.append(256+extra); extra+=1
    return dict(zip(base,map(chr,values)))
ENC=byte_encoder()
def pretokenize(text): return ["".join(ENC[b] for b in (" "+m.group(0)).encode("utf-8")) for m in TOKEN_RE.finditer(text)]
def replay(text,merges):
    output=[]
    for word in pretokenize(text):
        pieces=list(word)
        for left,right in merges:
            new=[];i=0
            while i<len(pieces):
                if i+1<len(pieces) and pieces[i]==left and pieces[i+1]==right:new.append(left+right);i+=2
                else:new.append(pieces[i]);i+=1
            pieces=new
        output.extend(pieces)
    return output
def gini(values):
    assert sum(values)>0
    return sum(abs(x-y) for x in values for y in values)/(2*len(values)*sum(values))
def quantile(values,p):
    s=sorted(values); x=(len(s)-1)*p; lo=int(math.floor(x)); hi=int(math.ceil(x))
    return s[lo] if lo==hi else s[lo]*(hi-x)+s[hi]*(x-lo)

free=int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())
Path('output/eval_capacity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'free':free,'required':268435456},indent=2)+"\n")
assert free>=268435456,'memory_wait_required'
verification=json.loads(Path('output/pure_replay_verification.json').read_text());assert verification['status']=='PASS' and verification['integer_cost_checks']==14550
plan=json.loads(Path('flores_plan.json').read_text());assert plan['primary_contrast']==json.loads(Path('flores_plan.json').read_text())['primary_contrast']
archive=Path('inputs/flores200_dataset.tar.gz');assert sha(archive)==EXPECTED_ARCHIVE
texts={}
with tarfile.open(archive,'r:gz') as bundle:
    names=set(bundle.getnames())
    for lang,member in MEMBERS.items():
        assert member in names
        texts[lang]=bundle.extractfile(member).read().decode('utf-8').splitlines()
assert {len(v) for v in texts.values()}=={1012} and all(all(line for line in texts[lang]) for lang in LANGS)
out={}
for name in ['classical','hybrid']:
    code=Path('inputs')/f'{name}.codes';assert sha(code)==EXPECTED_CODES[name]
    merges=[tuple(line.split()) for line in code.read_text().splitlines() if line and not line.startswith('#')];assert len(merges)==1000
    costs=[[len(replay(texts[lang][i],merges)) for lang in LANGS] for i in range(1012)]
    totals=[sum(row[j] for row in costs) for j in range(3)];means=[x/1012 for x in totals]
    out[name]={'codes_sha256':sha(code),'n':1012,'merges':1000,'vocab':1256,'mean_tokens':dict(zip(LANGS,means)),'gini':gini(means),'worst_language':LANGS[means.index(max(means))],'worst_cost':max(means),'total_cost':sum(means),'mean_sentence_gini':sum(gini(row) for row in costs)/1012,'paired_costs':costs}
base=out['classical']
for name,a in out.items():
    a['gini_improvement_vs_classical']=base['gini']-a['gini'];a['total_cost_relative_change']=a['total_cost']/base['total_cost']-1;a['worst_cost_relative_change']=a['worst_cost']/base['worst_cost']-1
rng=random.Random(20261012);gains=[];total_changes=[]
for _ in range(2000):
    bt={name:[0,0,0] for name in out}
    for _ in range(1012):
        i=rng.randrange(1012)
        for name in out:
            row=out[name]['paired_costs'][i]
            for j in range(3):bt[name][j]+=row[j]
    gains.append(gini(bt['classical'])-gini(bt['hybrid']))
    total_changes.append(sum(bt['hybrid'])/sum(bt['classical'])-1)
out['hybrid']['paired_gain_bootstrap95']=[quantile(gains,.025),quantile(gains,.975)]
out['hybrid']['total_cost_change_bootstrap95']=[quantile(total_changes,.025),quantile(total_changes,.975)]
result={'arms':out,'primary':{'gain':out['hybrid']['gini_improvement_vs_classical'],'paired_gain_bootstrap95':out['hybrid']['paired_gain_bootstrap95']},'archive_sha256':EXPECTED_ARCHIVE,'plan_sha256':sha('flores_plan.json'),'split':'devtest','rows':1012,'bootstrap':{'replicates':2000,'seed':20261012,'unit':'aligned sentence','limitation':'article IDs unavailable; descriptive interval may understate article dependence'},'scope':'Second untouched aligned-domain fixed-model confirmation; primary Classical vs pre-existing 500-global hybrid only. No tuning after text access.','secondary_arms_status':'base/window/ratio deferred, not used for primary inference','raw_text_persisted':False}
Path('output/flores_primary.json').write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({name:{k:v for k,v in a.items() if k!='paired_costs'} for name,a in out.items()},indent=2))
