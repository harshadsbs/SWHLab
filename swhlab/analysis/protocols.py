"""
scripts to help automated analysis of basic protocols.

All output data should be named:
    * 12345678_experiment_thing.jpg (time course experiment, maybe with drug)
    * 12345678_intrinsic_thing.jpg (any intrinsic property)
    * 12345678_micro_thing.jpg (anything copied, likely a micrograph)
    * 12345678_data_aps.npy (data stored in a numpy array)
    * 12345678_data_IVfast.npy (data stored in a numpy array)


INFORMAL GOAL: make all figures SQUARESIZE in height. Width is variable.
"""

import os
import sys
sys.path.append(r"C:\Users\swharden\Documents\GitHub\SWHLab") # for local run
sys.path.append(r"C:\Users\LabAdmin\Documents\GitHub\SWHLab") # for local run
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../'))
import glob
import matplotlib.pyplot as plt
import numpy as np

import swhlab
from swhlab import ABF
from swhlab.plotting import ABFplot
from swhlab.plotting.core import frameAndSave
from swhlab.analysis.ap import AP
import swhlab.plotting.core
import swhlab.common as cm
import swhlab.indexing.imaging as imaging

#from swhlab.swh_abf import ABF
#import swhlab.swh_index as index
#from swhlab.swh_ap import AP
#import swhlab.swh_plot
#from swhlab.swh_plot import ABFplot
#from swhlab.swh_plot import frameAndSave
#import swhlab.common as cm

SQUARESIZE=8

def proto_unknown(theABF):
    """protocol: unknown."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an unknown protocol")
    plot=ABFplot(abf)
    plot.rainbow=False
    plot.title=None
    plot.figure_height,plot.figure_width=SQUARESIZE,SQUARESIZE
    plot.kwargs["lw"]=.5
    plot.figure_chronological()
    plt.gca().set_axis_bgcolor('#AAAAAA') # different background if unknown protocol
    frameAndSave(abf,"UNKNOWN")

def proto_0101(theABF):
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC tau")
    #plot=ABFplot(abf)

    plt.figure(figsize=(SQUARESIZE/2,SQUARESIZE/2))
    plt.grid()
    plt.ylabel("relative potential (mV)")
    plt.xlabel("time (sec)")
    m1,m2=[.05,.1]
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        plt.plot(abf.sweepX2,abf.sweepY-abf.average(m1,m2),alpha=.2,color='#AAAAFF')
    average=abf.averageSweep()
    average-=np.average(average[int(m1**abf.pointsPerSec):int(m2*abf.pointsPerSec)])
    plt.plot(abf.sweepX2,average,color='b',lw=2,alpha=.5)
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)
    plt.axhline(0,color='r',ls="--",alpha=.5,lw=2)
    plt.margins(0,.1)

    # save it
    plt.tight_layout()
    frameAndSave(abf,"IC tau")
    plt.close('all')


def proto_0111(theABF):
    """protocol: IC ramp for AP shape analysis."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC ramp")

    # AP detection
    ap=AP(abf)
    ap.detect()

    # also calculate derivative for each sweep
    abf.derivative=True

    # create the multi-plot figure
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))
    ax1=plt.subplot(221)
    plt.ylabel(abf.units2)
    ax2=plt.subplot(222,sharey=ax1)
    ax3=plt.subplot(223)
    plt.ylabel(abf.unitsD2)
    ax4=plt.subplot(224,sharey=ax3)

    # put data in each subplot
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        ax1.plot(abf.sweepX,abf.sweepY,color='b',lw=.25)
        ax2.plot(abf.sweepX,abf.sweepY,color='b')
        ax3.plot(abf.sweepX,abf.sweepD,color='r',lw=.25)
        ax4.plot(abf.sweepX,abf.sweepD,color='r')

    # modify axis
    for ax in [ax1,ax2,ax3,ax4]: # everything
        ax.margins(0,.1)
        ax.grid(alpha=.5)
    for ax in [ax3,ax4]: # only derivative APs
        ax.axhline(-100,color='r',alpha=.5,ls="--",lw=2)
    for ax in [ax2,ax4]: # only zoomed in APs
        ax.get_yaxis().set_visible(False)
    if len(ap.APs):
        firstAP=ap.APs[0]["T"]
        ax2.axis([firstAP-.25,firstAP+.25,None,None])
        ax4.axis([firstAP-.01,firstAP+.01,None,None])

    # show message from first AP
    if len(ap.APs):
        firstAP=ap.APs[0]
        msg="\n".join(["%s = %s"%(x,str(firstAP[x])) for x in sorted(firstAP.keys()) if not "I" in x[-2:]])
        plt.subplot(221)
        plt.gca().text(0.02, 0.98, msg, transform= plt.gca().transAxes, fontsize=10, verticalalignment='top', family='monospace')

    # save it
    plt.tight_layout()
    frameAndSave(abf,"AP shape")
    plt.close('all')

def proto_gain(theABF,stepSize=25,startAt=-100):
    """protocol: gain function of some sort. step size and start at are pA."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC ramp")
    plot=ABFplot(abf)
    plot.kwargs["lw"]=.5
    plot.title=""
    currents=np.arange(abf.sweeps)*stepSize-startAt

    # AP detection
    ap=AP(abf)
    ap.detect_time1=.1
    ap.detect_time2=.7
    ap.detect()

    # stacked plot
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))

    ax1=plt.subplot(221)
    plot.figure_sweeps()

    ax2=plt.subplot(222)
    ax2.get_yaxis().set_visible(False)
    plot.figure_sweeps(offsetY=150)

    # add vertical marks to graphs:
    for ax in [ax1,ax2]:
        for limit in [ap.detect_time1,ap.detect_time2]:
            ax.axvline(limit,color='r',ls='--',alpha=.5,lw=2)

    # make stacked gain function
    ax4=plt.subplot(223)
    plt.ylabel("frequency (Hz)")
    plt.ylabel("seconds")
    plt.grid(alpha=.5)
    freqs=ap.get_bySweep("freqs")
    times=ap.get_bySweep("times")
    for i in range(abf.sweeps):
        if len(freqs[i]):
            plt.plot(times[i][:-1],freqs[i],'-',alpha=.5,lw=2,
                     color=plot.getColor(i/abf.sweeps))

    # make gain function graph
    ax4=plt.subplot(224)
    ax4.grid(alpha=.5)
    plt.plot(currents,ap.get_bySweep("median"),'b.-',label="median")
    plt.plot(currents,ap.get_bySweep("firsts"),'g.-',label="first")
    plt.xlabel("applied current (pA)")
    plt.legend(loc=2,fontsize=10)
    plt.axhline(40,color='r',alpha=.5,ls="--",lw=2)
    plt.margins(.02,.1)

    # save it
    plt.tight_layout()
    frameAndSave(abf,"AP Gain %d_%d"%(startAt,stepSize))
    plt.close('all')

    # make a second figure that just shows every sweep up to the first AP
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))
    plt.grid(alpha=.5)
    plt.ylabel("Membrane Potential (mV)")
    plt.xlabel("Time (seconds)")
    for sweep in abf.setsweeps():
        plt.plot(abf.sweepX2,abf.sweepY,color='b',alpha=.5)
        if np.max(abf.sweepY>0):
            break
    plt.tight_layout()
    plt.margins(0,.1)

    plt.axis([0,1,None,None])
    plt.title("%d pA Steps from Rest"%stepSize)
    frameAndSave(abf,"voltage response fromRest",closeWhenDone=False)
    plt.axis([1.5,2.5,None,None])
    plt.title("%d pA Steps from %d pA"%(stepSize,startAt))
    frameAndSave(abf,"voltage response hyperpol",closeWhenDone=False)
    plt.close('all')




def proto_0112(theABF):
    proto_gain(theABF,10,-50)

def proto_0113(theABF):
    proto_gain(theABF,25)

def proto_0114(theABF):
    proto_gain(theABF,100)

def proto_0201(theABF):
    """protocol: membrane test."""
    abf=ABF(theABF)
    abf.log.info("analyzing as a membrane test")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE/2,SQUARESIZE/2
    plot.figure_sweeps()

    # save it
    plt.tight_layout()
    frameAndSave(abf,"membrane test")
    plt.close('all')

def proto_0202(theABF):
    """protocol: MTIV."""
    abf=ABF(theABF)
    abf.log.info("analyzing as MTIV")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE,SQUARESIZE
    plot.title=""
    plot.kwargs["alpha"]=.6
    plot.figure_sweeps()

    # frame to uppwer/lower bounds, ignoring peaks from capacitive transients
    abf.setsweep(0)
    plt.axis([None,None,abf.average(.9,1)-100,None])
    abf.setsweep(-1)
    plt.axis([None,None,None,abf.average(.9,1)+100])

    # save it
    plt.tight_layout()
    frameAndSave(abf,"MTIV")
    plt.close('all')

def proto_0203(theABF):
    """protocol: vast IV."""
    abf=ABF(theABF)
    abf.log.info("analyzing as a fast IV")
    plot=ABFplot(abf)
    plot.title=""
    m1,m2=.7,1
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE/2))

    plt.subplot(121)
    plot.figure_sweeps()
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)

    plt.subplot(122)
    plt.grid(alpha=.5)
    Xs=np.arange(abf.sweeps)*5-110
    Ys=[]
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        Ys.append(abf.average(m1,m2))
    plt.plot(Xs,Ys,'.-',ms=10)
    plt.axvline(-70,color='r',ls='--',lw=2,alpha=.5)
    plt.axhline(0,color='r',ls='--',lw=2,alpha=.5)
    plt.margins(.1,.1)
    plt.xlabel("membrane potential (mV)")

    # save it
    plt.tight_layout()
    frameAndSave(abf,"fast IV")
    plt.close('all')

def proto_0204(theABF):
    """protocol: Cm ramp."""
    abf=ABF(theABF)
    abf.log.info("analyzing as Cm ramp")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE/2,SQUARESIZE/2
    plot.figure_sweeps()
    plt.tight_layout()
    frameAndSave(abf,"Cm ramp")
    plt.close('all')


def proto_0222(theABF):
    """protocol: VC sine sweep."""
    abf=ABF(theABF)
    abf.log.info("analyzing as VC sine sweep")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE/2,SQUARESIZE/2
    plot.figure_sweeps()
    plt.tight_layout()
    frameAndSave(abf,"VC sine sweep")
    plt.close('all')

def proto_0302(theABF):
    proto_0303(theABF)

def proto_0303(theABF):
    """protocol: repeated IC ramps."""

    abf=ABF(theABF)
    abf.log.info("analyzing as a halorhodopsin (2s pulse)")

    # show average voltage
    proto_avgRange(theABF,0.2,1.2)
    plt.close('all')

    # show stacked sweeps
    plt.figure(figsize=(8,8))
    for sweep in abf.setsweeps():
        color='b'
        if sweep in np.array(abf.comment_sweeps,dtype=int):
            color='r'
        plt.plot(abf.sweepX2,abf.sweepY+100*sweep,color=color,alpha=.5)
    plt.margins(0,.01)
    plt.tight_layout()
    frameAndSave(abf,"IC ramps")
    plt.close('all')

    # do AP event detection
    ap=AP(abf)
    ap.detect_time1=2.3
    ap.detect_time2=8.3
    ap.detect()
    apCount=[]
    apSweepTimes=[]

    for sweepNumber,times in enumerate(ap.get_bySweep("times")):
        apCount.append(len(times))
        if len(times):
            apSweepTimes.append(times[0])
        else:
            apSweepTimes.append(0)

    # plot AP frequency vs time
    plt.figure(figsize=(8,8))

    ax1=plt.subplot(211)
    plt.grid(alpha=.4,ls='--')
    plt.plot(np.arange(len(apCount))*abf.sweepLength/60,apCount,'.-',ms=15)
    comment_lines(abf)
    plt.ylabel("AP Count")

    plt.subplot(212,sharex=ax1)
    plt.grid(alpha=.4,ls='--')
    plt.plot(np.arange(len(apCount))*abf.sweepLength/60,apSweepTimes,'.-',ms=15)
    comment_lines(abf)
    plt.ylabel("First AP Time (s)")
    plt.xlabel("Experiment Duration (minutes)")
    plt.tight_layout()
    frameAndSave(abf,"IC ramp freq")
    plt.close('all')

def proto_0304(theABF):
    """protocol: repeated IC steps."""

    abf=ABF(theABF)
    abf.log.info("analyzing as repeated current-clamp step")

    # prepare for AP analysis
    ap=AP(abf)

    # calculate rest potential
    avgVoltagePerSweep = [];
    times = []
    for sweep in abf.setsweeps():
        avgVoltagePerSweep.append(abf.average(0,3))
        times.append(abf.sweepStart/60)

    # detect only step APs
    M1,M2=3.15,4.15
    ap.detect_time1, ap.detect_time2 = M1,M2
    ap.detect()
    apsPerSweepCos=[len(x) for x in ap.get_bySweep()]

    # detect all APs
    M1,M2=0,10
    ap.detect_time1, ap.detect_time2 = M1,M2
    ap.detect()
    apsPerSweepRamp=[len(x) for x in ap.get_bySweep()]

    # make the plot of APs and stuff
    plt.figure(figsize=(8,8))

    plt.subplot(311)
    plt.grid(ls='--',alpha=.5)
    plt.plot(times,avgVoltagePerSweep,'.-')
    plt.ylabel("Rest Potential (mV)")
    comment_lines(abf)

    plt.subplot(312)
    plt.grid(ls='--',alpha=.5)
    plt.plot(times,apsPerSweepCos,'.-')
    plt.ylabel("APs in Step (#)")
    comment_lines(abf)

    plt.subplot(313)
    plt.grid(ls='--',alpha=.5)
    plt.plot(times,apsPerSweepRamp,'.-')
    plt.ylabel("APs in Sweep (#)")
    comment_lines(abf)

    plt.tight_layout()

    frameAndSave(abf,"cos ramp")
    plt.close('all')



def proto_0314(theABF):
    abf=ABF(theABF)
    abf.log.info("analyzing a cosine + ramp protocol")

    if len(abf.comment_sweeps>0):
        # comments exist, so graph the average sweep before/after the first comment
        sweepsToAverage=10
        baselineSweep1=max(0, abf.comment_sweeps[0]-sweepsToAverage)
        baselineSweep2=abf.comment_sweeps[0]
        drugSweep1=abf.comment_sweeps[0]+1
        drugSweep2=min(abf.sweeps-1,abf.comment_sweeps[0]+1+sweepsToAverage)

        plt.figure(figsize=(16,4))
        plt.grid(ls='--',alpha=.5)
        plt.plot(abf.sweepX2,abf.averageSweep(baselineSweep1, baselineSweep2),
                 label="baseline (%d-%d)"%(baselineSweep1,baselineSweep2), alpha=.8)
        plt.plot(abf.sweepX2,abf.averageSweep(drugSweep1, drugSweep2),
                 label="drug (%d-%d)"%(drugSweep1,drugSweep2), alpha=.8)
        plt.margins(0,.05)
        plt.legend()
        plt.tight_layout()
        frameAndSave(abf,"cos ramp avg",closeWhenDone=False)
        plt.axis([2.25,4.5,None,None])
        frameAndSave(abf,"cos ramp avgSine",closeWhenDone=False)
        plt.axis([9,12.5,None,None])
        frameAndSave(abf,"cos ramp avgRamp")

    # prepare for AP analysis
    ap=AP(abf)

    # calculate rest potential
    avgVoltagePerSweep = [];
    times = []
    for sweep in abf.setsweeps():
        avgVoltagePerSweep.append(abf.average(0,2.25))
        times.append(abf.sweepStart/60)

    # detect only cos APs
    M1,M2=2.25,4.5
    ap.detect_time1, ap.detect_time2 = M1,M2
    ap.detect()
    apsPerSweepCos=[len(x) for x in ap.get_bySweep()]

    # detect only ramp APs
    M1,M2=9,12.5
    ap.detect_time1, ap.detect_time2 = M1,M2
    ap.detect()
    apsPerSweepRamp=[len(x) for x in ap.get_bySweep()]

    # make the plot of APs and stuff
    plt.figure(figsize=(8,8))

    plt.subplot(311)
    plt.grid(ls='--',alpha=.5)
    plt.plot(times,avgVoltagePerSweep,'.-')
    plt.ylabel("Rest Potential (mV)")
    comment_lines(abf)

    plt.subplot(312)
    plt.grid(ls='--',alpha=.5)
    plt.plot(times,apsPerSweepCos,'.-')
    plt.ylabel("APs in Cos (#)")
    comment_lines(abf)

    plt.subplot(313)
    plt.grid(ls='--',alpha=.5)
    plt.plot(times,apsPerSweepRamp,'.-')
    plt.ylabel("APs in Ramp (#)")
    comment_lines(abf)

    plt.tight_layout()

    frameAndSave(abf,"cos ramp")
    plt.close('all')



def proto_0401(theABF):
    proto_avgRange(theABF,.5,2.0)

def proto_0402(theABF):
    proto_avgRange(theABF,.5,2.0)

def proto_0404(theABF):
    proto_avgRange(theABF,1.0,1.1)

def proto_0405(theABF):
    proto_avgRange(theABF,1.0,None)

def proto_0406(theABF):
    proto_avgRange(theABF,1.0,None)

def proto_0501(theABF):
    BLS_average_stack(theABF)

def proto_0502(theABF):
    BLS_average_stack(theABF)

def proto_0911(theABF):
    abf=ABF(theABF)
    abf.log.info("analyzing as paired pulse stimulation with various increasing ISIs")
    plt.figure(figsize=(8,8))
    M1,M2=2.2,2.4
    I1,I2=int(M1*abf.pointsPerSec),int(M2*abf.pointsPerSec)
    Ip1=int(2.23440*abf.pointsPerSec) # time of first pulse in the sweep
    pw=int(1.5/1000*abf.pointsPerSec) # pulse width in ms
    B1,B2=1,2 # baseline time in seconds
    plt.axhline(0,alpha=.5,ls='--',lw=2,color='k')
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        Xs=abf.sweepX2[I1:I2]*1000
        baseline=np.average(abf.sweepY[int(B1*abf.pointsPerSec):int(B2*abf.pointsPerSec)])
        Ys=abf.sweepY[I1:I2]-baseline
        Ys[Ip1-I1:Ip1-I1+pw]=np.nan # erase the first pulse
        isi=int(10+sweep*10) # interspike interval (ms)
        Ip2d = int(isi/1000*abf.pointsPerSec)
        Ys[Ip1-I1+Ip2d:Ip1-I1+pw+Ip2d]=np.nan # erase the second pulse
        plt.plot(Xs-Xs[0],Ys,alpha=.8,label="%d ms"%isi)
    plt.margins(0,.1)
    plt.legend()
    plt.grid(alpha=.4,ls='--')
    plt.title("Paired Pulse Stimuation (varied ISIs)")
    plt.ylabel("clamp current (pA) [artifacts removed]")
    plt.xlabel("time (ms) [offset by %.02f s]"%M1)
    plt.tight_layout()
    frameAndSave(abf,"pp_varied")
    plt.close('all')

def proto_0912(theABF):
    abf=ABF(theABF)
    abf.log.info("analyzing as 40ms PPS experiment")

    BL1,BL2=1,2 # area for baseline
    ISI=40 # inter-stimulus-interval in ms
    Ip1=int(2.31255*abf.pointsPerSec) # time of first pulse in the sweep
    Ip2=int(Ip1+(ISI/1000)*abf.pointsPerSec) # second pulse is 40ms later
    Ip3=Ip2+(Ip2-Ip1) # distance after Ip2 to scan for the second peak
    pw=int(3/1000*abf.pointsPerSec) # pulse width in ms
    peakTimes,peak1heights,peak2heights,peakRatios,baselines,peakTransient=[],[],[],[],[],[]
    ROI=None
    ROIpad=int(.02*abf.pointsPerSec)

    # calculate peak ratios and all that
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        baseline=np.average(abf.sweepY[int(BL1*abf.pointsPerSec):int(BL2*abf.pointsPerSec)])
        Ra=np.max(abf.sweepY[int(.51*abf.pointsPerSec):int(.52*abf.pointsPerSec)])
        peakTransient.append(Ra-baseline)
        abf.sweepY=abf.sweepY-baseline
        for I in [Ip1,Ip2]:
            abf.sweepY[I:I+pw]=np.nan # blank out each pulse
        abf.sweepY[:Ip1-int(.05*abf.pointsPerSec)]=np.nan #blank out 50ms before P1
        abf.sweepY[Ip1+int(.15*abf.pointsPerSec):]=np.nan #blank out 15ms after P1
        peak1=abf.sweepY[int(Ip1):int(Ip2)]
        peak2=abf.sweepY[int(Ip2):int(Ip3)]
        peakTimes.append(abf.sweepStart)
        peak1heights.append(np.nanmin(peak1))
        peak2heights.append(np.nanmin(peak2))
        baselines.append(baseline)
        peakRatios.append(peak2heights[-1]/peak1heights[-1])
        thisROI=abf.sweepY[int(Ip1)-ROIpad:int(Ip3)+ROIpad]
        if ROI is None:
            ROI=thisROI.flatten()
        else:
            ROI=np.vstack((ROI,thisROI.flatten()))
    peakTimes=np.array(peakTimes)/60 # seconds to minutes

    # figure showing the averaged evoked response for certain time ranges
    avgSweeps=3*5 # 3 sweeps/minute, 5 minutes
    avgLocations=[10*3,20*3,30*3] # the end of the area for averaging
    plt.figure(figsize=(8,8))
    plt.grid(alpha=.4,ls='--')
    plt.axhline(0,alpha=.5,ls='--',lw=2,color='k')
    for S2 in avgLocations:
        S1=S2-avgSweeps
        AV=np.average(ROI[S1:S2],axis=0)
        ER=np.std(ROI[S1:S2],axis=0)#/np.sqrt(len(ROI))
        Xs=abf.sweepX[:len(AV)]
        plt.fill_between(Xs,AV-ER,AV+ER,alpha=.1)
        plt.plot(Xs,AV,label="sweeps %d-%d"%(S1,S2))
    plt.legend()
    plt.tight_layout()
    frameAndSave(abf,"pp_avg")
    plt.close('all')

    # figure showing peak height and ratio over time
    plt.figure(figsize=(8,8))
    plt.subplot(211)
    comment_lines(abf)
    plt.grid(alpha=.4,ls='--')
    plt.plot(peakTimes,peak1heights,'g.',ms=15,alpha=.6,label='pulse1')
    plt.plot(peakTimes,peak2heights,'m.',ms=15,alpha=.6,label='pulse2')
    plt.axis([None,None,None,0])
    plt.legend()
    plt.title("Paired Pulse Stimuation")
    plt.ylabel("Peak Amplitude (pA)")
    plt.subplot(212)
    comment_lines(abf)
    plt.grid(alpha=.4,ls='--')
    plt.axhline(100,alpha=.5,ls='--',lw=2,color='k')
    plt.plot(peakTimes,np.array(peakRatios)*100,'r.',ms=15,alpha=.6)
    plt.axis([None,None,0,None])
    plt.ylabel("Paired Pulse Ratio (%)")
    plt.xlabel("Experiment Duration (minutes)")
    plt.tight_layout()
    frameAndSave(abf,"pp_experiment")
    plt.close('all')

    # figure showing baseline over time (Ih)
    plt.figure(figsize=(8,8))

    plt.subplot(211)
    plt.grid(alpha=.4,ls='--')
    plt.plot(peakTimes,baselines,'b.',ms=15,alpha=.6)
    plt.margins(0,.1)
    plt.axis([None,None,plt.axis()[2]-100,plt.axis()[3]+100])
    comment_lines(abf)
    plt.title("Holding Current (pulse baseline)")
    plt.ylabel("Clamp Current (pA)")
    #plt.xlabel("Experiment Duration (minutes)")

    plt.subplot(212)
    plt.grid(alpha=.4,ls='--')
    access=np.array(peakTransient)/peakTransient[0]*100
    plt.plot(peakTimes,access,'r.',ms=15,alpha=.6)
    plt.axhspan(75,125,alpha=.1,color='k',label='+/- 25%')
    plt.margins(0,.5)
    plt.axis([None,None,0,None])
    comment_lines(abf)
    plt.title("Access Resistance")
    plt.ylabel("Peak Transient Current (% of first)")
    plt.xlabel("Experiment Duration (minutes)")

    plt.tight_layout()
    frameAndSave(abf,"pp_baselines")
    plt.close('all')

def comment_lines(abf,label=True):
    for i,t in enumerate(abf.comment_times):
        if label:
            label=abf.comment_tags[i]
        plt.axvline(t/60,alpha=.5,lw=2,ls=':',color='r',label=label)
    if label:
        plt.legend()

def BLS_average_stack(theABF):
    abf=ABF(theABF)
    T1,T2=abf.epochTimes(2)
    padding=.1
    if abf.units=="mV":
        padding=.25
    Tdiff=max([T2-T1,padding])
    Tdiff=min([T1,padding])
    X1,X2=T1-Tdiff,T2+Tdiff
    I1,I2=X1*abf.pointsPerSec,X2*abf.pointsPerSec

    plt.figure(figsize=(10,10))
    chunks=np.empty((int(abf.sweeps),int(I2-I1)))
    Xs=np.array(abf.sweepX2[int(I1):int(I2)])
    for sweep in abf.setsweeps():
        chunks[sweep]=abf.sweepY[int(I1):int(I2)].flatten()
        plt.subplot(211)
        plt.plot(Xs,chunks[sweep],alpha=.2,color='.5',lw=2)
        plt.subplot(212)
        if abf.units=='pA':
            plt.plot(Xs,chunks[sweep]+100*(abf.sweeps-sweep),alpha=.5,color='b',lw=2) # if VC, focus on BLS
        else:
            plt.plot(abf.sweepX2,abf.sweepY+100*(abf.sweeps-sweep),alpha=.5,color='b',lw=2) # if IC, show full sweep

    plt.subplot(211)
    plt.plot(Xs,np.average(chunks,axis=0),alpha=.5,lw=2)
    plt.title("%s.abf - BLS - average of %d sweeps"%(abf.ID,abf.sweeps))
    plt.ylabel(abf.units2)
    plt.axvspan(T1,T2,alpha=.2,color='y',lw=0)
    plt.margins(0,.1)

    plt.subplot(212)
    plt.xlabel("time (sec)")
    plt.ylabel("stacked sweeps")
    plt.axvspan(T1,T2,alpha=.2,color='y',lw=0)
    if abf.units=='mV':
        plt.axvline(T1,color='r',alpha=.2,lw=3)
#        plt.axvline(T2,color='r',alpha=.2,lw=3)
    plt.margins(0,.1)

    plt.tight_layout()
    frameAndSave(abf,"BLS","experiment")
    plt.close('all')


def proto_avgRange(theABF,m1=None,m2=None):
    """experiment: generic VC time course experiment."""

    abf=ABF(theABF)
    abf.log.info("analyzing as a fast IV")
    if m1 is None:
        m1=abf.sweepLength
    if m2 is None:
        m2=abf.sweepLength

    I1=int(abf.pointsPerSec*m1)
    I2=int(abf.pointsPerSec*m2)

    Ts=np.arange(abf.sweeps)*abf.sweepInterval
    Yav=np.empty(abf.sweeps)*np.nan # average
    Ysd=np.empty(abf.sweeps)*np.nan # standard deviation
    #Yar=np.empty(abf.sweeps)*np.nan # area

    for sweep in abf.setsweeps():
        Yav[sweep]=np.average(abf.sweepY[I1:I2])
        Ysd[sweep]=np.std(abf.sweepY[I1:I2])
        #Yar[sweep]=np.sum(abf.sweepY[I1:I2])/(I2*I1)-Yav[sweep]

    plot=ABFplot(abf)
    plt.figure(figsize=(SQUARESIZE*2,SQUARESIZE/2))

    plt.subplot(131)
    plot.title="first sweep"
    plot.figure_sweep(0)
    plt.title("First Sweep\n(shaded measurement range)")
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)

    plt.subplot(132)
    plt.grid(alpha=.5)
    for i,t in enumerate(abf.comment_times):
        plt.axvline(t/60,color='r',alpha=.5,lw=2,ls='--')
    plt.plot(Ts/60,Yav,'.',alpha=.75)
    plt.title("Range Average\nTAGS: %s"%(", ".join(abf.comment_tags)))
    plt.ylabel(abf.units2)
    plt.xlabel("minutes")
    plt.margins(0,.1)

    plt.subplot(133)
    plt.grid(alpha=.5)
    for i,t in enumerate(abf.comment_times):
        plt.axvline(t/60,color='r',alpha=.5,lw=2,ls='--')
    plt.plot(Ts/60,Ysd,'.',alpha=.5,color='g',ms=15,mew=0)
    #plt.fill_between(Ts/60,Ysd*0,Ysd,lw=0,alpha=.5,color='g')
    plt.title("Range Standard Deviation\nTAGS: %s"%(", ".join(abf.comment_tags)))
    plt.ylabel(abf.units2)
    plt.xlabel("minutes")
    plt.margins(0,.1)
    plt.axis([None,None,0,np.percentile(Ysd,99)*1.25])

    plt.tight_layout()
    frameAndSave(abf,"sweep vs average","experiment")
    plt.close('all')

def analyze(fname=False,save=True,show=None):
    """given a filename or ABF object, try to analyze it."""
    if fname and os.path.exists(fname.replace(".abf",".rst")):
        print("SKIPPING DUE TO RST FILE")
        return
    swhlab.plotting.core.IMAGE_SAVE=save
    if show is None:
        if cm.isIpython():
            swhlab.plotting.core.IMAGE_SHOW=True
        else:
            swhlab.plotting.core.IMAGE_SHOW=False
    #swhlab.plotting.core.IMAGE_SHOW=show
    abf=ABF(fname) # ensure it's a class
    print(">>>>> PROTOCOL >>>>>",abf.protocomment)
    runFunction="proto_unknown"
    if "proto_"+abf.protocomment in globals():
        runFunction="proto_"+abf.protocomment
    abf.log.debug("running %s()"%(runFunction))
    plt.close('all') # get ready
    globals()[runFunction](abf) # run that function
    try:
        globals()[runFunction](abf) # run that function
    except:
        abf.log.error("EXCEPTION DURING PROTOCOL FUNCTION")
        abf.log.error(sys.exc_info()[0])
        return "ERROR"
    plt.close('all') # clean up
    return "SUCCESS"

def analyzeFolder(folder, convertTifs=True):
    for fname in sorted(glob.glob(folder+"/*.abf")):
        analyze(fname)
    if convertTifs:
        imaging.TIF_to_jpg_all(folder)
    if not os.path.exists(folder+"/swhlab"):
        os.mkdir(folder+"/swhlab")
    for fname in glob.glob(folder+"/*.tif.jpg"):
        path1=os.path.abspath(fname)
        path2=os.path.abspath(folder+"/swhlab/"+os.path.basename(fname))
        os.rename(path1,path2)



if __name__=="__main__":

    if len(sys.argv)==1:
        print("YOU MUST BE TESTING OR DEBUGGING!")
        analyze(r"X:\Data\winstar\D2R NAc halo\abfs\180405_sh_0081.abf")
        print("DONE")

    if len(sys.argv)==2:
        print("protocols.py is getting a path...")
        abfPath=os.path.abspath(sys.argv[1])
        if not os.path.exists(abfPath):
            print(abfPath,"does not exist")
        elif not abfPath.endswith(".abf"):
            print(abfPath,"needs to be an ABF file")
        else:
            analyze(abfPath)



    #print("DONT RUN THIS DIRECTLY. Call analyze() externally.")
    #fname=r"X:\Data\SCOTT\2017-01-09 AT1 NTS\17503052.abf"
    #analyze(fname)
