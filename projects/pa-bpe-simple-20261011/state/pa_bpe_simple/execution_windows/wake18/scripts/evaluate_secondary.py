import hashlib, json, math, random, re, tarfile, datetime
from pathlib import Path

LANGS = ["en", "fr", "es"]
MEMBERS = {"en": "./flores200_dataset/devtest/eng_Latn.devtest", "fr": "./flores200_dataset/devtest/fra_Latn.devtest", "es": "./flores200_dataset/devtest/spa_Latn.devtest"}
EXPECTED_ARCHIVE = "b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6"
EXPECTED = {"base": "7e66fdd777005503c69b44f27ed58a591a9772309864f53f33a8333e1b4f5c7f", "window": "12d283dcfd73cca42b21b19fe25ec004ee5c4b1e81cdc151f3dcd11d27a561aa", "ratio": "6f67e4c4d5190b9db89465e055837d01a9f38e5b69c541c8b73deb693e04a068"}
TOKEN_RE = re.compile(r"\w+|[^\w\s]+", re.UNICODE)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def byte_encoder():
    base = list(range(ord("!"), ord("~") + 1)) + list(range(0xA1, 0xAD)) + list(range(0xAE, 0x100))
    values = base[:]; extra = 0
    for value in range(256):
        if value not in base: base.append(value); values.append(256 + extra); extra += 1
    return dict(zip(base, map(chr, values)))
ENC = byte_encoder()
def pretokenize(text): return ["".join(ENC[b] for b in (" " + m.group(0)).encode("utf-8")) for m in TOKEN_RE.finditer(text)]
def replay(text, merges):
    output = []
    for word in pretokenize(text):
        pieces = list(word)
        for left, right in merges:
            new = []; i = 0
            while i < len(pieces):
                if i + 1 < len(pieces) and pieces[i] == left and pieces[i + 1] == right: new.append(left + right); i += 2
                else: new.append(pieces[i]); i += 1
            pieces = new
        output.extend(pieces)
    return output
def gini(values): return sum(abs(x-y) for x in values for y in values) / (2 * len(values) * sum(values))
def quantile(values, p):
    s = sorted(values); x = (len(s)-1)*p; lo = int(math.floor(x)); hi = int(math.ceil(x))
    return s[lo] if lo == hi else s[lo]*(hi-x) + s[hi]*(x-lo)

free = int(Path('/sys/fs/cgroup/memory.max').read_text()) - int(Path('/sys/fs/cgroup/memory.current').read_text())
Path('output/eval_capacity.json').write_text(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'free': free, 'required': 268435456}, indent=2) + "\n")
assert free >= 268435456, 'memory_wait_required'
archive = Path('inputs/flores200_dataset.tar.gz'); assert sha(archive) == EXPECTED_ARCHIVE
with tarfile.open(archive, 'r:gz') as bundle:
    texts = {lang: bundle.extractfile(member).read().decode('utf-8').splitlines() for lang, member in MEMBERS.items()}
assert {len(v) for v in texts.values()} == {1012} and all(all(row for row in values) for values in texts.values())
primary = json.loads(Path('inputs/flores_primary.json').read_text())
assert primary['rows'] == 1012 and primary['archive_sha256'] == EXPECTED_ARCHIVE
arms = {name: primary['arms'][name] for name in ['classical', 'hybrid']}
for name in ['base', 'window', 'ratio']:
    code = Path('inputs') / f'{name}.codes'; assert sha(code) == EXPECTED[name]
    merges = [tuple(line.split()) for line in code.read_text().splitlines() if line and not line.startswith('#')]; assert len(merges) == 1000
    costs = [[len(replay(texts[lang][i], merges)) for lang in LANGS] for i in range(1012)]
    means = [sum(row[j] for row in costs) / 1012 for j in range(3)]
    arms[name] = {'codes_sha256': sha(code), 'n': 1012, 'merges': 1000, 'vocab': 1256, 'mean_tokens': dict(zip(LANGS, means)), 'gini': gini(means), 'worst_language': LANGS[means.index(max(means))], 'worst_cost': max(means), 'total_cost': sum(means), 'mean_sentence_gini': sum(gini(row) for row in costs) / 1012, 'paired_costs': costs}
base = arms['classical']
for name, arm in arms.items():
    arm['gini_improvement_vs_classical'] = base['gini'] - arm['gini']
    arm['total_cost_relative_change'] = arm['total_cost'] / base['total_cost'] - 1
    arm['worst_cost_relative_change'] = arm['worst_cost'] / base['worst_cost'] - 1
rng = random.Random(20261012); boot = {name: {'gain': [], 'total': []} for name in ['base', 'window', 'ratio']}
for _ in range(2000):
    sums = {name: [0, 0, 0] for name in ['classical', 'base', 'window', 'ratio']}
    for _ in range(1012):
        i = rng.randrange(1012)
        for name in sums:
            for j, value in enumerate(arms[name]['paired_costs'][i]): sums[name][j] += value
    for name in boot:
        boot[name]['gain'].append(gini(sums['classical']) - gini(sums[name]))
        boot[name]['total'].append(sum(sums[name]) / sum(sums['classical']) - 1)
for name in boot:
    arms[name]['paired_gain_bootstrap95'] = [quantile(boot[name]['gain'], .025), quantile(boot[name]['gain'], .975)]
    arms[name]['total_cost_change_bootstrap95'] = [quantile(boot[name]['total'], .025), quantile(boot[name]['total'], .975)]
hybrid = arms['hybrid']
pareto = {name: {'beats_hybrid_fairness': arms[name]['gini'] < hybrid['gini'], 'no_more_total_cost_than_hybrid': arms[name]['total_cost'] <= hybrid['total_cost'], 'no_more_worst_cost_than_hybrid': arms[name]['worst_cost'] <= hybrid['worst_cost']} for name in ['base', 'window', 'ratio']}
result = {'plan_sha256': sha('secondary_plan.json'), 'archive_sha256': EXPECTED_ARCHIVE, 'rows': 1012, 'arms': arms, 'pareto_vs_hybrid': pareto, 'bootstrap': {'replicates': 2000, 'seed': 20261012, 'unit': 'aligned sentence'}, 'scope': 'Retrospective fixed-arm descriptive analysis on exposed FLORES; no tuning or fresh-confirmation claim.', 'raw_text_persisted': False}
Path('output/flores_secondary.json').write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({'arms': {name: {k:v for k,v in arm.items() if k != 'paired_costs'} for name, arm in arms.items()}, 'pareto_vs_hybrid': pareto}, indent=2))
