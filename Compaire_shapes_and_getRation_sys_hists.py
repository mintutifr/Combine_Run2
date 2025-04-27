import ROOT
from ROOT import TColor
import os, json
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
    TColor.GetColor("#FF5733"), TColor.GetColor("#33FF57"), TColor.GetColor("#3357FF"),
    TColor.GetColor("#FF33A1"), TColor.GetColor("#A133FF"), TColor.GetColor("#FF8C33"),
    TColor.GetColor("#33FFF2"), TColor.GetColor("#FF3380"), TColor.GetColor("#80FF33")
]
# Dictionary to store custom ROOT color IDs

Combine_year_tag={
                'UL2016preVFP' :  "_ULpre16",
                'UL2016postVFP' : "_ULpost16",
                'UL2017' : "_UL17",
                'UL2018' : "_UL18",
                'UL2016' : "_UL16"}


# Function to set histogram style based on systematic type and whether it's Up or Down
def set_histogram_style(hist, syst_type, is_up):
    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(24 if is_up else 25)  # Arrow up for Up, arrow down for Down


def draw_histograms(Nominal_hist, histograms, canvas_name, canvas_title, output_path):
    # Set batch size to 15 histograms per canvas.
    batch_size = 15
    num_batches = (len(histograms) + batch_size - 1) // batch_size
    weight_sys_variation={}
    for batch_index in range(num_batches):
        # Determine the subset (batch) of histograms to draw.
        batch_histograms = histograms[batch_index * batch_size : (batch_index + 1) * batch_size]
        
        # Create the canvas with two pads (top for histograms, bottom for ratio)
        canvas = ROOT.TCanvas(f"{canvas_name}_{batch_index}", canvas_title, 800, 800)
        canvas.Divide(1, 2)
        
        ## Top pad: draw the histograms
        canvas.cd(1)
        ROOT.gStyle.SetOptStat(0)
        legend = ROOT.TLegend(0.7, 0.9 - min(len(batch_histograms) * 0.05, 0.8), 0.9, 0.9)
        legend.SetTextSize(0.03)
        
        # Draw the nominal histogram first
        Nominal_hist.Draw("HIST")
        #Nominal_hist.Print()
        legend.AddEntry(Nominal_hist, "Nominal", "l")
        
        # Draw each systematic histogram from the current batch
        for i, hist in enumerate(batch_histograms):
            is_up = 'Up' in hist.GetName()
            # Adjust the color index if needed.
            color_index = batch_index * batch_size + i
            hist.SetLineColor(color_list[color_index])
            hist.SetMarkerColor(color_list[color_index])
            hist.SetMarkerStyle(24 if is_up else 25)
            # hist.Print()
            hist.Draw("HIST SAME")
            legend.AddEntry(hist, hist.GetName().rsplit("_gt")[1], "l")
            yield_variation = hist.Integral() / Nominal_hist.Integral()
            #print("Systematic varied yield (%s): %.3f" % (hist.GetName(), yield_variation))
            sample = hist.GetName().rsplit("_")[0]+hist.GetName().rsplit("_")[1]
            key = hist.GetName().rsplit("_")[-1]
            if("bWeight" in  hist.GetName()):
                #print("%s: %s: %.3f" % (sample,key, yield_variation))
                weight_sys_variation[f'bWeight_'+key] = round(yield_variation,3)
            if("puWeight" in  hist.GetName()):
                #print("%s: %s: %.3f" % (sample,key, yield_variation))
                weight_sys_variation[key.rsplit("gt")[-1]] = round(yield_variation,3)
            if("SF_Iso" in  hist.GetName()):
                #print(hist.GetName())
                weight_sys_variation[key] = round(yield_variation,3)
        legend.Draw()
        #print(f"{weight_sys_variation = }")

        ## Bottom pad: create the ratio plot
        canvas.cd(2)
        ratio_histograms = []
        
        # Create the nominal ratio histogram: Nominal/ Nominal (all ones)
        nominal_ratio = Nominal_hist.Clone("Nominal_ratio")
        nominal_ratio.Divide(Nominal_hist)
        # Remove error bars for the nominal ratio histogram
        for bin in range(1, nominal_ratio.GetNbinsX() + 1):
            nominal_ratio.SetBinError(bin, 0)
        nominal_ratio.SetLineColor(ROOT.kBlack)
        nominal_ratio.SetMarkerColor(ROOT.kBlack)
        nominal_ratio.SetLineWidth(2)
        ratio_histograms.append(nominal_ratio)
        
        # Initialize range variables including the nominal (which is 1)
        min_ratio = 1.0
        max_ratio = 1.0
        min_ratio_with_error = 1.0
        max_ratio_with_error = 1.0
        
        # Create ratio histograms for each systematic histogram
        for i, hist in enumerate(batch_histograms):
            ratio_hist = hist.Clone(hist.GetName() + "_ratio")
            ratio_hist.Divide(Nominal_hist)
            color_index = batch_index * batch_size + i
            ratio_hist.SetLineColor(color_list[color_index])
            ratio_hist.SetMarkerColor(color_list[color_index])
            ratio_hist.SetMarkerStyle(24 if 'Up' in hist.GetName() else 25)
            ratio_histograms.append(ratio_hist)
            
            # Update y-axis range based on bin values and their errors.
            for bin in range(1, ratio_hist.GetNbinsX() + 1):
                ratio_value = ratio_hist.GetBinContent(bin)
                ratio_error = ratio_hist.GetBinError(bin)
                min_ratio_with_error = min(min_ratio_with_error, ratio_value - ratio_error)
                max_ratio_with_error = max(max_ratio_with_error, ratio_value + ratio_error)
                min_ratio = min(min_ratio, ratio_value)
                max_ratio = max(max_ratio, ratio_value)
        
        # Setup the ratio plot using the nominal ratio histogram as baseline.
        nominal_ratio.SetTitle("")
        nominal_ratio.GetYaxis().SetTitle("Ratio")
        # Add padding to the computed range.
        padding = 0.1
        range_span = max_ratio_with_error - min_ratio_with_error
        ratio_range_min = (min_ratio_with_error - padding * range_span) if min_ratio_with_error > 0 else 0
        ratio_range_max = max_ratio_with_error + padding * range_span
        if ratio_range_min < 0:
            ratio_range_min = 0
        if ratio_range_max < 0:
            ratio_range_max = 2
        
        nominal_ratio.GetYaxis().SetRangeUser(ratio_range_min, ratio_range_max)
        nominal_ratio.GetXaxis().SetTitle(Nominal_hist.GetXaxis().GetTitle())
        # Draw the nominal ratio histogram without error bars (errors have been set to zero)
        nominal_ratio.Draw("E1")
        
        # Draw each systematic ratio histogram (skip the first which is nominal)
        for ratio_hist in ratio_histograms[1:]:
            ratio_hist.Draw("E1 SAME")
        
        # Save the canvas; each batch gets its own file (e.g., plot_0.pdf, plot_1.pdf, etc.)
        batch_output_path = output_path.replace(".png", f"_{batch_index}.png")
        canvas.SaveAs(batch_output_path)
        batch_output_path = output_path.replace(".png", f"_{batch_index}.pdf")
        canvas.SaveAs(batch_output_path)
        canvas.Close()
    print(f"{weight_sys_variation = }")
    return weight_sys_variation

# Create dictionaries to store histograms based on the criteria
# Create dictionaries to store histograms based on the criteria for topSig, topBkg, and ewkBkg
histogram_categories = {
    'topSig': {
        'jes': [],
        'sample':[],
        'jer':[],
        'bweight': [],
        'puweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    },
    'topBkg': {
        'jes':[],
        'sample':[],
        'jer':[],
        'bweight': [],
        'puweight': [],
        'sf_iso': [],
        'isr_fsr': [],
        'hdamp': [],
        'nominal': None
    },
    'ewkBkg': {
        'jes':[],
        'sample':[],
        'jer':[],
        'bweight': [],
        'puweight': [],
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
            if substring + "puWeight" in hist_name:
                histogram_categories[category]['puweight'].append(hist)
            elif substring + "SF_Iso" in hist_name:
                histogram_categories[category]['sf_iso'].append(hist)
            elif substring + "ISR" in hist_name or substring +"FSR" in hist_name:
                histogram_categories[category]['isr_fsr'].append(hist)
            elif substring + "hdamp" in hist_name:
                histogram_categories[category]['hdamp'].append(hist)
            elif substring + "jes" in hist_name:
                histogram_categories[category]['jes'].append(hist)
            elif substring + "jer" in hist_name:
                histogram_categories[category]['jer'].append(hist)
            elif (substring + "erdON" in hist_name or substring + "Gluonmove" in hist_name or substring + "QCDinspired" in hist_name or substring + "TuneCP5up" in hist_name or substring + "TuneCP5down" in hist_name):
                histogram_categories[category]['sample'].append(hist)
            elif substring == hist_name:
                histogram_categories[category]['nominal'] = hist

# Function to draw histograms based on the categories
def plot_variations(category, year, lep, output_dir):
    weight_sys = {}
    nominal_hist = histogram_categories[category]['nominal']
    nominal_hist.SetLineColor(ROOT.kBlack)

    if nominal_hist is None:
        print(f"No nominal histogram found for {category}")
        return

    if histogram_categories[category]['bweight']:
        print("\n  = = = = = = = = =  =      "+ category +" bweight       = = = = = = = =  = = = \n")
        if ('bWeight' not in weight_sys.keys()):
            weight_sys['bWeight'] = {}
        weight_sys['bWeight'] = draw_histograms(nominal_hist, histogram_categories[category]['bweight'],
                        f"canvas_{category}_bweight", f"{category} bWeight Variations",
                        os.path.join(output_dir, f"{category}_bweight_variations_{year}_{lep}.png"))
        #print(f'{weight_sys_btag = }')

    if histogram_categories[category]['puweight']:
        print("\n  = = = = = = = = =  =      "+ category +" puweight       = = = = = = = =  = = = \n")
        if ('puWeight' not in weight_sys.keys()):
            weight_sys['puWeight'] = {}
        weight_sys['puWeight'] = draw_histograms(nominal_hist, histogram_categories[category]['puweight'],
                        f"canvas_{category}_puweight", f"{category} puWeight Variations",
                        os.path.join(output_dir, f"{category}_puweight_variations_{year}_{lep}.png"))
        #print(f'{weight_sys_btag = }')

    if histogram_categories[category]['sf_iso']:
        print("\n  = = = = = = = = =  =      "+ category +" sf_iso       = = = = = = = =  = = = \n")
        if ('sf_iso' not in weight_sys.keys()):
            weight_sys['sf_iso'] = {}
        weight_sys['sf_iso'] = draw_histograms(nominal_hist, histogram_categories[category]['sf_iso'],
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
    
    if histogram_categories[category]['jer']:
        print("\n  = = = = = = = = =  =      "+ category +" jer       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['jer'],
                        f"canvas_{category}_jer", f"{category} jer Variations",
                        os.path.join(output_dir, f"{category}_jer_variations_{year}_{lep}.png"))

    if histogram_categories[category]['sample']:
        print("\n  = = = = = = = = =  =      "+ category +" sample       = = = = = = = =  = = = \n")
        draw_histograms(nominal_hist, histogram_categories[category]['sample'],
                        f"canvas_{category}_sample", f"{category} jer Variations",
                        os.path.join(output_dir, f"{category}_sample_variations_{year}_{lep}.png"))

    return weight_sys
# Plot histograms for all categories
weight_sys = {}
for category in categories.keys():
    if (category not in weight_sys.keys()):
        weight_sys[category] = {}
    weight_sys[category] = plot_variations(category, year, lep, output_dir)
print(f"\n{weight_sys = }")
json_file_name = f'Weight_sys_{year}_{lep}.json'
with open(json_file_name, "w") as json_file:
        json.dump(weight_sys, json_file, indent=4)

print(f"\nJSON file {json_file_name} saved successfully!")

# Close the root file
root_file.Close()