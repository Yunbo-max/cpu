import collections
import datetime
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path('.')
LANGS = ['en', 'fr', 'es']
ARMS = ['classical', 'hybrid', 'base']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gini(values):
    values = [float(x) for x in values]
    return sum(abs(a - b) for a in values for b in values) / (2 * len(values) * sum(values))


def byte_encoder():
    bs = list(range(ord('!'), ord('~') + 1)) + list(range(0xA1, 0xAD)) + list(range(0xAE, 0x100))
    cs = list(bs)
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, map(chr, cs)))


BYTE_ENC = byte_encoder()
WS_RE = re.compile(r'\w+|[^\w\s]+', re.UNICODE)


def pretokens(text):
    # Whitespace removes separators. ByteLevel defaults to add_prefix_space=True;
    # use_regex=False means one byte-encoded unit for each incoming split.
    ans = []
    for part in WS_RE.findall(text):
        ans.append(''.join(BYTE_ENC[b] for b in (' ' + part).encode('utf-8')))
    return ans


def load_dict(path):
    out = collections.Counter()
    for line in path.read_text(encoding='utf-8').splitlines():
        word, count = line.rsplit(' ', 1)
        out[tuple(word)] += int(count)
    return out


def load_codes(path):
    return [tuple(line.split(' ')) for line in path.read_text(encoding='utf-8').splitlines()
            if line and not line.startswith('#')]


def apply_merge(seq, pair):
    a, b = pair
    if len(seq) < 2 or a not in seq or b not in seq:
        return seq
    new = []
    i = 0
    changed = False
    while i < len(seq):
        if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
            new.append(a + b)
            i += 2
            changed = True
        else:
            new.append(seq[i])
            i += 1
    return tuple(new) if changed else seq


def merge_counter(counter, pair):
    out = collections.Counter()
    reduction = 0
    for seq, count in counter.items():
        new = apply_merge(seq, pair)
        reduction += (len(seq) - len(new)) * count
        out[new] += count
    return out, reduction


def lengths(counters):
    return [sum(len(seq) * count for seq, count in c.items()) for c in counters]


def checkpoint(rank, dev_lengths, n_rows):
    means = [v / n_rows for v in dev_lengths]
    return {
        'rank': rank,
        'dev_total_tokens': dict(zip(LANGS, dev_lengths)),
        'dev_mean_tokens': dict(zip(LANGS, means)),
        'gini': gini(means),
        'total_mean_cost': sum(means),
        'worst_language': LANGS[means.index(max(means))],
        'worst_mean_cost': max(means),
    }


def phase_summary(steps, start_rank, end_rank):
    selected = collections.Counter(s['selected_target'] for s in steps if s['selected_target'] is not None)
    train_owner = collections.Counter(s['train_effect_owner'] for s in steps)
    dev_owner = collections.Counter(s['dev_effect_owner'] for s in steps)
    train_reduction = [sum(s['train_reduction'][j] for s in steps) for j in range(3)]
    dev_reduction = [sum(s['dev_reduction'][j] for s in steps) for j in range(3)]
    target_match = [s for s in steps if s['selected_target'] is not None]
    run_lengths = []
    last = None
    run = 0
    for s in target_match:
        x = s['selected_target']
        if x == last:
            run += 1
        else:
            if run:
                run_lengths.append(run)
            last, run = x, 1
    if run:
        run_lengths.append(run)
    return {
        'ranks': [start_rank, end_rank],
        'merges': len(steps),
        'train_reduction': dict(zip(LANGS, train_reduction)),
        'dev_reduction': dict(zip(LANGS, dev_reduction)),
        'selected_target_counts': dict(selected),
        'train_effect_owner_counts': dict(train_owner),
        'dev_effect_owner_counts': dict(dev_owner),
        'selected_target_is_dev_effect_owner': sum(s['selected_target'] == s['dev_effect_owner'] for s in target_match),
        'selected_target_has_positive_dev_effect': sum(s['dev_reduction'][LANGS.index(s['selected_target'])] > 0 for s in target_match),
        'targeted_merges': len(target_match),
        'target_switches': sum(a['selected_target'] != b['selected_target'] for a, b in zip(target_match, target_match[1:])),
        'max_consecutive_target_run': max(run_lengths, default=0),
        'gini_worsening_steps': sum(s['gini_after'] > s['gini_before'] + 1e-15 for s in steps),
        'pairwise_gap_sign_crossings': sum(s['pairwise_gap_sign_crossings'] for s in steps),
    }


def replay_arm(name, codes, train_initial, dev_initial, n_rows):
    train = [c.copy() for c in train_initial]
    dev = [c.copy() for c in dev_initial]
    train_initial_lengths = lengths(train)
    checkpoints = {'0': checkpoint(0, lengths(dev), n_rows)}
    steps = []
    prior_signs = None
    for idx, pair in enumerate(codes, start=1):
        before_dev = lengths(dev)
        before_means = [x / n_rows for x in before_dev]
        before_gini = gini(before_means)
        selected_target = None
        if name == 'base' or (name == 'hybrid' and idx > 500):
            selected_target = LANGS[max(range(3), key=lambda j: before_dev[j])]
        train_red = []
        dev_red = []
        for j in range(3):
            train[j], r = merge_counter(train[j], pair)
            train_red.append(r)
            dev[j], r = merge_counter(dev[j], pair)
            dev_red.append(r)
        after_dev = [before_dev[j] - dev_red[j] for j in range(3)]
        assert after_dev == lengths(dev)
        after_means = [x / n_rows for x in after_dev]
        pair_gaps = [after_dev[0] - after_dev[1], after_dev[0] - after_dev[2], after_dev[1] - after_dev[2]]
        signs = [0 if x == 0 else (1 if x > 0 else -1) for x in pair_gaps]
        crossings = 0 if prior_signs is None else sum(a and b and a != b for a, b in zip(prior_signs, signs))
        prior_signs = signs
        normalized_train = [train_red[j] / train_initial_lengths[j] for j in range(3)]
        steps.append({
            'rank': idx,
            'pair': list(pair),
            'selected_target': selected_target,
            'train_reduction': train_red,
            'dev_reduction': dev_red,
            'train_effect_owner': LANGS[max(range(3), key=lambda j: train_red[j])],
            'normalized_train_effect_owner': LANGS[max(range(3), key=lambda j: normalized_train[j])],
            'dev_effect_owner': LANGS[max(range(3), key=lambda j: dev_red[j])],
            'dev_lengths_before': before_dev,
            'dev_lengths_after': after_dev,
            'gini_before': before_gini,
            'gini_after': gini(after_means),
            'pairwise_gap_sign_crossings': crossings,
        })
        if idx in (500, 1000):
            checkpoints[str(idx)] = checkpoint(idx, after_dev, n_rows)
    return {
        'codes_sha256': sha(ROOT / 'inputs' / f'{name}.codes'),
        'initial_train_lengths': dict(zip(LANGS, train_initial_lengths)),
        'checkpoints': checkpoints,
        'phases': {
            'prefix_1_500': phase_summary(steps[:500], 1, 500),
            'tail_501_1000': phase_summary(steps[500:], 501, 1000),
            'all_1_1000': phase_summary(steps, 1, 1000),
        },
        'steps': steps,
    }


def main():
    mem_max = int(Path('/sys/fs/cgroup/memory.max').read_text())
    mem_cur = int(Path('/sys/fs/cgroup/memory.current').read_text())
    required = 512 * 1024 * 1024
    assert mem_max - mem_cur >= required, (mem_max, mem_cur, required)
    train = [load_dict(ROOT / 'inputs' / f'{lang}.dict') for lang in LANGS]
    rows = json.loads((ROOT / 'inputs/dev.json').read_text(encoding='utf-8'))
    dev = []
    for lang in LANGS:
        c = collections.Counter()
        for row in rows:
            for word in pretokens(row[lang]):
                c[tuple(word)] += 1
        dev.append(c)
    codes = {name: load_codes(ROOT / 'inputs' / f'{name}.codes') for name in ARMS}
    assert all(len(x) == 1000 for x in codes.values())
    common_prefix = next((i for i, (a, b) in enumerate(zip(codes['classical'], codes['hybrid'])) if a != b), 1000)
    assert common_prefix == 500
    arms = {name: replay_arm(name, codes[name], train, dev, len(rows)) for name in ARMS}
    frozen = json.loads((ROOT / 'inputs/wake16b_evaluation.json').read_text())['arms']
    final_validation = {}
    for name in ARMS:
        got = arms[name]['checkpoints']['1000']['dev_mean_tokens']
        expected = frozen[name]['mean_tokens']
        diffs = {lang: got[lang] - expected[lang] for lang in LANGS}
        assert max(abs(v) for v in diffs.values()) < 1e-12, (name, got, expected)
        final_validation[name] = {'expected': expected, 'replayed': got, 'differences': diffs}
    shared = arms['classical']['checkpoints']['500']
    assert shared == arms['hybrid']['checkpoints']['500']
    compact = {}
    for name, arm in arms.items():
        compact[name] = {k: v for k, v in arm.items() if k != 'steps'}
    result = {
        'schema_version': 1,
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Fixed-code mechanism audit on exposed TICO development data; no fresh confirmation or tuning claim.',
        'languages': LANGS,
        'rows': len(rows),
        'hybrid_classical_common_prefix_merges': common_prefix,
        'inputs': {p.name: sha(p) for p in sorted((ROOT / 'inputs').iterdir())},
        'pretokenization_validation': final_validation,
        'arms': compact,
    }
    raw = {'schema_version': 1, 'arms': {name: arm['steps'] for name, arm in arms.items()}}
    (ROOT / 'output/mechanism_raw.json').write_text(json.dumps(raw, separators=(',', ':')) + '\n')
    (ROOT / 'output/mechanism_summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
