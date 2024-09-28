#python Create_Workspace.py -m 1725 -y UL2018 -f sig
#python Create_Workspace.py -m 1725 -y UL2018 -f top_bkg
#python3 Create_Workspace.py -m 1725 -y UL2018 -f ewk_bkg

#python Create_Workspace.py -m 1725 -y UL2018 -f final_mu
#python Create_Workspace.py -m 1725 -y UL2018 -f final_el
#python Create_Workspace.py -m 1725 -y UL2018 -f final

#python3 Run_combine_on_Alternate_mass_samples.py -w 190 -y UL2018
#python Run_combine_on_Alternate_mass_samples.py -m 1725 -y UL2018 -s hdamp_Down

#python3 Run_combine_on_Alternate_mass_samples.py -m 1725 -y UL2018
#python3 Plot_fit_v2.py -m 1725 -y UL2018
#python3 Run_combine_on_Alternate_mass_samples.py -m 1725 -y UL2017
#python3 Plot_fit_v2.py -m 1725 -y UL2017
#python3 Run_combine_on_Alternate_mass_samples.py -m 1725 -y UL2016preVFP
#python3 Plot_fit_v2.py -m 1725 -y UL2016preVFP
#python3 Run_combine_on_Alternate_mass_samples.py -m 1725 -y UL2016postVFP
#python3 Plot_fit_v2.py -m 1725 -y UL2016postVFP
read -r -p 'Please enter mass value without point (1.e 1725)>>> ' width

python3 Run_combine_on_Alternate_mass_samples.py -y Run2 -m $width
exit 0
read -r -p 'Please enter any key to procced >>> ' anykey
python3 Plot_fit_v2.py -y UL2018 -m $width
python3 Plot_fit_v2.py -y UL2017 -m $width
python3 Plot_fit_v2.py -y UL2016preVFP -m $width
python3 Plot_fit_v2.py -y UL2016postVFP -m $width


#python3 Run_combine_on_Alternate_mass_samples_con.py -m 1725 -y UL2018
#python3 Plot_fit_v2_con.py -m 1725 -y UL2018


#python Plot_fit_v2.py -w 190 -y UL2018


#python compaire_shapes.py -y UL2018 -s EWK_bkg
#python compaire_shapes.py -y UL2017 -s EWK_bkg
#python compaire_shapes.py -y UL2016preVFP -s EWK_bkg
#python compaire_shapes.py -y UL2016postVFP -s EWK_bkg



#python3 Create_Workspace_con.py -m 1725 -y UL2018 -f sig
#python3 Create_Workspace_con.py -m 1725 -y UL2018 -f top_bkg
#python3 Create_Workspace_con.py -m 1725 -y UL2018 -f ewk_bkg

#python Create_Workspace_con.py -m 1725 -y UL2018 -f final_mu
#python Create_Workspace_con.py -m 1725 -y UL2018 -f final_el
#python Create_Workspace_con.py -m 1725 -y UL2018 -f final

#python3 Run_combine_on_Alternate_mass_samples_con.py -m 1725 -y UL2018
#python3 Plot_fit_v2_con.py -m 1725 -y UL2018
#python3 Plot_fit_v2.py -m 1725 -y UL2018

#python3 Plot_DNNfits_v1.py -y UL2018 -f ROOT/fitDiagnostics_M1725_DNNfit_UL2018.root

