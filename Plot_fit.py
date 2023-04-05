import sys
import ROOT as rt
import argparse as arg
from Hist_Style import *

parser = arg.ArgumentParser(description='Create workspace for higgs combine')
parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="MC top mass sample ['data','1695', '1715', '1725', '1735', '1755']")
parser.add_argument('-w', '--width', dest='width_sample', default=[None], type=str, nargs=1, help="MC top width sample ['data','x0p2','x0p5','x4','x8']")
#parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018']")
args = parser.parse_args()


mass  = args.mass_sample[0]
width = args.width_sample[0]
dataYear = args.Year[0]

def propagate_rate_uncertainity(hist, uncert):
    for i in range(hist.GetXaxis().GetNbins()):
        if hist.GetBinContent(i) != 0:
            hist.SetBinError(i, hist.GetBinContent(i) * uncert * 0.01)

def getcons(mass,width):
        if(mass!=None): fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
        else : fitfile = rt.TFile.Open("fitDiagnostics_width"+width+".root")
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
        Filename = rt.TFile("/home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_Input_histograms_"+dataYear+"_"+lep+".root","Read")
        
        #Data Vs Mc Condition
	rt.gROOT.cd()
        #Get the file and director where historgrams are stored for muon final state
        Dir = Filename.GetDirectory(lep+"jets")
        #Get Mc histograms for muon final state
	if(mass!=None):
        	top_sig = Dir.Get("top_sig_"+mass)
        	top_bkg = Dir.Get("top_bkg_"+mass)
        	EWK_bkg = Dir.Get("EWK_bkg")
                QCD = Dir.Get("QCD_DD")
	if(width!=None):
                top_sig = Dir.Get("top_sig_Nomix1")#+width)
                top_bkg = Dir.Get("top_bkg_Nomi"+width)
                EWK_bkg = Dir.Get("EWK_bkg")
                QCD = Dir.Get("QCD_DD")
	h1 = top_sig.Clone()
        h2 = top_bkg.Clone()
        h3 = EWK_bkg.Clone()
        h4 = QCD.Clone()
        hists.append(h1)
        hists.append(h2)
        hists.append(h3)
        hists.append(h4)
        #hists[0].Print()
        #print type(hists[0])
        #raw_input()
        return hists

def getthefit(mass,width,lep):
	if(mass!=None):fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
	else : fitfile = rt.TFile.Open("fitDiagnostics_width"+width+".root")
	fit = fitfile.Get(lep+"jets_logM_fit_s")
	fit.Print()

	Data = fit.findObject("h_"+lep+"jets")
	ResultPDF = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]")
	SigPDF = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]_Comp[shapeSig*]")
	BkgPDF = fit.findObject("pdf_bin"+lep+"jets_Norm[logM]_Comp[shapeBkg*]")

        print type(ResultPDF)

	legend = rt.TLegend(0.60193646, 0.5548435, 0.8093552, 0.79026143)
	legend.SetBorderSize(1)
	legend.SetTextSize(0.045)
	legend.SetLineColor(0)
	legend.SetLineStyle(1)
	legend.SetLineWidth(1)
	legend.SetFillColor(0)
	legend.SetFillStyle(1001)
	#legend.SetHeader("beNDC", "C")
	legend.AddEntry(Data, "Data", "ple1")
	legend.AddEntry(ResultPDF, "Fit.", "l")
	legend.AddEntry(SigPDF, "#it{t}-ch.", "l")
	legend.AddEntry(BkgPDF, "Bkg Pdf", "l")

	#print(type(Data_postfit))
	
	can = rt.TCanvas("can","can",600,600)
	can.cd()
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
	frame = rt.gPad.DrawFrame(Data.GetXaxis().GetXmin(), 0.0,Data.GetXaxis().GetXmax(),Data.GetYaxis().GetXmax()*1.15,';Events')
	#frame.GetXaxis().SetTitle('#varepsilon_{Sig} (%)')
	frame.GetYaxis().SetTitle('Events / (0.099)')
	frame.GetYaxis().SetTitleSize(0.04)
	Data.Draw("P")
	ResultPDF.Draw("same")
	SigPDF.Draw("same")
	BkgPDF.Draw("same")
	legend.Draw("same")
	cmstext = Get_CMSPreliminary(0.36, 0.86, 0.41, 0.88)
        cmstext.Draw()
        finalstate = Get_FinalStateTag(0.24,0.81,0.37,0.83,lep)
        finalstate.Draw()
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
	prefit_hists = getprefit_hist(mass,width,lep) #return top_sig,topbkg,EWK_bkg

        #propagate_rate_uncertainity(QCD, 50.0)	
        rt.gROOT.cd()
	Data_prefit = prefit_hists[0].Clone()  
	Data_prefit.Add(prefit_hists[1])
	Data_prefit.Add(prefit_hists[2])
        Data_prefit.SetName("Data_prefit")
        print("Data_prefit integral from input files = ",prefit_hists[0].Integral())

        #Data_prefit = fitfile.Get("shapes_prefit/"+lep+"jets/total")	These histograms has wronf infromation or have infrokmation about someting else
	#print("Data_prefit Int from fitdiagonistic = ",Data_prefit.Integral())
	Data_postfit_fitdignostics = fitfile.Get("shapes_fit_s/"+lep+"jets/total") # this is done because if we use it dictrly in trgraph Ass error is shows error
        print("Data_postfit Int from fitdigonistic = ",Data_postfit_fitdignostics.Integral())


	nbin = Data_prefit.GetXaxis().GetNbins()
	ledge = Data_prefit.GetXaxis().GetXmin()
	uedge = Data_prefit.GetXaxis().GetXmax()
        Data_postfit = rt.TH1D('Data_postfit', '', nbin, ledge, uedge)
 
        for bin in range(1,Data_prefit.GetNbinsX()+1):
                Data_postfit.SetBinContent(bin,Data_postfit_fitdignostics.GetBinContent(bin)*Data_postfit.GetBinWidth(bin)) 
                Data_postfit.SetBinError(bin,Data_postfit_fitdignostics.GetBinError(bin))
                

        print("Data_postfit Int from fitdigonistic after multiply with bin width = ",Data_postfit.Integral())
        # take ratio using tgraph a symmetic errors
        Data_postfit.Print()
        Data_prefit.Print()
	#h_ratio = rt.TGraphAsymmErrors(Data_postfit, Data_prefit, 'pois')
        #print h_ratio.GetN()
        h_ratio = Data_postfit.Clone()
        h_ratio.Divide(Data_prefit)

        #Add QCD_DD for the syst band	
	Data_prefit_with_QCD = Data_prefit.Clone()
	Data_prefit_with_QCD.Add(prefit_hists[3])

	#norms = fitfile.Get("norm_fit_s")	
	axis = h_ratio.GetXaxis()
	axis.SetLimits(Data_postfit.GetXaxis().GetXmin(), Data_postfit.GetXaxis().GetXmax())
	h_ratio.SetMarkerColor(1)
	h_ratio.SetMarkerStyle(20)
	h_ratio.SetMarkerSize(0.89)
	h_ratio.SetLineColor(rt.kBlack)


	band = rt.TH1D('Band', '', nbin, ledge, uedge)
	rt.gStyle.SetOptStat(0)
	for i in range(nbin+1):
		#`print Data_postfit.GetBinContent(i+1) ," : ",Data_prefit.GetBinContent(i+1)
		band.SetBinContent(i+1, 1.0)
		if (Data_prefit.GetBinContent(i+1)!=0 and Data_postfit.GetBinContent(i+1)!=0):
			err = (Data_prefit.GetBinError(i+1) * h_ratio.GetBinContent(i+1)) / Data_prefit.GetBinContent(i+1)
		elif (Data_prefit.GetBinContent(i+1)!=0 and Data_postfit.GetBinContent(i+1)==0):
			err = 1
		else:
			err = 0
		band.SetBinError(i+1, err)

	band.SetFillColor(rt.kGray+3)
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
	h_ratio.Draw('PE1;SAME')
	can.Update()
	raw_input()
	if(mass!=None):can.Print("../Plots/new/Final_combine_fit_Control_"+mass+"_"+dataYear+"_"+lep+".png")
	if(width!=None):can.Print("../Plots/Final_combine_fit_Control_Nomi"+width+"_"+dataYear+"_"+lep+".png")
def getparams(mass,width):
	if(mass!=None): fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
	else : fitfile = rt.TFile.Open("fitDiagnostics_width"+width+".root")
	roofitResults = fitfile.Get("fit_s")
	
	mean = (roofitResults.floatParsFinal()).find("mean")
	print "mean : ",mean.getVal()," Error : ",mean.getError()

	Sigma = (roofitResults.floatParsFinal()).find("sigmaG")
	print "Sigma : ",Sigma.getVal()," Error : ",Sigma.getError()

if __name__ == "__main__":
	getthefit(mass,width,"el")
	getthefit(mass,width,"mu")
	#raw_input()
	#getparams(mass,width)
	#getcons(mass,width)
	#prefit_hist = getprefit_hist(mass,width,"mu")
	#prefit_hist[0].Draw()
	#prefit_hist[0].Print()
	#raw_input()
