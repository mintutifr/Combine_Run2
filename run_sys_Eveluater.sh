#!/bin/bash

# Define the arrays
YEARS=('Run2') #'Run2') # "UL2018" "UL2016postVFP" "UL2017" "UL2016preVFP") # "UL2016postVFP")
Sys=("all_sys") #("all_sys") #("top_weight_sys") #("JES_JER") # bWeight # Nomi

for year in "${YEARS[@]}"; do
    echo "Running for Year: $year"
    # Pull the systematic comparision plots
    if [ "$year" == "Run2" ]; then
        for subyear in "UL2016" "UL2018" "UL2017"; do # "UL2016postVFP" "UL2016preVFP"; do
            echo "pass"
            # python3 Compaire_shapes_and_getRation_sys_hists.py -y "$subyear" -l mu
            # python3 Compaire_shapes_and_getRation_sys_hists.py -y "$subyear" -l el

            # Estimate the deviation in mean and sigma due to systematic samples
            #python3 sys_fitter.py -y "$subyear" -m 1725 -s "$Sys"
            #python3 Run_combine_on_Alternate_mass_samples_sys.py  -m 1725 -y "$subyear" -s "$Sys"
        done
    else
        echo "pass"
        #python3 Compaire_shapes_and_getRation_sys_hists.py -y "$year" -l mu
        #python3 Compaire_shapes_and_getRation_sys_hists.py -y "$year" -l el

        # # Estimate the deviation in mean and sigma due to systematic samples
        #python3 sys_fitter.py -y "$year" -m 1725 -s "$Sys"
        #python3 Run_combine_on_Alternate_mass_samples_sys.py  -m 1725 -y "$year" -s "$Sys"
    fi
    # python3 Create_Workspace_sys.py -y "$year" -m 1725  -s "$Sys" # model will be rewritten with sys
    python3 Run_combine_on_Alternate_mass_samples_sys.py  -m 1725 -y "$year" -s "$Sys"
done