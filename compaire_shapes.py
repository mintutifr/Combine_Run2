import ROOT as R
import sys, datetime
import argparse as arg
from Hist_style import *
#from TOY_local_fit import Toy_Mc 
parser = arg.ArgumentParser(description='Create workspace for higgs combine')
parser.add_argument('-y', '--year', dest='Year', default=['UL2017'], type=str, nargs=1, help="Year of Data collection [ UL2016preVFP  UL2016postVFP  UL2017  UL2018 ]")
parser.add_argument('-s', '--shape', dest='shape', default=[None], type=str, nargs=1, help="shape for  [for lntopMass use 'top' beacuse hist file are stored with this name]")
args = parser.parse_args()

        
mass  = "1725"
dataYear = args.Year[0]
shape = args.shape[0]
date   = datetime.datetime.now()


print("mass: ",mass)
print("dataYear: ",dataYear)
print("shape: ",shape)




Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18"}

tag = Combine_year_tag[dataYear]

if __name__ == "__main__":
    
    #read the file to get the hustogrms
    Dir = "/feynman/home/dphp/mk277705/work/HiggsCombine/CMSSW_12_3_4/src/PhysicsTools/NanoAODTools/crab/WorkSpace/"
    Filename_mu_sig = Dir+"Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_gteq0p7_withoutDNNfit_rebin.root"
    Filename_el_sig = Dir+"Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_gteq0p7_withoutDNNfit_rebin.root"
    #read the file to get the hustogrms
    print(f'{Filename_mu_sig = }')
    print(f'{Filename_el_sig = }')

    Filename_mu_con = Dir+"Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_lt0p7gteq0p3_withoutDNNfit_rebin.root"
    Filename_el_con = Dir+"Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_lt0p7gteq0p3_withoutDNNfit_rebin.root"
    print(f'{Filename_mu_con = }')
    print(f'{Filename_el_con = }')

    Filename_mu_sig_plus_con = Dir+"Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_mu_gteq0p3_withoutDNNfit_rebin.root"
    Filename_el_sig_plus_con = Dir+"Hist_for_workspace/Combine_Input_lntopMass_histograms_"+dataYear+"_el_gteq0p3_withoutDNNfit_rebin.root"
    print(f'{Filename_mu_sig_plus_con = }')
    print(f'{Filename_el_sig_plus_con = }')

    File_mu_sig = R.TFile(Filename_mu_sig,"Read")
    File_el_sig = R.TFile(Filename_el_sig,"Read")
    File_mu_con = R.TFile(Filename_mu_con,"Read")
    File_el_con = R.TFile(Filename_el_con,"Read")
    File_mu_sig_plus_con = R.TFile(Filename_mu_sig_plus_con,"Read")
    File_el_sig_plus_con = R.TFile(Filename_el_sig_plus_con,"Read")
    #Data Vs Mc Condition

    #Get the file and director where historgrams are stored for muon final state
    dir_mu_sig = File_mu_sig.GetDirectory("mujets")
    dir_el_sig = File_el_sig.GetDirectory("eljets")
    dir_mu_con = File_mu_con.GetDirectory("mujets")
    dir_el_con = File_el_con.GetDirectory("eljets")
    dir_mu_sig_plus_con = File_mu_sig_plus_con.GetDirectory("mujets")
    dir_el_sig_plus_con = File_el_sig_plus_con.GetDirectory("eljets")
    #Get Mc histograms for muon final state
    if("top" in shape):
        print("trying to get hist with name : ", shape+"_"+mass+tag+"_gt")
        shape_mu_sig = dir_mu_sig.Get(shape+"_"+mass+tag+"_gt")
        shape_el_sig = dir_el_sig.Get(shape+"_"+mass+tag+"_gt")
        shape_mu_con = dir_mu_con.Get(shape+"_"+mass+tag+"_lt")
        shape_el_con = dir_el_con.Get(shape+"_"+mass+tag+"_lt")
        shape_mu_sig_plus_con = dir_mu_sig_plus_con.Get(shape+"_"+mass+tag+"_gt")
        shape_el_sig_plus_con = dir_el_sig_plus_con.Get(shape+"_"+mass+tag+"_gt")
        
    else:
        #rt.gROOT.cd()
        print("trying to get hist with name : ", shape+tag+"_gt")
        shape_mu_sig = dir_mu_sig.Get(shape+tag+"_gt").Clone()
        shape_el_sig = dir_el_sig.Get(shape+tag+"_gt")
        shape_mu_con = dir_mu_con.Get(shape+tag+"_gt_lt")
        shape_el_con = dir_el_con.Get(shape+tag+"_gt_lt")
        shape_mu_sig_plus_con = dir_mu_sig_plus_con.Get(shape+tag+"_gt")
        shape_el_sig_plus_con = dir_el_sig_plus_con.Get(shape+tag+"_gt")

    shape_mu_sig.SetLineColor(R.kBlue+2) 
    shape_el_sig.SetLineColor(R.kBlue+2)
    shape_mu_con.SetLineColor(R.kRed+2)
    shape_el_con.SetLineColor(R.kRed+2)
    shape_mu_sig_plus_con.SetLineColor(R.kGreen+2)
    shape_el_sig_plus_con.SetLineColor(R.kGreen+2)
    
    shape_mu_sig.Scale(1/shape_mu_sig.Integral())
    shape_el_sig.Scale(1/shape_el_sig.Integral())
    shape_mu_con.Scale(1/shape_mu_con.Integral())
    shape_el_con.Scale(1/shape_el_con.Integral())
    shape_mu_sig_plus_con.Scale(1/shape_mu_sig_plus_con.Integral())
    shape_el_sig_plus_con.Scale(1/shape_el_sig_plus_con.Integral())

    legend = R.TLegend(0.50, 0.70, 0.87, 0.88)
    #legend.SetNColumns(2)
    legend.SetBorderSize(1)
    legend.SetTextSize(0.045)
    legend.SetLineColor(0)
    legend.SetLineStyle(1)
    legend.SetLineWidth(1)
    legend.SetFillColor(0)
    legend.SetFillStyle(1001)
    #legend.SetHeader("beNDC", "C")
    legend.AddEntry(shape_mu_sig_plus_con, "DNN #geq 0.3", "l")
    legend.AddEntry(shape_mu_sig, "DNN #geq 0.7", "l")
    legend.AddEntry(shape_mu_con, "0.3 #leq DNN < 0.7", "l")
    
    

    can = R.TCanvas("can","can",1400,700); 
    can.Divide(2,1);
    can.cd(1)
    shape_mu_sig_plus_con.SetTitle("")
    shape_mu_sig_plus_con.GetYaxis().SetRangeUser(0.0,0.25)
    
    shape_mu_sig_plus_con.GetYaxis().SetTitle('Unit Normalized')
    shape_mu_sig_plus_con.GetYaxis().SetTitleOffset(1.1)              
    shape_mu_sig_plus_con.GetYaxis().SetTitleSize(0.05)
    shape_mu_sig_plus_con.GetYaxis().SetLabelSize(0.04)
    
    shape_mu_sig_plus_con.GetXaxis().SetTitle('ln(m_{t} / 1 GeV)')
    shape_mu_sig_plus_con.GetXaxis().SetTitleOffset(1.1)              
    shape_mu_sig_plus_con.GetXaxis().SetTitleSize(0.04)
    shape_mu_sig_plus_con.GetXaxis().SetLabelSize(0.04)
    
    shape_mu_sig_plus_con.Draw("E1")
    shape_mu_sig.Draw("E1;same")
    shape_mu_con.Draw("E1;same")
    
    legend.Draw()

    CMSTAG  = getCMSInt_tag(x1=0.32, y1=0.86, x2=0.4, y2=0.88)
    lepton_tag_mu = leptonjet_tag(lep="mu",x1=0.32, y1=0.82, x2=0.4, y2=0.84)
    year_tag = year_tag(dataYear,x1=0.85, y1=0.92, x2=0.9, y2=0.95)
    CMSTAG.Draw()
    lepton_tag_mu.Draw()
    year_tag.Draw()


    can.cd(2)
    shape_el_sig_plus_con.SetTitle("")
    shape_el_sig_plus_con.GetYaxis().SetRangeUser(0.0,0.25)

    shape_el_sig_plus_con.GetYaxis().SetTitle('Unit Normalized')
    shape_el_sig_plus_con.GetYaxis().SetTitleOffset(1.1)              
    shape_el_sig_plus_con.GetYaxis().SetTitleSize(0.05)
    shape_el_sig_plus_con.GetYaxis().SetLabelSize(0.04)

    shape_el_sig_plus_con.GetXaxis().SetTitle('ln(m_{t} / 1 GeV)')
    shape_el_sig_plus_con.GetXaxis().SetTitleOffset(1.1)              
    shape_el_sig_plus_con.GetXaxis().SetTitleSize(0.04)
    shape_el_sig_plus_con.GetXaxis().SetLabelSize(0.04)
    
    shape_el_sig_plus_con.Draw("E1")
    shape_el_sig.Draw("E1;same")
    shape_el_con.Draw("E1;same")
    
    legend.Draw()

    #CMSTAG  = getCMSInt_tag(x1=0.32, y1=0.86, x2=0.4, y2=0.88)
    lepton_tag_el = leptonjet_tag(lep="el",x1=0.32, y1=0.82, x2=0.4, y2=0.84)
    #year_tag = year_tag(dataYear,x1=0.85, y1=0.92, x2=0.9, y2=0.95)
    CMSTAG.Draw()
    lepton_tag_el.Draw()
    year_tag.Draw()

    can.Print("Plots/"+shape+"_"+dataYear+"_shape_comparision.png")
    can.Print("Plots/"+shape+"_"+dataYear+"_shape_comparision.pdf")
