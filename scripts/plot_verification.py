from pathlib import Path
import csv
from statistics import NormalDist
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'results'
P=ROOT/'results/figures/verification'
P.mkdir(parents=True,exist_ok=True)
with (H/'raw_ROC_DET.csv').open(encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':9.5,'axes.labelsize':9.5,'xtick.labelsize':9.5,'ytick.labelsize':9.5,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
conditions=[('CSAFE_all','CSAFE Gaussian'),('ForensiCam_indoor','Core ForensiCam indoor'),('ForensiCam_outdoor','Core ForensiCam outdoor'),('JPEG_Q50','JPEG Q50'),('JPEG_Q75','JPEG Q75')]
for kind in ['ROC','DET']:
    fig,axes=plt.subplots(3,2,figsize=(6.7,7.1))
    fig.subplots_adjust(hspace=.65,wspace=.35,bottom=.09,top=.96,left=.09,right=.98)
    for ax,(case,title) in zip(axes.flat,conditions):
        for score,color in [('D+L','#0072B2'),('D','#D55E00')]:
            for state,style in [('before','--'),('after','-')]:
                rr=[r for r in rows if r['case']==case and r['score']==score and r['state']==state]
                if not rr:
                    continue
                pts=[(float(r['FPR']),float(r['TPR'])) for r in rr]
                if kind=='ROC':
                    ax.plot([x for x,y in pts],[y for x,y in pts],style,color=color,lw=1.2)
                    ax.set(xlim=(0,1),ylim=(0,1),xlabel='False-positive rate',ylabel='True-positive rate')
                else:
                    pts=[(NormalDist().inv_cdf(x),NormalDist().inv_cdf(1-y)) for x,y in pts if 0<x<1 and 0<y<1]
                    ax.plot([x for x,y in pts],[y for x,y in pts],style,color=color,lw=1.2)
                    ticks=[.001,.01,.1,.5,.9]
                    ax.set(xticks=[NormalDist().inv_cdf(x) for x in ticks],xticklabels=['.001','.01','.1','.5','.9'],yticks=[NormalDist().inv_cdf(x) for x in ticks],yticklabels=['.001','.01','.1','.5','.9'],xlabel='False-positive rate',ylabel='False-negative rate')
        ax.set_title(title,fontsize=10)
        ax.grid(alpha=.17,lw=.5)
    axes.flat[-1].axis('off')
    handles=[Line2D([],[],color='#0072B2',label=r'$D+L$'),Line2D([],[],color='#D55E00',label=r'$D$'),Line2D([],[],color='#444444',ls='--',label='Before'),Line2D([],[],color='#444444',ls='-',label='After')]
    fig.legend(handles=handles,loc='lower center',ncol=4,frameon=False,fontsize=9.5)
    for ext in ['pdf','svg','png']:
        fig.savefig(P/f'raw_{kind.lower()}.{ext}',dpi=180)
    plt.close(fig)
print('Created vector ROC and DET panels for five original-score conditions.')
