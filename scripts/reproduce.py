"""Reconstruct paper diagnostics from curated saved scores, without model inference."""
from pathlib import Path
from collections import Counter
import argparse,csv,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from camera_attribution.scoring import component_scores,strict_correct,decision
from camera_attribution.uncertainty import exact_range

def load(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
def rows(path):
    with path.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(path,records):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def compare(name,records,tolerance=0):
    expected=rows(ROOT/'expected'/name)
    assert len(records)==len(expected),(name,len(records),len(expected))
    for a,b in zip(records,expected):
        assert set(a)==set(b),(name,set(a),set(b))
        for key,value in a.items():
            if isinstance(value,(int,float)):
                assert abs(float(value)-float(b[key]))<=tolerance,(name,key,value,b[key])
            else:assert str(value)==b[key],(name,key,value,b[key])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--core-only',action='store_true',help='Use only the Python standard library.');parser.add_argument('--output',type=Path,default=ROOT/'results')
    options=parser.parse_args();out=options.output.resolve();out.mkdir(parents=True,exist_ok=True)
    core=load('core_scores.json');rank=[];cross=[]
    for case in core:
        g=case['gallery']
        for domain in ['all'] if case['material']=='CSAFE' else ['indoor','outdoor']:
            role='query' if domain=='all' else 'query_'+domain
            aa=sorted([p for p in case['records'] if p['role']==role and p['state']=='noisy'],key=lambda p:p['order'])
            bm={p['parent_id']:p for p in case['records'] if p['role']==role and p['state']=='restormer'};bb=[bm[p['parent_id']] for p in aa]
            for score in ['full','D']:
                a=[strict_correct(p[score],g.index(p['device'])) for p in aa];b=[strict_correct(p[score],g.index(p['device'])) for p in bb]
                rank.append(dict(material=case['material'],domain=domain,score=score,n=len(a),before=sum(a),after=sum(b),lost=sum(x and not y for x,y in zip(a,b)),gained=sum(not x and y for x,y in zip(a,b))))
            if case['material']=='CSAFE':
                for state,records in [('noisy',aa),('restormer',bb)]:
                    for cutstate in ['noisy','restormer']:
                        cutoff=case['raw_cutoffs']['full'][cutstate]
                        for action in ['set','winner']:
                            ev=[decision(p['full'],g.index(p['device']),cutoff,action) for p in records];c=Counter(p['status'] for p in ev)
                            cross.append(dict(state=state,cutoff_state=cutstate,action=action,n=len(ev),C=c['C'],W=c['W'],R=c['R']))
    compare('core_ranks.csv',rank);compare('CSAFE_crossed_answers.csv',cross);write(out/'core_ranks.csv',rank);write(out/'CSAFE_crossed_answers.csv',cross)
    native=load('native_components.json');g=native['gallery'];flags=[];native_summary=[]
    expected_vectors={p['parent_id']:p['vectors'] for p in json.loads((ROOT/'expected/native_vectors.json').read_text(encoding='utf-8'))}
    for p in native['parents']:
        vv={}
        for ds,ls,name in [('noisy','noisy','00'),('restormer','noisy','10'),('noisy','restormer','01'),('restormer','restormer','11')]:
            vv[name]=component_scores(p['components'][ds]['1400']['D'],p['components'][ls]['1400']['L'],p['components'][ds]['1024']['D'],p['components'][ls]['1024']['L'])
        for state,name in [('noisy','D0'),('restormer','D1')]:vv[name]=component_scores(p['components'][state]['1400']['D'],None,p['components'][state]['1024']['D'],None)
        assert vv==expected_vectors[p['parent_id']],p['parent_id']
        t=g.index(p['device'])
        flags.append(dict(parent_id=p['parent_id'],device=p['device'],domain=p['domain'],scene=p['scene'],**{'c'+k:strict_correct(v,t) for k,v in vv.items()},**{'tie'+k:int(v.count(max(v))>1) for k,v in vv.items()}))
    compare('native_parent_flags.csv',flags)
    for domain in ['indoor','outdoor']:
        rr=[r for r in flags if r['domain']==domain]
        for score,a,b in [('D+L','c00','c11'),('D','cD0','cD1')]:native_summary.append(dict(domain=domain,program=score,n=80,before=sum(r[a] for r in rr),after=sum(r[b] for r in rr),lost=sum(r[a] and not r[b] for r in rr),gained=sum(not r[a] and r[b] for r in rr)))
    compare('native_rank_summary.csv',native_summary);write(out/'native_rank_summary.csv',native_summary)
    amplitude=load('amplitude_scores.json');coverage=[];amplitude_counts=[]
    for program,score in [('published_raw_dot_plus_logit','D+L'),('raw_dot_only_control','D')]:
        for restorer in ['bm3d','restormer']:
            yy=[]
            for p in amplitude['parents']:
                t=amplitude['gallery'].index(p['device']);v=p['vectors'][program]
                yy.append([strict_correct(v[k],t) for k in ['noisy',restorer+'_amplitude_only',restorer+'_structure_only',restorer]])
            amplitude_counts.append(dict(score=score,restorer=restorer,baseline=sum(y[0] for y in yy),amplitude_only=sum(y[1] for y in yy),structure_only=sum(y[2] for y in yy),restored=sum(y[3] for y in yy)))
            if score=='D+L':
                lost=[y for y in yy if y[0] and not y[3]]
                coverage.append(dict(restorer=restorer,actual_losses=len(lost),reproduced=sum(not y[1] for y in lost),rescued=sum(y[2] for y in lost),both=sum(not y[1] and y[2] for y in lost)))
    compare('amplitude_counts.csv',amplitude_counts);compare('amplitude_coverage.csv',coverage);write(out/'amplitude_coverage.csv',coverage)
    classical=load('classical_centering_scores.json');g=classical['gallery'];answers=[]
    raw={(p['parent_id'],p['state']):p['scores'] for p in classical['records'] if p['program']=='raw'}
    for p in classical['records']:
        if p['program']=='delta':
            v=raw[p['parent_id'],p['state']]
            centered=[v[j]-sum(x for i,x in enumerate(v) if i!=j)/(len(v)-1) for j in range(len(v))]
            assert centered==p['scores']
            t=g.index(p['device']);assert strict_correct(v,t)==strict_correct(centered,t)
    for program in ['raw','delta']:
        for state in ['noisy','restormer']:
            rr=[p for p in classical['records'] if p['program']==program and p['state']==state]
            for action in ['set','winner']:
                cc=Counter(decision(p['scores'],g.index(p['device']),classical['state_cutoffs'][program][state],action)['status'] for p in rr)
                answers.append(dict(program=program,state=state,action=action,n=len(rr),C=cc['C'],W=cc['W'],R=cc['R']))
    compare('classical_centering_answers.csv',answers);write(out/'classical_centering_answers.csv',answers)
    # The contrast matrix retains the complete paired sampling unit per query.
    matrix=rows(ROOT/'data/paired_contrasts.csv');contrasts=[];keys=list(dict.fromkeys((r['case'],r['contrast']) for r in matrix))
    for case,contrast in keys:
        rr=[r for r in matrix if (r['case'],r['contrast'])==(case,contrast)];unit='fixed_device_parent' if case.startswith(('CSAFE','JPEG')) else 'shared_S_block'
        if unit=='fixed_device_parent':groups=[[int(r['delta']) for r in rr if r['device']==d] for d in sorted({r['device'] for r in rr})]
        else:groups=[[sum(int(r['delta']) for r in rr if r['scene']==s) for s in sorted({r['scene'] for r in rr})]]
        lo,hi=exact_range(groups);contrasts.append(dict(case=case,contrast=contrast,n=len(rr),delta=sum(int(r['delta']) for r in rr),lo=lo,hi=hi,unit=unit,method='exact_empirical_resampling_pointwise'))
    compare('conditional_ranges.csv',contrasts);write(out/'conditional_ranges.csv',contrasts)
    verified={'core_rank_groups':len(rank),'crossed_answer_cells':len(cross),'native_queries':len(flags),'native_float32_vectors':len(flags)*6,'amplitude_queries':len(amplitude['parents']),'amplitude_coverage':coverage,'classical_centering_answer_cells':len(answers),'exact_conditional_contrasts':len(contrasts)}
    if not options.core_only:
        import numpy as np
        from camera_attribution.verification import evaluate
        records=load('raw_verification_scores.json');weights=np.load(ROOT/'data/resampling_weights.npz');auc=[];curves=[]
        for key,score in dict.fromkeys((r['case'],r['score']) for r in records):
            points=[];draw=[]
            for state in ['before','after']:
                rr=[r for r in records if (r['case'],r['score'],r['state'])==(key,score,state)];g=rr[0]['gallery'];ww=weights['CSAFE_all' if key.startswith('JPEG') else key]
                a,d,curve=evaluate([r['scores'] for r in rr],[g.index(r['device']) for r in rr],ww);points.append(a);draw.append(d)
                for r in curve:curves.append(dict(case=key,score=score,state=state,**r))
            n=len(rr);lo,hi=np.quantile(draw[1]-draw[0],[.025,.975],method='linear')
            auc.append(dict(case=key,score=score,n_queries=n,n_genuine=n,n_impostor=n*(len(g)-1),before_AUC=points[0],after_AUC=points[1],delta_AUC=points[1]-points[0],lo=float(lo),hi=float(hi),resampling_unit='fixed_device_parent' if key.startswith(('CSAFE','JPEG')) else 'shared_S_block',replicates=2000))
        compare('raw_verification_AUC.csv',auc,tolerance=1e-12);compare('raw_ROC_DET.csv',curves,tolerance=1e-12);write(out/'raw_verification_AUC.csv',auc);write(out/'raw_ROC_DET.csv',curves);verified.update(raw_AUC_comparisons=len(auc),raw_verification_curves=16,empirical_curve_points=len(curves))
    verified.update(status='PASS_SAVED_SCORE_REPRODUCTION',image_residual_neural_execution=0,parameter_fits=0)
    (out/'verification.json').write_text(json.dumps(verified,indent=2)+'\n',encoding='utf-8');print(json.dumps(verified))
if __name__=='__main__':main()
