import ROOT
import sys
from array import array
import pickle
from array import array
import ctypes
import math

drawprelim = True

class plotter_base(object):

    def __init__(self):
        self.fillstyle=1001
        self.linestyle=1
        self.linecolor=1
        self.linewidth=2
        self.fillcolor=ROOT.kOrange-3
        self.markerstyle=20
        self.corrFactors=[]

    def addCorrectionFactor(self,value,model):
        corr=dict()
        corr['value']=value
        corr['model']=model
        self.corrFactors.append(corr)

    def setLineProperties(self,linestyle,linecolor,linewidth):
        self.linestyle=linestyle
        self.linecolor=linecolor
        self.linewidth=linewidth 

    def setFillProperties(self,fillstyle,fillcolor):
        self.fillstyle=fillstyle
        self.fillcolor=fillcolor

    def setMarkerProperties(self,markerstyle):
        self.markerstyle=markerstyle



class rdf_plotter(plotter_base):
    def __init__(self,file,isMC=False,weight = "1.0",tree='Events',defaultCuts = "1.0",report='report'):
        self.rdf = ROOT.RDataFrame(tree,file)
        self.weight=weight
        self.defaultCuts = defaultCuts
        self.file = file
        self.report = report
        super(rdf_plotter,self).__init__()
        #if MC read the sum of weights and weigh the event
        if isMC:
            f=ROOT.TFile(file)
            t=f.Get('Runs')
            sumw = 0.0
            for event in t:
                sumw += event.genEventSumw
            self.weight = self.weight+'*(genWeight/{})*(sample_sigma)*(Pileup_weight)'.format(sumw if sumw>0 else 1.0)
            f.Close()

    def readReport(self):
        out = {}
        report = ROOT.TFile(self.file).Get(self.report)
        cuts = report.GetListOfBranches()
        for c in cuts:
            out[c] = 0
        for event in report:
            for c in cuts:
                out[c] += getattr(event, c)
        report.Close()
        return out

    def define(self, var, definition):
        self.rdf = self.rdf.Define(var, definition)

    def redefine(self, var, definition):
        self.rdf = self.rdf.Redefine(var, definition)

        
    def hist1d(self,var,cuts,lumi,model,titlex = "",units = ""):
        corrString="1.0"
        for corr in self.corrFactors:
            corrString = corrString+"*("+str(corr['value'])+")" 
        c = "("+self.defaultCuts+")*("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")"
        rdf=self.rdf.Define('plot_weight',c)
        h=rdf.Histo1D(model,var,'plot_weight')
        h.Sumw2()
        h.SetLineStyle(self.linestyle)
        h.SetLineColor(self.linecolor)
        h.SetLineWidth(self.linewidth)
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.SetMarkerStyle(self.markerstyle)
        if units=="":
            h.GetXaxis().SetTitle(titlex)
        else:
            h.GetXaxis().SetTitle(titlex+ " ["+units+"]")
        for n in range(1, h.GetNbinsX()+1):
            if h.GetBinContent(n) < 0:
                h.SetBinContent(n, 0)
        return h


    def profile1d(self,var1,var2,cuts,lumi,model,titlex = "",unitsx = "",titley = "",unitsy = ""):
        corrString="1.0"
        for corr in self.corrFactors:
            corrString = corrString+"*("+str(corr['value'])+")" 
        c = "("+self.defaultCuts+")*("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")"
        rdf=self.rdf.Define('plot_weight',c)
        h=rdf.Profile1D(model,var1,var2,'plot_weight')
        h.SetLineStyle(self.linestyle)
        h.SetLineColor(self.linecolor)
        h.SetLineWidth(self.linewidth)
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.SetMarkerStyle(self.markerstyle)
        if unitsx=="":
            h.GetXaxis().SetTitle(titlex)
        else:
            h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        if unitsy=="":
            h.GetYaxis().SetTitle(titley)
        else:
            h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")
        return h


    def hist2d(self,var1,var2,cuts,lumi,model,titlex = "",unitsx = "",titley="",unitsy=""):
        corrString="1.0"
        for corr in self.corrFactors:
            corrString = corrString+"*("+str(corr['value'])+")" 
        c = "("+self.defaultCuts+")*("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")"
        rdf=self.rdf.Define('plot_weight',c)
        h=rdf.Histo2D(model,var1,var2,'plot_weight')
        h.Sumw2()
        h.SetLineStyle(self.linestyle)
        h.SetLineColor(self.linecolor)
        h.SetLineWidth(self.linewidth)
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.SetMarkerStyle(self.markerstyle)
        if unitsx=="":
            h.GetXaxis().SetTitle(titlex)
        else:
            h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        if unitsy=="":
            h.GetYaxis().SetTitle(titley)
        else:
            h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")
        return h




def convertToPoisson(h):
    graph = ROOT.TGraphAsymmErrors()
    q = (1-0.6827)/2.

    for i in range(1,h.GetNbinsX()+1):
        x=h.GetXaxis().GetBinCenter(i)
        xLow =h.GetXaxis().GetBinLowEdge(i) 
        xHigh =h.GetXaxis().GetBinUpEdge(i) 
        y=h.GetBinContent(i)
        yLow=0
        yHigh=0
        if y !=0.0:
            yLow = y-ROOT.Math.chisquared_quantile_c(1-q,2*y)/2.
            yHigh = ROOT.Math.chisquared_quantile_c(q,2*(y+1))/2.-y
            graph.SetPoint(i-1,x,y)
            graph.SetPointEYlow(i-1,yLow)
            graph.SetPointEYhigh(i-1,yHigh)
            graph.SetPointEXlow(i-1,0.0)
            graph.SetPointEXhigh(i-1,0.0)


    graph.SetMarkerStyle(20)
    graph.SetLineWidth(2)
    graph.SetMarkerSize(1.)
    graph.SetMarkerColor(ROOT.kBlack)
    

    return graph    



class merged_plotter(plotter_base):

    def __init__(self, plotters):
        self.fillstyle=1001
        self.linestyle=1
        self.linecolor=1
        self.linewidth=2
        self.fillcolor=ROOT.kOrange-3
        self.markerstyle=20
        self.corrFactors=[]
        self.plotters = plotters

    def define(self, var, definition):
        for plotter in self.plotters:
            plotter.define(var, definition)

    def redefine(self, var, definition):
        for plotter in self.plotters:
            plotter.redefine(var, definition)

    def hist1d(self,var,cuts,lumi,model,titlex = "",units = ""):
        h = None
        for plotter in self.plotters:
            if h is None:
                h = plotter.hist1d(var, cuts, lumi, model, titlex, units)
            else:
                h.Add(plotter.hist1d(var, cuts, lumi, model, titlex, units).GetValue())
        if h is None:
            tmprdf = ROOT.RDataFrame(1)
            tmprdf = tmprdf.Define("x", "0")
            h = tmprdf.Define("goodX", "x!=0").Histo1D(model, "goodX")
        h.Sumw2()
        h.SetLineStyle(self.linestyle)
        h.SetLineColor(self.linecolor)
        h.SetLineWidth(self.linewidth)
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.SetMarkerStyle(self.markerstyle)
        if units=="":
            h.GetXaxis().SetTitle(titlex)
        else:
            h.GetXaxis().SetTitle(titlex+ " ["+units+"]")
        return h


    def hist2d(self,var1,var2,cuts,lumi,model,titlex = "",unitsx = "",titley="",unitsy=""):
        h = None
        for plotter in self.plotters:
            if h is None:
                h = plotter.hist2d(var1,var2, cuts, lumi, model, titlex, unitsx, titley, unitsy)
            else:
                h.Add(plotter.hist2d(var1,var2, cuts, lumi, model, titlex, unitsx, titley, unitsy).GetValue())
        h.Sumw2()
        h.SetLineStyle(self.linestyle)
        h.SetLineColor(self.linecolor)
        h.SetLineWidth(self.linewidth)
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.SetMarkerStyle(self.markerstyle)
        if unitsx=="":
            h.GetXaxis().SetTitle(titlex)
        else:
            h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        if unitsy=="":
            h.GetYaxis().SetTitle(titley)
        else:
            h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")
        return h


    def readReport(self):
        out = {}
        for plotter in self.plotters:
            r = plotter.readReport()
            for cut in r:
                if cut in out:
                    out[cut] += r[cut]
                else:
                    out[cut] = r[cut]
        return out

class combined_plotter(object):
    def __init__(self,defaultCut="1"):
        self.plotters = []
        self.types    = []
        self.labels   = []
        self.names    = []
        self.log=False
        self.defaultCut=defaultCut

    def setLog(self,doLog):
        self.log=doLog

    def add_plotter(self,plotter,name="",label = "label",typeP = "background"):
        self.plotters.append(plotter)
        self.types.append(typeP)
        self.labels.append(label)
        self.names.append(name)

    def define(self, var, definition):
        for plotter in self.plotters:
            plotter.define(var, definition)

    def redefine(self, var, definition):
        for plotter in self.plotters:
            plotter.redefine(var, definition)


    def draw_stack(self,var,cut,lumi,model,titlex = "", units = "",expandY=0.0,SFs="(1)", verbose = False, prelim = "Work in progress", lumi_label = ""):
        canvas = ROOT.TCanvas("canvas","")
#        ROOT.gStyle.SetOptStat(0)
#        ROOT.gStyle.SetOptTitle(0)
#        canvas.Range(-68.75,-7.5,856.25,42.5)
#        canvas.SetFillColor(0)
#        canvas.SetBorderMode(0)
#        canvas.SetBorderSize(2)
#        canvas.SetTickx(1)
#        canvas.SetTicky(1)
#        canvas.SetLeftMargin(0.15)
        canvas.SetRightMargin(0.05)
#        canvas.SetTopMargin(0.05)
#        canvas.SetBottomMargin(0.15)
#        canvas.SetFrameFillStyle(0)
#        canvas.SetFrameBorderMode(0)
#        canvas.SetFrameFillStyle(0)
#        canvas.SetFrameBorderMode(0)


        canvas.cd()
        hists=[]
        stack = ROOT.THStack("stack","")
        
        signal=0
        background=0
        backgroundErr=0
        
        data=None
        dataG=None
        error=ctypes.c_double(0.0)

        cutL="("+self.defaultCut+")*("+cut+")"

        for (plotter,typeP,label,name) in zip(self.plotters,self.types,self.labels,self.names):
            if typeP == "signal" or typeP =="background":
                hist = plotter.hist1d(var,cutL+"*("+SFs+")",lumi,model,titlex,units)
                hist.SetName(name)

                stack.Add(hist.GetValue())
                hists.append(hist.GetValue())
                if verbose:
                    print( label+" : %f\n" % hist.Integral())
 
                if typeP == "signal" :
                    signal+=hist.Integral()
                if typeP == "background" :
                    background+=hist.IntegralAndError(1,hist.GetNbinsX(),error)
                    backgroundErr+=error.value*error.value
       
            if typeP =="data":
                hist = plotter.hist1d(var,cutL,"1",model,titlex,units)
                hist.SetName(hist.GetName()+label)
                hists.append(hist.GetValue())
                data=hist.GetValue()
                dataG=convertToPoisson(hist.GetValue())
                dataG.SetLineWidth(1)
                if verbose:
                    print( label+" : %f\n" % hist.Integral())
                
       
        #if data not found plot stack only
        if data != None:                  
            datamax = ROOT.Math.chisquared_quantile_c((1-0.6827)/2.,2*(data.GetMaximum()+1))/2.

        else: 
            datamax = stack.GetMaximum()
        if not self.log:
            frame = canvas.DrawFrame(hists[0].GetXaxis().GetXmin(),0.0,hists[0].GetXaxis().GetXmax(),max(stack.GetMaximum(),datamax)*(1.20+expandY*0.3))
        else:    
            frame = canvas.DrawFrame(hists[0].GetXaxis().GetXmin(),0.1,hists[0].GetXaxis().GetXmax(),max(stack.GetMaximum(),datamax)*100)

#        frame.GetXaxis().SetLabelFont(42)
#        frame.GetXaxis().SetLabelOffset(0.007)
#        frame.GetXaxis().SetLabelSize(0.045)
        frame.GetXaxis().SetTitleSize(0.05)
#        frame.GetXaxis().SetTitleOffset(1.15)
#        frame.GetXaxis().SetTitleFont(42)
#        frame.GetYaxis().SetLabelFont(42)
#        frame.GetYaxis().SetLabelOffset(0.007)
#        frame.GetYaxis().SetLabelSize(0.045)
        frame.GetYaxis().SetTitleSize(0.05)
#        frame.GetYaxis().SetTitleOffset(1.4)
#        frame.GetYaxis().SetTitleFont(42)
#        frame.GetZaxis().SetLabelFont(42)
#        frame.GetZaxis().SetLabelOffset(0.007)
#        frame.GetZaxis().SetLabelSize(0.045)
#        frame.GetZaxis().SetTitleSize(0.05)
#        frame.GetZaxis().SetTitleFont(42)

        if len(units)>0:
            frame.GetXaxis().SetTitle(titlex + " (" +units+")")
            frame.GetYaxis().SetTitle("Events / "+str((hists[0].GetXaxis().GetXmax()-hists[0].GetXaxis().GetXmin())/hists[0].GetNbinsX())+ " "+units)
        else:    
            frame.GetXaxis().SetTitle(titlex)
            frame.GetYaxis().SetTitle("Events")

        frame.Draw()
        stack.Draw("A,HIST,SAME")
        if data !=None:
            dataG.Draw("Psame")              

        legend = ROOT.TLegend(0.62,0.6,0.92,0.90,"","brNDC")
        legend.SetBorderSize(0)
        legend.SetLineColor(1)
        legend.SetLineStyle(1)
        legend.SetLineWidth(1)
        legend.SetFillColor(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)

        legend.SetFillColor(ROOT.kWhite)
        for (histo,label,typeP) in  list(zip(hists,self.labels,self.types))[::-1]:
            if typeP != "data" and typeP !='signal':
                legend.AddEntry(histo,label,"f")
            elif typeP == 'data':
                legend.AddEntry(histo,label,"p")

        for (histo,label,typeP) in  list(zip(hists,self.labels,self.types))[::-1]:
            if typeP == "signal":
                legend.AddEntry(histo,label,"f")

        tex_prelim = ROOT.TLatex()
        if drawprelim:
            if prelim != "":
                tex_prelim.SetTextSize(0.03)
                tex_prelim.DrawLatexNDC(.11, .91, "#scale[1.5]{CMS}"+" {}".format(prelim))
                tex_prelim.Draw("same")
        
        float_lumi = float(lumi)
        float_lumi = float_lumi/1000.
        tex_lumi = ROOT.TLatex()
        tex_lumi.SetTextSize(0.035)
        tex_lumi.SetTextAlign(31)
        tex_lumi.DrawLatexNDC(.93, .91, "13 TeV ({:.1f}".format(float_lumi) + " fb^{-1})")
        tex_lumi.Draw("same")


 #       ROOT.SetOwnership(legend,False)

        legend.Draw()
        if self.log:
            canvas.SetLogy()
#       canvas.SetLeftMargin(canvas.GetLeftMargin()*1.15)
        canvas.Update()



        if verbose:
            print("---------------------------")
            print( "Signal = %f" %(signal))
            print( "Bkg    = %f" %(background))
            if data is not None:
                print ("Observed = %f"%(data.Integral()))
                integral = data.IntegralAndError(1,data.GetNbinsX(),error)
                if background>0.0:
                    print ("Data/Bkg= {ratio} +- {err}".format(ratio=integral/background,err=math.sqrt(error.value*error.value/(background*background)+integral*integral*backgroundErr/(background*background*background*background))))

        canvas.RedrawAxis()
        canvas.Update()
        plot={'canvas':canvas,'stack':stack,'legend':legend,'data':data,'dataG':dataG,'hists':hists,'prelim':tex_prelim, 'lumi': tex_lumi}

        return plot


# The nostack option normalizes the background and signal
# contributions separately. Without this all MC contributions
# are normalized together and drawn stacked
    def draw_comp(self,var,cut,model,titlex = "", units = "",expandY=0.0,nostack=True,prelim="Work in progress",SFs = "(1)"): 
        canvas = ROOT.TCanvas("canvas","")
#        ROOT.gStyle.SetOptStat(0)
#        ROOT.gStyle.SetOptTitle(0)
#        canvas.Range(-68.75,-7.5,856.25,42.5)
#        canvas.SetFillColor(0)
#        canvas.SetBorderMode(0)
#        canvas.SetBorderSize(2)
#        canvas.SetTickx(1)
#        canvas.SetTicky(1)
#        canvas.SetLeftMargin(0.15)
        canvas.SetRightMargin(0.05)
#        canvas.SetTopMargin(0.05)
#        canvas.SetBottomMargin(0.15)
#        canvas.SetFrameFillStyle(0)
#        canvas.SetFrameBorderMode(0)
#        canvas.SetFrameFillStyle(0)
#        canvas.SetFrameBorderMode(0)


        canvas.cd()
        hists=[]
        labels = {}
        stack = ROOT.THStack("stack","")
        
        signal=0
        background=0
        backgroundErr=0
        
        data=[]

        cutL="("+self.defaultCut+")*("+cut+")"
        scale = 0.0
        for (plotter,typeP,label,name) in zip(self.plotters,self.types,self.labels,self.names):
            hist = plotter.hist1d(var,cutL+"*("+SFs+")","1",model,titlex,units)
            hist.SetFillStyle(0)
            hist.SetName(name+label)
            labels[hist.GetValue()] = label
            if nostack:
                if hist.Integral() == 0:
                    stack.Add(hist.GetValue())
                    hists.append(hist)
                    continue
                hist.Scale(1.0/hist.Integral())
                stack.Add(hist.GetValue())
                hists.append(hist.GetValue())
            else:
                if typeP =="data":
                    if hist.Integral() > 0:
                        hist.Scale(1.0/hist.Integral())
                    data.append(hist.GetValue())
                else:
                    scale += hist.Integral()
                    hists.append(hist.GetValue())
                    
        if nostack:
            stack.Draw("hist,nostack")
        else:
            for h in hists:
                h.Scale(1./scale)
                stack.Add(h)
            stack.Draw("hist")
            for h in data:
                h.Draw("hist,same")

        canvas.SetLeftMargin(canvas.GetLeftMargin()*1.15)
        stack.SetMinimum(0)
        if len(units):
            stack.GetXaxis().SetTitle(titlex + " ["+units+"]")
        else:
            stack.GetXaxis().SetTitle(titlex)

        stack.GetYaxis().SetTitle("a.u.")
        stack.GetYaxis().SetTitleOffset(0.9)
        stack.GetYaxis().SetTitleSize(0.05)
        stack.GetXaxis().SetTitleSize(0.05)

        legend = ROOT.TLegend(0.6, 0.6, 0.9, 0.9)
        legend.SetFillColor(ROOT.kWhite)
        for histo in labels.keys():
            legend.AddEntry(histo, labels[histo], 'lf')
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        ROOT.SetOwnership(legend, False)
        legend.Draw()
        
        if drawprelim:
            tex_prelim = ROOT.TLatex()
            if prelim != "":
                tex_prelim.SetTextSize(0.03)
                tex_prelim.DrawLatexNDC(.11, .91, "#scale[1.5]{CMS}"+" {}".format(prelim))
                tex_prelim.Draw("same")
        
        canvas.Update()

        return {'canvas': canvas, 'stack': stack, 'legend': legend, 'data': data, 'hists': hists}

