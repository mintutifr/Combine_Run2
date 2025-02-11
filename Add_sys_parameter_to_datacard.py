import os

def update_sys_parameters_to_datacard(file_path, systematics):
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
    try:
        insert_index = filtered_lines.index("# ===== sys  ====\n") + 1
    except ValueError:
        print("Could not find the sys section marker in the file.")
        return

    # Compute maximum width among both "nuisance_<sys>_mean" and "nuisance_<sys>_sigmaG"
    max_length = max(len(f"nuisance_{sys}_mean") for sys in systematics)

    # Generate parameter lines for each systematic with aligned formatting
    param_lines = []
    for sys in systematics:
        param_lines.append(f"{f'nuisance_{sys}_mean':<{max_length}}   param   0.0   1.0\n")
        param_lines.append(f"{f'nuisance_{sys}_sigmaG':<{max_length}}   param   0.0   1.0\n")

    # Insert the new parameter lines after the marker
    new_lines = filtered_lines[:insert_index] + param_lines + filtered_lines[insert_index:]

    with open(file_path, "w") as file:
        file.writelines(new_lines)

    print(f"Updated parameters in {file_path}.")