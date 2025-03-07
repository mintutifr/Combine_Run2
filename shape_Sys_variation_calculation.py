import json


def compute_variations_simultanous_fit(json_filename, systematic_key):
    """
    Reads a JSON file and computes percentage variations for a given systematic.
    
    The JSON file is expected to have a structure like:
    
    {
        "Nomi": {
            "Nomi": {
                "mean_fit": {
                    "mean": [<nominal_mu_mean>, <error>]
                },
                "sigmaG_fit": {
                    "sigmaG": [<nominal_mu_sigma>, <error>]
                }
            }
        },
        "<systematic_key>": {
            "Up": {
                "mean_fit": {
                    "mean": [<up_mu_mean>, <error>]
                },
                "sigmaG_fit": {
                    "sigmaG": [<up_mu_sigma>, <error>
                }
            },
            "Down": {
                "mean_fit": {
                    "mean": [<down_mu_mean>, <error>]
                },
                "sigmaG_fit": {
                    "sigmaG": [<down_mu_sigma>, <error>]
                }
            }
        }
    }
    
    For each variation ("Up" and "Down") the percentage variation is calculated as:
      (1 - systematic_value / nominal_value) * 100
      
    Parameters:
      json_filename (str): Path to the JSON file.
      systematic_key (str): The key for the systematic (e.g., "bWeight_hf").
    
    Returns:
      dict: A dictionary with the computed percentage variations.
    """
    # Read the JSON file
    with open(json_filename, "r") as f:
        data = json.load(f)
    
    # Extract nominal values from the "Nomi" key
    nomi = data.get("Nomi", {}).get("Nomi", {})
    nominal_mean   = nomi.get("mean_fit", {}).get("mean", [None])[0]
    nominal_sigmaG = nomi.get("sigmaG_fit", {}).get("sigmaG", [None])[0]
    
    # Ensure nominal values are found
    if None in [nominal_mean,nominal_sigmaG]:
        raise ValueError("Nominal values under 'Nomi' are missing or not formatted correctly.")
    
    # Get systematic data
    sys_data = data.get(systematic_key)
    if sys_data is None:
        raise ValueError(f"Systematic '{systematic_key}' not found in the JSON file.")
    
    # Dictionary to store the variations
    variations = {}
    
    # Loop over the two variations: "Up" and "Down"
    for variation in ["Up", "Down"]:
        #print(f"{variation = }")
        variation_data = sys_data.get(variation)
        if variation_data is None:
            print(f"Warning: '{variation}' variation not found for systematic '{systematic_key}'.")
            continue
        
        variations[variation] = {}
        
        # Mean values for mu and el
        sys_mean = variation_data.get("mean_fit", {}).get("mean", [None])[0]
        #print(f"{sys_mean= }")
        # SigmaG values for mu and el
        sys_sigmaG = variation_data.get("sigmaG_fit", {}).get("sigmaG", [None])[0]
        
        # Check that the values are present before computing
        if sys_mean is None :
            raise ValueError(f"Mean values missing in {systematic_key} -> {variation}")
        if sys_sigmaG is None :
            raise ValueError(f"SigmaG values missing in {systematic_key} -> {variation}")

        # Calculate variations:
        var_mean = (1 - sys_mean / nominal_mean )
        ratio = sys_sigmaG / nominal_sigmaG
        # print(f" sys_sigmaG : {sys_sigmaG}   nominal_sigmaG {nominal_sigmaG}  ratio : {sys_sigmaG / nominal_sigmaG}")
        var_sigmaG = (1 - sys_sigmaG / nominal_sigmaG)
        
        # Save the variations in the dictionary
        variations[variation]["mean"]   = var_mean
        variations[variation]["sigmaG"] = var_sigmaG

    maxi_variations = {}
    #print(variations["Up"]["sigmaG"],variations["Down"]["sigmaG"])
    maxi_variations["Nui_mean"] = variations["Up"]["mean"] if abs(variations["Up"]["mean"]) > abs(variations["Down"]["mean"]) else variations["Down"]["mean"]
    maxi_variations["Nui_sigmaG"] = variations["Up"]["sigmaG"] if abs(variations["Up"]["sigmaG"]) > abs(variations["Down"]["sigmaG"]) else variations["Down"]["sigmaG"]

    print(f"{maxi_variations}")
    return variations, maxi_variations


def compute_variations(json_filename, systematic_key):
    """
    Reads a JSON file and computes percentage variations for a given systematic.
    
    The JSON file is expected to have a structure like:
    
    {
        "Nomi": {
            "Nomi": {
                "mean_fit": {
                    "mean_mu": [<nominal_mu_mean>, <error>],
                    "mean_el": [<nominal_el_mean>, <error>]
                },
                "sigmaG_fit": {
                    "sigmaG_mu": [<nominal_mu_sigma>, <error>],
                    "sigmaG_el": [<nominal_el_sigma>, <error>]
                }
            }
        },
        "<systematic_key>": {
            "Up": {
                "mean_fit": {
                    "mean_mu": [<up_mu_mean>, <error>],
                    "mean_el": [<up_el_mean>, <error>]
                },
                "sigmaG_fit": {
                    "sigmaG_mu": [<up_mu_sigma>, <error>],
                    "sigmaG_el": [<up_el_sigma>, <error>]
                }
            },
            "Down": {
                "mean_fit": {
                    "mean_mu": [<down_mu_mean>, <error>],
                    "mean_el": [<down_el_mean>, <error>]
                },
                "sigmaG_fit": {
                    "sigmaG_mu": [<down_mu_sigma>, <error>],
                    "sigmaG_el": [<down_el_sigma>, <error>]
                }
            }
        }
    }
    
    For each variation ("Up" and "Down") the percentage variation is calculated as:
      (1 - systematic_value / nominal_value) * 100
      
    Parameters:
      json_filename (str): Path to the JSON file.
      systematic_key (str): The key for the systematic (e.g., "bWeight_hf").
    
    Returns:
      dict: A dictionary with the computed percentage variations.
    """
    # Read the JSON file
    with open(json_filename, "r") as f:
        data = json.load(f)
    
    # Extract nominal values from the "Nomi" key
    nomi = data.get("Nomi", {}).get("Nomi", {})
    nominal_mean_mu   = nomi.get("mean_fit", {}).get("mean_mu", [None])[0]
    nominal_mean_el   = nomi.get("mean_fit", {}).get("mean_el", [None])[0]
    nominal_sigmaG_mu = nomi.get("sigmaG_fit", {}).get("sigmaG_mu", [None])[0]
    nominal_sigmaG_el = nomi.get("sigmaG_fit", {}).get("sigmaG_el", [None])[0]
    
    # Ensure nominal values are found
    if None in [nominal_mean_mu, nominal_mean_el, nominal_sigmaG_mu, nominal_sigmaG_el]:
        raise ValueError("Nominal values under 'Nomi' are missing or not formatted correctly.")
    
    # Get systematic data
    sys_data = data.get(systematic_key)
    if sys_data is None:
        raise ValueError(f"Systematic '{systematic_key}' not found in the JSON file.")
    
    # Dictionary to store the variations
    variations = {}
    
    # Loop over the two variations: "Up" and "Down"
    for variation in ["Up", "Down"]:
        #print(f"{variation = }")
        variation_data = sys_data.get(variation)
        if variation_data is None:
            print(f"Warning: '{variation}' variation not found for systematic '{systematic_key}'.")
            continue
        
        variations[variation] = {}
        
        # Mean values for mu and el
        sys_mean_mu = variation_data.get("mean_fit", {}).get("mean_mu", [None])[0]
        sys_mean_el = variation_data.get("mean_fit", {}).get("mean_el", [None])[0]
        #print(f"{sys_mean_mu = }")
        #print(f"{sys_mean_el = }")
        # SigmaG values for mu and el
        sys_sigmaG_mu = variation_data.get("sigmaG_fit", {}).get("sigmaG_mu", [None])[0]
        sys_sigmaG_el = variation_data.get("sigmaG_fit", {}).get("sigmaG_el", [None])[0]
        
        # Check that the values are present before computing
        if sys_mean_mu is None or sys_mean_el is None:
            raise ValueError(f"Mean values missing in {systematic_key} -> {variation}")
        if sys_sigmaG_mu is None or sys_sigmaG_el is None:
            raise ValueError(f"SigmaG values missing in {systematic_key} -> {variation}")

        #print(f"{nominal_mean_mu = }")
        # Calculate percentage variations:
        # For "mean" in the mu final state
        var_mean_mu = (1 - sys_mean_mu / nominal_mean_mu )
        # For "mean" in the el final state
        var_mean_el = (1 - sys_mean_el / nominal_mean_el)
        # For "sigmaG" in the mu final state
        var_sigmaG_mu = (1 - sys_sigmaG_mu / nominal_sigmaG_mu)
        # For "sigmaG" in the el final state
        var_sigmaG_el = (1 - sys_sigmaG_el / nominal_sigmaG_el)
        
        # Save the variations in the dictionary
        variations[variation]["mean_mu"]   = var_mean_mu
        variations[variation]["mean_el"]   = var_mean_el
        variations[variation]["sigmaG_mu"] = var_sigmaG_mu
        variations[variation]["sigmaG_el"] = var_sigmaG_el

    maxi_variations = {}
    maxi_variations["Nui_mean_mu"] = round(variations["Up"]["mean_mu"],5) if abs(variations["Up"]["mean_mu"]) > abs(variations["Down"]["mean_mu"]) else round(variations["Down"]["mean_mu"],5)
    maxi_variations["Nui_mean_el"] = round(variations["Up"]["mean_el"],5) if abs(variations["Up"]["mean_el"]) > abs(variations["Down"]["mean_el"]) else round(variations["Down"]["mean_el"],5)

    maxi_variations["Nui_sigmaG_mu"] = variations["Up"]["sigmaG_mu"] if abs(variations["Up"]["sigmaG_mu"]) > abs(variations["Down"]["sigmaG_mu"]) else variations["Down"]["sigmaG_mu"]
    maxi_variations["Nui_sigmaG_el"] = variations["Up"]["sigmaG_el"] if abs(variations["Up"]["sigmaG_el"]) > abs(variations["Down"]["sigmaG_el"]) else variations["Down"]["sigmaG_el"]

    return variations, maxi_variations

# Example usage:
if __name__ == "__main__":
    json_file = "Sys_fit_results.json"  # Replace with your actual JSON file path
    systematic = "bWeight_hf"       # The systematic you want to analyze
    
    try:
        variation,maxi_variation = compute_variations(json_file, systematic)
        print("Percentage variations for systematic", systematic)
        print(json.dumps(variation, indent=4))
        print(json.dumps(maxi_variation, indent=4))
    except Exception as e:
        print("Error:", e)

