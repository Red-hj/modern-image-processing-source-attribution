"""Replay recorded raw paths and fixed-weight component merges using saved scalars."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import csv,json,math,sys,itertools
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from camera_attribution.scoring import component_scores,strict_correct,decision,f32
def load(p):
    return json.loads(p.read_text(encoding='utf-8'))
def rows(p):
    with p.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))
def leader(v):
    a=max(v)
    ii=[i for i,x in enumerate(v) if x==a]
    return ii[0] if len(ii)==1 else -1
def main():
    expected={(r['case'],r['policy'],r['action'],int(r['k'])):r for r in rows(ROOT/'expected/raw_paths.csv')}
    checked=0
    for ds in load(ROOT/'data/raw_path_inputs.json'):
        m=ds['m']
        bounds={}
        for st in ['N','T']:
            a=sorted((max(v for j,v in enumerate(p['scores']) if j!=p['truth']) for p in ds['calibration'][st]),reverse=True)
            bounds[st]=[math.nextafter(x,math.inf) for x in a]+[-math.inf]
        for k in range(m+1):
            for policy,(c0,c1) in {'SS':('N','T'),'CN':('N','N'),'CR':('T','T')}.items():
                for action in ['set','winner']:
                    z=expected[ds['case'],policy,action,k]
                    ev=[]
                    for st,cs,prefix in [('N',c0,'before'),('T',c1,'after')]:
                        e=[decision(p['scores'],p['truth'],bounds[cs][k],action) for p in ds['evaluation'][st]]
                        ev.append(e)
                        counts=Counter(r['status'] for r in e)
                        for key in 'CWR':
                            assert counts[key]==int(z[prefix+'_'+key])
                        for key in ['K','J','M']:
                            assert sum(r[key] for r in e)==int(z[prefix+'_'+key])
                    assert sum(a['status']=='C' and b['status']!='C' for a,b in zip(*ev))==int(z['lost'])
                    assert sum(a['status']!='C' and b['status']=='C' for a,b in zip(*ev))==int(z['gained'])
                    checked+=1
    inputs={r['case']:r for r in load(ROOT/'data/merge_components.json')}
    parents={k:{p['parent_id']:p for p in d['parents']} for k,d in inputs.items()}
    vectors=0
    candidates=0
    w=f32(1024/1400)
    for r in rows(ROOT/'expected/merge_precision_rows.csv'):
        p=parents[r['case']][r['parent_id']]
        ds=r['D_state']
        ls=r['L_state']
        t=int(r['truth'])
        a=p['components'][ds]['1400']['D']
        b=p['components'][ds]['1024']['D']
        x=p['components'][ls]['1400']['L'] if ls else None
        y=p['components'][ls]['1024']['L'] if ls else None
        v32=component_scores(a,x,b,y)
        v64=[(d0+(l0 if ls else 0.))+(d1+(l1 if ls else 0.))*w for d0,d1,l0,l1 in zip(a,b,x or [0.]*len(a),y or [0.]*len(a))]
        exact=[Fraction(d0)+Fraction(l0)+Fraction(w)*(Fraction(d1)+Fraction(l1)) for d0,d1,l0,l1 in zip(a,b,x or [0.]*len(a),y or [0.]*len(a))]
        for prec,v in [('32',v32),('64',v64)]:
            assert strict_correct(v,t)==int(r['correct'+prec])
            assert leader(v)==int(r['leader'+prec])
            assert v[t]-max(v[:t]+v[t+1:])==float(r['truth_margin'+prec])
        pairchanges=sum(((a>b)-(a<b))!=((c>d)-(c<d)) for (a,b),(c,d) in zip(itertools.combinations(v32,2),itertools.combinations(v64,2)))
        assert pairchanges==int(r['candidate_pair_order_changes'])
        delta=max(abs(Fraction(a)-b) for a,b in zip(v32,exact))
        assert delta<=Fraction(float(r['conservative_change_bound']))
        margin=Fraction(v32[t])-max(Fraction(v32[j]) for j in range(len(v32)) if j!=t)
        if int(r['truth_margin_bound_pass']):
            assert abs(margin)>2*delta
        assert strict_correct(exact,t)==int(r['correct32'])
        candidates+=len(v32)
        vectors+=1
    assert checked==4758 and vectors==8916 and candidates==81204
    out=ROOT/'results'
    out.mkdir(exist_ok=True)
    result=dict(status='PASS_RAW_PATHS_AND_EXACT_MERGE_REPLAY',existing_raw_path_rows=checked,precision_configurations=vectors,exact_candidate_scores=candidates,new_model_forwards=0)
    (out/'paths_precision_replay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':
    main()
