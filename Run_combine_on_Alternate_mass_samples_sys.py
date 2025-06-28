import fileinput, string, sys, os, time, subprocess
import argparse as arg
import ROOT as rt
import numpy
import time
from Read_and_print_fit_parameters import get_paramters
from Add_sys_parameter_to_datacard import update_sys_parameters_to_datacard_simultanous_fit
parser = arg.ArgumentParser(description='Run Higgs combine Tool')
parser.add_argument('-mOw', '--massORwidth', dest='massORwidth_sample', default=[None], type=str, nargs=1, help="is Alternate MC top mass or width sample used ['data','1695', '1715', '1725', '1735', '1755', '190','170','150','130','090','075]")
#parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018','Run2']")
parser.add_argument('-s', '--sys', dest='sys', default=[''], type=str, nargs=1, help='systematic sample replace the sig and background  ["top_weight_sys","bWeight", "JES_JER", "lep_SF"]')
args = parser.parse_args()

import csv
from datetime import datetime
import os

def write_fit_results_to_csv(filename, Datayear, True_massORwidth, mean_fit_list, sigmaG_fit_list):
    """
    Appends fit results to a CSV file with columns:
    Date, Mean(GeV), Uncertainty(GeV), SigmaG(GeV), Uncertainty(GeV)
    
    Parameters:
    - filename: str, output CSV file
    - mean_fit_list: list [mean_value, mean_uncertainty]
    - sigmaG_fit_list: list [sigmaG_value, sigmaG_uncertainty]
    """
    from datetime import datetime
    import os
    import csv

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        timestamp,
        Datayear,
        True_massORwidth,
        mean_fit_list[0],
        mean_fit_list[1],
        sigmaG_fit_list[0],
        sigmaG_fit_list[1]
    ]

    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Datayear", "True_massORwidth","Mean(GeV)", "Uncertainty(GeV)", "SigmaG(GeV)", "Uncertainty(GeV)"])
        writer.writerow(row)

    print(f"Appended result to {filename}")

def getparams(massORwidth,parms=[]):
    fitfile = rt.TFile.Open("fitDiagnostics_MoW_"+massORwidth+".root")
    roofitResults = fitfile.Get("fit_s")

    print
    print("results from one fit_s from ",fitfile.GetName()," file is (do not qoute this results from toy results) : ")

    for par in parms:
       var = (roofitResults.floatParsFinal()).find(par)
       print(par," : ",var.getVal()," Error : ",var.getError())


Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18",
                'UL2016' : "_UL16",
                'Run2' : ""}

massORwidth  = args.massORwidth_sample[0]
year = args.Year[0]
massORwidth_points= []
massORwidth_points.append(massORwidth)
tag = Combine_year_tag[year]
sys = args.sys[0]

def run_cmd(command = "root -l -q"):
    exit_code = os.system(command)
    if exit_code != 0:
        print(f"\n ERROR: {command} failed with exit code: {exit_code}. Please try running the command locally.")
        exit(0)

if(massORwidth=="ALL"):
    massORwidth_points = ["1695","1705","1715","1725","1735","1745","1755", '075', '090','110','130','1725','150','170','190']


for MoW in massORwidth_points:
    #scp_file = "scp /home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Create_Workspace.py ."
    #os.system(scp_file)
    
    if(year=="Run2"):
        for subyear in ['UL2016','UL2017', 'UL2018']: #'UL2016preVFP', 'UL2016postVFP'
            subtag = Combine_year_tag[subyear]
            cmd_add_datacards = f"combineCards.py mujets{subtag}=datacards/datacard_top_shape_mu_para{subtag}.txt eljets{subtag}=datacards/datacard_top_shape_el_para{subtag}.txt > datacard_top_shape_comb_para{subtag}.txt"
            print("\n",cmd_add_datacards)
            run_cmd(cmd_add_datacards)
            # Update systematic nuisance parameter in datacards
            update_sys_parameters_to_datacard_simultanous_fit(f"datacard_top_shape_comb_para{subtag}.txt",sys,subyear)
            # crete Workshpace with modified physics model
            
            cmd_createWorkspace = f"python3 Create_Workspace_sys.py -mOw {MoW} -y  {subyear} -s {sys}"
            print(cmd_createWorkspace)
            run_cmd(cmd_createWorkspace)
        #cmd_add_datacards = f"combineCards.py _UL18=datacard_top_shape_comb_para_UL18.txt _UL17=datacard_top_shape_comb_para_UL17.txt _UL16preVFP=datacard_top_shape_comb_para_ULpre16.txt _UL16postVFP=datacard_top_shape_comb_para_ULpost16.txt > datacard_top_shape_comb_para.txt"
        cmd_add_datacards = f"combineCards.py _UL18=datacard_top_shape_comb_para_UL18.txt _UL17=datacard_top_shape_comb_para_UL17.txt _UL16=datacard_top_shape_comb_para_UL16.txt > datacard_top_shape_comb_para.txt"
        print(cmd_add_datacards)
        run_cmd(cmd_add_datacards)
    else:
        cmd_add_datacards = f"combineCards.py mujets{tag}=datacards/datacard_top_shape_mu_para{tag}.txt eljets{tag}=datacards/datacard_top_shape_el_para{tag}.txt > datacard_top_shape_comb_para{tag}.txt"
        print("\n",cmd_add_datacards)
        run_cmd(cmd_add_datacards)
        # Update systematic nuisance parameter in datacards
        update_sys_parameters_to_datacard_simultanous_fit(f"datacard_top_shape_comb_para{tag}.txt",sys,year)
        # crete Workshpace with modified physics model
        
        cmd_createWorkspace = f"python3 Create_Workspace_sys.py -mOw {MoW} -y  {year} -s {sys}"
        print(cmd_createWorkspace)
        run_cmd(cmd_createWorkspace)

    cmd_Runtext2workspace = f"env PYTHONNOUSERSITE=1 text2workspace.py datacard_top_shape_comb_para{tag}.txt -o workspace_top_MoW_{MoW}_shape_comb_para{tag}.root"
    print("\n",cmd_Runtext2workspace)
    run_cmd(cmd_Runtext2workspace)

    #cmd_RunCombine = f"combine -M FitDiagnostics workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -n _M{MoW}  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters mean,sigmaG --trackErrors mean,sigmaG --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --plots  --saveShapes --saveWithUncertainties --saveWorkspace"# --expectSignal 1 -t -1 --saveToys" #--signalPdfNames='shapeSig_top_sig*' --backgroundPdfNames='shapeBkg_EWK_bkg*,shapeBkg_top_bkg*' 
    cmd_RunCombine = f"combine -M FitDiagnostics workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -n _MoW{MoW}{tag}  --redefineSignalPOIs mean,sigmaG  --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7  --X-rtd ADDNLL_CBNLL=0  --trackParameters r,mean,sigmaG --trackErrors r,mean,sigmaG --X-rtd TMCSO_PseudoAsimov=0 --saveShapes --saveWithUncertainties --saveWorkspace --freezeParameters  r --plots" #-t -1 --saveToys"# --plots"
    #cmd_RunCombine_freeze_nuisance = f"combine -M FitDiagnostics workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -n _MoW{MoW}{tag}  --redefineSignalPOIs mean,sigmaG  --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7  --X-rtd ADDNLL_CBNLL=0  --trackParameters r,mean,sigmaG --trackErrors r,mean,sigmaG --X-rtd TMCSO_PseudoAsimov=0 --saveShapes --saveWithUncertainties --saveWorkspace  --freezeParameters r,rgx{nuisance_.*},rgx{CMS_.*},rgx{lumi_.*},rgx{x-sec.*}"
    run_cmd(cmd_RunCombine)
    print(cmd_RunCombine)
    
    mean_fit,sigmaG_fit = get_paramters(tag,MoW)
    print("\n=====================================")
    print("Fit results : mean = %.5f +- %.5f GeV, sigmaG = %.5f +- %.5f GeV"%(mean_fit['mean'][0],mean_fit['mean'][1],sigmaG_fit['sigmaG'][0],sigmaG_fit['sigmaG'][1]))
    print("=====================================\n")

    write_fit_results_to_csv("Fit_results.CSV",year,MoW, mean_fit['mean'], sigmaG_fit['sigmaG'])

    if(sys != "Nomi"):
        #for likelihood scans when using robustFit 1
        cmd_doInitialFit = f"combineTool.py -M Impacts -d workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -m {MoW}   -n _MoW{MoW}{tag}_Impacts --redefineSignalPOIs mean,sigmaG  --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7 --freezeParameters r  --X-rtd ADDNLL_CBNLL=0 --robustFit 1 --doInitialFit" 
        print("\n =====  doInitialFit   ",cmd_doInitialFit,"    ====\n")
        run_cmd(cmd_doInitialFit)


        #nuisance parameter with the --doFits and -o impacts_mtop_"+year+".json options
        cmd_Impact_doFit = f"combineTool.py -M Impacts -d workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -m {MoW} -n _MoW{MoW}{tag}_Impacts  --redefineSignalPOIs mean,sigmaG --setParameters mean=5.1,r=1,sigmaG=0.11  --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7 --freezeParameters r --X-rtd ADDNLL_CBNLL=0 --robustFit 1 --doFits -o impacts_mtop_{year}.json"
        print("\n =====  do Impact Fits   ",cmd_Impact_doFit,"    ====\n")
        run_cmd(cmd_Impact_doFit)


        cmd_Impact_json = f"combineTool.py -M Impacts -d workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -m {MoW}  -n _MoW{MoW}{tag}_Impacts --redefineSignalPOIs mean,sigmaG --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7  --freezeParameters r --X-rtd ADDNLL_CBNLL=0  -o impacts_mtop_{year}.json  --exclude r"  #--named r, bWeight_lf, bWeight_hf , bWeight_cferr1, bWeight_cferr2, bWeight_lfstats1, bWeight_lfstats2, bWeight_hfstats1, bWeight_hfstats2, bWeight_jes"
        print("\n =====  save json   ",cmd_Impact_json,"    ====\n")
        run_cmd(cmd_Impact_json)

        # impact Plot for Mean
        cmd_Impact_plot = f"plotImpacts.py -i impacts_mtop_{year}.json -o impacts_mtop_{year}_mean --POI mean"
        print("\n",cmd_Impact_plot)
        run_cmd(cmd_Impact_plot)

        # impact Plot for SigmaG
        cmd_Impact_plot = f"plotImpacts.py -i impacts_mtop_{year}.json -o impacts_mtop_{year}_sigmaG --POI sigmaG"
        print("\n",cmd_Impact_plot)
        run_cmd(cmd_Impact_plot)
    


#     if (sys=="Tried before"):
#         cmd_GoodnessOfFit = f"combine -M GoodnessOfFit workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -n .goodnessOfFit_data --freezeParameters r --redefineSignalPOIs mean,sigmaG --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0 --algo saturated  --expectSignal 1 -m {MoW}"
#         #print("\n",cmd_GoodnessOfFit)
#         #os.system(cmd_GoodnessOfFit)
#         #os.system(cmd_GoodnessOfFit+" -t 1000")
        
#         cms_create_json = f"combineTool.py -M CollectGoodnessOfFit --input higgsCombine.goodnessOfFit_data.GoodnessOfFit.mH172.5.root higgsCombine.goodnessOfFit_data.GoodnessOfFit.mH172.5.123456.root -m {MoW} -o gof.json"
#         #print("\n",cms_create_json)
#         #os.system(cms_create_json)
#         #os.system("plotGof.py gof.json --statistic saturated --MoW 172.5 -o part2_gof")
        
#         # MultiDimFit for stat with fix mean
#         #print("\n=================       runnig MultiDimFit     ======================== \n")
#         cmd_RunCombine = f"combine -M MultiDimFit workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -m {MoW}  --redefineSignalPOIs mean,sigmaG --setParameters mean=5.1023,r=1,sigmaG=0.114 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7 --freezeParameters  r -n .scanformean.with_syst.statonly --algo grid --points 20     --X-rtd ADDNLL_CBNLL=0"
#         #print("\n",cmd_RunCombine)
#         #os.system(cmd_RunCombine)

#         # MultiDimFit for syst with fix mean
#         cmd_RunCombine = f"combine -M MultiDimFit workspace_top_MoW_{MoW}_shape_comb_para{tag}.root  -m {MoW} --redefineSignalPOIs mean  --setParameters mean=5.1023,r=1,sigmaG=0.114   --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7 --freezeParameters r,sigmaG -n .scanformean.with_syst --algo grid --points 20  --X-rtd ADDNLL_CBNLL=0"
#         #print("\n",cmd_RunCombine)
#         #os.system(cmd_RunCombine)

#         #plot scan
#         #print("\n=================       scan plot     ======================== \n")
#         cms_scan_ploting = 'plot1DScan.py higgsCombine.scanformean.with_syst.MultiDimFit.mH125.root --main-label "With systematics" --main-color 1 --others higgsCombine.scanformean.with_syst.statonly.MultiDimFit.mH125.root:"Stat-only":2 -o Plots/mean_scan --POI mean'
#         cms_scan_ploting = 'plot1DScan.py higgsCombine.scanformean.with_syst.statonly.MultiDimFit.mH125.root --main-label "With systematics" --main-color 1  -o Plots/mean_scan --POI sigmaG  --y-max 3'
#         #os.system(cms_scan_ploting)

#         #MultiDimFit for stat with fix sigma
#         cmd_RunCombine = f"combine -M MultiDimFit workspace_top_MoW_{MoW}_shape_comb_para{tag}.root -m {MoW} --redefineSignalPOIs sigmaG --setParameters mean=5.1023,r=1,sigmaG=0.114 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7 --freezeParameters  r,mean,allConstrainedNuisances -n .scanforSigma.with_syst.statonly --algo grid --points 20 --setParameterRanges sigmaG=0.123,0.126 --setParameters mean=5.1023,r=1,sigmaG=0.114 --redefineSignalPOIs sigmaG  --X-rtd ADDNLL_CBNLL=0"
#         #print("\n",cmd_RunCombine)
#         #os.system(cmd_RunCombine)

#         #MultiDimFit for syst with fix Sigma
#         cmd_RunCombine = f"combine -M MultiDimFit workspace_top_MoW_{MoW}_shape_comb_para{tag}.root  -m {MoW} --freezeParameters r,sigmaG -n .scanforSigma.with_syst --algo grid --points 20 --setParameterRanges mean=5.0,5.3:sigmaG=0.05,0.7 --setParameters mean=5.1023,r=1,sigmaG=0.114 --redefineSignalPOIs sigmaG  --X-rtd ADDNLL_CBNLL=0"
#         #print("\n",cmd_RunCombine)
#         #os.system(cmd_RunCombine)

#         #plot scan
#         cms_scan_ploting = 'plot1DScan.py higgsCombine.scanforSigma.with_syst.MultiDimFit.mH125.root --main-label "With systematics" --main-color 1 --others higgsCombine.scanforSigma.with_syst.statonly.MultiDimFit.mH125.root:"Stat-only":2 -o Plots/Sigma_scan --POI sigmaG'
#         #print("\n",cms_scan_ploting)
#         #os.system(cms_scan_ploting)

#         # Plot impact Plots
#         cmd_diffNuisances = f"python3 diffNuisances.py fitDiagnostics_MoW{MoW}.root -a -g higgsCombine_MoW{MoW}_{year}.FitDiagnostics_nuisance.mH120.root "
#         #print("\n",cmd_diffNuisances)
#         #os.system(cmd_diffNuisances)
        