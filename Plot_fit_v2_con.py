import sys
import math
import ROOT as rt
import argparse as arg
from Hist_style import *

parser = arg.ArgumentParser(description='Create workspace for higgs combine')
parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="MC top mass sample ['data','1695', '1715', '1725', '1735', '1755']")
parser.add_argument('-w', '--width', dest='width_sample', default=[None], type=str, nargs=1, help="MC top width sample ['data','190','170','150','130','090','075']")
#parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018']")
args = parser.parse_args()


mass  = args.mass_sample[0]
width = args.width_sample[0]
dataYear = args.Year[0]
Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18"}

tag = Combine_year_tag[dataYear]
def propagate_rate_uncertainity(hist, uncert):
    for i in range(hist.GetXaxis().GetNbins()):
        if hist.GetBinContent(i) != 0:
            hist.SetBinError(i, hist.GetBinContent(i) * uncert * 0.01)

def getcons(mass,width):
        if(mass!=None): fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
        else : fitfile = rt.TFile.Open("fitDiagnostics_W"+width+".root")
        roofitResults = fitfile.Get("fit_s")

        cons_top_sig = (roofitResults.floatParsFinal()).find("cons_EWK_bkg")
        print "cons_top_sig : ",cons_top_sig.getVal()," Error : ",cons_top_sig.getError()

        cons_top_bkg = (roofitResults.floatParsFinal()).find("cons_top_bkg")
        print "cons_top_bkg : ",cons_top_bkg.getVal()," Error : ",cons_top_bkg.getError()

        cons_EWK_bkg = (roofitResults.floatParsFinal()).find("cons_EWK_bkg")
        print "cons_EWK_bkg : ",cons_EWK_bkg.getVal()," Error : ",cons_EWK_bkg.getError()

        return cons_top_sig.getVal(),cons_top_bkg.getVal(),cons_top_bkg.getVal()

def getprefit_hist(mass,width,lep):
    hists = []
    Filename = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_"+lep+"_lt0p7gteq0p5_withoutDNNfit_rebin.root"
    Filename_cont = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_"+lep+"_gteq0p3_withoutDNNfit_rebin.root"
    File = rt.TFile(Filename,"Read")
    File_cont = rt.TFile(Filename_cont,"Read")
    gt_or_lt_tag=''
    if('gteq' in Filename):gt_or_lt_tag = gt_or_lt_tag+'_gt'
    if('lt' in Filename):gt_or_lt_tag = gt_or_lt_tag+'_lt'   
        #Data Vs Mc Condition
    rt.gROOT.cd()
    #Get the file and director where historgrams are stored for muon final state
    Dir = File.GetDirectory(lep+"jets")
    Dir_cont = File_cont.GetDirectory(lep+"jets")
    #Get Mc histograms for muon final state
    if(mass!=None):
        top_sig = Dir.Get("top_sig_"+mass+tag+gt_or_lt_tag) 
    if(width!=None):
        top_sig = Dir.Get("top_sig_"+width+tag+gt_or_lt_tag)#+width)
    print("top_bkg_1725"+tag+gt_or_lt_tag)
    top_bkg = Dir.Get("top_bkg_1725"+tag+gt_or_lt_tag)
    EWK_bkg = Dir.Get("EWK_bkg"+tag+gt_or_lt_tag)
    EWK_bkg_cont = Dir_cont.Get("EWK_bkg"+tag+"_gt")
    EWK_bkg_cont.Scale(EWK_bkg.Integral()/EWK_bkg_cont.Integral())
    EWK_bkg = EWK_bkg_cont.Clone()
    QCD = Dir.Get("QCD_DD"+tag+gt_or_lt_tag)
    Data = Dir.Get("data_obs")
   
    h1 = top_sig.Clone()
    h2 = top_bkg.Clone()
    h3 = EWK_bkg.Clone()
    h4 = QCD.Clone()
    h5 = Data.Clone()
    hists.append(h1)
    hists.append(h2)
    hists.append(h3)
    hists.append(h4)
    hists.append(h5)
    #hists[0].Print()
    #print type(hists[0])
    #raw_input()
    return hists

def Match_hist_from_Tgraph_asy_Error(Hist_input,Hist_fitgia):
    print("bins = ",Hist_input.GetNbinsX())
    for Bin in range(1,Hist_input.GetNbinsX()+1):
        print(Bin,Hist_input.GetBinContent(Bin),Hist_fitgia.GetBinContent(Bin)*Hist_input.GetBinWidth(1))
        

def Get_hist_from_Tgraph_asy_Error(Tgraph,Hist):
    newHist = Hist.Clone()
    print("================================")
    newHist.Print()
    newHist.Reset()
    print("bins = ",Hist.GetNbinsX())
    for Bin in range(1,Hist.GetNbinsX()+1):
        #print(Bin,Tgraph.Eval(Hist.GetBinCenter(Bin))*Hist.GetBinWidth(1),Hist.GetBinContent(Bin),Tgraph.GetErrorY(Bin)*Hist.GetBinWidth(1),Hist.GetBinError(Bin))
        newHist.SetBinContent(Bin,int(Tgraph.Eval(Hist.GetBinCenter(Bin))*Hist.GetBinWidth(1)))
        newHist.SetBinError(Bin,Tgraph.GetErrorY(Bin)*Hist.GetBinWidth(1))
        #print("================================")
        #newHist.Print()
    return newHist

def getthefit(mass,width,lep):
    if(mass!=None):fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
    else : fitfile = rt.TFile.Open("fitDiagnostics_W"+width+".root")
    print(lep+"jets"+tag+"_con_logM_fit_s")
    fit = fitfile.Get(lep+"jets"+tag+"_con_logM_fit_s")
    fit.Print()
    prefit_hists = getprefit_hist(mass,width,lep) #return top_sig,topbkg,EWK_bkg
    rt.gROOT.cd()
    Data_prefit_from_input_file = prefit_hists[0].Clone()  
    Data_prefit_from_input_file.Add(prefit_hists[1])
    Data_prefit_from_input_file.Add(prefit_hists[2])
    
    Data_prefit_from_input_file_saved_as_data = prefit_hists[4].Clone()  
    
    prefit_total = fitfile.Get("shapes_prefit/"+lep+"jets"+tag+"_con/total")
    prefit_total.Print()
    
    prefit_data_TError = fitfile.Get("shapes_prefit/"+lep+"jets"+tag+"_con/data")#.GetHistogram()
    #prefit_data_TError.Print()
    
    prefit_signal = fitfile.Get("shapes_prefit/"+lep+"jets"+tag+"_con/top_sig_con")#.GetHistogram()
    
    nbin = prefit_total.GetXaxis().GetNbins()
    ledge = prefit_total.GetXaxis().GetXmin()
    uedge = prefit_total.GetXaxis().GetXmax()
    
    Data_prefit = rt.TH1D('Data_refit_hist', '', nbin, ledge, uedge)
    Data_prefit = Get_hist_from_Tgraph_asy_Error(prefit_data_TError,Data_prefit_from_input_file)
    Match_hist_from_Tgraph_asy_Error(prefit_hists[0],prefit_signal)
    print("================================")
    Data_prefit.Print()
    #Data_prefit=Data_prefit_from_input_file
    Data_prefit.SetName("Data_prefit")
    print(Data_prefit.Print())
    Data_prefit.SetLineColor(rt.kBlack)
    Data_prefit.SetMarkerStyle(20)

    print("Data_prefit info from from Combine input files ")
    Data_prefit.Print()
  
    
    Data_postfit_roohist = fit.findObject("h_"+lep+"jets"+tag+"_con")
    #Data_postfit_roohist.SetFillCOlor(R.kRed)
    ResultPDF = fit.findObject("pdf_bin"+lep+"jets"+tag+"_con_Norm[logM]")
    ResultPDF_error = fit.findObject("pdf_bin"+lep+"jets"+tag+"_con_Norm[logM]_errorband")
    SigPDF = fit.findObject("pdf_bin"+lep+"jets"+tag+"_con_Norm[logM]_Comp[shapeSig*]")
    BkgPDF = fit.findObject("pdf_bin"+lep+"jets"+tag+"_con_Norm[logM]_Comp[shapeBkg*]")
    
    """if(mass!=None):fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
    else : fitfile = rt.TFile.Open("fitDiagnostics_width"+width+".root")
    fit = fitfile.Get(lep+"jets_logM_fit_s")
    #fit.Print()

    Data_postfit_roohist = fit.findObject("h_"+lep+"jets")
    #Data_postfit_roohist.SetFillCOlor(R.kRed)
    ResultPDF = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]")
    ResultPDF_error = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]_errorband")
    SigPDF = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]_Comp[shapeSig*]")
    BkgPDF = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]_Comp[shapeBkg*]")"""

        
    legend = rt.TLegend(0.58, 0.55, 0.78, 0.79)
    legend.SetBorderSize(1)
    legend.SetTextSize(0.045)
    legend.SetLineColor(0)
    legend.SetLineStyle(1)
    legend.SetLineWidth(1)
    legend.SetFillColor(0)
    legend.SetFillStyle(1001)
    #legend.SetHeader("beNDC", "C")
    legend.AddEntry(Data_prefit, "QCD Substr. MC", "ple1")
    legend.AddEntry(ResultPDF, "Fit.", "l")
    legend.AddEntry(SigPDF, "corr. top", "l")
    legend.AddEntry(BkgPDF, "Incorr. top + EWK", "l")


    can = rt.TCanvas("can","can",600,600)
    rt.gStyle.SetOptStat(0)
    can.cd()
    rt.gStyle.SetErrorX(0)
    rt.TGaxis.SetMaxDigits(3)

    pad1 = rt.TPad('pad1', 'pad1', 0.0, 0.195259, 1.0, 0.990683)
    pad1.SetBottomMargin(0.089)
    pad1.SetTicky()
    pad1.SetTickx()
    #pad1.GetGridy().SetMaximum(Data.GetMaximum() * 1.2)
    #pad1.SetRightMargin(0.143)
    pad1.Draw()
    pad1.cd()
    pad1.cd()
    frame = rt.gPad.DrawFrame(Data_postfit_roohist.GetXaxis().GetXmin(), 0.0,Data_postfit_roohist.GetXaxis().GetXmax(),Data_postfit_roohist.GetYaxis().GetXmax()*1.15,';Events')#,rt.RooFit.Title(" "))

    frame.SetTitle(".")
    frame.GetYaxis().SetTitle('Events / (0.099)')
    frame.GetYaxis().SetTitleSize(0.04)

    Data_prefit.SetTitle("")
    Data_prefit.Draw("P")
    #prefit_data_hist.Draw("P")
    
    #Data_postfit_roohist.Draw("same;P")
    ResultPDF_error.Draw("same")
    ResultPDF.Draw("same")
    SigPDF.Draw("same")
    BkgPDF.Draw("same")
    legend.Draw("same")
    yeartag = year_tag(dataYear,0.82,0.92,0.90,0.95)
    cmstext = getCMSInt_tag(0.33, 0.86, 0.38, 0.88)
    finalstate = leptonjet_tag(lep,0.24,0.81,0.37,0.83)
    
    cmstext.Draw()
    finalstate.Draw()
    yeartag.Draw()
    can.Update()

    can.cd()
    pad2 = rt.TPad("pad2", "pad2", 0.0, 0.0, 1.0, 0.2621035)
    pad2.SetTopMargin(0.0)
    pad2.SetBottomMargin(0.3)
    pad2.SetGridy()
    pad2.SetTicky()
    pad2.SetTickx()
    pad2.Draw()
    pad2.cd()

    rt.gROOT.cd()
    Data_postfit_fitdignostics = fitfile.Get("shapes_fit_s/"+lep+"jets"+tag+"_con/total") # this is done because if we use it dictrly in trgraph Ass error is shows error
    #Data_postfit_fitdignostics = fitfile.Get("shapes_fit_s/"+lep+"jets/total")
    print("Data_postfit info from fitdigonistic ")
    Data_postfit_fitdignostics.Print()

    nbin = Data_prefit.GetXaxis().GetNbins()
    ledge = Data_prefit.GetXaxis().GetXmin()
    uedge = Data_prefit.GetXaxis().GetXmax()
    Data_postfit = rt.TH1F('Data_postfit', '', nbin, ledge, uedge)
    print("prefit-postfit = res")
    
    for bin in range(1,nbin+1):
        #print(Data_postfit_roohist.GetBinContent(bin))
        #print("%s-%s = %s"%(Data_postfit_fitdignostics.GetBinContent(bin)*Data_postfit.GetBinWidth(bin),Data_prefit.GetBinContent(bin),(Data_postfit_fitdignostics.GetBinContent(bin)*Data_postfit.GetBinWidth(bin))-Data_prefit.GetBinContent(bin)))
        
        Data_postfit.SetBinContent(bin,Data_postfit_fitdignostics.GetBinContent(bin)*Data_postfit.GetBinWidth(bin)) 
        Data_postfit.SetBinError(bin,Data_postfit_fitdignostics.GetBinError(bin))

        #print("Data_postfit Info from fitdigonistic after multiply with bin width ")
        #Data_postfit.Print()

    #pad1.cd()
    #Data_postfit.Draw("same")
    pad2.cd()
    #Data_prefit = fitfile.Get("shapes_prefit/"+lep+"jets/total")	These histograms has wronf infromation or have infrokmation about someting else
    #print("Data_prefit Int from fitdiagonistic = ",Data_prefit.Integral())


    #h_ratio = rt.TGraphAsymmErrors(Data_postfit, Data_postfit)# 'pois')
    #print h_ratio.GetN()

    h_ratio = rt.TH1F('h_ratio', '', nbin, ledge, uedge)
    
    #print("pull, : , pull_err,  : ,sigma_pull,  : ,  prefit - postfit")
    for iBin in range(1,nbin+1):
        error_prefit = Data_prefit.GetBinError(iBin)
        error_postfit = Data_postfit.GetBinError(iBin)
        cont_prefit = Data_prefit.GetBinContent(iBin)
        cont_postfit = Data_postfit.GetBinContent(iBin)
        #h_ratio.SetBinContent(i,(Data_prefit.GetBinContent(i)-Data_postfit.GetBinContent(i))/math.sqrt(error_prefit*error_prefit+error_postfit*error_postfit))
        sigma_pull = rt.TMath.Sqrt( abs(error_prefit*error_prefit - error_postfit*error_postfit) )
        pull= ( cont_prefit - cont_postfit )/ sigma_pull
        pull_err = ( error_postfit-error_prefit )/ sigma_pull
        #print(pull," : ", pull_err, " : ",sigma_pull, " : ",  cont_prefit - cont_postfit)
        h_ratio.SetBinContent(iBin, pull)
        h_ratio.SetBinError(iBin, pull_err)
        #Add QCD_DD for the syst band"""

    h_ratio.SetFillColor(rt.kGray+3)
    h_ratio.SetFillStyle(3001)

    h_ratio.GetYaxis().SetTitle("Pull") 
    #band.GetXaxis().SetTitle(Data.GetXaxis().GetTitle())
    h_ratio.GetXaxis().SetTitle("ln(m_{t} / 1 GeV)")
    h_ratio.GetYaxis().CenterTitle(1) 
    h_ratio.GetYaxis().SetTitleOffset(0.35)              
    h_ratio.GetYaxis().SetTitleSize(0.12)
    h_ratio.GetXaxis().SetTitleSize(0.12)
    h_ratio.GetYaxis().SetLabelSize(0.07)
    h_ratio.GetXaxis().SetLabelSize(0.1)



    h_ratio.Draw('hist')
    can.Update()
    #raw_input()
    if(mass!=None):
        can.Print("Plots/Final_combine_fit_Control_"+mass+"_"+dataYear+"_"+lep+"_con.png")
        can.Print("Plots/Final_combine_fit_Control_"+mass+"_"+dataYear+"_"+lep+"_con.pdf")
    if(width!=None):
        can.Print("Plots/Final_combine_fit_Control_"+width+"_"+dataYear+"_"+lep+"_con.png")
        can.Print("Plots/Final_combine_fit_Control_"+width+"_"+dataYear+"_"+lep+"_con.pdf")
def getparams(mass,width):
    if(mass!=None): fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
    else : fitfile = rt.TFile.Open("fitDiagnostics_W"+width+".root")
    roofitResults = fitfile.Get("fit_s")

    mean = (roofitResults.floatParsFinal()).find("mean")
    print "mean : ",mean.getVal()," Error : ",mean.getError()

    Sigma = (roofitResults.floatParsFinal()).find("sigmaG")
    print "Sigma : ",Sigma.getVal()," Error : ",Sigma.getError()

if __name__ == "__main__":
    getthefit(mass,width,"mu")
    getthefit(mass,width,"el")
    #raw_input()
    #getparams(mass,width)
    #getcons(mass,width)
    #prefit_hist = getprefit_hist(mass,width,"mu")
    #prefit_hist[0].Draw()
    #prefit_hist[0].Print()
    #raw_input()
