"""Paired raw verification; query multiplicities retain all candidates."""
import numpy as np

def evaluate(vectors,truth,weights):
    v=np.asarray(vectors,dtype=np.float64)
    t=np.asarray(truth)
    n,k=v.shape
    positive=v[np.arange(n),t]
    negative=v[np.arange(k)[None,:]!=t[:,None]].reshape(n,k-1)
    twice_wins=2*(positive[:,None,None]>negative[None,:,:]).sum(2)+(positive[:,None,None]==negative[None,:,:]).sum(2)
    auc=float(twice_wins.sum()/(2*n*n*(k-1)))
    w=np.asarray(weights,dtype=np.int64)
    assert np.all(w.sum(1)==n)
    bootstrap_auc=np.einsum('bi,ij,bj->b',w,twice_wins,w,optimize=True)/(2*n*n*(k-1))
    labels=np.zeros_like(v,dtype=bool)
    labels[np.arange(n),t]=True
    order=np.argsort(-v.ravel(),kind='stable')
    scores=v.ravel()[order]
    labels=labels.ravel()[order]
    last=np.r_[np.flatnonzero(scores[1:]!=scores[:-1]),len(scores)-1]
    tp=np.cumsum(labels)[last]
    fp=last+1-tp
    curve=[dict(threshold='above_max',TP=0,FP=0,TPR=0.,FPR=0.,FNR=1.)]
    curve.extend(dict(threshold=float(scores[i]),TP=int(a),FP=int(b),TPR=float(a/n),FPR=float(b/(n*(k-1))),FNR=float(1-a/n)) for i,a,b in zip(last,tp,fp))
    assert abs(np.trapezoid([r['TPR'] for r in curve],[r['FPR'] for r in curve])-auc)<1e-12
    return auc,bootstrap_auc,curve
