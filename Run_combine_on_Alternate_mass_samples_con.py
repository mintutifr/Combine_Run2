import fileinput, string, sys, os, time, subprocess
import argparse as arg
import ROOT as rt

parser = arg.ArgumentParser(description='Run Higgs combine Tool')
parser.add_argument('-m', '--mass', dest='mass_sample', default=[None], type=str, nargs=1, help="is Alternate MC top mass sample used ['data','1695', '1715', '1725', '1735', '1755']")
parser.add_argument('-w', '--width', dest='width_sample', default=[None], type=str, nargs=1, help="is Altrnate MC top width sample used ['data','190','170','150','130','090','075']")
#parser.add_argument('-d', '--isdata', dest='isRealData', default=[False], type=bool, nargs=1, help="run over real data ['True', 'False']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018','Run2']")
parser.add_argument('-s', '--sys', dest='sys', default=[''], type=str, nargs=1, help='systematic sample replace the sig and background  ["PSWeight_ISR_Up", "PSWeight_ISR_Down", "PSWeight_FSR_Up", "PSWeight_FSR_Down","hdamp_Up", "hdamp_Down"]')
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
            cmd_createWorkspace_con = "python3 Create_Workspace_con.py -m "+Mass+" -y  "+yearloop
            print(cmd_createWorkspace_con)
            os.system(cmd_createWorkspace_con)
            cmd_createWorkspace = "python3 Create_Workspace.py -m "+Mass+" -y  "+yearloop
            print (cmd_createWorkspace)
            os.system(cmd_createWorkspace)

        cmd_adddatacards = "combineCards.py mujets_UL18=datacard_top_shape_mu_para_UL18.txt eljets_UL18=datacard_top_shape_el_para_UL18.txt mujets_UL17=datacard_top_shape_mu_para_UL17.txt eljets_UL17=datacard_top_shape_el_para_UL17.txt  mujets_ULpre16=datacard_top_shape_mu_para_ULpre16.txt eljets_ULpre16=datacard_top_shape_el_para_ULpre16.txt mujets_ULpost16=datacard_top_shape_mu_para_ULpost16.txt eljets_ULpost16=datacard_top_shape_el_para_ULpost16.txt > datacard_top_shape_comb_para.txt"
    else:
        cmd_createWorkspace_con = "python3 Create_Workspace_con.py -m "+Mass+" -y  "+year #+ " -s " + sys
        print (cmd_createWorkspace_con)
        os.system(cmd_createWorkspace_con)
        cmd_createWorkspace = "python3 Create_Workspace.py -m "+Mass+" -y  "+year #+ " -s " + sys
        print (cmd_createWorkspace)
        os.system(cmd_createWorkspace)

        #cmd_adddatacards = "combineCards.py mujets"+tag+"_con=datacard_top_shape_mu_para"+tag+"_con.txt eljets"+tag+"_con=datacard_top_shape_el_para"+tag+"_con.txt mujets"+tag+"=datacard_top_shape_mu_para"+tag+".txt eljets"+tag+"=datacard_top_shape_el_para"+tag+".txt > datacard_top_shape_comb_para.txt"
        cmd_adddatacards = "combineCards.py mujets"+tag+"_con=datacard_top_shape_mu_para"+tag+"_con.txt eljets"+tag+"_con=datacard_top_shape_el_para"+tag+"_con.txt  > datacard_top_shape_comb_para.txt"


    print("\n",cmd_adddatacards)
    os.system(cmd_adddatacards)
    
    cmd_Runtext2workspace = "text2workspace.py datacard_top_shape_comb_para.txt -o workspace_top_Mass_"+Mass+"_shape_comb_para.root"
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
    


    cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_"+Mass+"_shape_comb_para.root -n _M"+Mass+"  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters mean,sigmaG --trackErrors mean,sigmaG --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --plots  --saveShapes --saveWithUncertainties --saveWorkspace"# --expectSignal 1 -t -1 --saveToys" #--signalPdfNames='shapeSig_top_sig*' --backgroundPdfNames='shapeBkg_EWK_bkg*,shapeBkg_top_bkg*' 
    


    cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_"+Mass+"_shape_comb_para.root -n _M"+Mass+"  --redefineSignalPOIs r,sigmaG,mean  --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters r,mean,sigmaG --trackErrors r,mean,sigmaG --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --saveShapes --saveWithUncertainties"
    
    #cmd_RunCombine = "combine -M FitDiagnostics workspace_top_Mass_"+Mass+"_shape_comb_para.root -n _M"+Mass+"  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --trackParameters mean,sigmaG --trackErrors mean,sigmaG --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0" --plots --saveShapes# -t 10
    
    #cmd_RunCombine = "combine -M MultiDimFit workspace_top_Mass_"+Mass+"_shape_comb_para.root -n _M"+Mass+"  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  -t 10000 --saveToys --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0"
    #--trackParameters mean,sigmaG --trackErrors mean,sigmaG "
    #--ignoreCovWarning"#--plots --saveShapes"#  --backgroundPdfNames=EWK_bkg,top_bkg"#-t 1000 --saveNLL"# --plots --saveShapes"# --saveWithUncertainties "#--plots -v3" 
    #FitDiagnostics
    #MultiDimFit

    print("\n",cmd_RunCombine)
    os.system(cmd_RunCombine)


    

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
    
    cmd_Runtext2workspace = "text2workspace.py datacard_top_shape_comb_para.txt -o workspace_top_width_"+width+"_shape_comb_para.root"
    print("\n",cmd_Runtext2workspace)
    os.system(cmd_Runtext2workspace)
    
    
    cmd_RunCombine = "combine -M FitDiagnostics workspace_top_width_"+width+"_shape_comb_para.root -n _W"+width+"  --freezeParameters r --redefineSignalPOIs sigmaG,mean --setParameters mean=5.1,r=1,sigmaG=0.15  --X-rtd ADDNLL_CBNLL=0  --saveShapes --plots"
    
    print("\n",cmd_RunCombine)
    os.system(cmd_RunCombine)
    
def getparams(mass,width):
    if(mass!=None): fitfile = rt.TFile.Open("fitDiagnostics_M"+mass+".root")
    else : fitfile = rt.TFile.Open("fitDiagnostics_W"+width+".root")
    roofitResults = fitfile.Get("fit_s")

    print
    print("results from one fit_s from ",fitfile.GetName()," file is (do not qoute this results from toy results) : ")

    mean = (roofitResults.floatParsFinal()).find("mean")
    print("mean : ",mean.getVal()," Error : ",mean.getError())

    Sigma = (roofitResults.floatParsFinal()).find("sigmaG")
    print("Sigma : ",Sigma.getVal()," Error : ",Sigma.getError())
    
    r = (roofitResults.floatParsFinal()).find("r")
    print("r : ",r.getVal()," Error : ",r.getError())

#if(len(mass_point)==1 and len(width_point)==0): getparams(mass_point[0],None)
#if(len(mass_point)==0 and len(width_point)==1): getparams(None,width_point[0])
