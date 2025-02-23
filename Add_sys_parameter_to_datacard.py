import os, json

def update_sys_parameters_to_datacard_simultanous_fit(file_path, systematics):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Remove all lines that start with "nuisance_"
    filtered_lines = [line for line in lines if not line.startswith("nuisance_")]

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
    systematic_list = systematic_dic[systematics]
    print(systematic_list)

    # Compute maximum width among both "nuisance_<sys>_mean" and "nuisance_<sys>_sigmaG"
    max_length = max(len(f"nuisance_{sys}_mean") for sys in systematic_list)

    # Generate parameter lines for each systematic with aligned formatting
    param_lines = []
    param_lines.append(f"\n# ==============   sys   ===============\n")
    for sys in systematic_list:
        param_lines.append(f"{f'nuisance_{sys}_mean':<{max_length}}   param   0.0   1.0\n")
        param_lines.append(f"{f'nuisance_{sys}_sigmaG':<{max_length}}   param   0.0   1.0\n")

    # Insert the new parameter lines after the marker
    new_lines = filtered_lines[:insert_index] + param_lines + filtered_lines[insert_index:]

    # Modify number of nuisance
    updated_lines = []
    for line in new_lines:
        updated_lines.append(
            line.replace("kmax 3 number of nuisance parameters", f"kmax {3+2*len(systematic_list)} number of nuisance parameters")
        )
    
    with open(file_path, "w") as file:
        file.writelines(updated_lines)
        
    print(f"Updated parameters in {file_path}.")

def write_datacard_for_systematic(file_path, systematic,lep):
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
            line.replace("workspace_UL18.root", f"workspace_UL18{systematic}.root")
        )
    
    # Write the modified content to the new file
    with open(new_file_path, "w") as file:
        file.writelines(updated_lines)
    
    print(f"Created modified datacard at {new_file_path}.")