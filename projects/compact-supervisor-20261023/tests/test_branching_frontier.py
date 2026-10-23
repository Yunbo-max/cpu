import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from branching_frontier import verify, packet, advance, Invalid


def ref(root, name, text):
    path=root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text)
    return {'path':name,'sha256':hashlib.sha256(text.encode()).hexdigest(),'kind':'math'}


class FrontierTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        p=self.root/'research-state/continuous/loop.json'
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({'project_id':'test','status':'active','mode':'branching','revision':5}))
        self.refs=[ref(self.root,f'evidence/{i}.txt',f'proof-{i}') for i in range(5)]
        def node(id,parent,status,mechanism,evidence):
            return dict(id=id,parent_id=parent,status=status,mechanism=mechanism,
                question='Can this mechanism be distinguished from the baseline?',
                falsifier='Existing baseline fully explains all of the observations',
                next_actor='designer',next_action='read two sources',budget={'gpu':False},
                formal_review='pending',evidence=evidence)
        self.tree={
            'schema':'persistent-research-tree-v1','mode':'branching','project_id':'test',
            'root_id':'root','revision':0,'events':[],'adopted_loop_revision':5,
            'adopted_project_commit':'a'*40,'wake_cursor':0,'max_active':3,
            'max_children':4,'max_depth':4,'native_gpu_authorized':False,
            'active_frontier':['G1','G2','G3'],
            'nodes':[node('root',None,'root','programme',[]),
                     node('graph','root','expanded','flow-condensation',[]),
                     node('G1','graph','active','entropy',[self.refs[0]]),
                     node('G2','graph','active','high-order',[self.refs[1]]),
                     node('G3','graph','active','identity',[self.refs[2]])]}
    def tearDown(self):
        self.tmp.cleanup()

    def test_multi_frontier_restores_and_selects_three(self):
        result=verify(self.tree,self.root)
        self.assertEqual(result['active_leaves'],3)
        first=packet(self.tree,max_items=3)
        self.assertEqual(len(first['selected']),3)
        self.assertEqual(len({n['mechanism'] for n in first['selected']}),3)
        self.assertEqual(first,packet(self.tree,max_items=3))

    def test_depth_and_cycle_invalid(self):
        t=copy.deepcopy(self.tree)
        t['nodes'][1]['parent_id']='G1'
        with self.assertRaises(Invalid):verify(t,self.root)

    def test_duplicate_mechanism_invalid(self):
        t=copy.deepcopy(self.tree)
        t['nodes'][-1]['mechanism']='entropy'
        with self.assertRaises(Invalid):verify(t,self.root)

    def test_no_evidence_no_progress(self):
        ev={'event_id':'event-1','node_id':'G1','action':'deepen',
            'causal_reason':'Observed a nontrivial difference in two mechanisms',
            'evidence':[],'next_question':'How large is the gap?',
            'next_falsifier':'No measurable gap','next_action':'read source'}
        with self.assertRaises(Invalid):advance(self.tree,ev,self.root)

    def test_park_does_not_change_siblings_and_blocks_replay(self):
        ev={'event_id':'event-2','node_id':'G1','action':'park',
            'causal_reason':'Closer prior shows exact overlap in the claimed method',
            'evidence':[self.refs[3]]}
        result=advance(self.tree,ev,self.root)
        self.assertEqual(result['active_frontier'],['G2','G3'])
        self.assertEqual(result['revision'],1)
        self.assertEqual(result['nodes'][2]['status'],'parked')
        self.assertEqual(result['nodes'][3]['status'],'active')
        self.assertEqual(len(result['events']),1)
        with self.assertRaises(Invalid):advance(result,ev,self.root)

    def test_spawn_children_requires_room_and_proof(self):
        t=copy.deepcopy(self.tree)
        t['nodes'][-1]['status']='parked'
        t['active_frontier'].remove('G3')
        t['max_active']=3
        def child(i):
            return dict(id=i,parent_id='G1',status='active',mechanism=i,
                question='Does a distinct formal mechanism apply to this case?',
                falsifier='Independent counterexample invalidates the hypothesis',
                next_actor='designer',next_action='paper check',budget={'gpu':False},
                formal_review='pending',evidence=[])
        ev={'event_id':'event-branch','node_id':'G1','action':'branch',
            'causal_reason':'Two genuinely distinguishable cases were found in a proof',
            'evidence':[self.refs[3]],'children':[child('G1a'),child('G1b')]}
        result=advance(t,ev,self.root)
        self.assertEqual(set(result['active_frontier']),{'G1a','G1b','G2'})
        self.assertEqual(result['nodes'][2]['status'],'expanded')
        bad=copy.deepcopy(self.tree)
        with self.assertRaises(Invalid):advance(bad,ev,self.root)

    def test_pause_from_parent_blocks_everything(self):
        p=self.root/'research-state/continuous/loop.json'
        p.write_text(json.dumps({'project_id':'test','status':'paused','mode':'branching','revision':5}))
        with self.assertRaises(Invalid):verify(self.tree,self.root)

    def test_file_mutation_is_detected(self):
        (self.root/self.refs[0]['path']).write_text('mutated')
        with self.assertRaises(Invalid):verify(self.tree,self.root)


if __name__=='__main__':unittest.main()
