import ROOT as R
from ROOT import RooFit 
import sys, datetime
from Hist_style import *
import argparse as arg
import os
#from TOY_local_fit import Toy_Mc 
parser = arg.ArgumentParser(description='Create workspace for higgs combine')
parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="MC top mass sample [data , 1695, 1715, 1735, 1755]")
parser.add_argument('-w', '--width', dest='width_sample', default=[None], type=str, nargs=1, help="MC top width sample ['data','190', '170', '150','130','090','075']")
#parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['UL2017'], type=str, nargs=1, help="Year of Data collection [ UL2016preVFP  UL2016postVFP  UL2017  UL2018 ]")
parser.add_argument('-f', '--localfit', dest='local_fit', default=[None], type=str, nargs=1, help="Local fit run for  ['sig','top_bkg','ewk_bkg','final', 'final_mu', 'final_el']")
parser.add_argument('-s', '--sys', dest='sys', default=[''], type=str, nargs=1, help='systematic sample replace the sig and background  ["PSWeight_ISR_Up", "PSWeight_ISR_Down", "PSWeight_FSR_Up", "PSWeight_FSR_Down","hdamp_Up", "hdamp_Down"]')
args = parser.parse_args()

        
mass  = args.mass_sample[0]
width = args.width_sample[0]
dataYear = args.Year[0]
local_fit = args.local_fit[0]
sys = args.sys[0]
date   = datetime.datetime.now()

if(mass=='data' or width =='data'):
	RealData = True
	mass = "1725"
else:
	RealData = False

print( "mass: ",mass)
print( "width: ",width)
print( "RealData: ",RealData)
print( "dataYear: ",dataYear)
print( "localfit: ",local_fit)

def PrintPar(x1=0.385, y1=0.86, x2=0.495, y2=0.88,name="#chi^2/NDF",val=0.0):
        cntrl = R.TPaveText(x1,y1,x2,y2,"brNDC")
        cntrl.SetFillStyle(0)
        cntrl.SetBorderSize(0)
        cntrl.SetMargin(0)
        cntrl.SetTextFont(42)
        cntrl.SetTextSize(0.05)
        cntrl.SetTextColor(R.kRed)
        cntrl.SetTextAlign(33)
        cntrl.AddText(name+" "+str(val))
        return cntrl

def propagate_rate_uncertainity(hist, uncert):
    for i in range(hist.GetXaxis().GetNbins()):
        if hist.GetBinContent(i) != 0:
            hist.SetBinError(i, hist.GetBinContent(i) * uncert * 0.01)

Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18"}

tag = Combine_year_tag[dataYear]

CMSTAG  = getCMSInt_tag(x1=0.32, y1=0.86, x2=0.4, y2=0.88)
lepton_tag_mu = leptonjet_tag(lep="mu",x1=0.32, y1=0.82, x2=0.4, y2=0.84)
lepton_tag_el = leptonjet_tag(lep="el",x1=0.32, y1=0.82, x2=0.4, y2=0.84)
year_tag = year_tag(dataYear,x1=0.85, y1=0.92, x2=0.9, y2=0.95)
   


if __name__ == "__main__":
    #define Variable
    logM = R.RooRealVar("logM","#it{ln} m_{t}",R.TMath.Log(100.0),R.TMath.Log(300))
    #create RooDataHist
    #------------------------------------------------i
    #read the file to get the hustogrms
    Filename_mu = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_gteq0p7_withDNNfit_rebin.root"
    Filename_el = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_gteq0p7_withDNNfit_rebin.root"
    Filename_mu_cont = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_gteq0p3_withDNNfit_rebin.root"
    Filename_el_cont = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_gteq0p3_withDNNfit_rebin.root"

    File_mu = R.TFile(Filename_mu,"Read")
    File_el = R.TFile(Filename_el,"Read")
    File_mu_cont = R.TFile(Filename_mu_cont,"Read")
    File_el_cont = R.TFile(Filename_el_cont,"Read")
    #Data Vs Mc Condition

    gt_or_lt_tag = ''
    if('gteq' in Filename_mu):gt_or_lt_tag = gt_or_lt_tag+'_gt'
    if('lt' in Filename_mu):gt_or_lt_tag = gt_or_lt_tag+'_lt'

    #Get the file and director where historgrams are stored for muon final state
    dir_mu = File_mu.GetDirectory("mujets")
    dir_mu_cont = File_mu_cont.GetDirectory("mujets")
    #Get Mc histograms for muon final state
    if(mass!= None):
        top_sig_mu = dir_mu.Get("top_sig_"+mass+tag+gt_or_lt_tag+sys)
    if(width!= None):
        top_sig_mu = dir_mu.Get("top_sig_"+width+tag+gt_or_lt_tag+sys)
        
    top_bkg_mu = dir_mu.Get("top_bkg_1725"+tag+gt_or_lt_tag+sys)
    EWK_bkg_mu = dir_mu.Get("EWK_bkg"+tag+gt_or_lt_tag)
    EWK_bkg_mu_cont = dir_mu_cont.Get("EWK_bkg"+tag+"_gt")
    QCD_DD = dir_mu.Get("QCD_DD"+tag+gt_or_lt_tag)

    print( "top_sig_mu Integral : ",top_sig_mu.Integral() )
    print( " top_bkg_mu Integral : ",top_bkg_mu.Integral())
    print( " EWK_bkg_mu Integral : ",EWK_bkg_mu.Integral())
    print( " EWK_bkg_mu_cont Integral : ",EWK_bkg_mu_cont.Integral())
    if(RealData==False):
        #Add all Mc histogram to creat full MC hisogram for muon final state
        histData_mu=top_sig_mu.Clone()
        histData_mu.Add(top_bkg_mu)  # for a cross check i have commented this line. i uncommented it before pushing the code. so !!warning!!
        EWK_bkg_mu_cont.Scale(EWK_bkg_mu.Integral()/EWK_bkg_mu_cont.Integral())
        EWK_bkg_mu=EWK_bkg_mu_cont #replace the sig region template with control region template
        histData_mu.Add(EWK_bkg_mu)
        print( "Total MC",histData_mu.Integral())
        #get real data

    if(RealData):
        histData_mu = dir_mu.Get("data_obs")
        print( "data hist integral: ",histData_mu.Integral())

    print( R.TMath.Exp(histData_mu.GetBinLowEdge(15)+histData_mu.GetBinWidth(15)))
    #Get the file and director where historgrams are stored for electron final state
    dir_el = File_el.GetDirectory("eljets")
    dir_el_cont = File_el_cont.GetDirectory("eljets")
    #Get Mc histograms for electron final state
    if(mass!= None):
        top_sig_el = dir_el.Get("top_sig_"+mass+tag+gt_or_lt_tag+sys)
    if(width!= None):
        top_sig_el = dir_el.Get("top_sig_"+width+tag+gt_or_lt_tag+sys)

    top_bkg_el = dir_el.Get("top_bkg_1725"+tag+gt_or_lt_tag+sys)
    EWK_bkg_el = dir_el.Get("EWK_bkg"+tag+gt_or_lt_tag)
    EWK_bkg_el_cont = dir_el_cont.Get("EWK_bkg"+tag+"_gt")
    QCD_DD = dir_mu.Get("QCD_DD"+tag+gt_or_lt_tag)

    print( "top_sig_el Integral : ",top_sig_el.Integral() )
    print( " top_bkg_el Integral : ",top_bkg_el.Integral() )
    print( " EWK_bkg_el Integral : ",EWK_bkg_el.Integral())
    print( " EWK_bkg_el_cont Integral : ",EWK_bkg_el_cont.Integral())
    if(RealData==False):
        #Add all Mc histogram to creat full MC hisogram for electron final state
        histData_el = top_sig_el.Clone()
        histData_el.Add(top_bkg_el) # for a cross check i have commented this line. i uncommented it before pushing the code. so !!warning!!
        EWK_bkg_el_cont.Scale(EWK_bkg_el.Integral()/EWK_bkg_el_cont.Integral())
        EWK_bkg_el=EWK_bkg_el_cont #replace the sig region template with control region template
        histData_el.Add(EWK_bkg_el)
        print("Totle MC : ",histData_el.Integral(), )
    #get real data
    if(RealData):
        histData_el = dir_el.Get("data_obs")
        print( "data hist integral: ",histData_el.Integral())

    #Create RooDatahist for muon final state
    data_mu = R.RooDataHist("data_mu","data_mu",R.RooArgList(logM),histData_mu)
    #Create RooDatahist for muon final state
    data_el = R.RooDataHist("data_el","data_el",R.RooArgList(logM),histData_el)

    
    mean = R.RooRealVar("mean","mean",5.1,4.5,5.5)
    sigmaG = R.RooRealVar("sigmaG","sigmaG",0.15098,0.01,5)#0.186
    sigmaG2Frac_mu = R.RooRealVar("sigmaG2Frac_mu","sigmaG2Frac_mu",0.1,0.0,5.0) #Best Fit Value
    sigmaG2Frac_el = R.RooRealVar("sigmaG2Frac_el","sigmaG2Frac_el",0.1,0.0,5.0) #Best Fit Value
    sigmaG2_mu = R.RooFormulaVar("sigmaG2_mu","sigmaG2_mu","@0/@1",R.RooArgList(sigmaG,	sigmaG2Frac_mu))#R.RooFit.RooConst(0.935)))#R.RooFit.RooConst(0.935)))
    sigmaG2_el = R.RooFormulaVar("sigmaG2_el","sigmaG2_el","@0/@1",R.RooArgList(sigmaG,sigmaG2Frac_el))#R.RooFit.RooConst(0.917)))#sigmaG2Frac_el))#R.RooFit.RooConst(0.917)))
    #signal Bifrac gaussian pdf
    """gauss_mu = R.RooBifurGauss("gauss_mu","gauss_mu",logM,mean,sigmaG,R.RooFit.RooConst(0.1430)) #only core sigma flaoted frac fixed
    gauss_el = R.RooBifurGauss("gauss_el","gauss_el",logM,mean, sigmaG,R.RooFit.RooConst(0.1394)) #only core sigma flaoted

    #Landau pdf
    lnd_mu = R.RooLandau("lnd_mu","lnd_mu",logM,R.RooFit.RooConst(5.4),R.RooFit.RooConst(0.0689)) # sigma fixed
    lnd_el = R.RooLandau("lnd_el","lnd_el",logM,R.RooFit.RooConst(5.456871),R.RooFit.RooConst(0.08981)) # sigma fixed
    sig_pdf_mu = R.RooAddPdf("sig_pdf_mu","Gaussian+Landau",R.RooArgList(gauss_mu,lnd_mu),R.RooArgList(R.RooFit.RooConst(0.9186)),True)
    sig_pdf_el = R.RooAddPdf("sig_pdf_el","Gaussian+Landau",R.RooArgList(gauss_el,lnd_el),R.RooArgList(R.RooFit.RooConst(0.9298)),True)"""


   
    #redefine the sig pdf
    #sig_pdf_mu = R.RooGaussian("sig_pdf_mu","gauss_mu",logM,mean,sigmaG)
    #sig_pdf_el = R.RooGaussian("sig_pdf_el","gauss_el",logM,mean,sigmaG)

    sig_pdf_mu = R.RooBifurGauss("sig_pdf_mu","gauss_mu",logM,mean,sigmaG,sigmaG2_mu)#R.RooFit.RooConst(0.147))#sigmaG2)#R.RooFit.RooConst(0.141887))
    sig_pdf_el = R.RooBifurGauss("sig_pdf_el","gauss_el",logM,mean,sigmaG,sigmaG2_el)#R.RooFit.RooConst(0.140))#sigmaG2)#R.RooFit.RooConst(0.138264))

    #Top background pdf CristalBall Shape
    alpha = R.RooRealVar("alpha","alpha",-0.6642,-12.0,12.0)
    num = R.RooRealVar("num","num",100.0,1.,500.0)
    num2 = R.RooRealVar("num2","num2",100.0,1.,500.0)

   


    sigmaL_topbkg_mu = R.RooFit.RooConst(0.169)
    #sigmaL_topbkg_mu = R.RooRealVar("sigmaL_topbkg_mu","sigmaL_topbkg_mu",0.15098,0.01,1)
    sigmaL_topbkg_el = R.RooFit.RooConst(0.180)
    #sigmaL_topbkg_el = R.RooRealVar("sigmaL_topbkg_el","sigmaL_topbkg_el",0.15098,0.01,1)
    #mean_top_bkg_mu = R.RooRealVar("mean_top_bkg_mu","mean_top_bkg_mu",5.1,4.5,5.5)
    #mean_top_bkg_el = R.RooRealVar("mean_top_bkg_el","mean_top_bkg_el",5.1,4.5,5.5)
    
    #sigmaFrac_el = R.RooRealVar("sigmaFrac_el","sigmaFrac_el",0.1,0.0,5.0) #Best Fit Value
    #sigmaFrac_mu = R.RooRealVar("sigmaFrac_mu","sigmaFrac_mu",0.1,0.0,5.0)
    sigmaR_mu = R.RooFormulaVar("sigmaR_mu","sigmaR_mu","@0/@1",R.RooArgList(sigmaL_topbkg_mu,R.RooFit.RooConst(0.98)))#sigmaFrac))#R.RooFit.RooConst(0.90)))
    sigmaR_el = R.RooFormulaVar("sigmaR_el","sigmaR_el","@0/@1",R.RooArgList(sigmaL_topbkg_el,R.RooFit.RooConst(1.08)))#sigmaFrac))#R.RooFit.RooConst(0.87)))
    topbkg_pdf_mu = R.RooBifurGauss("topbkg_pdf_mu","gauss_mu",logM,R.RooFit.RooConst(5.116),sigmaL_topbkg_mu,sigmaR_mu)#mean_top_bkg,sigmaL_topbkg_mu,sigmaR_mu) R.RooFit.RooConst(5.111)
    topbkg_pdf_el = R.RooBifurGauss("topbkg_pdf_el","gauss_el",logM,R.RooFit.RooConst(5.124),sigmaL_topbkg_el,sigmaR_el)#logM,mean_top_bkg,sigmaL_topbkg_el,sigmaR_el)#R.RooFit.RooConst(5.101),sigmaL_topbkg_el,sigmaR_el)
    
    
    #topbkg_pdf_mu = R.RooBifurGauss("topbkg_pdf_mu","gauss_mu",logM,mean,sigmaG2_mu,sigmaG)
    #topbkg_pdf_el = R.RooBifurGauss("topbkg_pdf_el","gauss_el",logM,mean,sigmaG2_el,sigmaG)

    #EWK bakground pdf Novosibirsk
    #peak_el = R.RooRealVar("peak_el","peak_el",5.,1.,10.0)
    #peak_mu = R.RooRealVar("peak_mu","peak_mu",5.,1.,10.0)
    #width_Novo_el = R.RooRealVar("width_Novo_el","width_Novo_el",0.1,0.0,5.0)
    #width_Novo_mu = R.RooRealVar("width_Novo_mu","width_Novo_mu",0.1,0.0,5.0)
    #tail_el = R.RooRealVar("tail_el","tail_el",-0.25,-5.,1.0) 
    #tail_mu = R.RooRealVar("tail_mu","tail_mu",-0.25,-5.,1.0) 
    EWKbkg_pdf_mu = R.RooNovosibirsk("EWKbkg_pdf_mu","Novosibirsk PDF",logM,R.RooFit.RooConst(5.095),R.RooFit.RooConst(0.1789),R.RooFit.RooConst(-0.0155))
    EWKbkg_pdf_el = R.RooNovosibirsk("EWKbkg_pdf_el","Novosibirsk PDF",logM,R.RooFit.RooConst(5.081),R.RooFit.RooConst(0.2014),R.RooFit.RooConst(-0.053))
    

    #yields of signal and the background
    nSig_mu = top_sig_mu.Integral() 
    nTop_mu = top_bkg_mu.Integral()
    nEWK_mu = EWK_bkg_mu.Integral()   
    print("\nEvent Yield mu+jets\n=============================================")
    print( "Nsig_norm: ",nSig_mu,"\tNTop_norm: ",nTop_mu,"\tNEwk_norm: ",nEWK_mu,'\n')

    sig_pdf_mu_norm = R.RooRealVar("sig_pdf_mu_norm","sig_pdf_mu_norm",nSig_mu)
    topbkg_pdf_mu_norm = R.RooRealVar("topbkg_pdf_mu_norm","topbkg_pdf_mu_norm",nTop_mu)#,0,10*nTop_mu)
    EWKbkg_pdf_mu_norm = R.RooRealVar("EWKbkg_pdf_mu_norm","EWKbkg_pdf_mu_norm",nEWK_mu)#,0,10*nEWK_mu)

    #yields of signal and the background
    nSig_el = top_sig_el.Integral()
    nTop_el = top_bkg_el.Integral()
    nEWK_el = EWK_bkg_el.Integral()   
    print("Event Yield el+jets\n=============================================")
    print( "Nsig_norm: ",nSig_el, "\tNTop_norm: ",nTop_el,"\tNEwk_norm: ",nEWK_el,"\n")

    sig_pdf_el_norm = R.RooRealVar("sig_pdf_el_norm","sig_pdf_el_norm",nSig_el)
    topbkg_pdf_el_norm = R.RooRealVar("topbkg_pdf_el_norm","topbkg_pdf_el_norm",nTop_el)#,0,10*nTop_el)
    EWKbkg_pdf_el_norm = R.RooRealVar("EWKbkg_pdf_el_norm","EWKbkg_pdf_el_norm",nEWK_el)#,0,10*nEWK_el)

    if(local_fit == None):
        #Create a new empty workspace
        w = R.RooWorkspace("w"+tag,"workspace"+tag+gt_or_lt_tag)
        #Import model and all its components into the workspace
        getattr(w, 'import')(data_mu)
        getattr(w, 'import')(sig_pdf_mu)
        getattr(w, 'import')(topbkg_pdf_mu)
        getattr(w, 'import')(EWKbkg_pdf_mu)

        getattr(w, 'import')(sig_pdf_mu_norm)
        getattr(w, 'import')(topbkg_pdf_mu_norm)
        getattr(w, 'import')(EWKbkg_pdf_mu_norm)
        getattr(w, 'import')(data_el)
        getattr(w, 'import')(sig_pdf_el)
        getattr(w, 'import')(topbkg_pdf_el)
        getattr(w, 'import')(EWKbkg_pdf_el)

        getattr(w, 'import')(sig_pdf_el_norm)
        getattr(w, 'import')(topbkg_pdf_el_norm)
        getattr(w, 'import')(EWKbkg_pdf_el_norm)

        #Print workspace contents
        #w.Print() ;
        # S a v e   w o r k s p a c e   i n   f i l e
        # -------------------------------------------
        # Save the workspace into a ROOT file
        w.writeToFile("/home/mikumar/t3store/workarea/Higgs_Combine/CMSSW_11_3_4/src/Combine_Run2/workspace"+tag+".root")
        # Workspace will remain in memory after macro finishes
        R.gDirectory.Add(w)

        
      
        
        
#########----------------------------------------------------###############------------------###########        
    if(local_fit == "final" ):
        print("locally fitting with full model")
        #define Canvas
        can = R.TCanvas("ln_mtop_mu","ln_mtop_mu",800,600)
        #define Legend
        leg = R.TLegend(0.12,0.45,0.35,0.7);
        leg.SetTextSize(0.03)
        leg.SetBorderSize(0)
        leg.SetLineStyle(0)
        leg.SetFillStyle(0)
        leg.SetFillColor(0)

        #create dummy histogram to show color in legend
        h1 = R.TH1F("h1","h1",2,0,2)
        h1.SetLineColor(R.kBlue)
        h1.SetLineWidth(2)
        h2 = R.TH1F("h2","h2",2,0,2)
        h2.SetLineColor(R.kRed)
        h2.SetLineWidth(2)
        h3 = R.TH1F("h3","h3",2,0,2)
        h3.SetLineColor(R.kOrange-2)
        h3.SetLineWidth(2)
        h4 = R.TH1F("h4","h4",2,0,2)
        h4.SetLineColor(R.kGreen-2)
        h4.SetLineWidth(2)

        leg.AddEntry("data","Combined MC","ple1")
        leg.AddEntry(h1,"Final Model","l")
        leg.AddEntry(h2,"Signal PDF","l")
        leg.AddEntry(h3,"TOP-bkg PDF","l")
        leg.AddEntry(h4,"EWK-bkg PDF","l")
            
        data_mu.Print("v");	

        #Create an empty plot frame 
        Frame = logM.frame(R.RooFit.Title(" "))


        #define the yeilds of the signal and background for muon final state 
        sigY_mu = R.RooRealVar("sigY_mu","Signal Yield mu",nSig_mu)
        topY_mu = R.RooRealVar("topY_mu","Top Bkg Yield mu",nTop_mu)
        ewkY_mu = R.RooRealVar("ewkY_mu","EWK Bkg Yield mu",nEWK_mu)

        #define the yeilds of the signal and background for electron final state
        sigY_el = R.RooRealVar("sigY_el","Signal Yield el",nSig_el)
        topY_el = R.RooRealVar("topY_el","Top Bkg Yield el",nTop_el)
        ewkY_el = R.RooRealVar("ewkY_el","EWK Bkg Yield el",nEWK_el)

        #define factor for variation in the yields for
        sf_tch = R.RooRealVar("sf_tch","Scale factor for signal",1.0,0.1,5.0)
        sf_top = R.RooRealVar("sf_top","Scale factor for Top Bkg",1.0,0.1,5.0)
        sf_ewk = R.RooRealVar("sf_ewk","Scale factor for EWK Bkg",1.0,0.1,5.0)

        #link yield values with the normalization factor fro muon final state
        Nsig_mu = R.RooFormulaVar("Nsig_mu","sf_tch*sigY_mu",R.RooArgList(sf_tch,sigY_mu))
        Ntop_mu = R.RooFormulaVar("Ntop_mu","sf_top*topY_mu",R.RooArgList(sf_top,topY_mu))
        Newk_mu = R.RooFormulaVar("Newk_mu","sf_ewk*ewkY_mu",R.RooArgList(sf_ewk,ewkY_mu))

        #link yield values with the normalization factor fro melectron final state
        Nsig_el = R.RooFormulaVar("Nsig_el","sf_tch*sigY_el",R.RooArgList(sf_tch,sigY_el))
        Ntop_el = R.RooFormulaVar("Ntop_el","sf_top*topY_el",R.RooArgList(sf_top,topY_el))
        Newk_el = R.RooFormulaVar("Newk_el","sf_ewk*ewkY_el",R.RooArgList(sf_ewk,ewkY_el))

        #lognormal constrend 16% 6% and 10%
        tch_constraint = R.RooLognormal("tch_constraint","Constraint on tch sf",sf_tch,R.RooFit.RooConst(1.0),R.RooFit.RooConst(R.TMath.Exp(0.16)))
        top_constraint = R.RooLognormal("top_constraint","Constraint on Top scale factor",sf_top,R.RooFit.RooConst(1.0),R.RooFit.RooConst(R.TMath.Exp(0.06)))
        ewk_constraint = R.RooLognormal("ewk_constraint","Constraint on ewk scale factor",sf_ewk,R.RooFit.RooConst(1.0),R.RooFit.RooConst(R.TMath.Exp(0.1)))


        #define final model
        model_mu = R.RooAddPdf("model_mu","Total Model mu",R.RooArgList(sig_pdf_mu,topbkg_pdf_mu,EWKbkg_pdf_mu),R.RooArgList(Nsig_mu,Ntop_mu,Newk_mu))
        model_mu_Final= R.RooProdPdf("model_mu_Final","Total Model mu with constraints",R.RooArgList(model_mu,tch_constraint, top_constraint, ewk_constraint))
        print(topbkg_pdf_el.getNorm(),"  =====================================")
        model_el = R.RooAddPdf("model_el","Total Model el",R.RooArgList(sig_pdf_el,topbkg_pdf_el,EWKbkg_pdf_el),R.RooArgList(Nsig_el,Ntop_el,Newk_el))
        model_el_Final = R.RooProdPdf("model_el_Final","Total Model el with constraints",R.RooArgList(model_el,tch_constraint, top_constraint, ewk_constraint))

        
        
        
        
 
        
#########----------------------------------------------------###############------------------###########
        
        sample = R.RooCategory("sample", "sample")
        sample.defineType("mu")
        sample.defineType("el")

        simPdf=R.RooSimultaneous("simPdf", "simultaneous pdf", sample)
        simPdf.addPdf(model_mu_Final,"mu")
        simPdf.addPdf(model_el_Final,"el")
        #simPdf.addPdf(model_mu,"mu")
        #simPdf.addPdf(model_el,"el")

        combData = R.RooDataHist("combData", "combined data", R.RooArgList(logM), RooFit.Index(sample), R.RooFit.Import("mu", data_mu),R.RooFit.Import("el", data_el))

        # Create MINUIT interface object
        #m = ROOT.RooMinimizer(nll)

        # Activate verbose logging of MINUIT parameter space stepping
        #m.setVerbose(True)

        # Call MIGRAD to minimize the likelihood
        #m.migrad() 

        fitResult=simPdf.fitTo(combData, "S",R.RooFit.Extended(R.kTRUE), R.RooFit.NumCPU(4), R.RooFit.Save(R.kTRUE), R.RooFit.SumW2Error(R.kTRUE), R.RooFit.Minimizer("Minuit2","migrad"))
        fitResult.Print("v")
        print(fitResult.status())

        #   // P  L  O   T  I  N  G  ------------------------
        #   // ----------------------------------------------
        # Plot model on frame

        can=rt.TCanvas("Canvas","Canvas")
        can.Divide(2,1)
        can.cd(1)
        R.TGaxis.SetMaxDigits(3)
        Frame_mu = logM.frame(R.RooFit.Title(" "))
        data_mu.plotOn(Frame_mu,R.RooFit.Name("Data_mu"),R.RooFit.LineColor(rt.kBlack))
        model_mu_Final.plotOn(Frame_mu, R.RooFit.Name("Data_mu"), R.RooFit.LineColor(rt.kBlue), R.RooFit.LineStyle(1), R.RooFit.LineWidth(3),R.RooFit.Normalization(Ntop_mu.getVal()+Newk_mu.getVal()+ Nsig_mu.getVal(),R.RooAbsReal.NumEvent ))
        sig_pdf_mu.plotOn(Frame_mu,R.RooFit.Normalization( (Nsig_mu.getVal()),R.RooAbsReal.NumEvent  ), R.RooFit.Name("sig_mu"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kRed), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
        topbkg_pdf_mu.plotOn(Frame_mu,R.RooFit.Normalization( (Ntop_mu.getVal()),R.RooAbsReal.NumEvent ), R.RooFit.Name("top_mu"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kOrange-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
        EWKbkg_pdf_mu.plotOn(Frame_mu,R.RooFit.Normalization(Newk_mu.getVal(),R.RooAbsReal.NumEvent ), R.RooFit.Name("ewk_mu"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kGreen-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines()); 
        Frame_mu.Draw()

        #plotOn(Frame,R.RooFit.Normalization( (Nsig_el.getVal()),R.RooAbsReal.NumEvent  ), R.RooFit.Name("sig_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kRed), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())

        can.cd(2)
        R.TGaxis.SetMaxDigits(3)
        Frame_el = logM.frame(R.RooFit.Title(" "))
        data_el.plotOn(Frame_el,R.RooFit.Name("Data_el"),R.RooFit.LineColor(rt.kBlack))
        model_el_Final.plotOn(Frame_el,R.RooFit.Name("Data_el"), R.RooFit.LineColor(rt.kBlue), R.RooFit.LineStyle(1), R.RooFit.LineWidth(3),R.RooFit.Normalization(Ntop_el.getVal()+Newk_el.getVal()+ Nsig_el.getVal(),R.RooAbsReal.NumEvent ))
        sig_pdf_el.plotOn(Frame_el,R.RooFit.Normalization( (Nsig_el.getVal()),R.RooAbsReal.NumEvent  ), R.RooFit.Name("sig_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kRed), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
        topbkg_pdf_el.plotOn(Frame_el,R.RooFit.Normalization( (Ntop_el.getVal()),R.RooAbsReal.NumEvent ), R.RooFit.Name("top_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kOrange-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
        EWKbkg_pdf_el.plotOn(Frame_el,R.RooFit.Normalization(Newk_el.getVal(),R.RooAbsReal.NumEvent ), R.RooFit.Name("ewk_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kGreen-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines()); 
        Frame_el.Draw() 

        leg.Draw()
        if(mass!=None):can.Print("Plots/final_model_comb_"+mass+tag+gt_or_lt_tag+".png")
        if(width!=None):can.Print("Plots/final_model_comb_"+width+tag+gt_or_lt_tag+".png")


    if(local_fit == None):

        cmd_Runtext2workspace = "text2workspace.py datacard_top_shape_comb_para_higgs_tutorial.txt -o workspace_top_Mass_1725_shape_comb_para.root"
        print "\n",cmd_Runtext2workspace
        os.system(cmd_Runtext2workspace)


        #cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_1725_shape_comb_para.root -n _M1725  --redefineSignalPOIs r,sigmaG,mean  --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters r,mean,sigmaG --trackErrors r,mean,sigmaG --plots  --saveShapes --saveWithUncertainties --saveWorkspace"
        cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_1725_shape_comb_para.root -n _M1725  --redefineSignalPOIs sigmaG,mean  --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters mean,sigmaG --trackErrors mean,sigmaG --freezeParameters r --plots  --saveShapes --saveWithUncertainties --saveWorkspace"
        print "\n",cmd_RunCombine
        os.system(cmd_RunCombine)
        
        fitDiagnostics  = R.TFile.Open("fitDiagnostics_M"+mass+".root")
        fit = fitDiagnostics.Get("fit_s")
        fit.Print("v")
            
