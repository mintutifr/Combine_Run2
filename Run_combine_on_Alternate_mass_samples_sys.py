import fileinput, string, sys, os, time, subprocess
import argparse as arg
import ROOT as rt
import numpy
from Add_sys_parameter_to_datacard import update_sys_parameters_to_datacard_simultanous_fit
parser = arg.ArgumentParser(description='Run Higgs combine Tool')
parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="is Alternate MC top mass sample used ['data','1695', '1715', '1725', '1735', '1755']")
parser.add_argument('-w', '--width', dest='width_sample', default=[None], type=str, nargs=1, help="is Altrnate MC top width sample used ['data','190','170','150','130','090','075']")
#parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018','Run2']")
parser.add_argument('-s', '--sys', dest='sys', default=[''], type=str, nargs=1, help='systematic sample replace the sig and background  ["top_weight_sys","bWeight", "JES_JER", "lep_SF"]')
args = parser.parse_args()

Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18",
                'Run2' : ""}

mass  = args.mass_sample[0]
width = args.width_sample[0]
year = args.Year[0]
mass_point, mass_points, width_point, width_points = ([] for i in range(4)) 
tag = Combine_year_tag[year]
sys = args.sys[0]

if(mass!=None):
    mass_point = []#,"data"]
    mass_point.append(mass)
    mass_points = ["1695","1715","1725","1735","1755","data"]
if(width != None):
    width_point = []
    width_point.append(width)
    width_points = ['190','170','150','130','090','075']

for Mass in mass_point:
    #scp_file = "scp /home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Create_Workspace.py ."
    #os.system(scp_file)
    if(year=="Run2"):
        for yearloop in ['UL2016preVFP', 'UL2016postVFP','UL2017', 'UL2018']:
            cmd_add_datacards = f"combineCards.py mujets{tag}=datacard_top_shape_mu_para{tag}.txt eljets{tag}=datacard_top_shape_el_para{tag}.txt > datacard_top_shape_comb_para{tag}.txt"
            print("\n",cmd_add_datacards)
            os.system(cmd_add_datacards)
            update_sys_parameters_to_datacard_simultanous_fit(f"datacard_top_shape_comb_para{tag}.txt",sys)
            cmd_createWorkspace = f"python3 Create_Workspace_sys.py -m {Mass} -y  {yearloop} -s {sys}"
            os.system(cmd_createWorkspace)
        #cmd_adddatacards = "combineCards.py mujets_UL18=datacard_top_shape_mu_para_UL18.txt eljets_UL18=datacard_top_shape_el_para_UL18.txt mujets_UL17=datacard_top_shape_mu_para_UL17.txt eljets_UL17=datacard_top_shape_el_para_UL17.txt  mujets_ULpre16=datacard_top_shape_mu_para_ULpre16.txt eljets_ULpre16=datacard_top_shape_el_para_ULpre16.txt mujets_ULpost16=datacard_top_shape_mu_para_ULpost16.txt eljets_ULpost16=datacard_top_shape_el_para_ULpost16.txt > datacard_top_shape_comb_para.txt"
    else:
        cmd_add_datacards = f"combineCards.py mujets{tag}=datacard_top_shape_mu_para{tag}.txt eljets{tag}=datacard_top_shape_el_para{tag}.txt > datacard_top_shape_comb_para{tag}.txt"
        print("\n",cmd_add_datacards)
        os.system(cmd_add_datacards)
        # Update systematic nuisance parameter in datacards
        update_sys_parameters_to_datacard_simultanous_fit(f"datacard_top_shape_comb_para{tag}.txt",sys)
        # crete Workshpace with modified physics model
        cmd_createWorkspace = f"python3 Create_Workspace_sys.py -m {Mass} -y  {year} -s {sys}"
        print(cmd_createWorkspace)
        os.system(cmd_createWorkspace)
    
    cmd_Runtext2workspace = f"env PYTHONNOUSERSITE=1 text2workspace.py datacard_top_shape_comb_para{tag}.txt -o workspace_top_Mass_"+Mass+"_shape_comb_para.root"
    print("\n",cmd_Runtext2workspace)
    os.system(cmd_Runtext2workspace)

    cmd_GoodnessOfFit = "combine -M GoodnessOfFit workspace_top_Mass_"+Mass+"_shape_comb_para.root -n .goodnessOfFit_data --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0 --algo saturated  --expectSignal 1 -m 172.5"
    
    print("\n",cmd_GoodnessOfFit)
    #os.system(cmd_GoodnessOfFit)
    #os.system(cmd_GoodnessOfFit+" -t 1000")
    
    cms_create_json = "combineTool.py -M CollectGoodnessOfFit --input higgsCombine.goodnessOfFit_data.GoodnessOfFit.mH172.5.root higgsCombine.goodnessOfFit_data.GoodnessOfFit.mH172.5.123456.root -m 172.5 -o gof.json"

    print("\n",cms_create_json)
    #os.system(cms_create_json)
    #os.system("plotGof.py gof.json --statistic saturated --mass 172.5 -o part2_gof")
    


    #cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_"+Mass+"_shape_comb_para.root -n _M"+Mass+"  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters mean,sigmaG --trackErrors mean,sigmaG --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --plots  --saveShapes --saveWithUncertainties --saveWorkspace"# --expectSignal 1 -t -1 --saveToys" #--signalPdfNames='shapeSig_top_sig*' --backgroundPdfNames='shapeBkg_EWK_bkg*,shapeBkg_top_bkg*' 
    


    cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_"+Mass+"_shape_comb_para.root -n _M"+Mass+"  --redefineSignalPOIs sigmaG,mean  --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.08,5.12:sigmaG=0.10,0.12 --freezeParameters  r  --X-rtd ADDNLL_CBNLL=0  --trackParameters r,mean,sigmaG --trackErrors r,mean,sigmaG --X-rtd TMCSO_PseudoAsimov=0 --saveShapes --saveWithUncertainties --saveWorkspace --plots" #-t -1 --saveToys"# --plots"
    print("\n",cmd_RunCombine)
    os.system(cmd_RunCombine)

    # MultiDimFit for stat with fix mean
    #print("\n=================       runnig MultiDimFit     ======================== \n")
    cmd_RunCombine = "combine -M MultiDimFit workspace_top_Mass_"+Mass+"_shape_comb_para.root -m 125  --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1023,r=1,sigmaG=0.114 --setParameterRanges mean=5.08,5.12:sigmaG=0.10,0.12 --freezeParameters  r -n .scanformean.with_syst.statonly --algo grid --points 20     --X-rtd ADDNLL_CBNLL=0"
    #print("\n",cmd_RunCombine)
    #os.system(cmd_RunCombine)

    # MultiDimFit for syst with fix mean
    cmd_RunCombine = "combine -M MultiDimFit workspace_top_Mass_"+Mass+"_shape_comb_para.root  -m 125 --redefineSignalPOIs mean  --setParameters mean=5.1023,r=1,sigmaG=0.114   --setParameterRanges mean=5.08,5.12 --freezeParameters r,sigmaG -n .scanformean.with_syst --algo grid --points 20  --X-rtd ADDNLL_CBNLL=0"
    print("\n",cmd_RunCombine)
    #os.system(cmd_RunCombine)

    #plot scan
    #print("\n=================       scan plot     ======================== \n")
    cms_scan_ploting = 'plot1DScan.py higgsCombine.scanformean.with_syst.MultiDimFit.mH125.root --main-label "With systematics" --main-color 1 --others higgsCombine.scanformean.with_syst.statonly.MultiDimFit.mH125.root:"Stat-only":2 -o Plots/mean_scan --POI mean'
    cms_scan_ploting = 'plot1DScan.py higgsCombine.scanformean.with_syst.statonly.MultiDimFit.mH125.root --main-label "With systematics" --main-color 1  -o Plots/mean_scan --POI sigmaG  --y-max 3'
    #os.system(cms_scan_ploting)

    #MultiDimFit for stat with fix sigma
    cmd_RunCombine = "combine -M MultiDimFit workspace_top_Mass_"+Mass+"_shape_comb_para.root -m 125 --redefineSignalPOIs sigmaG --setParameters mean=5.1023,r=1,sigmaG=0.114 --setParameterRanges sigmaG=0.123,0.126 --freezeParameters  r,mean,allConstrainedNuisances -n .scanforSigma.with_syst.statonly --algo grid --points 20 --setParameterRanges sigmaG=0.123,0.126 --setParameters mean=5.1023,r=1,sigmaG=0.114 --redefineSignalPOIs sigmaG  --X-rtd ADDNLL_CBNLL=0"
    #print("\n",cmd_RunCombine)
    #os.system(cmd_RunCombine)

    #MultiDimFit for syst with fix Sigma
    cmd_RunCombine = "combine -M MultiDimFit workspace_top_Mass_"+Mass+"_shape_comb_para.root  -m 125 --freezeParameters r,sigmaG -n .scanforSigma.with_syst --algo grid --points 20 --setParameterRanges sigmaG=0.10,0.12 --setParameters mean=5.1023,r=1,sigmaG=0.114 --redefineSignalPOIs sigmaG  --X-rtd ADDNLL_CBNLL=0"
    #print("\n",cmd_RunCombine)
    #os.system(cmd_RunCombine)

    #plot scan
    cms_scan_ploting = 'plot1DScan.py higgsCombine.scanforSigma.with_syst.MultiDimFit.mH125.root --main-label "With systematics" --main-color 1 --others higgsCombine.scanforSigma.with_syst.statonly.MultiDimFit.mH125.root:"Stat-only":2 -o Plots/Sigma_scan --POI sigmaG'
    #print("\n",cms_scan_ploting)
    #os.system(cms_scan_ploting)

    # Plot impact Plots
    cmd_diffNuisances = "python3 diffNuisances.py fitDiagnostics_M"+mass+".root -a -g higgsCombine_M"+mass+"_"+year+".FitDiagnostics_nuisance.mH120.root "
    print("\n",cmd_diffNuisances)
    #os.system(cmd_diffNuisances)

    #for likelihood scans when using robustFit 1
    cmd_Impact_doInitialFit = "combineTool.py -M Impacts -d workspace_top_Mass_"+Mass+"_shape_comb_para.root -m 172.5   -n _M"+Mass+"_InitialFit --redefineSignalPOIs mean,sigmaG  --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.08,5.12:sigmaG=0.10,0.12 --freezeParameters r  --X-rtd ADDNLL_CBNLL=0 --robustFit 1 --doInitialFit" 
    print("\n =====  doInitialFit   ",cmd_Impact_doInitialFit,"    ====\n")
    os.system(cmd_Impact_doInitialFit)

    #nuisance parameter with the --doFits and -o impacts_mtop_"+year+".json options
    cmd_Impact_doFit = "combineTool.py -M Impacts -d workspace_top_Mass_"+Mass+"_shape_comb_para.root -m 172.5 -n _M"+Mass+"_InitialFit  --redefineSignalPOIs mean,sigmaG --setParameters mean=5.1,r=1,sigmaG=0.11  --setParameterRanges mean=5.08,5.12:sigmaG=0.10,0.12 --freezeParameters r --X-rtd ADDNLL_CBNLL=0 --robustFit 1 --doFits -o impacts_mtop_"+year+".json"
    print("\n =====  doFit   ",cmd_Impact_doFit,"    ====\n")
    os.system(cmd_Impact_doFit)

    cmd_Impact_json = "combineTool.py -M Impacts -d workspace_top_Mass_"+Mass+"_shape_comb_para.root -m 172.5  -n _M"+Mass+"_InitialFit --redefineSignalPOIs mean,sigmaG --setParameters mean=5.1,r=1,sigmaG=0.11 --setParameterRanges mean=5.08,5.12:sigmaG=0.10,0.12  --freezeParameters r --X-rtd ADDNLL_CBNLL=0  -o impacts_mtop_"+year+".json"  #--named r, bWeight_lf, bWeight_hf , bWeight_cferr1, bWeight_cferr2, bWeight_lfstats1, bWeight_lfstats2, bWeight_hfstats1, bWeight_hfstats2, bWeight_jes"
    print("\n =====  save json   ",cmd_Impact_json,"    ====\n")
    os.system(cmd_Impact_json)

    cmd_Impact_plot = "plotImpacts.py -i impacts_mtop_"+year+".json -o impacts_mtop_"+year
    print("\n",cmd_Impact_plot)
    os.system(cmd_Impact_plot)
    

for width in width_point:
    #scp_file = "scp /home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Create_Workspace.py ."
    #os.system(scp_file)
    if(year=="Run2"):
        for yearloop in ['UL2016preVFP', 'UL2016postVFP','UL2017', 'UL2018']:
            cmd_createWorkspace = "python3 Create_Workspace.py -m "+width+" -y  "+yearloop
            os.system(cmd_createWorkspace)
        cmd_adddatacards = "combineCards.py mujets_UL18=datacard_top_shape_mu_para_UL18.txt eljets_UL18=datacard_top_shape_el_para_UL18.txt mujets_UL17=datacard_top_shape_mu_para_UL17.txt eljets_UL17=datacard_top_shape_el_para_UL17.txt  mujets_ULpre16=datacard_top_shape_mu_para_ULpre16.txt eljets_ULpre16=datacard_top_shape_el_para_ULpre16.txt mujets_ULpost16=datacard_top_shape_mu_para_ULpost16.txt eljets_ULpost16=datacard_top_shape_el_para_ULpost16.txt > datacard_top_shape_comb_para.txt"
    else:
        cmd_createWorkspace = "python3 Create_Workspace.py -w "+width+" -y  "+year
        print(cmd_createWorkspace)
        os.system(cmd_createWorkspace)
        cmd_adddatacards = "combineCards.py mujets"+tag+"=datacard_top_shape_mu_para"+tag+".txt eljets"+tag+"=datacard_top_shape_el_para"+tag+".txt > datacard_top_shape_comb_para.txt"

    print("\n",cmd_adddatacards)
    os.system(cmd_adddatacards)
    
    cmd_Runtext2workspace = "env PYTHONNOUSERSITE=1 text2workspace.py datacard_top_shape_comb_para.txt -o workspace_top_width_"+width+"_shape_comb_para.root"
    print("\n",cmd_Runtext2workspace)
    os.system(cmd_Runtext2workspace)
    
    
    #cmd_RunCombine = "combine -M FitDiagnostics workspace_top_width_"+width+"_shape_comb_para.root -n _W"+width+"  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --saveShapes --plots"
    cmd_RunCombine = "combine -M FitDiagnostics workspace_top_width_"+width+"_shape_comb_para.root -n _W"+width+"   --redefineSignalPOIs sigmaG,mean  --setParameters mean=5.1,r=1,sigmaG=0.15 --freezeParameters r  --X-rtd ADDNLL_CBNLL=0  --trackParameters r,mean,sigmaG --trackErrors r,mean,sigmaG --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0  --saveShapes --saveWithUncertainties --saveWorkspace" #--plots

    print("\n",cmd_RunCombine)
    os.system(cmd_RunCombine)
    
def getparams(mass,width,parms=[]):
    if(mass!=None): fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
    else : fitfile = rt.TFile.Open("fitDiagnostics_W"+width+".root")
    roofitResults = fitfile.Get("fit_s")

    print
    print("results from one fit_s from ",fitfile.GetName()," file is (do not qoute this results from toy results) : ")

    for par in parms:
       var = (roofitResults.floatParsFinal()).find(par)
       print(par," : ",var.getVal()," Error : ",var.getError())
       
