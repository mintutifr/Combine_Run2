import sys
import math
import ROOT as R
import numpy as np
import argparse as arg
from Hist_style import *
parser = arg.ArgumentParser(description='Create workspace for higgs combine')
parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="MC top mass sample ['data','1695', '1715', '1725', '1735', '1755']")
parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018']")
args = parser.parse_args()


mass  = args.mass_sample[0]
dataYear = args.Year[0]

def propagate_rate_uncertainity(hist, uncert):
    for i in range(hist.GetXaxis().GetNbins()):
        if hist.GetBinContent(i) != 0:
            hist.SetBinError(i, hist.GetBinContent(i) * uncert * 0.01)

def getcons(mass):
        fitfile = R.TFile.Open("fitDiagnostics_M"+mass+"_DNNfit_mu_UL2017.root")
        roofitResults = fitfile.Get("fit_s")

        cons_top_sig = (roofitResults.floatParsFinal()).find("cons_EWK_bkg")
        print "cons_top_sig : ",cons_top_sig.getVal()," Error : ",cons_top_sig.getError()

        cons_top_bkg = (roofitResults.floatParsFinal()).find("cons_top_bkg")
        print "cons_top_bkg : ",cons_top_bkg.getVal()," Error : ",cons_top_bkg.getError()

	cons_EWK_bkg = (roofitResults.floatParsFinal()).find("cons_EWK_bkg")
        print "cons_EWK_bkg : ",cons_EWK_bkg.getVal()," Error : ",cons_EWK_bkg.getError()
	
	return cons_top_sig.getVal(),cons_top_bkg.getVal(),cons_top_bkg.getVal()

def getprefit_hist(mass,lep):
	hists = []
        Filename = R.TFile("/home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_DNNFit_Input_t_ch_CAsi_histograms_"+dataYear+"_"+lep+".root","Read")
        
        #Data Vs Mc Condition
	R.gROOT.cd()
        #Get the file and director where historgrams are stored for muon final state
        Dir = Filename.GetDirectory(lep+"jets")
        #Get Mc histograms for muon final state
	if(mass!=None):
                top_sig = Dir.Get("top_sig_"+mass)
                top_bkg = Dir.Get("top_bkg_"+mass)
                EWK_bkg = Dir.Get("EWK_bkg")
                QCD = Dir.Get("QCD_DD")

                hists.append(top_sig.Clone())
                hists.append(top_bkg.Clone())
                hists.append(EWK_bkg.Clone())
                hists.append(QCD.Clone())
        else:
                data = Dir.Get("data_obs")
                hists.append(data.Clone())
        return hists
def Rebase_Xaxies_scale(hist,hist_unct_propagated):
    nbin=hist.GetXaxis().GetNbins()
    BINS = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,1.0]
    print("redefine assymatic histogram bins ", BINS)
    new_hist = R.TH1F(hist.GetName(),hist.GetName(),len(BINS)-1,np.array(BINS))

    for bin in range(1,nbin+1):
        new_hist.SetBinContent(bin,hist.GetBinContent(bin))
        new_hist.SetBinError(bin,hist_unct_propagated.GetBinError(bin))
    return new_hist
def getthefit(mass,lep):
        	
	prefit_hists = getprefit_hist(mass,lep) #return top_sig,topbkg,EWK_bkg
        R.gROOT.cd()
	Data_prefit = prefit_hists[0].Clone()  
        if(mass!=None):
	        Data_prefit.Add(prefit_hists[1])
	        Data_prefit.Add(prefit_hists[2])
                Data_prefit.Add(prefit_hists[3])
        Data_prefit.SetName("Data_prefit")
        Data_prefit.SetLineColor(R.kBlack)
        Data_prefit.SetMarkerStyle(20)

        print("Data_prefit info from from Combine input files ")
        Data_prefit.Print()


	fitfile = R.TFile.Open("fitDiagnostics_M1725_DNNfit_"+lep+"_"+dataYear+".root") 
	fit = fitfile.Get(lep+"jets_CMS_th1x_fit_s")
	#fit.Print()

	Data_postfit_roohist = fit.findObject("h_"+lep+"jets")

	SigFitHist = fitfile.Get("shapes_fit_s/"+lep+"jets/top_sig_1725"); #SigFitHist = Rebase_Xaxies_scale(SigFitHist)
	TopBkgFitHist = fitfile.Get("shapes_fit_s/"+lep+"jets/top_bkg_1725"); #TopBkgFitHist = Rebase_Xaxies_scale(TopBkgFitHist)
        EWKBkgFitHist = fitfile.Get("shapes_fit_s/"+lep+"jets/EWK_bkg"); #EWKBkgFitHist = Rebase_Xaxies_scale(EWKBkgFitHist)
        QCDBkgFitHist = fitfile.Get("shapes_fit_s/"+lep+"jets/QCD_DD"); #QCDBkgFitHist = Rebase_Xaxies_scale(QCDBkgFitHist)

        propagate_rate_uncertainity(SigFitHist,15.0); SigFitHist = Rebase_Xaxies_scale(SigFitHist,SigFitHist)
        propagate_rate_uncertainity(TopBkgFitHist,6.0); TopBkgFitHist = Rebase_Xaxies_scale(TopBkgFitHist,TopBkgFitHist)
        propagate_rate_uncertainity(EWKBkgFitHist,10.0); EWKBkgFitHist = Rebase_Xaxies_scale(EWKBkgFitHist,EWKBkgFitHist)
        propagate_rate_uncertainity(QCDBkgFitHist,50.0); QCDBkgFitHist = Rebase_Xaxies_scale(QCDBkgFitHist,QCDBkgFitHist)     
 
        ResultFitHist_unct_prop = SigFitHist.Clone(); SigFitHist.Print();print(SigFitHist.Integral(1,7));print(SigFitHist.Integral(8,10))
        ResultFitHist_unct_prop.Add(TopBkgFitHist);   TopBkgFitHist.Print();print(TopBkgFitHist.Integral(1,7));print(TopBkgFitHist.Integral(8,10))
        ResultFitHist_unct_prop.Add(EWKBkgFitHist);   EWKBkgFitHist.Print();print(EWKBkgFitHist.Integral(1,7));print(EWKBkgFitHist.Integral(8,10))
        ResultFitHist_unct_prop.Add(QCDBkgFitHist);   QCDBkgFitHist.Print();print(QCDBkgFitHist.Integral(1,7));print(QCDBkgFitHist.Integral(8,10))

        QCDBkgFitHist.SetFillColor(R.kGray)
        QCDBkgFitHist.SetLineColor(R.kGray)
        EWKBkgFitHist.SetFillColor(R.kGreen+2)
        EWKBkgFitHist.SetLineColor(R.kGreen+2)
        TopBkgFitHist.SetFillColor(R.kOrange-1)
        TopBkgFitHist.SetLineColor(R.kOrange-1)
        SigFitHist.SetFillColor(R.kRed)
        SigFitHist.SetLineColor(R.kRed)

        hs = R.THStack("hs","");
        hs.Add(QCDBkgFitHist)
        hs.Add(EWKBkgFitHist)
        hs.Add(TopBkgFitHist)
        hs.Add(SigFitHist)
        
	ResultFitHist = fitfile.Get("shapes_fit_s/"+lep+"jets/total"); 
        ResultFitHist=Rebase_Xaxies_scale(ResultFitHist,ResultFitHist_unct_prop)
        del ResultFitHist_unct_prop
        ResultFitHist.SetLineColor(R.kBlue)
        ResultFitHist.SetLineWidth(2)

	legend = R.TLegend(0.60193646, 0.5048435, 0.8093552, 0.79026143)
	legend.SetBorderSize(1)
	legend.SetTextSize(0.045)
	legend.SetLineColor(0)
	legend.SetLineStyle(1)
	legend.SetLineWidth(1)
	legend.SetFillColor(0)
	legend.SetFillStyle(1001)
	#legend.SetHeader("beNDC", "C")
	legend.AddEntry(Data_prefit, "Data", "ple1")
	legend.AddEntry(ResultFitHist, "Fit.", "l")
	legend.AddEntry(SigFitHist, "corr. top", "f")
	legend.AddEntry(TopBkgFitHist, "top bkg", "f")
        legend.AddEntry(EWKBkgFitHist, "EWK bkg", "f")
        legend.AddEntry(QCDBkgFitHist, "QCD bkg", "f")

	
	can = R.TCanvas("can","can",600,600)
        R.gStyle.SetOptStat(0)
	can.cd()
        R.gStyle.SetErrorX(0)
	R.TGaxis.SetMaxDigits(3)

	pad1 = R.TPad('pad1', 'pad1', 0.0, 0.195259, 1.0, 0.990683)
	pad1.SetBottomMargin(0.089)
	pad1.SetTicky()
	pad1.SetTickx()
        pad1.SetLogy()
	#pad1.GetGridy().SetMaximum(Data.GetMaximum() * 1.2)
	#pad1.SetRightMargin(0.143)
	pad1.Draw()
	pad1.cd()
	pad1.cd()
	frame = R.gPad.DrawFrame(Data_postfit_roohist.GetXaxis().GetXmin(), 0.0,Data_postfit_roohist.GetXaxis().GetXmax(),Data_postfit_roohist.GetYaxis().GetXmax()*1.15,';Events')

	#frame.GetXaxis().SetTitle('#varepsilon_{Sig} (%)')
	frame.GetYaxis().SetTitle('Events / (0.1)')
	frame.GetYaxis().SetTitleSize(0.04)
        
        hs.Draw("hist")
        Data_prefit.Draw("P;same")
	ResultFitHist.Draw("same;hist")
	legend.Draw("same")
	"""cmstext = Get_CMSPreliminary(0.46, 0.86, 0.51, 0.88)
        cmstext.Draw()
        finalstate = Get_FinalStateTag(0.34,0.81,0.47,0.83,lep)
        finalstate.Draw()
	can.Update()"""

        CMSpreliminary = getCMSpre_tag(0.46, 0.86, 0.51, 0.88)
        CMSpreliminary.Draw("same")
        lepjet_tag = leptonjet_tag(lep,0.34,0.81,0.47,0.83)
        lepjet_tag.Draw("same")
        yearNlumitag = year_tag(dataYear,0.82, 0.92, 0.9, 0.96)
        yearNlumitag.Draw("same")


	can.Update()

 	can.cd()
	pad2 = R.TPad("pad2", "pad2", 0.0, 0.0, 1.0, 0.2621035)
	pad2.SetTopMargin(0.0)
	pad2.SetBottomMargin(0.3)
	pad2.SetGridy()
	pad2.SetTicky()
	pad2.SetTickx()
	pad2.Draw()
	pad2.cd()

	R.gROOT.cd()
        Data_postfit = ResultFitHist.Clone()
 

	#h_ratio = R.TGraphAsymmErrors(Data_postfit, Data_postfit, 'pois')
        #print h_ratio.GetN()

        nbin = Data_prefit.GetXaxis().GetNbins()
        ledge = Data_prefit.GetXaxis().GetXmin()
        uedge = Data_prefit.GetXaxis().GetXmax()
        BINS = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,1.0]
        print("redefine assymatic histogram bins ", BINS)
        h_ratio = R.TH1F('h_ratio', '', len(BINS)-1,np.array(BINS))
	for iBin in range(1,nbin+1):
                error_prefit = Data_prefit.GetBinError(iBin)
                error_postfit = Data_postfit.GetBinError(iBin)
                cont_prefit = Data_prefit.GetBinContent(iBin)
                cont_postfit = Data_postfit.GetBinContent(iBin)
                #h_ratio.SetBinContent(i,(Data_prefit.GetBinContent(i)-Data_postfit.GetBinContent(i))/math.sqrt(error_prefit*error_prefit+error_postfit*error_postfit))
                sigma_pull = R.TMath.Sqrt( R.TMath.Abs(error_prefit*error_prefit - error_postfit*error_postfit ))
                pull= ( cont_postfit-cont_prefit) / sigma_pull
                pull_err = ( error_prefit - error_postfit )/ sigma_pull
                print(error_prefit, error_postfit, sigma_pull)
                h_ratio.SetBinContent(iBin, pull)
                h_ratio.SetBinError(iBin, pull_err)
                #print(pull,pull_err)
        #Add QCD_DD for the syst band	

        h_ratio.SetFillColor(R.kBlue+3)
        h_ratio.SetFillStyle(3001)
         
        h_ratio.GetYaxis().SetTitle("#frac{Fit-MC}{#Delta}") 
        #band.GetXaxis().SetTitle(Data.GetXaxis().GetTitle())
        h_ratio.GetXaxis().SetTitle("DNN Score (Corr. Assign Signal)")
        h_ratio.GetYaxis().CenterTitle(1) 
        h_ratio.GetYaxis().SetTitleOffset(0.35)              
        h_ratio.GetYaxis().SetTitleSize(0.12)
        h_ratio.GetXaxis().SetTitleSize(0.12)
        h_ratio.GetYaxis().SetLabelSize(0.07)
        h_ratio.GetXaxis().SetLabelSize(0.1)
        h_ratio.GetYaxis().SetRangeUser(-5.0,5.0)
        h_ratio.SetLineColor(R.kBlack)
        h_ratio.SetMarkerStyle(20)


        c = h_ratio.GetYaxis();
        c.SetNdivisions(6);
        c.SetTickSize(0.01);

	h_ratio.Draw("hist")
	can.Update()

        """Ratio_hist= R.TGraphAsymmErrors(Data_postfit, Data_postfit,"pois")
        axis = Ratio_hist.GetXaxis()
        axis.SetLimits(Data_postfit.GetXaxis().GetXmin(),Data_postfit.GetXaxis().GetXmax())
        Ratio_hist.SetMarkerColor(1)
        Ratio_hist.SetMarkerStyle(20)
        Ratio_hist.SetMarkerSize(0.89)
        Ratio_hist.SetLineColor(kBlack)

        #Draw Uncertanity band
        TH1F* dummyData;
        dummyData=(TH1F*)h[15]->Clone();
        dummyData->Divide(hMC);
        nBin=dummyData->GetXaxis()->GetNbins();
        lEdge=dummyData->GetXaxis()->GetXmin();
        uEdge=dummyData->GetXaxis()->GetXmax();
        TString bandTitle="Band_"+Variable;

        band=new TH1F(bandTitle,"",nBin,lEdge,uEdge);gStyle->SetOptStat(0);
        for(int nn=0; nn<=nBin; nn++){
                band->SetBinContent(nn+1,1.0);  // nn+1 because 0-th bin is the underflow bin.

                if( hMC->GetBinContent(nn+1)!=0 && h[15]->GetBinContent(nn+1)!=0 ){
                    err=(hMC->GetBinError(nn+1))*(dummyData->GetBinContent(nn+1))/hMC->GetBinContent(nn+1);
                }
                else{
                    if(h[15]->GetBinContent(nn+1)==0 && hMC->GetBinContent(nn+1)!=0 ) err = (hMC->GetBinError(nn+1))/hMC->GetBinContent(nn+1);
                    else err=0.0;
                }
                band->SetBinError(nn+1,err);
        }
        band->SetFillColor(kGray+3);
        band->SetFillStyle(3018);
        band->GetYaxis()->SetTitle("Data/MC");"""        



	raw_input()
	if(mass!=None):can.Print("../Plots/new/Final_combine_DNNfit_Control_"+mass+"_"+dataYear+"_"+lep+".png")
def getparams(mass):
	fitfile = R.TFile.Open("fitDiagnostics_M"+mass+".root")
	roofitResults = fitfile.Get("fit_s")
	
	mean = (roofitResults.floatParsFinal()).find("mean")
	print "mean : ",mean.getVal()," Error : ",mean.getError()

	Sigma = (roofitResults.floatParsFinal()).find("sigmaG")
	print "Sigma : ",Sigma.getVal()," Error : ",Sigma.getError()

if __name__ == "__main__":
	getthefit(mass,"el")
	getthefit(mass,"mu")
	#getparams(mass)
	#getcons(mass)
	#prefit_hist = getprefit_hist(mass,"mu")
	#prefit_hist[0].Draw()
	#prefit_hist[0].Print()
	#raw_input()
