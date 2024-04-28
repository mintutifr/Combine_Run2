import ROOT
from  Linearity_Calibration import *
import math

def fit_gauss(hist,variable):
    can = ROOT.TCanvas("can", "can",800,700)
    can.Divide(1, 2)

    # Create a RooRealVar to represent the variable
    """if("mean" in variable):
        x = ROOT.RooRealVar("x", "x", 5.098, 5.102)

    hist.Print()
    # Create a RooDataSet from the histogram
    data = ROOT.RooDataHist("data","data",ROOT.RooArgList(x),hist)

    frame = x.frame(ROOT.RooFit.Title(" "))  # Frame definition

    data.plotOn(frame, ROOT.RooFit.MarkerSize(0.9))  # Data definition

    sigma = ROOT.RooRealVar("sigma", "sigma", 1.0, 0.1, 5.0)
    mean = ROOT.RooRealVar("mean", "mean", 5.0, 0.0, 10.0)
    gauss = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)

    res = gauss.fitTo(data, ROOT.RooFit.SumW2Error(ROOT.kTRUE), ROOT.RooFit.Save())

    gauss.plotOn(frame, ROOT.RooFit.Name("Fit"))
    gauss.paramOn(frame)
    frame.Draw()
    can.Draw()"""
    hist.SetLineWidth(2)
    hist.Draw("hist")
    can.SaveAs("Plots/"+variable+"_Gauss_fit.png")
    can.SaveAs("Plots/"+variable+"_Gauss_fit.pdf")
    #return res


def unbinned_gaussian_fit(data,variable):
    # Define the Gaussian PDF
    if("mean" in variable):
        #x = ROOT.RooRealVar("x", "x", 5.095, 5.105)
        #sigma = ROOT.RooRealVar("sigma", "sigma", 0.004, 0.0001, 0.01)
        x = ROOT.RooRealVar("x", "x",174.5, 177.5)
        mean = ROOT.RooRealVar("mean", "mean", 175.0, 174.5, 177.5)
        sigma = ROOT.RooRealVar("sigma", "sigma", 2.0, 0.1, 3)
    if("sigmaG" in variable):
        x = ROOT.RooRealVar("x", "x", 0.146, 0.154)
        mean = ROOT.RooRealVar("mean", "mean", 0.15, 0.146, 0.154)
        sigma = ROOT.RooRealVar("sigma", "sigma", 0.004, 0.0001, 0.01)
   
    gauss = ROOT.RooGaussian("gauss", "gauss", x, mean, sigma)
    
    
    # Create a Gaussian PDF fit result
    x.setRange("signal",0.147, 0.153) 
    fit_result = gauss.fitTo(data, ROOT.RooFit.Save())#,ROOT.RooFit.Range("signal"))

    # Create a RooPlot for visualization
    frame = x.frame()
    data.plotOn(frame)
    gauss.plotOn(frame)
    gauss.paramOn(frame,ROOT.RooFit.Layout(0.53, 0.87, 0.88))

    # Create a canvas and draw the fit result
    canvas = ROOT.TCanvas("canvas", "Unbinned Gaussian Fit")
    frame.Draw()
    canvas.Draw()
    canvas.SaveAs("Plots/"+variable+"_Gauss_fit.png")
    canvas.SaveAs("Plots/"+variable+"_Gauss_fit.pdf")

    # Return the fit result
    #return fit_result

def get_calibrated_mass(mass,sigmaG,m,c): #linear for now
    lnmass = math.exp(mass+(sigmaG*sigmaG)/2)
    deltaM = lnmass*m+c
    mass_calibrated = lnmass+deltaM
    #print(mass_calibrated)
    return mass_calibrated
 
def get_calibrated_width(mass,sigmaG,m,c): #linear for now
    lnsigma = math.sqrt(math.exp(2*mass+sigmaG*sigmaG)*(math.exp(sigmaG*sigmaG)-1))
    resolution = lnsigma*m+c
    #print(lnsigma,resolution)
    width_calibrated = math.sqrt(lnsigma*lnsigma-resolution*resolution)
    return width_calibrated

def histo_fill(filename="higgsCombine_M1725.FitDiagnostics.mH120.123456.root",variable = "trackedParam_mean"):
    Filename = ROOT.TFile(filename, "READ")
    tree = Filename.Get("limit")
    #tree.GetListOfLeaves().Print()
    #fit_gauss(tree)
    # Create a histogram
    if("mean" in variable):
        histogram = ROOT.TH1F("histogram", "Example Histogram", 1000, 5.09995, 5.10005)  # Define histogram
    if("sigmaG" in variable):
        histogram = ROOT.TH1F("histogram", "Example Histogram", 1000, 0.1, 0.2)  # Define histogram
    print(tree.GetEntries())
    # Loop through TTree entries and fill the histogram
    max_value = -100
    min_value = 100
    if("mean" in variable):
        #x = ROOT.RooRealVar("x", "x", 5.095, 5.105)
        x = ROOT.RooRealVar("x", "x", 174.5, 177.5)
    if("sigmaG" in variable):
        x = ROOT.RooRealVar("x", "x", 0.146, 0.154)
    # Create a dataset
    data = ROOT.RooDataSet("data", "Dataset", ROOT.RooArgSet(x))

    
    
    
    for entry in tree:
        # Access the variable you want to fill into the histogram (e.g., "your_variable")
        mass = entry.GetLeaf("trackedParam_mean").GetValue()
        sigmaG = entry.GetLeaf("trackedParam_sigmaG").GetValue()
        if("mean" in variable):
            #value = mass
            #print(value)
            value=get_calibrated_mass(mass,sigmaG,0.8633,-133.3)
        if("sigmaG" in variable):
            value = sigmaG
            #print(value)
            get_calibrated_width(mass,sigmaG,0.4335,10.64)
        x.setVal(value)  # Replace "your_variable" with the actual variable name in the TTree
        data.add(ROOT.RooArgSet(x))
        if(max_value<value):max_value = value
        if(min_value>value):min_value = value
        # Fill the histogram
        histogram.Fill(value)
    print(max_value,min_value)
    histogram.SetDirectory(0)
    return data

if __name__ == '__main__':
    ROOT.gROOT.SetBatch(ROOT.kTRUE)  # Set batch mode to avoid GUI
    variable = "trackedParam_sigmaG"
    hist = histo_fill("higgsCombine_M1725.MultiDimFit.mH120.123456.root", variable)
    hist.Print()
    unbinned_gaussian_fit(hist,variable)
    #fit_gauss(hist,variable)