#!/bin/bash

# Define the arrays
YEARS=("UL2018") # "UL2017" "UL2016preVFP" "UL2016postVFP")
LEP=("el" "mu")
Sys=("JES_JER")

# Loop through each combination
# for year in "${YEARS[@]}"; do
#     for lepton in "${LEP[@]}"; do
#         echo "Running for Year: $year, Lepton: $lepton"
#         python3 Compiare_shapes_and_getRation_sys_hists.py -y "$year" -l "$lepton" &> "sys_hist_Integral_ratios/sys_ratio_${lepton}_${year}.txt"
#     done
# done

for year in "${YEARS[@]}"; do
    echo "Running for Year: $year"
    # Pull the systematic comparision plots
    # python3 Compaire_shapes_and_getRation_sys_hists.py -y "$year" -l mu
    # python3 Compaire_shapes_and_getRation_sys_hists.py -y "$year" -l el
    # estimate the davation im mean and isgma due to systematic samples
    python3 sys_fitter.py  -y "$year" -m 1725  -f final -s "$Sys"
    # python3 Create_Workspace_sys.py -y "$year" -m 1725  -s "$Sys" # model will be rewritten with sys
    # python3 Run_combine_on_Alternate_mass_samples_sys.py  -m 1725 -y "$year" -s "$Sys"
done

