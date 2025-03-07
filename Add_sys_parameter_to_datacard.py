import os, json

def get_weight_sys(file_path_el, file_path_mu, systematic_dic,sys):
    with open(file_path_el, "r") as f:
        weight_sys_el = json.load(f)
    with open(file_path_mu, "r") as f:
        weight_sys_mu = json.load(f)
    weight_sys_lep = {}
    weight_sys_lep["el"] = weight_sys_el
    weight_sys_lep["mu"] = weight_sys_mu
    del weight_sys_el, weight_sys_mu
    sys_lines = {}
    for weight_sys in systematic_dic[sys]:
        sys_line = f'CMS_{weight_sys}  lnN  '
        for lep in ["mu","el"]:
            for S_and_B in ['topSig','topBkg','ewkBkg']:
                up_frac = weight_sys_lep[lep][S_and_B][sys][f"{weight_sys}Up"]
                down_frac = weight_sys_lep[lep][S_and_B][sys][f"{weight_sys}Down"]
                if(down_frac < up_frac): frac = f'{down_frac}/{up_frac}'
                elif(down_frac > up_frac): frac = f'{up_frac}/{down_frac}'
                elif(down_frac == up_frac and up_frac==1.00): frac = f'-'
                elif(down_frac == up_frac and up_frac!=1.00): frac = f'{up_frac}'
                sys_line = sys_line+f'  {frac}  '
                #print(f'{lep} {S_and_B} sys : {weight_sys},  frac up : {up_frac} frac down : {down_frac}')
        #print(sys_line)
        sys_lines[weight_sys] = sys_line+f'\n'
    return sys_lines

def get_lepton_weight_sys(file_path, lep,systematic_dic):
    with open(file_path, "r") as f:
        weight_sys_lep = json.load(f)
    sys_lines = {}
    for weight_sys in systematic_dic["lep_SF"][f'{lep}']:
        sys_line = f''
        for S_and_B in ['topSig','topBkg','ewkBkg']:
            up_frac = weight_sys_lep[S_and_B]["sf_iso"][f"{weight_sys}Up"]
            down_frac = weight_sys_lep[S_and_B]["sf_iso"][f"{weight_sys}Down"]
            if(down_frac < up_frac): frac = f'{down_frac}/{up_frac}'
            elif(down_frac > up_frac): frac = f'{up_frac}/{down_frac}'
            elif(down_frac == up_frac and up_frac==1.00): frac = f'-'
            elif(down_frac == up_frac and up_frac!=1.00): frac = f'{up_frac}'
            sys_line = sys_line+f'  {frac}  '
            #print(f'{S_and_B} sys : {weight_sys},  frac up : {up_frac} frac down : {down_frac}')
        #print(f'{sys_line}')
        #print(f"{S_and_B} {weight_sys_lep[S_and_B]['sf_iso'] = }")
        if(lep == "mu"):
            sys_line = f'CMS_{weight_sys}_{lep}  lnN  '+sys_line+f'  -  -  -  \n'
        elif(lep=="el"):
            sys_line = f'CMS_{weight_sys}_{lep}  lnN  '+f'  -  -  -  '+sys_line+f'\n'
        sys_lines[weight_sys] = sys_line
    return sys_lines

def update_sys_parameters_to_datacard_simultanous_fit(file_path, systematics,year):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Remove all lines that start with "nuisance_"
    filtered_lines = [line for line in lines if ((not line.startswith("nuisance_")) or (not line.startswith("CMS_")))]

    if len(systematics) == 0:
        # If no systematics are provided, only remove nuisance parameters and do not add new ones
        with open(file_path, "w") as file:
            file.writelines(filtered_lines)
        print(f"Removed all nuisance parameters from {file_path}.")
        return

    # Find the index of the sys section marker
    # try:
    #     insert_index = filtered_lines.index("# ===== sys  ====\n") + 1
    # except ValueError:
    #     print("Could not find the sys section marker in the file.")
    #     return
    insert_index = len(lines)

    # Get the systematic you want to analyze
    with open("Sys_list.json", "r") as f:
        systematic_dic = json.load(f)
    if(systematics=="all_sys"):
            systematic_list = systematic_dic["sample"]+systematic_dic["top_weight_sys"] + systematic_dic["JES_JER"]
    else:
        systematic_list = systematic_dic[systematics]
    print(systematic_list)

    # Compute maximum width among both "nuisance_<sys>_mean" and "nuisance_<sys>_sigmaG"
    if(len(systematic_list)>0):
        max_length = max(len(f"nuisance_{sys}_mean") for sys in systematic_list)

    # Generate parameter lines for each systematic with aligned formatting
    param_lines = []
    param_lines.append(f"\n# ==============   sys   ===============\n")
    for sys in systematic_list:
        param_lines.append(f"{f'nuisance_{sys}_mean':<{max_length}}   param   0.0   1.0\n")
        param_lines.append(f"{f'nuisance_{sys}_sigmaG':<{max_length}}   param   0.0   1.0\n")

    # add sustematic for scales and weights
    Num_weight_sys = 0
    if(systematics=="all_sys"):
        sys_lines_el_SF = get_lepton_weight_sys(f'Weight_sys_{year}_mu.json', "mu", systematic_dic)
        Num_weight_sys += len(sys_lines_el_SF.keys())
        for key in sys_lines_el_SF.keys():
            #print(sys_lines_el_SF[key])
            param_lines.append(sys_lines_el_SF[key])

        sys_lines_mu_SF = get_lepton_weight_sys(f'Weight_sys_{year}_el.json', "el", systematic_dic)
        Num_weight_sys += len(sys_lines_mu_SF.keys())
        for key in sys_lines_mu_SF.keys():
            #print(sys_lines_mu_SF[key])
            param_lines.append(sys_lines_mu_SF[key])

        sys_lines_bweight = get_weight_sys(f'Weight_sys_{year}_el.json', f'Weight_sys_{year}_mu.json', systematic_dic,"bWeight")
        Num_weight_sys += len(sys_lines_bweight.keys())
        for key in sys_lines_bweight.keys():
            #print(sys_lines_bweight[key])
            param_lines.append(sys_lines_bweight[key])

        sys_lines_puweight = get_weight_sys(f'Weight_sys_{year}_el.json', f'Weight_sys_{year}_mu.json', systematic_dic,"puWeight")
        Num_weight_sys += len(sys_lines_puweight.keys())
        for key in sys_lines_puweight.keys():
            #print(sys_lines_bweight[key])
            param_lines.append(sys_lines_puweight[key])

    
    # Insert the new parameter lines after the marker
    new_lines = filtered_lines[:insert_index] + param_lines + filtered_lines[insert_index:]

    # Modify number of nuisance
    updated_lines = []
    for line in new_lines:
        updated_lines.append(
            line.replace("kmax 3 number of nuisance parameters", f"kmax {3+2*len(systematic_list)+Num_weight_sys} number of nuisance parameters")
        )
    
    with open(file_path, "w") as file:
        file.writelines(updated_lines)
        
    print(f"Updated parameters in {file_path}.")

def write_datacard_for_systematic(file_path, systematic,lep,year_tag):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
    
    # Create the output directory if it doesn't exist
    output_dir = "Per_sys_datacards"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate new file path
    file_name = os.path.basename(file_path)
    file_name_with_systematic = f"{os.path.splitext(file_name)[0]}{systematic}.txt"
    new_file_path = os.path.join(output_dir, file_name_with_systematic)
    
    with open(file_path, "r") as file:
        lines = file.readlines()
    
    # Find the index of the sys section marker
    try:
        sys_index = lines.index("# ===== sys  ====\n")
    except ValueError:
        print("Could not find the sys section marker in the file.")
        return
    
    # Keep only lines up to the sys section marker (inclusive)
    new_lines = lines[:sys_index + 1]
    
    # Modify specific lines with the systematic name
    updated_lines = []
    for line in new_lines:
        updated_lines.append(
            line.replace(f"workspace{year_tag}.root", f"workspace{year_tag}{systematic}.root")
        )
    
    # Write the modified content to the new file
    with open(new_file_path, "w") as file:
        file.writelines(updated_lines)
    
    print(f"Created modified datacard at {new_file_path}.")

if __name__ == "__main__":
    update_sys_parameters_to_datacard_simultanous_fit(f"datacard_top_shape_comb_para_UL17.txt","all_sys","UL2017")