import fileinput, string, sys, os, time, subprocess
import argparse as arg
import ROOT as rt

parser = arg.ArgumentParser(description='Run Higgs combine Tool')
parser.add_argument('-l', '--lepton', dest='lepton_flavour', default=["mu"], type=str, nargs=1, help="Fit has to fromed for lepton flavour ['el','mu']")
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018']")
args = parser.parse_args()

lep  = args.lepton_flavour[0]
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

Datacard = "datacard_DNN_hist_"+lep+".txt"
update_rootfile = "shapes * "+lep+"jets /home/mikumar/t3store3/workarea/Nanoaod_tools/CMSSW_10_2_28/src/PhysicsTools/NanoAODTools/crab/WorkSpace/Hist_for_workspace/Combine_DNNFit_Input_t_ch_CAsi_histograms_"+year+"_"+lep+".root "+lep+"jets/$PROCESS "+lep+"jets/$PROCESS_$SYSTEMATIC"+"\n"
print "\tshape are used from Root File: ",update_rootfile

replacemachine(Datacard,'shapes', update_rootfile)


cmd_Runtext2workspace = "text2workspace.py datacard_DNN_hist_"+lep+".txt -m 172.5 -o workspace_DNN_"+lep+"_"+year+".root"
print "\n",cmd_Runtext2workspace
#os.system(cmd_Runtext2workspace)

cmd_RunCombine = "combine -M FitDiagnostics workspace_DNN_"+lep+"_"+year+".root --rMin -2 --rMax 2 -n _M1725_DNNfit_"+lep+"_"+year+" --plots --saveShapes --algo impact"
print "\n",cmd_RunCombine
os.system(cmd_RunCombine)

cms_diffNuisances = "python diffNuisances.py fitDiagnostics_M1725_DNNfit_"+lep+"_"+year+".root -a -g higgsCombine_M1725_DNNfit_"+lep+"_"+year+".FitDiagnostics.mH120.root"
print "\n",cms_diffNuisances
os.system(cms_diffNuisances)
