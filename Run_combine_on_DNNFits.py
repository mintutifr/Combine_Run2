import fileinput, string, sys, os, time, subprocess
import argparse as arg
import ROOT as rt

parser = arg.ArgumentParser(description='Run Higgs combine Tool')
#parser.add_argument('-l', '--lepton', dest='lepton_flavour', default=["mu"], type=str, nargs=1, help="Fit has to fromed for lepton flavour ['el','mu']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018']")
args = parser.parse_args()

#lep  = args.lepton_flavour[0]
year = args.Year[0]

def replacemachine(fileName, sourceText, replaceText):
    print "editing ",fileName,
    ##################################################################
    for line in fileinput.input(fileName, inplace=True):
        if line.strip().startswith(sourceText):
                line = replaceText
        sys.stdout.write(line)
    print "All went well, the modifications are done"
    ##################################################################

for lep in ["mu","el"]:
        Datacard = "datacard_DNN_hist_"+lep+"_"+year+".txt"
        update_rootfile = "shapes * "+lep+"jets /home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_DNNFit_Input_t_ch_CAsi_histograms_"+year+"_"+lep+"_Nomi.root "+lep+"jets/$PROCESS "+lep+"jets/$PROCESS_$SYSTEMATIC"+"\n"
        print "\tshape are used from Root File: ",update_rootfile

        replacemachine(Datacard,'shapes', update_rootfile)


cmd_adddatacards = "combineCards.py mujets=datacard_DNN_hist_mu_"+year+".txt eljets=datacard_DNN_hist_el_"+year+".txt > Combine_datacard_DNN_"+year+".txt"
print "\n",cmd_adddatacards
os.system(cmd_adddatacards)

cmd_Runtext2workspace = "text2workspace.py Combine_datacard_DNN_"+year+".txt -m 172.5 -o workspace_DNN_"+year+".root"
print "\n",cmd_Runtext2workspace
os.system(cmd_Runtext2workspace)

cmd_RunCombine = "combine -M FitDiagnostics workspace_DNN_"+year+".root --rMin -2 --rMax 2 -n _M1725_DNNfit_"+year+" --saveShapes " #--plots
print "\n",cmd_RunCombine
os.system(cmd_RunCombine)

cmd_diffNuisances = "python diffNuisances.py fitDiagnostics_M1725_DNNfit_"+year+".root -a -g higgsCombine_M1725_DNNfit_"+year+".FitDiagnostics_nuisance.mH120.root"
print "\n",cmd_diffNuisances
os.system(cmd_diffNuisances)

cmd_Impact_doInitialFit = "combineTool.py -M Impacts -d workspace_DNN_"+year+".root -m 172.5 --doInitialFit --robustFit 1"   #for likelihood scans when using robustFit 1
print "\n",cmd_Impact_doInitialFit
os.system(cmd_Impact_doInitialFit)

cmd_Impact_doFit = "combineTool.py -M Impacts -d workspace_DNN_"+year+".root -m 172.5 --robustFit 1 --doFits"   #nuisance parameter with the --doFits options
print "\n",cmd_Impact_doFit
os.system(cmd_Impact_doFit)

cmd_Impact_json = "combineTool.py -M Impacts -d workspace_DNN_"+year+".root -m 172.5 -o impacts_DNN_"+year+".json"
print "\n",cmd_Impact_json
os.system(cmd_Impact_json)

cmd_Impact_plot = "plotImpacts.py -i impacts_DNN_"+year+".json -o impacts_DNN_"+year
print "\n",cmd_Impact_plot
os.system(cmd_Impact_plot)
