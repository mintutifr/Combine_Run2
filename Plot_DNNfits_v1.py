import sys
import json
import math
import ROOT as R
import numpy as np
import argparse as arg
from Hist_style import *
from mlfitNormsToText import *

def propagate_rate_uncertainity(hist, uncert):
    for i in range(hist.GetXaxis().GetNbins()):
        if hist.GetBinContent(i) != 0:
            hist.SetBinError(i, hist.GetBinContent(i) * uncert * 0.01)

def GetCons_fromJson(jsonfile):
        # Opening JSON file
        f = open(jsonfile)

        # returns JSON object as 
        # a dictionary
        data = json.load(f)

        # Iterating through the json
        # list
        POI_name = data['POIs'][0]['name']
        POI_fit = data['POIs'][0]['fit']
        #print POI_name
        #print POI_fit

        r_impact_hi = POI_fit[2] - POI_fit[1] #r values are dtored by andding and substraction the error
        r_impact_lo = POI_fit[0] - POI_fit[1]

        #print r_impact_hi, r_impact_lo


        params = data["params"]
        #print params[0]['fit']

        parameter_to_track = ["cons_EWK_bkg", "cons_QCD_bkg","cons_top_bkg"]
        parameter_info = {}

        parameter_info[POI_name]=[r_impact_lo,POI_fit[1],r_impact_hi]

        for i,para in enumerate(data["params"]):
                para_name = params[i]['name']
                if para_name in parameter_to_track:
                        #print params[i]['name']
                        #print params[i]['fit']
                        parameter_info[para_name]=params[i]['fit']


        #print(parameter_info)
        f.close()

        cons_N_Er = {"cons_val":{"top_sig": parameter_info['r'][1],
                      "top_bkg": parameter_info['cons_top_bkg'][1],
                      "EWK_bkg": parameter_info['cons_EWK_bkg'][1],
                      "QCD_bkg": parameter_info['cons_QCD_bkg'][1]
                      },
               "cons_Error":{
                        "top_sig": abs(parameter_info['r'][0]) if abs(parameter_info['r'][0])>abs(parameter_info['r'][2]) else abs(parameter_info['r'][2]),
                        "top_bkg": abs(parameter_info['cons_top_bkg'][0]) if abs(parameter_info['cons_top_bkg'][0])>abs(parameter_info['cons_top_bkg'][2]) else abs(parameter_info['cons_top_bkg'][2]),
                        "EWK_bkg": abs(parameter_info['cons_EWK_bkg'][0]) if abs(parameter_info['cons_EWK_bkg'][0])>abs(parameter_info['cons_EWK_bkg'][2]) else abs(parameter_info['cons_EWK_bkg'][2]), 
                        "QCD_bkg": abs(parameter_info['cons_QCD_bkg'][0]) if abs(parameter_info['cons_QCD_bkg'][0])>abs(parameter_info['cons_QCD_bkg'][2]) else abs(parameter_info['cons_QCD_bkg'][2]),
                     }
                }
        for category in ["top_sig","top_bkg","EWK_bkg","QCD_bkg"]:
                print(category," ", cons_N_Er['cons_val'][category],"  ",cons_N_Er['cons_Error'][category])
        return cons_N_Er


def getcons(File,lep):
        fitfile = File 
 
        #fitfile = R.TFile.Open("fitDiagnostics_M1725_DNNfit_"+dataYear+".root") 
        fit = fitfile.Get(lep+"jets_CMS_th1x_fit_s")

        roofitResults = fitfile.Get("fit_s")

        cons_top_sig = (roofitResults.floatParsFinal()).find("r")
        print("cons_top_sig : ",cons_top_sig.getVal()," Error : ",cons_top_sig.getError())

        cons_top_bkg = (roofitResults.floatParsFinal()).find("cons_top_bkg")
        print("cons_top_bkg : ",cons_top_bkg.getVal()," Error : ",cons_top_bkg.getError())

        cons_EWK_bkg = (roofitResults.floatParsFinal()).find("cons_EWK_bkg")
        print("cons_EWK_bkg : ",cons_EWK_bkg.getVal()," Error : ",cons_EWK_bkg.getError())

        cons_QCD_bkg = (roofitResults.floatParsFinal()).find("cons_QCD_bkg")
        print("cons_QCD_bkg : ",cons_QCD_bkg.getVal()," Error : ",cons_QCD_bkg.getError())
        
        cons_N_Er = {"cons_val":{"top_sig": cons_top_sig.getVal(),
                      "top_bkg": cons_top_bkg.getVal(),
                      "EWK_bkg": cons_EWK_bkg.getVal(),
                      "QCD_bkg": cons_QCD_bkg.getVal()
                      },
               "cons_Error":{"top_sig": cons_top_sig.getError(),
                            "top_bkg": cons_top_bkg.getError(),
                            "EWK_bkg": cons_EWK_bkg.getError(), 
                            "QCD_bkg": cons_QCD_bkg.getError(),
                         }
                }
        for category in ["top_sig","top_bkg","EWK_bkg","QCD_bkg"]:
                print(category," ", cons_N_Er['cons_val'][category],"  ",cons_N_Er['cons_Error'][category])
        return cons_N_Er

def getprefit_hist(mass,lep,year,Combine_year_tag):
        hists = []
        Filename = R.TFile("/feynman/home/dphp/mk277705/work/HiggsCombine/CMSSW_12_3_4/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_DNNFit_Input_t_ch_CAsi_histograms_"+year+"_"+lep+".root","Read")
        
        #Data Vs Mc Condition
        R.gROOT.cd()
        #Get the file and director where historgrams are stored for muon final state
        Dir = Filename.GetDirectory(lep+"jets")
        #Get Mc histograms for muon final state
        if(mass!=None):
                tag = Combine_year_tag[year]
                top_sig = Dir.Get("top_sig_"+mass+tag)
                top_bkg = Dir.Get("top_bkg_"+mass+tag)
                EWK_bkg = Dir.Get("EWK_bkg"+tag)
                QCD = Dir.Get("QCD_DD"+tag)

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
def getthefit(mass,lep,year,fitdignostic):
        Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18"} 
        prefit_hists = getprefit_hist(mass,lep,year,Combine_year_tag) #return top_sig,topbkg,EWK_bkg
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

        tag = Combine_year_tag[year] 
        del Combine_year_tag

        fitfile = R.TFile.Open(fitdignostic)
        fitname = lep+"jets"+tag+"_CMS_th1x_fit_s" 
        fit = fitfile.Get(fitname)
        print("reading fit from "+fitdignostic+"/"+fitname)
        del fitname
        #fit.Print()

        Data_postfit_roohist = fit.findObject("h_"+lep+"jets"+tag)

        TopSigFitHist_Mc = fitfile.Get("shapes_fit_s/"+lep+"jets"+tag+"/top_sig_1725"+tag) 
        TopBkgFitHist_Mc = fitfile.Get("shapes_fit_s/"+lep+"jets"+tag+"/top_bkg_1725"+tag) 
        EWKBkgFitHist_Mc = fitfile.Get("shapes_fit_s/"+lep+"jets"+tag+"/EWK_bkg"+tag)
        QCDBkgFitHist_Mc = fitfile.Get("shapes_fit_s/"+lep+"jets"+tag+"/QCD_DD"+tag)

        #constaints_from_fit = getcons(fitfile,lep)
        #constaints_from_fit = GetCons_fromJson('impacts_DNN_'+year+'.json')
        Norm_and_error_from_fit = Get_Norm_N_error(errors=True,InFile = fitdignostic,year=year)
        #del filenams
        #print(Norm_and_error_from_fit)
        top_sig_cons_el = (Norm_and_error_from_fit['eljets'+tag]['top_sig_1725'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['eljets'+tag]['top_sig_1725'+tag]['S+B-Fit']['Norm'])*100
        top_sig_cons_mu = (Norm_and_error_from_fit['mujets'+tag]['top_sig_1725'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['mujets'+tag]['top_sig_1725'+tag]['S+B-Fit']['Norm'])*100
        top_sig_cons = top_sig_cons_el if(top_sig_cons_el > top_sig_cons_mu) else top_sig_cons_mu

        top_bkg_cons_el = (Norm_and_error_from_fit['eljets'+tag]['top_bkg_1725'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['eljets'+tag]['top_bkg_1725'+tag]['S+B-Fit']['Norm'])*100
        top_bkg_cons_mu = (Norm_and_error_from_fit['mujets'+tag]['top_bkg_1725'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['mujets'+tag]['top_bkg_1725'+tag]['S+B-Fit']['Norm'])*100
        top_bkg_cons = top_bkg_cons_el if(top_bkg_cons_el > top_bkg_cons_mu) else top_bkg_cons_mu

        EWK_bkg_cons_el = (Norm_and_error_from_fit['eljets'+tag]['EWK_bkg'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['eljets'+tag]['EWK_bkg'+tag]['S+B-Fit']['Norm'])*100
        EWK_bkg_cons_mu = (Norm_and_error_from_fit['mujets'+tag]['EWK_bkg'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['mujets'+tag]['EWK_bkg'+tag]['S+B-Fit']['Norm'])*100
        EWK_bkg_cons = EWK_bkg_cons_el if(EWK_bkg_cons_el > EWK_bkg_cons_mu) else EWK_bkg_cons_mu

        QCD_bkg_cons_el = (Norm_and_error_from_fit['eljets'+tag]['QCD_DD'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['eljets'+tag]['QCD_DD'+tag]['S+B-Fit']['Norm'])*100
        QCD_bkg_cons_mu = (Norm_and_error_from_fit['mujets'+tag]['QCD_DD'+tag]['S+B-Fit']['Error']/Norm_and_error_from_fit['mujets'+tag]['QCD_DD'+tag]['S+B-Fit']['Norm'])*100
        QCD_bkg_cons = QCD_bkg_cons_el if(QCD_bkg_cons_el > QCD_bkg_cons_mu) else QCD_bkg_cons_mu
        
        print("\n new constraints : \n top_sig_1725 : %s , top_bkg_1725 : %s , EWK_bkg : %s , QCD_DD : %s  \n" % (round(top_sig_cons,2),round(top_bkg_cons,2),round(EWK_bkg_cons,2),round(QCD_bkg_cons,2)))


        propagate_rate_uncertainity(TopSigFitHist_Mc,(top_sig_cons)); TopSigFitHist_Mc = Rebase_Xaxies_scale(TopSigFitHist_Mc,TopSigFitHist_Mc)
        propagate_rate_uncertainity(TopBkgFitHist_Mc,(top_bkg_cons)); TopBkgFitHist_Mc = Rebase_Xaxies_scale(TopBkgFitHist_Mc,TopBkgFitHist_Mc)
        propagate_rate_uncertainity(EWKBkgFitHist_Mc,(EWK_bkg_cons)); EWKBkgFitHist_Mc = Rebase_Xaxies_scale(EWKBkgFitHist_Mc,EWKBkgFitHist_Mc)
        propagate_rate_uncertainity(QCDBkgFitHist_Mc,(QCD_bkg_cons)); QCDBkgFitHist_Mc = Rebase_Xaxies_scale(QCDBkgFitHist_Mc,QCDBkgFitHist_Mc)     
 
        ResultFitHist_Mc_unct_prop = TopSigFitHist_Mc.Clone(); TopSigFitHist_Mc.Print();#print(TopSigFitHist_Mc.Integral())
        ResultFitHist_Mc_unct_prop.Add(TopBkgFitHist_Mc);   TopBkgFitHist_Mc.Print();#print(TopBkgFitHist_Mc.Integral())
        ResultFitHist_Mc_unct_prop.Add(EWKBkgFitHist_Mc);   EWKBkgFitHist_Mc.Print();#print(EWKBkgFitHist_Mc.Integral())
        ResultFitHist_Mc_unct_prop.Add(QCDBkgFitHist_Mc);   QCDBkgFitHist_Mc.Print();#print(QCDBkgFitHist_Mc.Integral())

        """DNN_postfit_Norm = {lep :{
                                year:{
                                        "top_sig_1725": TopSigFitHist_Mc.Integral(),
                                        "top_bkg_1725": TopBkgFitHist_Mc.Integral(),
                                        "EWK_bkg": EWKBkgFitHist_Mc.Integral(),
                                        "QCD_DD": QCDBkgFitHist_Mc.Integral()
                                        }
                                }
                           }
        for category in ["top_sig_1725","top_bkg_1725","EWK_bkg","QCD_DD"]:
               print lep," ",category," ", DNN_postfit_Norm[lep][year][category]
               print Norm_and_error_from_fit[lep+'jets'][category]['S+B-Fit']['Norm']
        print(DNN_postfit_Norm)"""
         
        QCDBkgFitHist_Mc.SetFillColor(R.kGray)
        QCDBkgFitHist_Mc.SetLineColor(R.kGray)
        EWKBkgFitHist_Mc.SetFillColor(R.kGreen+2)
        EWKBkgFitHist_Mc.SetLineColor(R.kGreen+2)
        TopBkgFitHist_Mc.SetFillColor(R.kOrange-1)
        TopBkgFitHist_Mc.SetLineColor(R.kOrange-1)
        TopSigFitHist_Mc.SetFillColor(R.kRed)
        TopSigFitHist_Mc.SetLineColor(R.kRed)

        hs = R.THStack("hs","");
        hs.Add(QCDBkgFitHist_Mc)
        hs.Add(EWKBkgFitHist_Mc)
        hs.Add(TopBkgFitHist_Mc)
        hs.Add(TopSigFitHist_Mc)
        
        MC_error_band = QCDBkgFitHist_Mc.Clone(); MC_error_band.Add(EWKBkgFitHist_Mc)
        MC_error_band.Add(TopBkgFitHist_Mc); MC_error_band.Add(TopSigFitHist_Mc)       
        MC_error_band.SetFillColor(rt.kGray+3)
        MC_error_band.SetFillStyle(3018)
 
        ResultFitHist_total = fitfile.Get("shapes_fit_s/"+lep+"jets"+tag+"/total");
        ResultFitHist_total=Rebase_Xaxies_scale(ResultFitHist_total,ResultFitHist_Mc_unct_prop)
        del ResultFitHist_Mc_unct_prop
        del tag
        ResultFitHist_total.SetLineColor(R.kBlue)
        ResultFitHist_total.SetLineWidth(2)

        legend = R.TLegend(0.50, 0.70, 0.88, 0.88)
        legend.SetNColumns(2)
        legend.SetBorderSize(1)
        legend.SetTextSize(0.045)
        legend.SetLineColor(0)
        legend.SetLineStyle(1)
        legend.SetLineWidth(1)
        legend.SetFillColor(0)
        legend.SetFillStyle(1001)
        #legend.SetHeader("beNDC", "C")
        legend.AddEntry(Data_prefit, "Data", "ple1")
        legend.AddEntry(ResultFitHist_total, "Fit.", "l")
        legend.AddEntry(TopSigFitHist_Mc, "corr. top", "f")
        legend.AddEntry(TopBkgFitHist_Mc, "top bkg", "f")
        legend.AddEntry(EWKBkgFitHist_Mc, "EWK bkg", "f")
        legend.AddEntry(QCDBkgFitHist_Mc, "QCD bkg", "f")

        del TopSigFitHist_Mc
        del TopBkgFitHist_Mc
        del EWKBkgFitHist_Mc
        del QCDBkgFitHist_Mc        

        can = R.TCanvas("can","can",800,700)
        R.gStyle.SetOptStat(0)
        can.cd()
        R.gStyle.SetErrorX(0)
        R.TGaxis.SetMaxDigits(3)

        pad1 = R.TPad('pad1', 'pad1', 0.0, 0.195259, 1.0, 0.990683)
        pad1.SetBottomMargin(0.089)
        pad1.SetTicky()
        pad1.SetTickx()
        
        #pad1.GetGridy().SetMaximum(Data.GetMaximum() * 1.2)
        #pad1.SetRightMargin(0.143)
        pad1.Draw()
        pad1.cd()
        print(type(Data_postfit_roohist))
        frame = R.gPad.DrawFrame(Data_postfit_roohist.GetXaxis().GetXmin(), 0.0,Data_postfit_roohist.GetXaxis().GetXmax(),Data_postfit_roohist.GetYaxis().GetXmax()*1.15,';Events')

        #frame.GetXaxis().SetTitle('#varepsilon_{Sig} (%)')
        #frame.GetYaxis().SetTitle('Events / (0.1)')
        #frame.GetYaxis().SetTitleSize(0.04)

        frame.Draw()  
        hs.Draw("hist")
        
        Variable="t_ch_CAsi"
        if(Variable in ['bJetdeepJet','lJetdeepJet',"t_ch_WAsi" , "t_ch_CAsi" , "ttbar_CAsi" , "ttbar_WAsi" , "EWK" , "QCD"]):
            fix_range = pad1.GetUymax()*10
            pad1.SetLogy()
            minimum = 10
        else:    
            fix_range = pad1.GetUymax() + (pad1.GetUymax() / 3.0)
            minimum = 0.001

        print(fix_range,"  <------------------------------------------------------------")

              
        #    print("fix_range = " + str(fix_range))
        hs.SetMaximum(fix_range)
        hs.SetMinimum(minimum)
        #Data_prefit.GetXaxis().SetRangeUser(minimum,maxximum)
        hs.GetYaxis().SetTitle('Events')
        #hs.GetYaxis().SetTitleSize(0.04)
        hs.GetYaxis().SetTitleOffset(0.9)              
        hs.GetYaxis().SetTitleSize(0.05)
        hs.GetYaxis().SetLabelSize(0.04)
        Data_prefit.Draw("P;same")
        ResultFitHist_total.Draw("same;hist")
        MC_error_band.Draw("E2;same")
        legend.Draw("same")

        CMSpreliminary = getCMSInt_tag(0.36, 0.86, 0.38, 0.88)
        CMSpreliminary.Draw("same")
        lepjet_tag = leptonjet_tag(lep,0.24,0.81,0.37,0.83)
        lepjet_tag.Draw("same")
        yearNlumitag = year_tag(year,0.72, 0.92, 0.9, 0.96)
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
 

        #h_ratio = R.TGraphAsymmErrors(ResultFitHist_total, ResultFitHist_total, 'pois')
        #print h_ratio.GetN()

        nbin = Data_prefit.GetXaxis().GetNbins()
        ledge = Data_prefit.GetXaxis().GetXmin()
        uedge = Data_prefit.GetXaxis().GetXmax()
        BINS = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,1.0]
        print("redefine assymatic histogram bins ", BINS)
        h_ratio = R.TH1F('h_ratio', '', len(BINS)-1,np.array(BINS))
        for iBin in range(1,nbin+1):
                error_prefit = Data_prefit.GetBinError(iBin)
                error_postfit = ResultFitHist_total.GetBinError(iBin)
                cont_prefit = Data_prefit.GetBinContent(iBin)
                cont_postfit = ResultFitHist_total.GetBinContent(iBin)
                #h_ratio.SetBinContent(i,(Data_prefit.GetBinContent(i)-ResultFitHist_total.GetBinContent(i))/math.sqrt(error_prefit*error_prefit+error_postfit*error_postfit))
                sigma_pull = R.TMath.Sqrt( R.TMath.Abs(error_prefit*error_prefit - error_postfit*error_postfit ))
                pull= ( cont_postfit-cont_prefit) / sigma_pull
                pull_err = ( error_prefit - error_postfit )/ sigma_pull
                #print(error_prefit, error_postfit, sigma_pull)
                h_ratio.SetBinContent(iBin, pull)
                h_ratio.SetBinError(iBin, pull_err)
                #print(pull,pull_err)
        #Add QCD_DD for the syst band	

        h_ratio.SetFillColor(R.kBlue+3)
        h_ratio.SetFillStyle(3001)
         
        h_ratio.GetYaxis().SetTitle("#frac{Data-Fit}{#Delta}") 
        #band.GetXaxis().SetTitle(Data.GetXaxis().GetTitle())
        h_ratio.GetXaxis().SetTitle("DNN Score (Corr. Assign Signal)")
        h_ratio.GetYaxis().CenterTitle(1) 
        h_ratio.GetYaxis().SetTitleOffset(0.35)              
        h_ratio.GetYaxis().SetTitleSize(0.12)
        h_ratio.GetXaxis().SetTitleSize(0.12)
        h_ratio.GetYaxis().SetLabelSize(0.12)
        h_ratio.GetXaxis().SetLabelSize(0.12)
        h_ratio.GetYaxis().SetRangeUser(-1.2,1.2)
        h_ratio.SetLineColor(R.kBlack)
        h_ratio.SetMarkerStyle(20)


        c = h_ratio.GetYaxis();
        c.SetNdivisions(6);
        c.SetTickSize(0.01);

        h_ratio.Draw("hist")
        can.Update()

        """Ratio_hist= R.TGraphAsymmErrors(ResultFitHist_total, ResultFitHist_total,"pois")
        axis = Ratio_hist.GetXaxis()
        axis.SetLimits(ResultFitHist_total.GetXaxis().GetXmin(),ResultFitHist_total.GetXaxis().GetXmax())
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



        #raw_input()
        can.Print("Plots/Final_combine_DNNfit_Control_data_"+year+"_"+lep+".png")
        can.Print("Plots/Final_combine_DNNfit_Control_data_"+year+"_"+lep+".pdf")
def getparams(mass):
	fitfile = R.TFile.Open("fitDiagnostics_M"+mass+".root")
	roofitResults = fitfile.Get("fit_s")
	
	mean = (roofitResults.floatParsFinal()).find("mean")
	print("mean : ",mean.getVal()," Error : ",mean.getError())

	Sigma = (roofitResults.floatParsFinal()).find("sigmaG")
	print("Sigma : ",Sigma.getVal()," Error : ",Sigma.getError())

if __name__ == "__main__":
        parser = arg.ArgumentParser(description='Create workspace for higgs combine')
        parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="MC top mass sample ['data','1695', '1715', '1725', '1735', '1755']")
        parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
        parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018, Run2']")
        parser.add_argument('-f', '--fitdignostic_outFile ', dest='fitdignostic_outFile', type=str, nargs=1, help="Fit dignostic output file which has histogram files i.e /home/mikumar/t3store/workarea/Higgs_Combine/CMSSW_11_3_4/src/Combine_Run2/fitDiagnostics_M1725_DNNfit_UL2017.root")
        args = parser.parse_args()


        mass  = args.mass_sample[0]
        dataYear = args.Year[0]
        Fitdignostic_outFile = args.fitdignostic_outFile[0]

        getthefit(mass,"mu",year=dataYear,fitdignostic=Fitdignostic_outFile)
        getthefit(mass,"el",year=dataYear,fitdignostic=Fitdignostic_outFile)
	#getparams(mass)
	#getcons(mass)
	#prefit_hist = getprefit_hist(mass,"mu")
	#prefit_hist[0].Draw()
	#prefit_hist[0].Print()
	#raw_input()
