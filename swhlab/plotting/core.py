"""
This module contains scripts to plot SWHLab ABF objects.
Try to keep analysis (event detection, etc) out of this.
"""

# start out this way so tests will import the local swhlab module
import sys
import os
sys.path.insert(0,os.path.abspath('../../'))
import swhlab

# now import things regularly
import logging
import glob
import matplotlib.pyplot as plt

import swhlab.version as version
from swhlab.core import ABF

# global module variables which control behavior
IMAGE_SAVE=True
IMAGE_SHOW=True

def frameAndSave(abf,tag="",dataType="plot",saveAsFname=False,closeWhenDone=True):
    """
    frame the current matplotlib plot with ABF info, and optionally save it.
    Note that this is entirely independent of the ABFplot class object.
    if saveImage is False, show it instead.

    Datatype should be:
        * plot
        * experiment
    """
    print("closeWhenDone",closeWhenDone)
    plt.tight_layout()
    plt.subplots_adjust(top=.93,bottom =.07)
    plt.annotate(tag,(.01,.99),xycoords='figure fraction',ha='left',va='top',family='monospace',size=10,alpha=.5)
    msgBot="%s [%s]"%(abf.ID,abf.protocomment)
    plt.annotate(msgBot,(.01,.01),xycoords='figure fraction',ha='left',va='bottom',family='monospace',size=10,alpha=.5)
    fname=tag.lower().replace(" ",'_')+".jpg"
    fname=dataType+"_"+fname
    plt.tight_layout()
    if IMAGE_SAVE:
        abf.log.info("saving [%s]",fname)
        try:
            if saveAsFname:
                saveAs=os.path.abspath(saveAsFname)
            else:
                saveAs=os.path.abspath(abf.outPre+fname)
            if not os.path.exists(abf.outFolder):
                os.mkdir(abf.outFolder)
            plt.savefig(saveAs)
        except Exception as E:
            abf.log.error("saving [%s] failed! 'pip install pillow'?",fname)
            print(E)
    if IMAGE_SHOW==True:
        if closeWhenDone==False:
            print("NOT SHOWING (because closeWhenDone==True and showing would mess things up)")
        else:
            abf.log.info("showing [%s]",fname)
            plt.show()
    if closeWhenDone:
        print("closing figure")
        plt.close('all')

class ABFplot:
    def __init__(self,abf):
        """Load an ABF and get ready to plot stuff."""
        self.log = logging.getLogger("swhlab plot")
        self.log.setLevel(swhlab.loglevel)

        self.close(True) # premptive?

        # prepare ABF class
        if type(abf) is str:
            self.log.debug("filename given, turning it into an ABF class")
            abf=ABF(abf)
        self.abf=abf

        # TODO: size in pixels
        self.figure_width=10
        self.figure_height=5
        self.figure_dpi=300
        self.subplot=False # set to True to prevent running plt.figure()

        self.gridAlpha=.5
        self.title=os.path.basename(abf.filename)
        self.traceColor='b'
        self.kwargs={"alpha":.8}
        self.rainbow=True
        self.colormap="Dark2"
        self.marginX,self.marginY=0,.1

        self.log.debug("plot initiated")


    ### high level plot operations

    def figure(self,forceNew=False):
        """make sure a figure is ready."""
        if plt._pylab_helpers.Gcf.get_num_fig_managers()>0 and forceNew is False:
            self.log.debug("figure already seen, not creating one.")
            return

        if self.subplot:
            self.log.debug("subplot mode enabled, not creating new figure")
        else:
            self.log.debug("creating new figure")
            plt.figure(figsize=(self.figure_width,self.figure_height))

    def show(self):
        numFigures=plt._pylab_helpers.Gcf.get_num_fig_managers()
        self.log.debug("showing figures (%d)"%numFigures)
        plt.show()

    def close(self,closeAll=True):
        numFigures=plt._pylab_helpers.Gcf.get_num_fig_managers()
        if closeAll:
            self.log.debug("closing all %d figures"%numFigures)
            plt.close('all')
        else:
            self.log.debug("closing 1 figure (of %d)"%numFigures)
            plt.close()

    def save(self,callit="misc",closeToo=True,fullpath=False):
        """save the existing figure. does not close it."""
        if fullpath is False:
            fname=self.abf.outPre+"plot_"+callit+".jpg"
        else:
            fname=callit
        if not os.path.exists(os.path.dirname(fname)):
            os.mkdir(os.path.dirname(fname))
        plt.savefig(fname)
        self.log.info("saved [%s]",os.path.basename(fname))
        if closeToo:
            plt.close()

    ### misc
    def getColor(self,fraction,reverse=False):
        cm=plt.get_cmap(self.colormap)
        if reverse:
            fraction=1-fraction
        return cm(fraction)

    def setColorBySweep(self):
        if self.rainbow:
            self.kwargs["color"]=self.getColor(self.abf.sweep/self.abf.sweeps)
        else:
            self.kwargs["color"]=self.traceColor
    ### plot modifications

    def comments(self,minutes=False):
        """
        Add comment lines/text to an existing plot. Defaults to seconds.
        Call after a plot has been made, and after margins have been set.
        """
        if self.comments==0:
            return
        self.log.debug("adding comments to plot")
        for i,t in enumerate(self.abf.comment_times):
            if minutes:
                t/=60.0
            plt.axvline(t,color='r',ls=':')
            X1,X2,Y1,Y2=plt.axis()
            Y2=Y2-abs(Y2-Y1)*.02
            plt.text(t,Y2,self.abf.comment_tags[i],color='r',rotation='vertical',
                     ha='right',va='top',weight='bold',alpha=.5,size=8,)

    def decorate(self,show=False,protocol=False):
        self.log.debug("decorating")
        if self.title:
            plt.title("{}".format(self.abf.ID))
        plt.xlabel("seconds")
        if protocol:
            plt.ylabel(self.abf.protoUnits2)
        else:
            plt.ylabel(self.abf.units2)
        if self.gridAlpha:
            plt.grid(alpha=self.gridAlpha)
        plt.margins(self.marginX,self.marginY)
        plt.tight_layout()
        if show:
            plt.show()

    ### figure creation

    def figure_chronological(self):
        """plot every sweep of an ABF file (with comments)."""
        self.log.debug("creating chronological plot")
        self.figure()
        for sweep in range(self.abf.sweeps):
            self.abf.setsweep(sweep)
            self.setColorBySweep()
            if self.abf.derivative:
                plt.plot(self.abf.sweepX,self.abf.sweepD,**self.kwargs)
            else:
                plt.plot(self.abf.sweepX,self.abf.sweepY,**self.kwargs)
        self.comments()
        self.decorate()

    def figure_sweep(self,sweep=0):
        self.log.debug("plotting sweep %d",sweep)
        self.figure()
        self.abf.setsweep(sweep)
        plt.plot(self.abf.sweepX2,self.abf.sweepY,**self.kwargs)
        self.decorate()

    def figure_sweeps(self, offsetX=0, offsetY=0):
        """plot every sweep of an ABF file."""
        self.log.debug("creating overlayed sweeps plot")
        self.figure()
        for sweep in range(self.abf.sweeps):
            self.abf.setsweep(sweep)
            self.setColorBySweep()
            plt.plot(self.abf.sweepX2+sweep*offsetX,
                     self.abf.sweepY+sweep*offsetY,
                     **self.kwargs)
        if offsetX:
            self.marginX=.05
        self.decorate()

    def figure_protocol(self):
        """plot the current sweep protocol."""
        self.log.debug("creating overlayed protocols plot")
        self.figure()
        plt.plot(self.abf.protoX,self.abf.protoY,color='r')
        self.marginX=0
        self.decorate(protocol=True)

    def figure_protocols(self):
        """plot the protocol of all sweeps."""
        self.log.debug("creating overlayed protocols plot")
        self.figure()
        for sweep in range(self.abf.sweeps):
            self.abf.setsweep(sweep)
            plt.plot(self.abf.protoX,self.abf.protoY,color='r')
        self.marginX=0
        self.decorate(protocol=True)



if __name__=="__main__":
    #fnames=glob.glob(r"C:\Users\scott\Documents\important\abfs\*.abf")
    fnames=glob.glob(r"C:\Users\swharden\Desktop\limited\*.abf")

    for fname in fnames:
        plot=ABFplot(fname)

        plot.figure_chronological()
        plot.save("chronological")

        plot.figure_sweeps()
        plot.save("sweeps")

    print("found %d files"%len(fnames))
    print("DONE")