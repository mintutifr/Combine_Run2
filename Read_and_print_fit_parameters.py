import json, os
import ROOT as R
from ROOT import RooFit 
import sys, datetime
import argparse as arg

def get_paramters(tag,mass,width):
    
    if(mass and width):
        print("Both mass and width should not provided")
        exit(1)
    mass_or_decay_width =f'{mass}'
    if(width != None): mass_or_decay_width = f'{width}'
    print(mass_or_decay_width)

    fitfile = R.TFile.Open(f"fitDiagnostics_M{mass_or_decay_width}{tag}.root")
    roofitResults = fitfile.Get("fit_s")

    print(f"\nresults from one fit_s from {fitfile.GetName()}")

    Mean = (roofitResults.floatParsFinal()).find("mean")
    SigmaG = (roofitResults.floatParsFinal()).find("sigmaG")

    mean_fit = {}
    sigmaG_fit = {}

    mean_fit["mean"] = [Mean.getVal(), Mean.getError()]
    try:
        sigmaG_fit["sigmaG"] = [SigmaG.getVal(), SigmaG.getError()]
    except:
        sigmaG_fit["sigmaG"] = [-999, -999]
    return mean_fit, sigmaG_fit

if __name__ == "__main__":
    parser = arg.ArgumentParser(description='Create workspace for higgs combine')
    parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="MC top mass sample [data , 1695, 1715, 1735, 1755]")
    parser.add_argument('-w', '--width', dest='width_sample', default=[None], type=str, nargs=1, help="MC top width sample ['data','190', '170', '150','130','090','075']")
    parser.add_argument('-y', '--year', dest='Year', default=['UL2017'], type=str, nargs=1, help="Year of Data collection [ UL2016preVFP  UL2016postVFP  UL2017  UL2018 ]")
    args = parser.parse_args()

    Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18",
                "Run2":""
                }

    mass  = args.mass_sample[0]
    width = args.width_sample[0]
    year = args.Year[0]
    tag = Combine_year_tag[year]
    print(tag)

    
    mean_fit,sigmaG_fit = get_paramters(tag,mass,width)
    print("\n=====================================")
    print("Fit results : mean = %.5f +- %.5f GeV, sigmaG = %.5f +- %.5f GeV"%(mean_fit['mean'][0],mean_fit['mean'][1],sigmaG_fit['sigmaG'][0],sigmaG_fit['sigmaG'][1]))
    print("=====================================\n")
