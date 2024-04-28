import numpy as np
#import argparse 
#import pandas as pd
import ROOT as rt

wFile=rt.TFile.Open("workspace_UL18.root","READ")
wspace=wFile.Get("w_UL18")
rt.gROOT.cd()
wspace.Print("t")

logM = wspace.['logM']
mean = wspace['mean']
sigmaG = wspace['sigmaG']
sigmaL_topbkg = wspace['sigmaL_topbkg']

sf_sig=rt.RooRealVar("sf_sig","signal SF",1.0,0.1,10.0)
sf_top=rt.RooRealVar("sf_top","Top bkg SF",1.0,0.1,10.0)
sf_ewk=rt.RooRealVar("sf_ewk","EWK bkg SF",1.0,0.1,10.0)

sig_mean=rt.RooRealVar("sig_mean","mean of signal sf",1.0)
sig_width=rt.RooRealVar("sig_width","uncertanty on t-ch sf",rt.TMath.Exp(0.16))

top_mean=rt.RooRealVar("top_mean","mean of top sf",1.0)
top_width=rt.RooRealVar("top_width","uncertanty on top sf",rt.TMath.Exp(0.05))

ewk_mean=rt.RooRealVar("ewk_mean","mean of ewk sf",1.0)
ewk_width=rt.RooRealVar("ewk_width","uncertanty on ewk sf",rt.TMath.Exp(0.10))
 
sig_constraint=rt.RooLognormal("sig_constraint","Constraint on signal norm",sf_sig,sig_mean,sig_width)
top_constraint=rt.RooLognormal("top_constraint","Constraint on top bkg norm",sf_top,top_mean,top_width)
ewk_constraint=rt.RooLognormal("ewk_constraint","Constraint on ewk bkg norm",sf_ewk,ewk_mean,ewk_width)

sample = rt.RooCategory("sample", "sample")

sig_pdf_norm=dict()
top_pdf_norm=dict()
ewk_pdf_norm=dict()
data=dict()
sig_pdf=dict()
top_pdf=dict()
ewk_pdf=dict()
model=dict()
modelFinal=dict()
sigYield=dict()
topYield=dict()
ewkYield=dict()
frame=dict()

for lep in ['mu','el']: 

	frame[lep]=logM.frame(Title=lep)
	sig_pdf_norm[lep]=wspace["sig_pdf_"+lep+"_norm"]
	top_pdf_norm[lep]=wspace["topbkg_pdf_"+lep+"_norm"]
	ewk_pdf_norm[lep]=wspace["EWKbkg_pdf_"+lep+"_norm"]
	sigYield[lep]=rt.RooFormulaVar("sigYield_"+lep,"@0*@1",rt.RooArgList(sf_sig,sig_pdf_norm[lep]))
	topYield[lep]=rt.RooFormulaVar("topYield_"+lep,"@0*@1",rt.RooArgList(sf_top,top_pdf_norm[lep]))
	ewkYield[lep]=rt.RooFormulaVar("ewkYield_"+lep,"@0*@1",rt.RooArgList(sf_ewk,ewk_pdf_norm[lep]))

	data[lep]=wspace["data_"+lep]
	sample.defineType(lep)

	sig_pdf[lep]=wspace["sig_pdf_"+lep]
	top_pdf[lep]=wspace["top_bkg_pdf_"+lep]
	ewk_pdf[lep]=wspace["EWKbkg_pdf_"+lep]
	model[lep]=rt.RooAddPdf("model_"+lep,"model_"+lep,rt.RooArgList(sig_pdf[lep],top_pdf[lep],ewk_pdf[lep]),rt.RooArgList(sigYield[lep],topYield[lep],ewkYield[lep]))
	modelFinal[lep]=rt.RooProdPdf("modelFinal_"+lep,"model with constraint for "+lep,rt.RooArgSet(model[lep],sig_constraint,top_constraint,ewk_constraint))
#	modelFinal[lep]=rt.RooProdPdf("modelFinal_"+lep,"model with constraint for "+lep,rt.RooArgSet(model[lep],top_constraint,ewk_constraint))
	
simPdf=rt.RooSimultaneous("simPdf", "simultaneous pdf", {"mu": modelFinal['mu'], "el": modelFinal['el']}, sample)
combData=rt.RooDataSet("combData","combined data",{logM},Index=sample,Import={"mu": data['mu'], "el": data['el']})
fitResult=simPdf.fitTo(combData, Extended=True, NumCPU=4, Save=True)
fitResult.Print("v")
print(fitResult.status())
c=rt.TCanvas("Canvas","Canvas")
c.Divide(2,1)
for lep in ['mu','el']:
	c.cd(1) if lep == 'mu' else c.cd(2)
	rt.TGaxis.SetMaxDigits(3)
	data[lep].plotOn(frame[lep],Name="Data_"+lep,LineColor=rt.kBlack)
	modelFinal[lep].plotOn(frame[lep],Name="Fit_"+lep,LineColor=rt.kBlue,LineStyle=1,LineWidth=3)
#	modelFinal[lep].plotOn(frame[lep],Components=rt.RooArgList(sig_pdf[lep]),Name="signal_"+lep,LineColor=rt.kRed,LineStyle=1,LineWidth=3)
#	modelFinal[lep].plotOn(frame[lep],Components=rt.RooArgList(top_pdf[lep]),Name="Top_"+lep,LineColor=rt.kOrange-1,LineStyle=1,LineWidth=3)
#	modelFinal[lep].plotOn(frame[lep],Components=rt.RooArgList(ewk_pdf[lep]),Name="EWK_"+lep,LineColor=rt.kGreen-2,LineStyle=1,LineWidth=3)
	data[lep].plotOn(frame[lep],LineColor=rt.kBlack)
	frame[lep].Draw()

rt.gROOT.cd()
rt.EnableImplicitMT(rt.kTRUE)
#mgr=rt.RooMCStudy(simPdf,rt.RooArgSet(logM,sample),Constrain=rt.RooArgSet(sf_sig,sf_top,sf_ewk),Binned=rt.kTRUE,Silence=rt.kTRUE,Extended=rt.kTRUE,FitOptions=dict(Extended=rt.kTRUE,Save=rt.kTRUE,PrintEvalErrors=0))
mgr=rt.RooMCStudy(simPdf,rt.RooArgSet(logM,sample),Constrain=rt.RooArgSet(sf_top,sf_ewk),Binned=rt.kTRUE,Silence=rt.kTRUE,Extended=rt.kTRUE,FitOptions=dict(Extended=rt.kTRUE,Save=rt.kTRUE,PrintEvalErrors=0))
mgr.generateAndFit(10000)
rt.EnableImplicitMT(rt.kFALSE)

mean_=mgr.plotParam(mean,Bins=15)
mean_Pull=mgr.plotPull(mean,Bins=15,FitGauss=rt.kTRUE)

sigma_=mgr.plotParam(sigmaG,Bins=15)
sigma_Pull=mgr.plotPull(sigmaG,Bins=15,FitGauss=rt.kTRUE)

sf_sig_=mgr.plotParam(sf_sig,Bins=15)
sf_sig_Pull=mgr.plotPull(sf_sig,Bins=15,FitGauss=rt.kTRUE)

sf_top_=mgr.plotParam(sf_top,Bins=15)
sf_top_Pull=mgr.plotPull(sf_top,Bins=15,FitGauss=rt.kTRUE)

sf_ewk_=mgr.plotParam(sf_ewk,Bins=15)
sf_ewk_Pull=mgr.plotPull(sf_ewk,Bins=15,FitGauss=rt.kTRUE)

outFile=rt.TFile("outFile_NoFreeSignal.root","RECREATE")
outFile.cd()
c.Write()
mean_.Write()
mean_Pull.Write()
sigma_.Write()
sigma_Pull.Write()
sf_sig_.Write()
sf_sig_Pull.Write()
sf_top_.Write()
sf_top_Pull.Write()
sf_ewk_.Write()
sf_ewk_Pull.Write()
outFile.Write()
outFile.Close()
