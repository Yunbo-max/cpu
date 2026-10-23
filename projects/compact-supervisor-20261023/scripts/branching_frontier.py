#!/usr/bin/env python3
"""Persistent research tree, separate from the historical linear science ledger.

This script is read-only unless explicitly called with advance. It does not
launch agents, sign off reviews, call a provider, or change resource authority.
The host integrator must CAS/commit the result to the actual research Git repo.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import tempfile
import os

STATE = 'research-state/counterexample/portfolio.json'
LOOP = 'research-state/continuous/loop.json'
SCHEMA = 'persistent-research-tree-v1'
STATUS = {'root', 'expanded', 'active', 'await', 'parked', 'focus', 'rejected'}
ACTORS = {'designer', 'reviewer', 'local'}
ACTIONS = {'deepen', 'branch', 'focus', 'park', 'await'}


class Invalid(ValueError):
    pass


def check(condition, reason):
    if not condition:
        raise Invalid(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n'


def checked_file(root, rel):
    check(isinstance(rel, str) and rel and not rel.startswith('/') and '\\' not in rel,
          'invalid evidence path')
    check(all(p not in ('..', '.') for p in Path(rel).parts), 'evidence path traversal')
    base = root.resolve(strict=True)
    target = root / rel
    check(target.resolve(strict=False).is_relative_to(base) and target.is_file(),
          'evidence missing or outside project')
    check(not target.is_symlink(), 'evidence is symlink')
    return target


def verify_evidence(root, evidence):
    check(isinstance(evidence, list), 'evidence list required')
    for e in evidence:
        check(isinstance(e, dict) and set(e) == {'path', 'sha256', 'kind'},
              'invalid evidence reference')
        check(e['kind'] in {'math', 'paper', 'code', 'experiment', 'search', 'other'},
              'bad evidence kind')
        content = checked_file(root, e['path']).read_bytes()
        check(digest(content) == e['sha256'], 'evidence digest mismatch: ' + e['path'])


def verify(tree, root, *, check_files=True):
    check(tree.get('schema') == SCHEMA, 'unexpected schema')
    check(tree.get('mode') == 'branching', 'tree not in branching mode')
    check(type(tree.get('revision')) is int and tree['revision'] >= 0, 'bad revision')
    check(type(tree.get('max_active')) is int and 1 <= tree['max_active'] <= 8,
          'invalid bounded active size')
    nodes = tree.get('nodes')
    check(isinstance(nodes, list) and nodes, 'nodes absent')
    by_id = {node.get('id'): node for node in nodes}
    check(len(by_id) == len(nodes), 'duplicate node IDs')
    check(all(isinstance(i, str) and i for i in by_id), 'invalid node ID')
    root_id = tree['root_id']
    check(root_id in by_id, 'missing root')
    check(by_id[root_id].get('parent_id') is None and by_id[root_id].get('status') == 'root',
          'invalid root')
    for node in nodes:
        check(node.get('status') in STATUS, 'invalid node status')
        check(node.get('next_actor') in ACTORS, 'invalid actor')
        check(isinstance(node.get('mechanism'), str) and node['mechanism'],
              'mechanism missing')
        check(isinstance(node.get('question'), str) and len(node['question']) >= 15,
              'question missing')
        check(isinstance(node.get('falsifier'), str) and len(node['falsifier']) >= 15,
              'falsifier missing')
        check(isinstance(node.get('evidence'), list), 'missing evidence list')
        check(isinstance(node.get('budget'), dict), 'missing budget')
        if check_files:
            verify_evidence(root, node['evidence'])
        cur = node
        seen = {node['id']}
        while cur['id'] != root_id:
            parent = cur.get('parent_id')
            check(parent in by_id, 'missing parent: ' + str(parent))
            check(parent not in seen, 'parent cycle')
            seen.add(parent)
            cur = by_id[parent]
        check(len(seen)-1 <= tree.get('max_depth', 4), 'depth exceeded')
    children = {}
    for node in nodes:
        if node['parent_id'] is not None:
            children.setdefault(node['parent_id'], []).append(node['id'])
    for parent_id, kids in children.items():
        check(by_id[parent_id]['status'] in {'root','expanded'},
              'a leaf cannot have children')
        check(len(kids) <= tree.get('max_children', 4), 'too many children')
    active = [n for n in nodes if n['status'] == 'active']
    check(len(active) <= tree['max_active'], 'active budget exceeded')
    declared = tree.get('active_frontier')
    check(isinstance(declared,list) and set(declared) == {n['id'] for n in active},
          'stale or incomplete active frontier')
    check(len(declared) == len(set(declared)), 'frontier has duplicates')
    mechanisms = [n['mechanism'] for n in active]
    check(len(set(mechanisms)) == len(mechanisms),
          'duplicate mechanisms in active leaves')
    check(all(n['id'] not in children for n in active), 'active parent not leaf')
    check(isinstance(tree.get('events'), list), 'missing event log')
    check(len(tree['events']) == tree['revision'], 'revision does not match events')
    loop = json.loads(checked_file(root, LOOP).read_text())
    check(loop['project_id'] == tree['project_id'] and loop['status'] == 'active',
          'parent project is paused or a different project')
    check(loop['mode'] == 'branching', 'parent linear ledger does not permit branching')
    check(loop['revision'] >= tree['adopted_loop_revision'], 'parent loop stale')
    check(tree.get('native_gpu_authorized') is False,
          'tree may not elevate inherited GPU authority')
    return {'revision': tree['revision'], 'active_leaves':len(active),
            'parked':sum(x['status']=='parked' for x in nodes),
            'await':sum(x['status']=='await' for x in nodes),
            'total_nodes':len(nodes), 'node_ids':sorted(by_id)}


def packet(tree, *, max_items=3):
    nodes = {n['id']:n for n in tree['nodes']}
    check(1 <= max_items <= tree['max_active'], 'invalid task count')
    active = [nodes[nid] for nid in tree['active_frontier']]
    active.sort(key=lambda n: (-n.get('priority', 0), n['id']))
    if active:
        pos = tree['wake_cursor'] % len(active)
        active = active[pos:] + active[:pos]
    out = []
    for n in active[:max_items]:
        check(n['next_actor'] == 'designer', 'active node requires external actor')
        ticket = digest(canonical({'node':n['id'],'question':n['question'],
                                  'tree_revision':tree['revision'],
                                  'project_parent':tree['adopted_project_commit']}).encode())[:20]
        out.append({'ticket_id':ticket,'node_id':n['id'],
                    'parent_id':n['parent_id'],'mechanism':n['mechanism'],
                    'question':n['question'],'falsifier':n['falsifier'],
                    'next_action':n['next_action'], 'budget':n['budget'],
                    'formal_review':n['formal_review']})
    return {'schema':'research-tree-manual-wake-ticket-v1',
            'project_id':tree['project_id'],'mode':'branching',
            'tree_revision':tree['revision'],
            'tree_checkpoint_sha256':digest(canonical(tree).encode()),
            'selected':out,'all_active':[n['id'] for n in active],
            'warning':'Tickets are read-only tasks, not launched agents or review receipts'}


def advance(tree, event, root):
    check(event['action'] in ACTIONS, 'unknown action')
    check(event['node_id'] in tree['active_frontier'], 'node not actively delegated')
    check(event['event_id'] not in [e['event_id'] for e in tree['events']],
          'replayed event')
    check(isinstance(event['causal_reason'],str) and len(event['causal_reason']) >= 20,
          'missing causal reason')
    evidence = event.get('evidence',[])
    verify_evidence(root,evidence)
    if event['action'] != 'await':
        check(len(evidence)>0, 'science change requires actual evidence')
        seen = {(e['path'],e['sha256']) for node in tree['nodes'] for e in node['evidence']}
        check(any((e['path'],e['sha256']) not in seen for e in evidence),
              'cannot advance a branch without new pinned evidence')
    else:
        check(event.get('waiting_for'), 'await requires actual blocker')
    result = json.loads(json.dumps(tree))
    node = next(n for n in result['nodes'] if n['id'] == event['node_id'])
    node['evidence'].extend(evidence)
    if event['action'] == 'branch':
        child = event.get('children')
        check(isinstance(child,list) and len(child)>=2, 'branch needs 2+ distinct children')
        node['status'] = 'expanded'
        result['active_frontier'].remove(node['id'])
        result['nodes'].extend(child)
        result['active_frontier'].extend(c['id'] for c in child if c.get('status')=='active')
    elif event['action'] == 'await':
        node['status'] = 'await'
        node['waiting_for'] = event['waiting_for']
        result['active_frontier'].remove(node['id'])
    elif event['action'] in ('park','focus'):
        node['status'] = 'parked' if event['action']=='park' else 'focus'
        result['active_frontier'].remove(node['id'])
    else:
        node['question'] = event['next_question']
        node['falsifier'] = event['next_falsifier']
        node['next_action'] = event['next_action']
    result['revision'] += 1
    result['wake_cursor'] += 1
    result['events'].append(event)
    verify(result,root)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('verify','packet','advance'))
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--max-items',type=int,default=3)
    parser.add_argument('--event',type=Path)
    parser.add_argument('--expect-revision',type=int)
    parser.add_argument('--expect-sha256')
    args=parser.parse_args()
    root=args.project.resolve(strict=True)
    path=checked_file(root,STATE)
    with (Path(tempfile.gettempdir())/'autopilot-branching-frontier.lock').open('a+') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        original=path.read_bytes()
        tree=json.loads(original)
        stats=verify(tree,root)
        if args.command=='verify':
            output=stats
        elif args.command=='packet':
            output=packet(tree,max_items=args.max_items)
        else:
            check(args.event is not None and args.expect_revision is not None
                  and args.expect_sha256 is not None, 'advance requires CAS and event')
            check(tree['revision']==args.expect_revision and
                  digest(original)==args.expect_sha256, 'stale tree checkpoint')
            event=json.loads(args.event.read_text())
            new=advance(tree,event,root)
            tmp=path.with_suffix('.pending')
            check(not tmp.exists(), 'pending write exists')
            tmp.write_text(canonical(new))
            os.replace(tmp,path)
            output={'result':'advanced','new_revision':new['revision'],
                    'sha256':digest(path.read_bytes())}
    print(canonical(output),end='')


if __name__=='__main__':
    try:
        main()
    except (Invalid, OSError, ValueError, KeyError) as e:
        raise SystemExit('ERROR: '+str(e))
