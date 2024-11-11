import ROOT
import os
import argparse as arg
parser = arg.ArgumentParser(description='Run Higgs combine Tool')
parser.add_argument('-y', '--year', dest='Year', default=['2016'], type=str, nargs=1, help="Year of Data collection ['2016', 'UL2017', 'UL2018','Run2']")
parser.add_argument('-l', '--lepton', dest='lepton', type=str, nargs=1, help="lepton [ el  mu ]")
args = parser.parse_args()


year = args.Year[0]
lep = args.lepton[0]

# Open the root file
file_path = "/eos/home-m/mikumar/Higgs_Combine/CMSSW_14_1_0_pre4/src/HiggsAnalysis/Hist_for_workspace/Combine_Input_lntopMass_histograms_"+year+"_"+lep+"_gteq0p7_withoutDNNfit_rebin.root"
print(f'{file_path  = }')
root_file = ROOT.TFile(file_path, "READ")

# Create directory to save plots
output_dir = "Plots"
os.makedirs(output_dir, exist_ok=True)

# Define the hex color palette
hex_colors = ["#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6", "#a96b59", "#e76300", "#b9ac70", "#717581"]

Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18"}

# Convert hex colors to ROOT color codes
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

def hex_to_root_color(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return ROOT.TColor.GetColor(r, g, b)

# Assign systematic types to color
systematic_colors = {}

# List of systematics by category
systematics = ["gtbWeight_lf", "gtbWeight_hf", "gtbWeight_cferr1", "gtbWeight_cferr2", 
               "ISR", "FSR", "hdamp", "SF_Iso"]

# Assign each systematic type a unique color from the hex color list
for i, syst in enumerate(systematics):
    systematic_colors[syst] = hex_to_root_color(hex_colors[i % len(hex_colors)])

# Function to determine the systematic name from the histogram name
def get_systematic_type(hist_name):
    for syst in systematic_colors:
        if syst in hist_name:
            return syst
    return None

# Function to set histogram style based on systematic type and whether it's Up or Down
def set_histogram_style(hist, syst_type, is_up):
    color = systematic_colors.get(syst_type, ROOT.kBlack)
    
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(24 if is_up else 25)  # Arrow up for Up, arrow down for Down

# Function to draw histograms in a canvas with a legend
def draw_histograms(Nominal_hist,histograms, canvas_name, canvas_title, output_path):
    canvas = ROOT.TCanvas(canvas_name, canvas_title, 800, 600)
    legend = ROOT.TLegend(0.7, 0.4, 0.9, 0.9)
    legend.SetTextSize(0.03)

    for i, hist in enumerate(histograms):
        syst_type = get_systematic_type(hist.GetName())
        is_up = 'Up' in hist.GetName()
        set_histogram_style(hist, syst_type, is_up)

        hist.Draw("HIST SAME" if i > 0 else "HIST")
        legend.AddEntry(hist, hist.GetName().rsplit("_gt")[1], "l")

        yield_variation = hist.Integral()/Nominal_hist.Integral()
        print("Systematic varied yield (%s): %.3f"%(hist.GetName(),yield_variation))

    legend.Draw()
    canvas.SaveAs(output_path)
    canvas.Close()

# Create dictionaries to store histograms based on the criteria
# Create dictionaries to store histograms based on the criteria for topSig, topBkg, and ewkBkg
histogram_categories = {
    'topSig': {
        'bweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    },
    'topBkg': {
        'bweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    },
    'ewkBkg': {
        'bweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    }
}

# Define the categories and their corresponding substrings
categories = {
    'topSig': f"top_sig_1725{Combine_year_tag[year]}_gt",
    'topBkg': f"top_bkg_1725{Combine_year_tag[year]}_gt",
    'ewkBkg': f"EWK_bkg{Combine_year_tag[year]}_gt"
}

# Loop through the histograms in the directory 'mujets'
root_dir = root_file.Get(lep+"jets")
for key in root_dir.GetListOfKeys():
    hist_name = key.GetName()
    hist = root_dir.Get(hist_name)

    # Loop over the categories (topSig, topBkg, ewkBkg)
    for category, substring in categories.items():
        if substring in hist_name:
            # Categorize based on histogram name for each category
            if substring + "bWeight" in hist_name:
                histogram_categories[category]['bweight'].append(hist)
            elif substring + "SF_Iso" in hist_name:
                histogram_categories[category]['sf_iso'].append(hist)
            elif substring + "ISR" in hist_name or "FSR" in hist_name:
                histogram_categories[category]['isr_fsr'].append(hist)
            elif substring + "hdamp" in hist_name:
                histogram_categories[category]['hdamp'].append(hist)
            elif substring == hist_name:
                histogram_categories[category]['nominal'] = hist

# Function to draw histograms based on the categories
def plot_variations(category, year, lep, output_dir):
    nominal_hist = histogram_categories[category]['nominal']

    if nominal_hist is None:
        print(f"No nominal histogram found for {category}")
        return

    if histogram_categories[category]['bweight']:
        print("\n  = = = = = = = = =  =      "+ category +" bweight       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['bweight'],
                        f"canvas_{category}_bweight", f"{category} bWeight Variations",
                        os.path.join(output_dir, f"{category}_bweight_variations_{year}_{lep}.png"))

    if histogram_categories[category]['sf_iso']:
        print("\n  = = = = = = = = =  =      "+ category +" sf_iso       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['sf_iso'],
                        f"canvas_{category}_sf_iso", f"{category} SF Iso Variations",
                        os.path.join(output_dir, f"{category}_sf_iso_variations_{year}_{lep}.png"))

    if histogram_categories[category]['isr_fsr']:
        print("\n  = = = = = = = = =  =      "+ category +" isr_fsr       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['isr_fsr'],
                        f"canvas_{category}_isr_fsr", f"{category} ISR and FSR Variations",
                        os.path.join(output_dir, f"{category}_isr_fsr_variations_{year}_{lep}.png"))

    if histogram_categories[category]['hdamp']:
        print("\n  = = = = = = = = =  =      "+ category +" hdamp       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['hdamp'],
                        f"canvas_{category}_hdamp", f"{category} hdamp Variations",
                        os.path.join(output_dir, f"{category}_hdamp_variations_{year}_{lep}.png"))

# Plot histograms for all categories
for category in categories.keys():
    plot_variations(category, year, lep, output_dir)

# Close the root file
root_file.Close()

