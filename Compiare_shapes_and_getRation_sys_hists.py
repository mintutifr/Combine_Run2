import ROOT
from ROOT import TColor
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
output_dir = "Plots_sys"
os.makedirs(output_dir, exist_ok=True)

# Define the hex color palette
color_list = [
    TColor.GetColor("#FF5733"), TColor.GetColor("#33FF57"), TColor.GetColor("#3357FF"),
    TColor.GetColor("#FF33A1"), TColor.GetColor("#A133FF"), TColor.GetColor("#FF8C33"),
    TColor.GetColor("#33FFF2"), TColor.GetColor("#FF3380"), TColor.GetColor("#80FF33"),
    TColor.GetColor("#3380FF"), TColor.GetColor("#FFD700"), TColor.GetColor("#DC143C"),
    TColor.GetColor("#6495ED"), TColor.GetColor("#32CD32"), TColor.GetColor("#8A2BE2"),
    TColor.GetColor("#FF4500"), TColor.GetColor("#1E90FF"), TColor.GetColor("#228B22"),
    TColor.GetColor("#FF1493"), TColor.GetColor("#9932CC"), TColor.GetColor("#FA8072"),
    TColor.GetColor("#4169E1"), TColor.GetColor("#3CB371"), TColor.GetColor("#D2691E"),
    TColor.GetColor("#8B0000"), TColor.GetColor("#00CED1"), TColor.GetColor("#FF6347"),
    TColor.GetColor("#008080"), TColor.GetColor("#FF69B4"), TColor.GetColor("#A0522D"),
    TColor.GetColor("#20B2AA"), TColor.GetColor("#4682B4"), TColor.GetColor("#CD5C5C"),
    TColor.GetColor("#ADFF2F"), TColor.GetColor("#7B68EE"), TColor.GetColor("#B22222"),
    TColor.GetColor("#5F9EA0"), TColor.GetColor("#FFDAB9"), TColor.GetColor("#6A5ACD"),
    TColor.GetColor("#D2B48C"), TColor.GetColor("#00FF7F"), TColor.GetColor("#8B4513"),
    TColor.GetColor("#F4A460"), TColor.GetColor("#48D1CC"), TColor.GetColor("#C71585"),
    TColor.GetColor("#00FA9A"), TColor.GetColor("#708090"), TColor.GetColor("#FFB6C1"),
    TColor.GetColor("#9370DB"), TColor.GetColor("#40E0D0")
]
# Dictionary to store custom ROOT color IDs

Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18"}

# Convert hex colors to ROOT color codes
# def hex_to_rgb(hex_color):
#     hex_color = hex_color.lstrip("#")
#     return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

# def hex_to_root_color(hex_color):
#     r, g, b = hex_to_rgb(hex_color)
#     return ROOT.TColor.GetColor(r, g, b)

# Assign systematic types to color
systematic_colors = {}

# List of systematics by category
systematics = ["jes","gtbWeight_lf", "gtbWeight_hf", "gtbWeight_cferr1", "gtbWeight_cferr2", 
               "ISR", "FSR", "hdamp", "SF_Iso"]

# Assign each systematic type a unique color from the hex color list
# for i, syst in enumerate(systematics):
#     systematic_colors[syst] = hex_to_root_color(hex_colors[i % len(hex_colors)])

# Function to determine the systematic name from the histogram name
def get_systematic_type(hist_name):
    for syst in systematics:
        if syst in hist_name:
            return syst
    return None

# Function to set histogram style based on systematic type and whether it's Up or Down
def set_histogram_style(hist, syst_type, is_up):
    color = systematic_colors.get(syst_type, ROOT.kBlack)
    print(f"{color = }")
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(24 if is_up else 25)  # Arrow up for Up, arrow down for Down

# Function to draw histograms in a canvas with a legend
def draw_histograms_old(Nominal_hist,histograms, canvas_name, canvas_title, output_path):
    canvas = ROOT.TCanvas(canvas_name, canvas_title, 800, 600)
    legend = ROOT.TLegend(0.7, 0.9-min(len(histograms)*.05,0.8), 0.9, 0.9)
    legend.SetTextSize(0.03)
    ROOT.gStyle.SetOptStat(0)
    Nominal_hist.Draw("HIST")
    legend.AddEntry(Nominal_hist, "Nominal", "l")
    for i, hist in enumerate(histograms):
        syst_type = get_systematic_type(hist.GetName())
        is_up = 'Up' in hist.GetName()
        hist.SetLineColor(color_list[i])
        hist.SetMarkerColor(color_list[i])
        hist.SetMarkerStyle(24 if is_up else 25)
        hist.Draw("HIST SAME")# if i > 0 else "HIST")
        legend.AddEntry(hist, hist.GetName().rsplit("_gt")[1], "l")

        yield_variation = hist.Integral()/Nominal_hist.Integral()
        print("Systematic varied yield (%s): %.3f"%(hist.GetName(),yield_variation))

    legend.Draw()
    canvas.SaveAs(output_path)
    canvas.Close()



def draw_histograms(Nominal_hist, histograms, canvas_name, canvas_title, output_path):
    # Create the canvas with two pads (one for the histograms, one for the ratio plot)
    canvas = ROOT.TCanvas(canvas_name, canvas_title, 800, 800)
    canvas.Divide(1, 2)  # Divide canvas into 2 parts, top for histograms and bottom for ratio

    # Top pad for the histograms
    canvas.cd(1)
    legend = ROOT.TLegend(0.7, 0.9-min(len(histograms)*.05, 0.8), 0.9, 0.9)
    legend.SetTextSize(0.03)
    ROOT.gStyle.SetOptStat(0)
    
    Nominal_hist.Draw("HIST")
    legend.AddEntry(Nominal_hist, "Nominal", "l")

    # Loop through the histograms, draw them and compute ratios
    for i, hist in enumerate(histograms):
        syst_type = get_systematic_type(hist.GetName())
        is_up = 'Up' in hist.GetName()
        hist.SetLineColor(color_list[i])
        hist.SetMarkerColor(color_list[i])
        hist.SetMarkerStyle(24 if is_up else 25)
        hist.Draw("HIST SAME")
        legend.AddEntry(hist, hist.GetName().rsplit("_gt")[1], "l")

        yield_variation = hist.Integral() / Nominal_hist.Integral()
        print("Systematic varied yield (%s): %.3f" % (hist.GetName(), yield_variation))

    legend.Draw()

    # Bottom pad for the ratio plot
    canvas.cd(2)

    # Create the ratio histograms
    ratio_histograms = []
    min_ratio = float('inf')  # Initialize minimum ratio
    max_ratio = -float('inf')  # Initialize maximum ratio

    # Create variables to track the range considering error bars
    min_ratio_with_error = float('inf')
    max_ratio_with_error = -float('inf')

    for i, hist in enumerate(histograms):
        ratio_hist = hist.Clone(hist.GetName() + "_ratio")
        ratio_hist.Divide(Nominal_hist)
        ratio_hist.SetLineColor(color_list[i])
        ratio_hist.SetMarkerColor(color_list[i])
        ratio_hist.SetMarkerStyle(24 if 'Up' in hist.GetName() else 25)
        ratio_histograms.append(ratio_hist)

        # Find min and max ratio values to set y-axis range later
        for bin in range(1, ratio_hist.GetNbinsX() + 1):
            ratio_value = ratio_hist.GetBinContent(bin)
            ratio_error = ratio_hist.GetBinError(bin)

            # Consider the ratio and its error to adjust the range
            min_ratio_with_error = min(min_ratio_with_error, ratio_value - ratio_error)
            max_ratio_with_error = max(max_ratio_with_error, ratio_value + ratio_error)

            # Update the min and max ratio without considering the error
            if ratio_value < min_ratio:
                min_ratio = ratio_value
            if ratio_value > max_ratio:
                max_ratio = ratio_value

    # Set up ratio plot
    ratio_histograms[0].SetTitle("")  # Remove the title
    ratio_histograms[0].GetYaxis().SetTitle("Ratio")
    
    # Dynamically adjust the y-axis range based on the ratio values and error bars
    # Add some padding to the min/max ratio
    padding = 0.1  # 10% padding for both min and max
    ratio_range_min = min_ratio_with_error - padding * (max_ratio_with_error - min_ratio_with_error) if min_ratio_with_error > 0 else 0
    ratio_range_max = max_ratio_with_error + padding * (max_ratio_with_error - min_ratio_with_error)

    # If the ratio values are too small or too large, adjust the range manually
    if ratio_range_min < 0:
        ratio_range_min = 0
    if ratio_range_max < 0:
        ratio_range_max = 2  # Default to 2 for ratios

    ratio_histograms[0].GetYaxis().SetRangeUser(ratio_range_min, ratio_range_max)
    ratio_histograms[0].GetXaxis().SetTitle(Nominal_hist.GetXaxis().GetTitle())
    ratio_histograms[0].Draw("E1")  # Draw first ratio histogram

    # Draw the remaining ratio histograms
    for i in range(1, len(ratio_histograms)):
        ratio_histograms[i].Draw("E1 SAME")

    # Save the canvas
    canvas.SaveAs(output_path)
    canvas.Close()



# Create dictionaries to store histograms based on the criteria
# Create dictionaries to store histograms based on the criteria for topSig, topBkg, and ewkBkg
histogram_categories = {
    'topSig': {
        'jes': [],
        'bweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    },
    'topBkg': {
        'jes':[],
        'bweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    },
    'ewkBkg': {
        'jes':[],
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
            elif substring + "ISR" in hist_name or substring +"FSR" in hist_name:
                histogram_categories[category]['isr_fsr'].append(hist)
            elif substring + "hdamp" in hist_name:
                histogram_categories[category]['hdamp'].append(hist)
            elif substring + "jes" in hist_name:
                histogram_categories[category]['jes'].append(hist)
            elif substring == hist_name:
                histogram_categories[category]['nominal'] = hist

# Function to draw histograms based on the categories
def plot_variations(category, year, lep, output_dir):
    nominal_hist = histogram_categories[category]['nominal']
    nominal_hist.SetLineColor(ROOT.kBlack)

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

    if histogram_categories[category]['jes']:
        print("\n  = = = = = = = = =  =      "+ category +" jes       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['jes'],
                        f"canvas_{category}_jes", f"{category} jes Variations",
                        os.path.join(output_dir, f"{category}_jes_variations_{year}_{lep}.png"))


# Plot histograms for all categories
for category in categories.keys():
    plot_variations(category, year, lep, output_dir)

# Close the root file
root_file.Close()

