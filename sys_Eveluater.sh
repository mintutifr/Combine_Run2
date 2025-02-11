#!/bin/bash

# Define the arrays
YEARS=("UL2018") # "UL2017" "UL2016preVFP" "UL2016postVFP")
LEP=("el" "mu")

# Loop through each combination
# for year in "${YEARS[@]}"; do
#     for lepton in "${LEP[@]}"; do
#         echo "Running for Year: $year, Lepton: $lepton"
#         python3 Compiare_shapes_and_getRation_sys_hists.py -y "$year" -l "$lepton" &> "sys_hist_Integral_ratios/sys_ratio_${lepton}_${year}.txt"
#     done
# done

for year in "${YEARS[@]}"; do
    echo "Running for Year: $year"
    #python3 sys_fitter.py  -y "$year" -m 1725 -s bWeight -f final
    #python3 Create_Workspace_sys.py -y UL2018 -m 1725 
    python3 Run_combine_on_Alternate_mass_samples_sys.py  -m 1725 -y "$year"
done

