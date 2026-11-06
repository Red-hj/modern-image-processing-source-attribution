"""Exact pointwise percentiles of a paired empirical resampling model."""
from collections import Counter,defaultdict

def exact_range(groups):
    mass={0:1}
    denominator=1
    for values in groups:
        n=len(values)
        frequencies=Counter(map(int,values))
        for _ in values:
            following=defaultdict(int)
            for total,count in mass.items():
                for value,frequency in frequencies.items():
                    following[total+value]+=count*frequency
            mass=following
            denominator*=n
    assert sum(mass.values())==denominator
    def quantile(numerator):
        cumulative=0
        for value,count in sorted(mass.items()):
            cumulative+=count
            if 40*cumulative>=numerator*denominator:
                return value
    return quantile(1),quantile(39)
