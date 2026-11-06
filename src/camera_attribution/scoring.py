"""Original scalar arithmetic, strict ranks, and accepted answers."""
import math,struct

def f32(x):
    return struct.unpack('f',struct.pack('f',x))[0]

def merge(a,b):
    weight=f32(f32(1024)/f32(1400))
    return f32(f32(a)+f32(f32(b)*weight))

def component_scores(d1400,l1400,d1024,l1024):
    if l1400 is None:
        return [merge(a,b) for a,b in zip(d1400,d1024)]
    return [merge(f32(f32(a)+f32(x)),f32(f32(b)+f32(y))) for a,x,b,y in zip(d1400,l1400,d1024,l1024)]

def strict_correct(scores,truth):
    if not all(math.isfinite(x) for x in scores):
        raise ValueError('Scores must be finite.')
    return int(scores[truth]>max(x for j,x in enumerate(scores) if j!=truth))

def candidate_scale(scores,divisors):
    if len(scores)!=len(divisors) or not all(math.isfinite(x) and x>0 for x in divisors):
        raise ValueError('Every candidate needs its original positive finite divisor.')
    return [a/b for a,b in zip(scores,divisors)]

def decision(scores,truth,cutoff,action):
    accepted=[j for j,x in enumerate(scores) if x>=cutoff]
    highest=max(scores)
    win=[j for j,x in enumerate(scores) if x==highest]
    k=strict_correct(scores,truth)
    j=int(k and highest<cutoff)
    m=int(k and highest>=cutoff and len(accepted)>1)
    if action=='winner':
        accepted=win if len(win)==1 and highest>=cutoff else []
    elif action!='set':
        raise ValueError('Choose set or winner.')
    status='W' if any(i!=truth for i in accepted) else 'C' if accepted else 'R'
    assert int(status=='C')==k-j-(m if action=='set' else 0)
    return dict(status=status,mask=sum(1<<i for i in accepted),K=k,J=j,M=m)
