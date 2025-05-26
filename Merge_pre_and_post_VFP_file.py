#!/usr/bin/env python3
"""
Script to combine UL2016 pre- and post-VFP histograms into UL16 sums.
It reads two ROOT files with a "mujets" directory, sums matching histograms,
and writes the results into a new ROOT file under "mujets/".
"""
import ROOT
import sys
import argparse as arg
#from TOY_local_fit import Toy_Mc 
parser = arg.ArgumentParser(description='Create workspace for higgs combine')
parser.add_argument('-l', '--lep', dest='Lep', default=['mu'], type=str, nargs=1, help="lepton flavour[ mu  el]")
args = parser.parse_args()

        

lep = args.Lep[0]


#--- User settings: update these file names as needed
file_pre  = f"../Hist_for_workspace/Combine_Input_lntopMass_histograms_UL2016preVFP_{lep}_gteq0p7_withoutDNNfit_rebin.root"
file_post = f"../Hist_for_workspace/Combine_Input_lntopMass_histograms_UL2016postVFP_{lep}_gteq0p7_withoutDNNfit_rebin.root"
out_file  = f"../Hist_for_workspace/Combine_Input_lntopMass_histograms_UL2016_{lep}_gteq0p7_withoutDNNfit_rebin.root"

#--- Open input ROOT files
f_pre  = ROOT.TFile.Open(file_pre,  "READ")
if not f_pre or f_pre.IsZombie():
    sys.exit(f"Error: cannot open pre-VFP file '{file_pre}'")
f_post = ROOT.TFile.Open(file_post, "READ")
if not f_post or f_post.IsZombie():
    sys.exit(f"Error: cannot open post-VFP file '{file_post}'")

#--- Create output file and mujets directory
f_out = ROOT.TFile.Open(out_file, "RECREATE")
f_out.mkdir(f"{lep}jets")
out_dir = f_out.Get(f"{lep}jets")

#--- Get the input directories
pre_dir  = f_pre.GetDirectory(f"{lep}jets")
post_dir = f_post.GetDirectory(f"{lep}jets")

#--- Loop over all histograms in the pre-VFP directory and combine ULpre16 → UL16
for key in pre_dir.GetListOfKeys():
    name_pre = key.GetName()
    # only process histograms tagged ULpre16
    if "ULpre16" not in name_pre:
        continue

    # find the matching post-VFP histogram
    name_post = name_pre.replace("ULpre16", "ULpost16")
    h_pre  = pre_dir.Get(name_pre)
    h_post = post_dir.Get(name_post)

    if not h_post:
        print(f"Warning: no matching post-VFP histogram for '{name_pre}'")
        continue

    # clone the pre histogram, rename it to UL16
    new_name = name_pre.replace("ULpre16", "UL16")
    h_sum = h_pre.Clone(new_name)
    h_sum.SetDirectory(0)     # detach from original file

    # sum histograms
    h_sum.Add(h_post)

    # write into output lepjets directory
    out_dir.cd()
    h_sum.Write()

#--- Also combine the special 'data_obs' histogram (no UL tag)
h_pre_data  = pre_dir.Get("data_obs")
h_post_data = post_dir.Get("data_obs")
if h_pre_data and h_post_data:
    # clone with the same name
    h_data_sum = h_pre_data.Clone("data_obs")
    h_data_sum.SetDirectory(0)
    h_data_sum.Add(h_post_data)
    out_dir.cd()
    h_data_sum.Write()
else:
    print("Warning: 'data_obs' histogram missing in one of the inputs")

#--- Clean up and close files
f_out.Close()
f_pre.Close()
f_post.Close()

print(f"Combined histograms written to '{out_file}' under directory '{lep}jets/'.")