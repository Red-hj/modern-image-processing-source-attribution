from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'expected'
P=ROOT/'results/figures'
P.mkdir(parents=True,exist_ok=True)
with (H/'raw_paths.csv').open(encoding='utf-8') as f:
    rr=list(csv.DictReader(f))
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':9,'axes.titlesize':9,'axes.labelsize':9,'xtick.labelsize':8.5,'ytick.labelsize':8.5,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
policies=[('SS','State-specific cutoff'),('CN','Shared degraded cutoff'),('CR','Shared restored cutoff')]
def panel(ax,case,policy,maxalpha):
    for action,color,line,mark,label in [('set','#0072B2','-','o','Singleton set'),('winner','#D55E00','--','s','Winner')]:
        z=[r for r in rr if r['case']==case and r['policy']==policy and r['action']==action and float(r['alpha_lo'])<=maxalpha]
        xx=[100*float(r['alpha_lo']) for r in z]
        yy=[int(r['delta_C']) for r in z]
        if xx[-1]<100*maxalpha:
            xx.append(100*maxalpha)
            yy.append(yy[-1])
        ax.step(xx,yy,where='post',color=color,linestyle=line,lw=1.25,label=label)
        for a in [.05,.1,.2]:
            r=next(r for r in z if int(r['k'])==int(int(r['m'])*a))
            ax.plot(100*a,int(r['delta_C']),marker=mark,ms=3,color=color,linestyle='none')
    ax.axhline(0,color='#555555',lw=.6)
    ax.axvline(20,color='#999999',lw=.65,ls=':')
    ax.set_xlim(0,100*maxalpha)
    ax.grid(axis='y',color='#e5e5e5',lw=.45)
    ax.margins(y=.15)
fig,axs=plt.subplots(1,3,figsize=(6.5,2.15),sharey=True)
for ax,(policy,title) in zip(axs,policies):
    panel(ax,'CSAFE_all',policy,.3)
    ax.set_title(policy+': '+title,fontsize=8.5)
    ax.set_xticks([0,10,20,30])
axs[0].set_ylabel('Change in correct answers')
fig.supxlabel('Nominal wrong-set calibration allowance (%)',fontsize=9,y=.015)
h,l=axs[0].get_legend_handles_labels()
fig.legend(h,l,loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.52,1.04),fontsize=9)
fig.subplots_adjust(left=.085,right=.99,bottom=.25,top=.78,wspace=.15)
for ext in ['pdf','svg','png']:
    fig.savefig(P/f'raw_paths_focus.{ext}',dpi=170)
plt.close(fig)
cases=[('CSAFE_all','CSAFE'),('ForensiCam_indoor','Core indoor'),('ForensiCam_outdoor','Core outdoor'),('JPEG_Q50','JPEG Q50'),('JPEG_Q75','JPEG Q75')]
fig,axs=plt.subplots(5,3,figsize=(6.5,7.2),sharex=True)
for i,(case,label) in enumerate(cases):
    for j,(policy,title) in enumerate(policies):
        ax=axs[i,j]
        panel(ax,case,policy,1.)
        ax.set_xticks([0,20,50,100])
        if i==0:
            ax.set_title(policy+': '+title,fontsize=8.5)
        if j==0:
            ax.set_ylabel(label+'\n'+r'$\Delta$ correct',fontsize=8.5)
h,l=axs[0,0].get_legend_handles_labels()
fig.legend(h,l,loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.52,1.),fontsize=9)
fig.supxlabel('Nominal wrong-set calibration allowance (%)',fontsize=9,y=.012)
fig.subplots_adjust(left=.12,right=.975,bottom=.075,top=.93,wspace=.32,hspace=.34)
for ext in ['pdf','svg','png']:
    fig.savefig(P/f'raw_paths_full.{ext}',dpi=170)
plt.close(fig)
print('Two vector figures exported from all five predeclared raw conditions.')
