import ROOT as R
from ROOT import RooFit 
import sys, datetime
from Hist_style import *
import argparse as arg
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
    Filename_mu = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_gteq0p7_withoutDNNfit.root"
    Filename_el = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_gteq0p7_withoutDNNfit.root"
    Filename_mu_cont = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_gteq0p3_withoutDNNfit.root"
    Filename_el_cont = "/home/mikumar/t3store/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_gteq0p3_withoutDNNfit.root"

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

    #Frame_mu = logM.frame(R.RooFit.Title("mu"))	
    #data_el.plotOn(Frame_mu)
    #Frame_mu.Draw()
    #raw_input()
    #sys.exit()
    # C r e a t e   m o d e l 
    # -----------------------------------------------
    # Declare observable mean and data
    
    mean = R.RooRealVar("mean","mean",5.1,4.5,5.5)
    sigmaG = R.RooRealVar("sigmaG","sigmaG",0.15098,0.01,5)#0.186
    sigmaG2Frac_mu = R.RooRealVar("sigmaG2Frac_mu","sigmaG2Frac_mu",0.1,0.0,5.0) #Best Fit Value
    sigmaG2Frac_el = R.RooRealVar("sigmaG2Frac_el","sigmaG2Frac_el",0.1,0.0,5.0) #Best Fit Value
    sigmaG2_mu = R.RooFormulaVar("sigmaG2_mu","sigmaG2_mu","@0/@1",R.RooArgList(sigmaG, R.RooFit.RooConst(0.858)))# R.RooFit.RooConst(0.860)))#R.RooFit.RooConst(0.860)))
    sigmaG2_el = R.RooFormulaVar("sigmaG2_el","sigmaG2_el","@0/@1",R.RooArgList(sigmaG, R.RooFit.RooConst(0.845))) # R.RooFit.RooConst(0.852)))# R.RooFit.RooConst(0.852)))
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

   


    #topbkg_pdf_mu = R.RooCBShape("topbkg_pdf_mu","Crystal Ball PDF",logM,R.RooFit.RooConst(5.119),mean,sigmaG,alpha,num)#R.RooFit.RooConst(0.171),R.RooFit.RooConst(-1.679),R.RooFit.RooConst(142.0))#mean,sigmaG,alpha,num)#R.RooFit.RooConst(-1.5047),R.RooFit.RooConst(100.0)) # sigma float
    #topbkg_pdf_el = R.RooCBShape("topbkg_pdf_el","Crystal Ball PDF",logM,mean,sigmaG,alpha,num)#R.RooFit.RooConst(5.113),R.RooFit.RooConst(0.172),R.RooFit.RooConst(-1.607),R.RooFit.RooConst(19.0))#mean,sigmaG,alpha,num2)#R.RooFit.RooConst(-1.5164),R.RooFit.RooConst(125)) # sigma float

    sigmaL_topbkg_mu = R.RooFit.RooConst(0.167)
    #sigmaL_topbkg_mu = R.RooRealVar("sigmaL_topbkg_mu","sigmaL_topbkg_mu",0.15098,0.01,1)
    sigmaL_topbkg_el = R.RooFit.RooConst(0.167)
    #sigmaL_topbkg_el = R.RooRealVar("sigmaL_topbkg_el","sigmaL_topbkg_el",0.15098,0.01,1)
    mean_top_bkg_mu = R.RooRealVar("mean_top_bkg_mu","mean_top_bkg_mu",5.1,4.5,5.5)
    
    sigmaFrac_el = R.RooRealVar("sigmaFrac_el","sigmaFrac_el",0.1,0.0,5.0) #Best Fit Value
    sigmaFrac_mu = R.RooRealVar("sigmaFrac_mu","sigmaFrac_mu",0.1,0.0,5.0)
    sigmaR_mu = R.RooFormulaVar("sigmaR_mu","sigmaR_mu","@0/@1",R.RooArgList(sigmaL_topbkg_mu,R.RooFit.RooConst(0.91)))#sigmaFrac))#R.RooFit.RooConst(0.90)))
    sigmaR_el = R.RooFormulaVar("sigmaR_el","sigmaR_el","@0/@1",R.RooArgList(sigmaL_topbkg_el,R.RooFit.RooConst(0.88)))#sigmaFrac))#R.RooFit.RooConst(0.87)))
    topbkg_pdf_mu = R.RooBifurGauss("topbkg_pdf_mu","gauss_mu",logM,R.RooFit.RooConst(5.111),sigmaL_topbkg_mu,sigmaR_mu)#mean_top_bkg,sigmaL_topbkg_mu,sigmaR_mu)
    topbkg_pdf_el = R.RooBifurGauss("topbkg_pdf_el","gauss_el",logM,R.RooFit.RooConst(5.101),sigmaL_topbkg_el,sigmaR_el)#logM,mean_top_bkg,sigmaL_topbkg_el,sigmaR_el)#R.RooFit.RooConst(5.100),sigmaL_topbkg_el,sigmaR_el)
    
    
    #topbkg_pdf_mu = R.RooBifurGauss("topbkg_pdf_mu","gauss_mu",logM,mean,sigmaG2_mu,sigmaG)
    #topbkg_pdf_el = R.RooBifurGauss("topbkg_pdf_el","gauss_el",logM,mean,sigmaG2_el,sigmaG)

    #EWK bakground pdf Novosibirsk
    peak = R.RooRealVar("peak","peak",5.,1.,10.0)
    width_Novo_el = R.RooRealVar("width_Novo_el","width_Novo_el",0.1,0.0,5.0)
    width_Novo_mu = R.RooRealVar("width_Novo_mu","width_Novo_mu",0.1,0.0,5.0)
    tail_mu = R.RooRealVar("tail_mu","tail_mu",-0.25,-5.,1.0) 
    EWKbkg_pdf_mu = R.RooNovosibirsk("EWKbkg_pdf_mu","Novosibirsk PDF",logM,R.RooFit.RooConst(5.08),R.RooFit.RooConst(0.1941),R.RooFit.RooConst(-0.1336))
    EWKbkg_pdf_el = R.RooNovosibirsk("EWKbkg_pdf_el","Novosibirsk PDF",logM,R.RooFit.RooConst(5.068),R.RooFit.RooConst(0.1921),R.RooFit.RooConst(-0.1349))
    

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
    if(local_fit == "sig"):
        print("locally fitting for the signal shapes only (gaussian core + landu tail)")
        xpad = [0.0,0.495,0.505,1.0]
        ypad = [0.,1.]
        #hadd histogram to data hist for ploting
        data_mu_sig = R.RooDataHist("data_mu_sig","data_mu_sig",R.RooArgList(logM),top_sig_mu)
        data_el_sig = R.RooDataHist("data_el_sig","data_el_sig",R.RooArgList(logM),top_sig_el)
        #define Canvas
        can_mu = R.TCanvas("ln_mtop_mu","ln_mtop_mu",1300,600); 
        can_mu.Divide(2,1);
        can_mu.cd(1)
        R.gPad.SetPad(xpad[0],ypad[0],xpad[1],ypad[1])
        R.gPad.SetTicky()
        R.gPad.SetTickx()
        R.TGaxis.SetMaxDigits(3)
        #fit to the signal model	
        res_mu =  sig_pdf_mu.fitTo(data_mu_sig,R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
        res_mu.Print()
        #deine frame for ploting
        Frame_mu = logM.frame(R.RooFit.Title("#mu"))#signal mu"))
        # draw fit on frame 
        data_mu_sig.plotOn(Frame_mu)
        sig_pdf_mu.plotOn(Frame_mu, R.RooFit.Name("Sig_mu"),R.RooFit.DrawOption("L"), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines());
        sig_pdf_mu.paramOn(Frame_mu,R.RooFit.Layout(0.53, 0.87, 0.88))#,R.RooFit.Layout(0.5, 0.8, 0.9),R.RooFit.Format("E",R.RooFit.FixedPrecision(2)),R.RooFit.FixedPrecision(2))
        Frame_mu.getAttText().SetTextSize(0.03)
        Frame_mu.Draw()
        print("frame chiSqure",Frame_mu.chiSquare())
        print("model chiSqure",sig_pdf_mu.createChi2(data_mu_sig).getVal()/15)
        chiqure_mu=PrintPar(0.585,0.66,0.88,0.68,name="#chi^2/NDF = ",val=round(sig_pdf_mu.createChi2(data_mu_sig).getVal()/15,1))
        chiqure_mu.Draw("same")
        CMSTAG.Draw()
        lepton_tag_mu.Draw()
        year_tag.Draw()
        can_mu.Update()

        can_mu.cd(2)
        R.gPad.SetPad(xpad[2],ypad[0],xpad[3],ypad[1])
        #R.gPad.SetGridy(1)
        R.gPad.SetTicky()
        R.gPad.SetTickx()
        #fit to the signal model
        res_el =  sig_pdf_el.fitTo(data_el_sig,R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
        #deine frame for ploting
        Frame_el = logM.frame(R.RooFit.Title("el"))#signal el"))
        # draw fit on framee will let you know as soon as we upload the new version of AN. 
        data_el_sig.plotOn(Frame_el)
        sig_pdf_el.plotOn(Frame_el, R.RooFit.Name("Sig_el"),R.RooFit.DrawOption("L"), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines());
        sig_pdf_el.paramOn(Frame_el,R.RooFit.Layout(0.53, 0.87, 0.88))
        Frame_el.getAttText().SetTextSize(0.03)
        Frame_el.Draw()
        
        print("frame chiSqure",Frame_el.chiSquare())
        print("model chiSqure",sig_pdf_el.createChi2(data_el_sig).getVal()/15)

        chiqure_el=PrintPar(0.585,0.66,0.88,0.68,name="#chi^2/NDF = ",val=round(sig_pdf_el.createChi2(data_el_sig).getVal()/15,1))
        chiqure_el.Draw("same")
        CMSTAG.Draw()
        lepton_tag_el.Draw()
        year_tag.Draw()
        can_mu.Update()
        #raw_input()
        #write canvas in png image
        can_mu.Print("Plots/Signal_only_local_fit"+mass+tag+gt_or_lt_tag+"_fix_par.png")

        
        
        
        
        
        
#########----------------------------------------------------###############------------------###########  
    if(local_fit == "top_bkg"):
        print("locally fitting for the top background shapes only (crystal ball)")
        xpad = [0.0,0.495,0.505,1.0]
        ypad = [0.,1.]
        #hadd histogram to data hist for ploting
        data_mu_top_bkg = R.RooDataHist("data_mu_sig_top_bkg","data_mu_sig_top_bkg",R.RooArgList(logM),top_bkg_mu)
        data_el_top_bkg = R.RooDataHist("data_el_sig_top_bkg","data_el_sig_top_bkg",R.RooArgList(logM),top_bkg_el)
        #define Canvas
        can_mu_topbkg = R.TCanvas("ln_mtop_mu_topbkg","ln_mtop_mu_topbkg",1300,600); 
        can_mu_topbkg.Divide(2,1);
        can_mu_topbkg.cd(1)
        R.gPad.SetPad(xpad[0],ypad[0],xpad[1],ypad[1])
        R.gPad.SetTicky()
        R.gPad.SetTickx()
        R.TGaxis.SetMaxDigits(3)
        #fit to the signal model	
        res_mu_topbkg =  topbkg_pdf_mu.fitTo(data_mu_top_bkg,R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
        #res_mu_topbkg.Print()
        #deine frame for ploting
        Frame_mu_topbkg = logM.frame(R.RooFit.Title("#mu"))
        # draw fit on frame 
        data_mu_top_bkg.plotOn(Frame_mu_topbkg)
        topbkg_pdf_mu.plotOn(Frame_mu_topbkg, R.RooFit.Name("topbkg_mu"),R.RooFit.DrawOption("L"), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines());

        topbkg_pdf_mu.paramOn(Frame_mu_topbkg,R.RooFit.Layout(0.55, 0.88, 0.88))
        #,R.RooFit.Format("E",R.RooFit.FixedPrecision(2)),R.RooFit.FixedPrecision(2))
        Frame_mu_topbkg.getAttText().SetTextSize(0.025)
        Frame_mu_topbkg.Draw()
        print("frame chiSqure",Frame_mu_topbkg.chiSquare())
        print("model chiSqure",topbkg_pdf_mu.createChi2(data_mu_top_bkg).getVal()/15)
        chiqure_mu=PrintPar(0.77,0.61,0.87,0.64,name="#chi^2/NDF = ",val=round(topbkg_pdf_mu.createChi2(data_mu_top_bkg).getVal()/15,1))
        chiqure_mu.Draw("same")
        CMSTAG.Draw()
        lepton_tag_mu.Draw()
        year_tag.Draw()
        can_mu_topbkg.Update()

        can_mu_topbkg.cd(2)
        R.gPad.SetPad(xpad[2],ypad[0],xpad[3],ypad[1])
        #R.gPad.SetGridy(1)
        R.gPad.SetTicky()
        R.gPad.SetTickx()
        #fit to the signal model
        res_el_topbkg =  topbkg_pdf_el.fitTo(data_el_top_bkg,R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
        #res_el_topbkg.Print()
        #deine frame for ploting
        Frame_el_topbkg = logM.frame(R.RooFit.Title("el"))
        # draw fit on frame
        data_el_top_bkg.plotOn(Frame_el_topbkg)
        topbkg_pdf_el.plotOn(Frame_el_topbkg, R.RooFit.Name("topbkg_el"),R.RooFit.DrawOption("L"), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines());

        topbkg_pdf_el.paramOn(Frame_el_topbkg,R.RooFit.Layout(0.55, 0.88, 0.88))
        Frame_el_topbkg.getAttText().SetTextSize(0.03)
        Frame_el_topbkg.Draw()
        print("frame chiSqure",Frame_el_topbkg.chiSquare())
        print("model chiSqure",topbkg_pdf_el.createChi2(data_el_top_bkg).getVal()/15)
        chiqure_el=PrintPar(0.77,0.61,0.87,0.64,name="#chi^2/NDF = ",val=round(topbkg_pdf_el.createChi2(data_el_top_bkg).getVal()/15,1))
        chiqure_el.Draw("same")
        CMSTAG.Draw()
        lepton_tag_el.Draw()
        year_tag.Draw()
        can_mu_topbkg.Update()
        #raw_input()
        #write canvas in png image
        
        if(mass!=None):
            can_mu_topbkg.Print("Plots/Topbkg_only_local_fit"+mass+tag+gt_or_lt_tag+"_fix_par.png")
        if(width!=None):
            can_mu_topbkg.Print("Plots/Topbkg_only_local_fit"+width+tag+gt_or_lt_tag+"_fix_par.png")

        
        
        
        
        
        
#########----------------------------------------------------###############------------------###########  
    if(local_fit == "ewk_bkg"):
        print("locally fitting for the EWK background shapes only (novosibrsk)")
        xpad = [0.0,0.495,0.505,1.0]
        ypad = [0.,1.]
        #hadd histogram to data hist for ploting
        data_mu_ewk_bkg = R.RooDataHist("data_mu_sig_ewk_bkg","data_mu_sig_ewk_bkg",R.RooArgList(logM),EWK_bkg_mu)
        data_el_ewk_bkg = R.RooDataHist("data_el_sig_ewk_bkg","data_el_sig_ewk_bkg",R.RooArgList(logM),EWK_bkg_el)
        #define Canvas
        can_mu_ewkbkg = R.TCanvas("ln_mtop_mu_ewkbkg","ln_mtop_mu_ewkbkg",1300,600); 
        can_mu_ewkbkg.Divide(2,1)
        can_mu_ewkbkg.cd(1)
        R.gPad.SetPad(xpad[0],ypad[0],xpad[1],ypad[1])
        R.gPad.SetTicky()
        R.gPad.SetTickx()
        R.TGaxis.SetMaxDigits(3)
        #fit to the signal model	
        res_mu_ewkbkg =  EWKbkg_pdf_mu.fitTo(data_mu_ewk_bkg,R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
        #res_mu_ewkbkg.Print()
        #deine frame for ploting
        Frame_mu_ewkbkg = logM.frame(R.RooFit.Title("#mu"))
        # draw fit on frame 
        data_mu_ewk_bkg.plotOn(Frame_mu_ewkbkg)
        EWKbkg_pdf_mu.plotOn(Frame_mu_ewkbkg, R.RooFit.Name("ewkbkg_mu"),R.RooFit.DrawOption("L"), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines());
        EWKbkg_pdf_mu.paramOn(Frame_mu_ewkbkg,R.RooFit.Layout(0.55, 0.88, 0.88))
        Frame_mu_ewkbkg.getAttText().SetTextSize(0.025)
        Frame_mu_ewkbkg.Draw()
        print("frame chiSqure",Frame_mu_ewkbkg.chiSquare())
        print("model chiSqure",EWKbkg_pdf_mu.createChi2(data_mu_ewk_bkg).getVal()/15)
        chiqure_mu=PrintPar(0.735,0.65,0.85,0.68,name="#chi^2/NDF = ",val=round(EWKbkg_pdf_mu.createChi2(data_mu_ewk_bkg).getVal()/15,1))
        chiqure_mu.Draw("same")
        CMSTAG.Draw()
        lepton_tag_mu.Draw()
        year_tag.Draw()
        can_mu_ewkbkg.Update()

        can_mu_ewkbkg.cd(2)
        R.gPad.SetPad(xpad[2],ypad[0],xpad[3],ypad[1])
        #R.gPad.SetGridy(1)
        R.gPad.SetTicky()
        R.gPad.SetTickx()
        #fit to the signal model
        res_el_ewkbkg =  EWKbkg_pdf_el.fitTo(data_el_ewk_bkg,R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
        #res_el_ewkbkg.Print()
        #deine frame for ploting
        Frame_el_ewkbkg = logM.frame(R.RooFit.Title("el"))
        # draw fit on frame
        data_el_ewk_bkg.plotOn(Frame_el_ewkbkg)
        EWKbkg_pdf_el.plotOn(Frame_el_ewkbkg, R.RooFit.Name("ewkbkg_el"),R.RooFit.DrawOption("L"), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines());
        EWKbkg_pdf_el.paramOn(Frame_el_ewkbkg,R.RooFit.Layout(0.55, 0.88, 0.88))
        Frame_el_ewkbkg.getAttText().SetTextSize(0.025)
        Frame_el_ewkbkg.Draw()
        print("frame chiSqure",Frame_el_ewkbkg.chiSquare())
        print("model chiSqure",EWKbkg_pdf_el.createChi2(data_el_ewk_bkg).getVal()/15)
        chiqure_el=PrintPar(0.735,0.65,0.85,0.68,name="#chi^2/NDF = ",val=round(EWKbkg_pdf_el.createChi2(data_el_ewk_bkg).getVal()/15,1))
        chiqure_el.Draw("same")
        CMSTAG.Draw()
        lepton_tag_el.Draw()
        year_tag.Draw()
        can_mu_ewkbkg.Update()
        #raw_input()
        #write canvas in png image
        if(mass!=None):
            can_mu_ewkbkg.Print("Plots/EWKbkg_only_local_fit_"+mass+tag+gt_or_lt_tag+"_fix_par.png")
        if(width!=None):
            can_mu_ewkbkg.Print("Plots/EWKbkg_only_local_fit_"+width+tag+gt_or_lt_tag+"_fix_par.png")
        
        
        
        
        
        
#########----------------------------------------------------###############------------------###########        
    if(local_fit == "final" or local_fit == "final_mu" or local_fit == "final_el"):
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
        if(local_fit == "final_mu"):
            #fit to the data
            res = model_mu_Final.fitTo(data_mu,R.RooFit.Constrain(R.RooArgSet(sf_tch,sf_top,sf_ewk)),R.RooFit.Extended(R.kTRUE),R.RooFit.NumCPU(4,0),R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
            res.Print()


            #   // P  L  O   T  I  N  G  ------------------------
            #   // ----------------------------------------------
            # Plot model on frame 
            #
            data_mu.plotOn(Frame)
            model_mu_Final.plotOn(Frame, R.RooFit.Name("Model_mu"),R.RooFit.Normalization(Nsig_mu.getVal()+Ntop_mu.getVal()+Newk_mu.getVal(),R.RooAbsReal.NumEvent),R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kBlue), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
            
            #print("PDF Integral : ",model_mu_Final.createIntegral(logM).getVal())#, R.RooFit.Range(R.TMath.Log(100.0),R.TMath.Log(441.63580547))))
            print("Total effective Norm of the model = ",(Ntop_mu.getVal()+Newk_mu.getVal()+ Nsig_mu.getVal()))
            sig_pdf_mu.plotOn(Frame,R.RooFit.Normalization( (Nsig_mu.getVal()),R.RooAbsReal.NumEvent ), R.RooFit.Name("sig_mu"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kRed), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
            topbkg_pdf_mu.plotOn(Frame,R.RooFit.Normalization( (Ntop_mu.getVal()),R.RooAbsReal.NumEvent), R.RooFit.Name("top_mu"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kOrange-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
            EWKbkg_pdf_mu.plotOn(Frame,R.RooFit.Normalization(Newk_mu.getVal(),R.RooAbsReal.NumEvent), R.RooFit.Name("ewk_mu"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kGreen-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines()) 

            
            pad1 = R.TPad('pad1', 'pad1', 0.0, 0.195259, 1.0, 0.990683)
            pad1.SetBottomMargin(0.089)
            pad1.SetTicky()
            pad1.SetTickx()
            
            pad1.Draw()
            pad1.cd()

            #Draw data on frame
            hist_dummy = data_mu.createHistogram("dummy",logM, R.RooFit.Binning(15)) 
            print("Integral just before ploting : ",hist_dummy.Integral())	
            Frame.Draw()
            #Draw Legend

            leg.Draw("SAME")
            CMSTAG.Draw()
            lepton_tag_mu.Draw()
            year_tag.Draw()
            pad1.Update()
            can.Update()

            fitDataLep_hist= data_mu.createHistogram("fitData_Lep",logM, R.RooFit.Binning(15)) 
            fitDataLep_hist.Sumw2() 
            fitDataLep_hist.SetNameTitle("Data_Lep_Hist","")
            fitModelLep_hist= model_mu_Final.createHistogram("fitModel_Lep",logM, R.RooFit.Binning(15)) 
            fitModelLep_hist.Sumw2()
            fitModelLep_hist.SetNameTitle("Model_Lep_Hist","")
            fitModelLep_hist.Scale((Ntop_mu.getVal()+Newk_mu.getVal()+ Nsig_mu.getVal())/fitModelLep_hist.Integral());
            gr_lep= R.TGraphAsymmErrors(fitDataLep_hist,fitModelLep_hist,"pois");	

            can.cd()

            pad2 = R.TPad("pad2", "pad2", 0.0, 0.0, 1.0, 0.2621035)
            pad2.SetTopMargin(0.0)
            pad2.SetBottomMargin(0.3)
            pad2.SetGridy()
            pad2.SetTicky()
            pad2.SetTickx()
            pad2.Draw()
            pad2.cd()
            dummyData_Lep=fitDataLep_hist.Clone()
            dummyData_Lep.Divide(fitModelLep_hist)
            dummyData_Lep.GetYaxis().SetTitle("#frac{MC}{Fit}") 
            dummyData_Lep.GetYaxis().CenterTitle(1)
            nbin=dummyData_Lep.GetXaxis().GetNbins()
            lEdge_Lep=dummyData_Lep.GetXaxis().GetXmin()
            uEdge_Lep=dummyData_Lep.GetXaxis().GetXmax()
            bandTitle_Lep="Band_Lep";
            band = R.TH1F(bandTitle_Lep,"",nbin,lEdge_Lep,uEdge_Lep);
            R.gStyle.SetOptStat(0)

            #propagate_rate_uncertainity(top_sig_mu, 15.0)
            #propagate_rate_uncertainity(top_bkg_mu, 6.0)
            #propagate_rate_uncertainity(EWK_bkg_mu, 10.0)
            #propagate_rate_uncertainity(QCD_DD, 50.0)	
            fitModelLep_hist.Reset()
            fitModelLep_hist = top_sig_mu.Clone()
            fitModelLep_hist.Add(top_bkg_mu)
            fitModelLep_hist.Add(EWK_bkg_mu)
            fitModelLep_hist.Add(QCD_DD)

            for i in range(nbin+1):
                    #`print fitDataLep_hist.GetBinContent(i+1) ," : ",Data_prefit.GetBinContent(i+1)
                    band.SetBinContent(i+1, 1.0)
                    if (fitModelLep_hist.GetBinContent(i+1)!=0 and fitDataLep_hist.GetBinContent(i+1)!=0):
                            err = (fitModelLep_hist.GetBinError(i+1) * dummyData_Lep.GetBinContent(i+1)) / fitModelLep_hist.GetBinContent(i+1)
                    elif (fitModelLep_hist.GetBinContent(i+1)!=0 and fitDataLep_hist.GetBinContent(i+1)==0):
                            err = 1
                    else:
                            err = 0
                    band.SetBinError(i+1, err)

            band.SetFillColor(R.kGray+3)
            band.SetFillStyle(3001)
            band.GetYaxis().SetTitle("Fit/MC")
            #band.GetXaxis().SetTitle(Data.GetXaxis().GetTitle())
            band.GetXaxis().SetTitle("ln(m_{t})")
            band.GetYaxis().CenterTitle(1)
            band.GetYaxis().SetTitleOffset(0.35)
            band.GetYaxis().SetTitleSize(0.12)
            band.GetXaxis().SetTitleSize(0.12)
            band.GetYaxis().SetLabelSize(0.07)
            band.GetXaxis().SetLabelSize(0.1)
            band.SetMaximum(1.545665)
            band.SetMinimum(0.464544)
            c = band.GetYaxis()
            c.SetNdivisions(10)
            c.SetTickSize(0.01)
            d = band.GetXaxis()
            d.SetNdivisions(10)
            d.SetTickSize(0.03)

            gr_lep.SetMarkerColor(1)
            gr_lep.SetMarkerStyle(20)
            gr_lep.SetMarkerSize(0.89)
            gr_lep.SetLineColor(R.kBlack)

            band.Draw('E2')
            gr_lep.Draw('PE1;SAME')

            pad2.Update()
            can.Update()
            #raw_input()
            if(mass!=None):can.Print("Plots/final_model_mu_"+mass+tag+gt_or_lt_tag+".png")
            if(width!=None):can.Print("Plots/final_model_mu_"+width+tag+gt_or_lt_tag+".png")
            #raw_input()
            #Toy_Mc(model_mu_Final,logM,mean)		


        
        
        
        
        
        
#########----------------------------------------------------###############------------------###########
        if(local_fit == "final_el"):
            #fit to the data
            res = model_el_Final.fitTo(data_el,R.RooFit.Constrain(R.RooArgSet(sf_tch,sf_top,sf_ewk)),R.RooFit.Extended(R.kTRUE),R.RooFit.NumCPU(4,0),R.RooFit.Save(),R.RooFit.SumW2Error(R.kTRUE))
            res.Print()


            #   // P  L  O   T  I  N  G  ------------------------
            #   // ----------------------------------------------
            # Plot model on frame 
            data_el.plotOn(Frame)
            model_el_Final.plotOn(Frame,R.RooFit.Normalization(Ntop_el.getVal()+Newk_el.getVal()+ Nsig_el.getVal(),R.RooAbsReal.NumEvent ), R.RooFit.Name("Model_el"),R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kBlue), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
            sig_pdf_el.plotOn(Frame,R.RooFit.Normalization( (Nsig_el.getVal()),R.RooAbsReal.NumEvent  ), R.RooFit.Name("sig_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kRed), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
            topbkg_pdf_el.plotOn(Frame,R.RooFit.Normalization( (Ntop_el.getVal()),R.RooAbsReal.NumEvent ), R.RooFit.Name("top_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kOrange-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines())
            EWKbkg_pdf_el.plotOn(Frame,R.RooFit.Normalization(Newk_el.getVal(),R.RooAbsReal.NumEvent ), R.RooFit.Name("ewk_el"), R.RooFit.DrawOption("L"), R.RooFit.LineColor(R.kGreen-2), R.RooFit.LineStyle(1), R.RooFit.LineWidth(2),R.RooFit.VLines()); 

            
            can.Update()
            
            pad1 = R.TPad('pad1', 'pad1', 0.0, 0.195259, 1.0, 0.990683)
            pad1.SetBottomMargin(0.089)
            pad1.SetTicky()
            pad1.SetTickx()
            #pad1.GetGridy().SetMaximum(Data.GetMaximum() * 1.2)
            #pad1.SetRightMargin(0.143)
            pad1.Draw()
            pad1.cd()

            
            Frame.Draw()
            #Draw Legend
            leg.Draw("SAME")
            CMSTAG.Draw()
            lepton_tag_el.Draw()
            year_tag.Draw()
            pad1.Update()
            can.Update()

            fitDataLep_hist= data_el.createHistogram("fitData_Lep",logM, R.RooFit.Binning(15)) 
            fitDataLep_hist.Sumw2() 
            fitDataLep_hist.SetNameTitle("Data_Lep_Hist","")
            fitModelLep_hist= model_el_Final.createHistogram("fitModel_Lep",logM, R.RooFit.Binning(15)) 
            fitModelLep_hist.Sumw2()
            fitModelLep_hist.SetNameTitle("Model_Lep_Hist","")
            fitModelLep_hist.Scale((Ntop_el.getVal()+Newk_el.getVal()+ Nsig_el.getVal())/fitModelLep_hist.Integral());
            gr_lep= R.TGraphAsymmErrors(fitDataLep_hist,fitModelLep_hist,"pois");	

            can.cd()

            pad2 = R.TPad("pad2", "pad2", 0.0, 0.0, 1.0, 0.2621035)
            pad2.SetTopMargin(0.0)
            pad2.SetBottomMargin(0.3)
            pad2.SetGridy()
            pad2.SetTicky()
            pad2.SetTickx()
            pad2.Draw()
            pad2.cd()

            dummyData_Lep=fitDataLep_hist.Clone()
            dummyData_Lep.Divide(fitModelLep_hist)
            dummyData_Lep.GetYaxis().SetTitle("#frac{MC}{Fit}") 
            dummyData_Lep.GetYaxis().CenterTitle(1)
            nbin=dummyData_Lep.GetXaxis().GetNbins()
            lEdge_Lep=dummyData_Lep.GetXaxis().GetXmin()
            uEdge_Lep=dummyData_Lep.GetXaxis().GetXmax()
            bandTitle_Lep="Band_Lep";
            band = R.TH1F(bandTitle_Lep,"",nbin,lEdge_Lep,uEdge_Lep);
            R.gStyle.SetOptStat(0)


            #propagate_rate_uncertainity(top_sig_el, 15.0)
            #propagate_rate_uncertainity(top_bkg_el, 6.0)
            #propagate_rate_uncertainity(EWK_bkg_el, 10.0)
            #propagate_rate_uncertainity(QCD_DD, 50.0)     
            fitModelLep_hist.Reset()
            fitModelLep_hist = top_sig_el.Clone()
            fitModelLep_hist.Add(top_bkg_el)
            fitModelLep_hist.Add(EWK_bkg_el)
            fitModelLep_hist.Add(QCD_DD)
            for i in range(nbin+1):
                #`print fitDataLep_hist.GetBinContent(i+1) ," : ",Data_prefit.GetBinContent(i+1)
                band.SetBinContent(i+1, 1.0)
                if (fitModelLep_hist.GetBinContent(i+1)!=0 and fitDataLep_hist.GetBinContent(i+1)!=0):
                        err = (fitModelLep_hist.GetBinError(i+1) * dummyData_Lep.GetBinContent(i+1)) / fitModelLep_hist.GetBinContent(i+1)
                elif (fitModelLep_hist.GetBinContent(i+1)!=0 and fitDataLep_hist.GetBinContent(i+1)==0):
                        err = 1
                else:
                        err = 0
                band.SetBinError(i+1, err)

            band.SetFillColor(R.kGray+3)
            band.SetFillStyle(3001)
            band.GetYaxis().SetTitle("Fit/MC")
            #band.GetXaxis().SetTitle(Data.GetXaxis().GetTitle())
            band.GetXaxis().SetTitle("ln(m_{t})")
            band.GetYaxis().CenterTitle(1)
            band.GetYaxis().SetTitleOffset(0.35)
            band.GetYaxis().SetTitleSize(0.12)
            band.GetXaxis().SetTitleSize(0.12)
            band.GetYaxis().SetLabelSize(0.07)
            band.GetXaxis().SetLabelSize(0.1)
            band.SetMaximum(1.545665)
            band.SetMinimum(0.464544)
            c = band.GetYaxis()
            c.SetNdivisions(10)
            c.SetTickSize(0.01)
            d = band.GetXaxis()
            d.SetNdivisions(10)
            d.SetTickSize(0.03)

            band.Draw('E2')

            gr_lep.SetMarkerColor(1)
            gr_lep.SetMarkerStyle(20)
            gr_lep.SetMarkerSize(0.89)
            gr_lep.SetLineColor(R.kBlack)	
            gr_lep.Draw('PE1;SAME')			

            pad2.Update()	
            can.Update()

            #raw_input()

            if(mass!=None):can.Print("Plots/final_model_el_"+mass+tag+gt_or_lt_tag+".png")
            if(width!=None):can.Print("Plots/final_model_el_"+width+tag+gt_or_lt_tag+".png")


        
        
        
        
        
        
#########----------------------------------------------------###############------------------###########
        if(local_fit == "final"):
            sample = R.RooCategory("sample", "sample")
            sample.defineType("mu")
            sample.defineType("el")
            
            simPdf=R.RooSimultaneous("simPdf", "simultaneous pdf", sample)
            #simPdf.addPdf(model_mu_Final,"mu")
            #simPdf.addPdf(model_el_Final,"el")
            simPdf.addPdf(model_mu,"mu")
            simPdf.addPdf(model_el,"el")
            
            combData = R.RooDataHist("combData", "combined data", R.RooArgList(logM), RooFit.Index(sample), R.RooFit.Import("mu", data_mu),R.RooFit.Import("el", data_el))

            fitResult=simPdf.fitTo(combData, R.RooFit.Extended(R.kTRUE), R.RooFit.NumCPU(4), R.RooFit.Save(R.kTRUE), R.RooFit.SumW2Error(R.kTRUE))
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
  
            