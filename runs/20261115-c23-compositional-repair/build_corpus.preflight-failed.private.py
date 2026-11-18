#!/usr/bin/env python3
"""C23 private author constructor. Do not disclose before public annotation freeze.

No production scorer, verifier, model response, metrics or inference imported.
Finite quality checks are implemented here. Historical input paths are closed.
"""
import collections
import datetime
import hashlib
import itertools
import json
from pathlib import Path
import random
import signal
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAX_ATTEMPTS = 50000
SECONDS = 300
BASE_SEED = 202611160023
FAMILY_KEYS = {'B':'budget','L':'min_count','U':'max_count','M':'required',
               'F':'forbidden','I':'implications'}
FAMILY_BITS = {'E':1,'B':2,'L':4,'U':8,'M':16,'F':32,'I':64}
GROUPS = [
    dict(key='p01',n=6,families='I',motif='three_arc_path',arcs=[[0,1],[1,2],[2,3]]),
    dict(key='p02',n=6,families='BI',motif='out_star',arcs=[[0,1],[0,2],[0,3]]),
    dict(key='p03',n=6,families='IL',motif='in_star',arcs=[[0,3],[1,3],[2,3]]),
    dict(key='p04',n=6,families='IU',motif='branch_after_arc',arcs=[[0,1],[1,2],[1,3]]),
    dict(key='p05',n=6,families='IM',motif='directed_three_cycle',arcs=[[0,1],[1,2],[2,0]],required=[4]),
    dict(key='p06',n=7,families='FI',motif='reciprocal_pair_disjoint_arc',arcs=[[0,1],[1,0],[2,3]],forbidden=[6]),
    dict(key='p07',n=7,families='BILU',motif='three_disjoint_arcs',arcs=[[0,1],[2,3],[4,5]]),
    dict(key='p08',n=7,families='BILM',motif='fork_with_extension',arcs=[[0,1],[0,2],[1,3]],required=[5]),
    dict(key='p09',n=7,families='FILMU',motif='shared_consequent_disjoint_arc',arcs=[[0,2],[1,2],[3,4]],required=[5],forbidden=[6],fixed=True),
    dict(key='p10',n=7,families='BFILMU',motif='dense_reciprocal_pair_disjoint_arc',arcs=[[0,1],[1,0],[2,3]],required=[4],forbidden=[6],fixed=True),
]


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path,value):
    with Path(path).open('x') as handle:
        handle.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def empty():
    return dict(budget=None,min_count=None,max_count=None,required=[],forbidden=[],implications=[])


def flags(data,spec,mask):
    chosen={i for i in range(data['n']) if (mask>>i)&1}
    edge_bad=sum(1<<j for j,(u,v) in enumerate(data['edges']) if u in chosen and v in chosen)
    imp_bad=sum(1<<j for j,(u,v) in enumerate(spec['implications']) if u in chosen and v not in chosen)
    f=FAMILY_BITS['E'] if edge_bad else 0
    if spec['budget'] is not None and sum(data['costs'][i] for i in chosen)>spec['budget']:f|=FAMILY_BITS['B']
    if spec['min_count'] is not None and len(chosen)<spec['min_count']:f|=FAMILY_BITS['L']
    if spec['max_count'] is not None and len(chosen)>spec['max_count']:f|=FAMILY_BITS['U']
    if not set(spec['required'])<=chosen:f|=FAMILY_BITS['M']
    if set(spec['forbidden'])&chosen:f|=FAMILY_BITS['F']
    if imp_bad:f|=FAMILY_BITS['I']
    return f,imp_bad,edge_bad


def active_families(spec):
    return ['E']+[f for f,k in FAMILY_KEYS.items() if spec[k] is not None and spec[k]!=[]]


def quality(data,spec):
    if len(spec['implications'])!=3 or len({tuple(a) for a in spec['implications']})!=3:
        return None,'implication_count'
    outcomes=[flags(data,spec,m) for m in range(1<<data['n'])]
    accepted=[m for m,row in enumerate(outcomes) if row[0]==0]
    if not accepted:return None,'infeasible'
    families={}
    for family in active_families(spec):
        additional=[m for m,row in enumerate(outcomes) if row[0]==FAMILY_BITS[family]]
        if not additional:return None,'inactive_family_'+family
        families[family]=dict(additional_masks=additional,witness_mask=additional[0])
    implications=[]
    for j in range(3):
        additional=[m for m,row in enumerate(outcomes) if row[0]==FAMILY_BITS['I'] and row[1]==1<<j]
        if not additional:return None,'inactive_implication_'+str(j)
        implications.append(dict(implication=spec['implications'][j],additional_masks=additional,witness_mask=additional[0]))
    edges=[]
    for j in range(len(data['edges'])):
        additional=[m for m,row in enumerate(outcomes) if row[0]==FAMILY_BITS['E'] and row[2]==1<<j]
        if not additional:return None,'inactive_edge_'+str(j)
        edges.append(dict(edge=data['edges'][j],additional_masks=additional,witness_mask=additional[0]))
    values={m:sum(w for i,w in enumerate(data['weights']) if (m>>i)&1) for m in accepted}
    best=max(values.values())
    return dict(feasible_masks=accepted,feasible_count=len(accepted),max_weight=best,
                optimal_masks=[m for m in accepted if values[m]==best],family_removal=families,
                implication_removal=implications,edge_removal=edges,assignments=1<<data['n']),None


def graph_key(data):
    return canonical(dict(n=data['n'],edges=sorted(sorted(edge) for edge in data['edges'])))


def history():
    public_paths=[]
    for cycle in ['20261114-c15-formulation-repair','20261115-c16-quantized-repair','20261115-c19-instruct-repair']:
        for split in ['dev','test']:
            p=ROOT/'runs'/cycle/(split+'_cases.json')
            if p.exists():public_paths.append(p)
    for cycle in ['20261115-c20-grounded-edits','20261115-c21-tool-grounded-edits']:
        p=ROOT/'runs'/cycle/'probe_cases.json'
        if p.exists():public_paths.append(p)
    publics=[case for p in public_paths for case in json.loads(p.read_text())]
    gold_paths=[ROOT/'runs'/cycle/'private_gold.review.json' for cycle in ['20261114-c15-formulation-repair','20261115-c16-quantized-repair','20261115-c19-instruct-repair']]
    counts=[len(row['constraints']['implications']) for p in gold_paths for row in json.loads(p.read_text())['cases']]
    if max(counts)>2:raise ValueError('historical annotation has more than two implications')
    return publics,{str(p.relative_to(ROOT)):sha(p) for p in public_paths+gold_paths},max(counts)


def draw(group,rng):
    n=group['n'];data=dict(n=n,weights=[rng.randint(17,61) for _ in range(n)],costs=[rng.randint(13,39) for _ in range(n)],edges=[])
    spec=empty();spec.update(required=group.get('required',[])[:],forbidden=group.get('forbidden',[])[:],implications=copy_arcs(group['arcs']))
    if group['key']=='p09':
        data['edges']=[[0,1]];spec.update(min_count=2,max_count=4)
    elif group['key']=='p10':
        pair=[rng.randint(13,16),rng.randint(13,16)];ante=rng.randint(36,39);conseq=rng.randint(13,16);mandatory=rng.randint(13,39)
        allowance=rng.randint(max(sum(pair)+conseq,ante),ante+conseq-1)
        data['costs']=pair+[ante,conseq,mandatory,rng.randint(13,24),rng.randint(13,24)]
        data['edges']=[[4,5]];spec.update(budget=mandatory+allowance,min_count=2,max_count=3)
    else:
        pairs=[list(pair) for pair in itertools.combinations(range(n),2) if not set(pair)&set(spec['forbidden'])]
        data['edges']=sorted(rng.sample(pairs,rng.randint(1,3)))
        baseline=[m for m in range(1<<n) if flags(data,spec,m)[0]==0]
        if not baseline:return data,spec,'empty_structural_domain'
        sizes=[m.bit_count() if hasattr(int,'bit_count') else bin(m).count('1') for m in baseline]
        minimum,maximum=min(sizes),max(sizes)
        if 'L' in group['families']:
            if minimum>=maximum:return data,spec,'no_lower_bound_interval'
            spec['min_count']=rng.randint(minimum+1,maximum)
        if 'U' in group['families']:
            low=max(minimum,spec['min_count'] or 0)
            if low>=maximum:return data,spec,'no_upper_bound_interval'
            spec['max_count']=rng.randint(low,maximum-1)
        counted=[m for m in baseline if flags(data,spec,m)[0]==0]
        if not counted:return data,spec,'empty_count_domain'
        if 'B' in group['families']:
            costs=sorted({sum(c for i,c in enumerate(data['costs']) if (m>>i)&1) for m in counted})
            if len(costs)<2:return data,spec,'no_budget_interval'
            spec['budget']=rng.choice(costs[:-1])
    return data,spec,None


def copy_arcs(arcs):
    return [row[:] for row in arcs]


def permute(data,spec,rng):
    n=data['n'];p=list(range(n));rng.shuffle(p)
    result=dict(n=n,weights=[0]*n,costs=[0]*n,edges=sorted(sorted([p[u],p[v]]) for u,v in data['edges']))
    for k in ('weights','costs'):
        for i,v in enumerate(data[k]):result[k][p[i]]=v
    target=dict(spec,required=sorted(p[i] for i in spec['required']),forbidden=sorted(p[i] for i in spec['forbidden']),implications=[[p[u],p[v]] for u,v in spec['implications']])
    rng.shuffle(target['implications'])
    return result,target


def render(identifier,lang,data,spec,group_index,rng):
    n=data['n'];clauses=[]
    if lang=='fr':
        openings=['Préparez le portefeuille de projets','Établissez la liste des expériences','Décidez quelles interventions financer','Choisissez les campagnes à retenir','Arrêtez le programme des ateliers','Constituez le lot de missions','Déterminez le sous-ensemble des études','Sélectionnez les activités du dossier','Planifiez les démonstrations retenues','Fixez le portefeuille des propositions']
        first=openings[group_index]+' pour le dossier '+identifier+'. '
        first+=f'Il existe {n} possibilités, d\'indices 0 à {n-1}. Chaque variable x_i est binaire; x_i=1 signifie que la possibilité i est choisie. Maximiser la somme des valeurs weights[i] des possibilités choisies. '
        first+='Les données edges énumèrent les seules incompatibilités : pour chacune de ces paires, ses deux indices ne peuvent pas être choisis simultanément. '
        if spec['budget'] is not None:clauses.append(f'La somme des coûts costs[i] des possibilités choisies doit être au plus {spec["budget"]}, égalité autorisée.')
        if spec['min_count'] is not None:clauses.append(f'Le nombre total de possibilités choisies doit être au moins {spec["min_count"]}.')
        if spec['max_count'] is not None:clauses.append(f'Il est permis de choisir au plus {spec["max_count"]} possibilités au total.')
        for i in spec['required']:clauses.append(f'La possibilité {i} doit être choisie.')
        for i in spec['forbidden']:clauses.append(f'La possibilité {i} est interdite.')
        implication_forms=['Choisir la possibilité {u} oblige à choisir aussi la possibilité {v}.','Si la possibilité {u} est retenue, la possibilité {v} doit également être retenue.','La sélection de la possibilité {u} requiert celle de la possibilité {v}.']
        clauses.extend(implication_forms[j].format(u=u,v=v) for j,(u,v) in enumerate(spec['implications']))
        last=' Ces restrictions sont exhaustives : ne pas ajouter de condition qui ne soit pas énoncée.'
    else:
        openings=['Prepare a portfolio of projects','Set the programme of experiments','Decide which interventions to support','Choose the campaigns to retain','Finalize the schedule of workshops','Assemble the set of missions','Determine the selected studies','Select the activities for review','Plan the retained demonstrations','Fix the portfolio of proposals']
        first=openings[group_index]+' for file '+identifier+'. '
        first+=f'There are {n} options with indices 0 through {n-1}. Every variable x_i is binary; x_i=1 means that option i is selected. Maximize the sum of weights[i] over the selected options. '
        first+='The edges data list the only incompatibilities: the two indices of each such pair cannot both be selected. '
        if spec['budget'] is not None:clauses.append(f'The sum of costs[i] over selected options must be at most {spec["budget"]}, including equality.')
        if spec['min_count'] is not None:clauses.append(f'At least {spec["min_count"]} options must be selected in total.')
        if spec['max_count'] is not None:clauses.append(f'Select no more than {spec["max_count"]} options in total.')
        for i in spec['required']:clauses.append(f'Option {i} must be selected.')
        for i in spec['forbidden']:clauses.append(f'Option {i} is forbidden.')
        implication_forms=['Selecting option {u} requires selecting option {v}.','If option {u} is selected, option {v} must also be selected.','Selection of option {u} is conditional on selection of option {v}.']
        clauses.extend(implication_forms[j].format(u=u,v=v) for j,(u,v) in enumerate(spec['implications']))
        last=' These requirements are exhaustive: do not add any condition that is not stated.'
    rng.shuffle(clauses)
    return first+' '.join(clauses)+last


def main():
    started=time.monotonic();status_path=HERE/'construction-status.private.json'
    for p in [HERE/'test_cases.json',HERE/'private_gold.author.json',HERE/'construction-attempts.private.jsonl',status_path]:
        if p.exists():raise ValueError('refuse overwrite '+p.name)
    def timeout(_s,_f):raise TimeoutError('global300s author construction bound')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(SECONDS)
    previous,pins,old_max=history();seen_graphs={graph_key(c['data']) for c in previous};seen_data={digest(c['data']) for c in previous};seen_ids={c['id'] for c in previous};seen_texts={c['intention'] for c in previous};public=[];gold=[];attempts=[];failures=collections.Counter();slot=0
    status=dict(status='running',created_local_date='2026-11-16',timezone='Europe/Paris',run_identifier='20261115-c23-compositional-repair',seed=BASE_SEED,max_attempts_per_case=MAX_ATTEMPTS,wall_seconds_limit=SECONDS,historical_max_implications=old_max,history_sha256=pins,groups=GROUPS)
    with (HERE/'construction-attempts.private.jsonl').open('x') as log:
        try:
            for group_index,group in enumerate(GROUPS):
                for lang in ['fr','en']:
                    slot+=1;rng=random.Random(BASE_SEED+slot*100003);identifier=hashlib.sha256(('C23-opaque-'+str(BASE_SEED)+'-'+str(slot)).encode()).hexdigest()[:12]
                    if identifier in seen_ids:raise ValueError('opaque ID collision')
                    accepted=False
                    for attempt in range(1,MAX_ATTEMPTS+1):
                        data,spec,reason=draw(group,rng)
                        if reason is None:
                            data,spec=permute(data,spec,rng);certificate,reason=quality(data,spec)
                        if reason is None and graph_key(data) in seen_graphs:reason='historical_or_intra_graph_collision'
                        if reason is None and digest(data) in seen_data:reason='historical_or_intra_data_collision'
                        if reason is None:
                            intention=render(identifier,lang,data,spec,group_index,rng)
                            if intention in seen_texts:reason='historical_or_intra_text_collision'
                        record=dict(slot=slot,attempt=attempt,candidate_digest=digest(dict(data=data,constraints=spec)),disposition='rejected' if reason else 'accepted',reason=reason)
                        log.write(canonical(record)+'\n')
                        if reason:
                            failures[reason]+=1;continue
                        public.append(dict(id=identifier,language=lang,intention=intention,data=data))
                        gold.append(dict(id=identifier,split='test',language=lang,group=group['key'],motif=group['motif'],constraints=spec,author_certificate=certificate,accepted_attempt=attempt,seed=BASE_SEED+slot*100003))
                        attempts.append(dict(slot=slot,attempts=attempt,rejections=attempt-1));seen_graphs.add(graph_key(data));seen_data.add(digest(data));seen_ids.add(identifier);seen_texts.add(intention);accepted=True;log.flush();break
                    if not accepted:raise RuntimeError('bounded search exhausted slot '+str(slot))
            assert len(public)==20 and collections.Counter(c['language'] for c in public)=={'fr':10,'en':10}
            assert collections.Counter(c['data']['n'] for c in public)=={6:10,7:10}
            assert all(len(c['constraints']['implications'])==3 and c['author_certificate']['feasible_count']>0 for c in gold)
            assert all(quality(c['data'],g['constraints'])[0]==g['author_certificate'] for c,g in zip(public,gold))
            public.sort(key=lambda c:c['id']);gold.sort(key=lambda c:c['id'])
            dump(HERE/'private_gold.author.json',dict(created_local_date='2026-11-16',private_until_reviewer_annotation_freeze=True,cases=gold))
            dump(HERE/'test_cases.json',public)
            status.update(status='completed',cases=20,languages={'fr':10,'en':10},sizes={'6':10,'7':10},all_feasible=True,individual_implications_active=60,all_present_families_active=True,all_individual_edges_active=True,all_labeled_graphs_new=True,attempts=attempts,rejections_by_reason=dict(failures),total_candidates=sum(a['attempts'] for a in attempts),public_sha256=sha(HERE/'test_cases.json'))
        except BaseException as exc:
            status.update(status='failed',error=type(exc).__name__+': '+str(exc),completed_private_cases=gold,completed_slots=len(gold),attempts=attempts,rejections_by_reason=dict(failures))
            raise
        finally:
            signal.alarm(0);status['elapsed_seconds']=time.monotonic()-started;status['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();status['builder_sha256']=sha(__file__);dump(status_path,status)
    print(canonical({k:status[k] for k in ['status','cases','languages','sizes','all_feasible','individual_implications_active','all_present_families_active','all_individual_edges_active','all_labeled_graphs_new','total_candidates','elapsed_seconds','public_sha256']}))


if __name__=='__main__':main()
