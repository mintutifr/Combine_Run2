import ROOT as R
import numpy as np
import math

def text():
    lumitext = R.TPaveText(0.80555, 0.93, 0.89555, 0.95, "brNDC")
    lumitext.SetFillStyle(0)
    lumitext.SetBorderSize(0)
    lumitext.SetMargin(0)
    lumitext.SetTextFont(42)
    lumitext.SetTextSize(0.03)
    lumitext.SetTextAlign(33)
    lumitext.AddText("59.2 fb^{-1} (13 TeV, 2018)")
    lumitext.GetListOfLines().Last().SetTextFont(42)

    cmstext = R.TPaveText(0.36, 0.86, 0.48, 0.88, "brNDC")
    cmstext.SetFillStyle(0)
    cmstext.SetBorderSize(0)
    cmstext.SetMargin(0)
    cmstext.SetTextFont(42)
    cmstext.SetTextSize(0.05)
    cmstext.SetTextAlign(33)
    cmstext.AddText("#bf{CMS} #it{Preliminary}")
    cmstext.GetListOfLines().Last().SetTextFont(42)

    finalstat = R.TPaveText(0.24, 0.80, 0.35, 0.825, "brNDC")
    finalstat.SetFillStyle(0)
    finalstat.SetBorderSize(0)
    finalstat.SetMargin(0)
    finalstat.SetTextFont(42)
    finalstat.SetTextSize(0.05)
    finalstat.SetTextAlign(33)
    finalstat.AddText("#it{l^{#pm}, 2J1T}")
    finalstat.GetListOfLines().Last().SetTextFont(42)

    cntrl0 = R.TPaveText(0.24, 0.72, 0.33, 0.75, "brNDC")
    cntrl0.SetFillStyle(0)
    cntrl0.SetBorderSize(0)
    cntrl0.SetMargin(0)
    cntrl0.SetTextFont(42)
    cntrl0.SetTextSize(0.03)
    cntrl0.SetTextAlign(33)
    cntrl0.AddText(" BDT > 0.82 ")

    lumitext.Draw()
    cmstext.Draw()
    finalstat.Draw()
    # cntrl0.Draw()

def get_linearity_plot(M_true, M_fit, Ey1, Size, variable="S", BDTCUT="0p8"):
    Num_points = Size
    print("size of the array:", Num_points)
    
    masspoint = R.TGraphErrors(Num_points, np.array(M_true), np.array(M_fit), np.zeros(Num_points), np.array(Ey1))
    masspoint.SetMarkerStyle(20)
    masspoint.SetLineWidth(2)
    
    f1 = R.TF1("f1", "pol1")
    f1.SetLineWidth(2)
    
    c1 = R.TCanvas("c1", "", 800, 700)
    R.gStyle.SetOptFit()
    c1.cd()
    
    pad1 = R.TPad("pad1", "pad1", 0.0, 0.0, 1.0, 1.0)
    pad1.Draw()
    pad1.cd()
    pad1.SetLeftMargin(0.12)
    
    masspoint.Fit("f1", "C", "", M_true[0] - 0.5, M_true[Num_points - 1] + 0.5)
    
    grint = R.TGraphErrors(Num_points)
    grint.SetTitle("")
    
    for i in range(Num_points):
        grint.SetPoint(i, masspoint.GetX()[i], 0)
    
    R.TVirtualFitter.GetFitter().GetConfidenceIntervals(grint)
    grint.Print()
    grint.SetLineColor(R.kRed)
    
    if variable == "M":
        grint.GetXaxis().SetTitle("m_{True} (GeV)")
        grint.GetYaxis().SetTitle("m_{Fit} (GeV)")
        grint.GetYaxis().SetTitleOffset(1.4)
        grint.SetMaximum(M_fit[Num_points - 1] + 1)
        grint.SetMinimum(M_fit[0] - 2)
    elif variable == "S":
        grint.GetXaxis().SetTitle("#Gamma (GeV)")
        grint.GetYaxis().SetTitle("#sigma_{Fit} (GeV)")
        grint.GetYaxis().SetTitleOffset(1.7)
        grint.SetMaximum(M_fit[Num_points - 1] + 0.3)
        grint.SetMinimum(M_fit[0] - 0.3)
    
    grint.Draw("ap")
    masspoint.Draw("psame")
    pad1.Update()
    c1.Update()
    
    ps = pad1.GetPrimitive("stats")
    ps.SetX1NDC(0.5)
    ps.SetX2NDC(0.85)
    ps.SetY1NDC(0.2)
    ps.SetY2NDC(0.33)
    ps.SetBorderSize(0)
    
    text()
    
    if variable == "S":
        variable = "fit_Sigma"
    if variable == "M":
        variable = "fit_Mass"
    
    outfilename = "Plots/Linearity_" + variable + "_" + BDTCUT
    c1.Print(outfilename + ".png")
    c1.Print(outfilename + ".pdf")
    c1.Print(outfilename + ".C")
    
# Example usage:
# M_true = [...]  # Fill in your data
# M_fit = [...]   # Fill in your data
# Ey1 = [...]     # Fill in your data
# get_linearity_plot(M_true, M_fit, Ey1)


"""def get_realWidth(h1, fitvalue, par0, par1, par2, Variable="M",poli = "pol1"):
    offset = fitvalue*fitvalue*par2 + fitvalue*par1 + par0
    bin = h1.FindBin(fitvalue)
    res = 0

    if(Variable == "M"):
        print(f"offset = Mfitmass*{par1} + ({par0})")
        print(f"#Delta M corresponding to mfit({fitvalue}) = {offset}")
        print(f"corresponding uncertainty = {h1.GetBinError(bin)}")
        print(f"true mass = {fitvalue + offset}")
        res = fitvalue + offset

    if(Variable == "S"):
        print(f"Resolution = FitSigma*FitSigma*{par2} + (FitSigma*{par1}) + {par0}")
        print(f"Resolution corresponding to FitSigma({fitvalue}) = {offset}")
        print(f"corresponding uncertainty = {h1.GetBinError(bin)}")
        True_Width_Square = fitvalue*fitvalue - offset*offset
        print(f"True Width Square = {True_Width_Square}")

        if True_Width_Square > 0:
            print(f"True Width = {R.TMath.Sqrt(True_Width_Square)}")
            res = R.TMath.Sqrt(True_Width_Square)
        else:
            print(f"True Width is negative = {True_Width_Square}")

    return res

# Example usage:
# h1 = ...  # Your TH1D histogram
# fitvalue = ...
# par0 = ...
# par1 = ...
# par2 = ...
# result = get_realWidth(h1, fitvalue, par0, par1, par2, "M")"""

def get_calibrated_mass(h1,mass,sigmaG,m,c): #linear for now
    lnmass = math.exp(mass+(sigmaG*sigmaG)/2)
    cali_error = h1.GetBinError(h1.FindBin(lnmass))
    deltaM = lnmass*m+c
    mass_calibrated = lnmass+deltaM
    #print(mass_calibrated)
    return [mass_calibrated,cali_error]
 
def get_calibrated_width(h1,mass,sigmaG,m,c): #linear for now
    lnsigma = math.sqrt(math.exp(2*mass+sigmaG*sigmaG)*(math.exp(sigmaG*sigmaG)-1))
    cali_error = h1.GetBinError(h1.FindBin(lnsigma))
    resolution = lnsigma*m+c
    print(lnsigma*lnsigma-resolution*resolution)
    width_calibrated = math.sqrt(lnsigma*lnsigma-resolution*resolution)
    return [width_calibrated,cali_error]


def get_calib_hist(M_fit, detaM, EM_Fit, Size, variable="S", BDTCUT="0p8", poli="pol1"):
    Num_points = Size
    mini = M_fit[0]
    maxi = M_fit[0]

    for i in range(Num_points):
        if M_fit[i] < mini:
            mini = M_fit[i]
        if M_fit[i] > maxi:
            maxi = M_fit[i]

    deltamass = R.TGraphErrors(Num_points,np.array(M_fit),np.array(detaM),np.zeros(Num_points),np.array(EM_Fit))
    deltamass.SetMarkerStyle(20)
    deltamass.SetLineWidth(2)

    if variable == "M":
        deltamass.GetYaxis().SetTitle("#Delta m (GeV)")
        deltamass.GetXaxis().SetTitle("m_{Fit} (GeV)")
        deltamass.GetYaxis().SetTitleOffset(1.25)
        
    else:
        deltamass.GetYaxis().SetTitle("Resolution (GeV)")
        deltamass.GetXaxis().SetTitle("#sigma (GeV)")
        

    c2 = R.TCanvas("c2", "", 800, 700)
    R.gStyle.SetOptFit()
    c2.cd()

    pad1 = R.TPad("pad1", "pad1", 0.0, 0.0, 1.0, 1.0)
    pad1.Draw()
    pad1.cd()
    pad1.SetLeftMargin(0.12)
    #pad1.SetTicky()
    #pad1.SetTickx()
    #pad1.GetGridy().SetMaximum(Data.GetMaximum() * 1.2)
    #pad1.SetRightMargin(0.143)
    
    f1 = R.TF1("f1", poli)
    f1.SetLineWidth(2)

    if variable == "M":
        deltamass.Fit("f1", "C", "", M_fit[0] - 0.2, M_fit[Num_points - 1] + 0.2)
        deltamass.SetMaximum(detaM[Num_points - 1] + 1)
        deltamass.SetMinimum(detaM[0] - 2)
        deltamass.SetTitle("")
        deltamass.Draw("Ap")
    else:
        deltamass.Fit("f1", "C", "", M_fit[0] - 0.0001, M_fit[Num_points - 1] + 0.0001)
        deltamass.SetMaximum(detaM[Num_points - 1] + 1)
        deltamass.SetMinimum(detaM[0] - 1)
        deltamass.SetTitle("")
        deltamass.Draw("Ap")

    print(M_fit[0], ":", M_fit[Num_points - 1])

    hban = R.TH1D("hban", "", 100, M_fit[0] - 0.0001, maxi + 0.0001)
    cl = 0.68
    R.TVirtualFitter.GetFitter().GetConfidenceIntervals(hban, cl)
    hban.SetStats(False)
    hban.SetLineColor(2)

    c2.Update()
    ps1 = pad1.GetPrimitive("stats")
    ps1.SetX1NDC(0.5)
    ps1.SetX2NDC(0.85)
    ps1.SetY1NDC(0.2)
    ps1.SetY2NDC(0.33)
    ps1.SetBorderSize(0)
    hban.Draw("e1 same")

    text()

    """if(variable=="M"):

        offset_truemass(hban,M_fit[1],f1->GetParameter(0),f1->GetParameter(1),"M");
       
    }
    if(variable=="S"):
        for (int i=0; i<Num_points; i++)   get_realWidth(hban,M_fit[i],f1->GetParameter(0),f1->GetParameter(1),f1->GetParameter(2),"S");
    
    }"""
    
    
    if variable == "S":
        variable = "fit_Sigma"
    if variable == "M":
        variable = "fit_Mass"

    outfilename = "Plots/Calibration_" + poli + "_" + variable + "_" + BDTCUT
    c2.Print(outfilename + ".png")
    c2.Print(outfilename + ".pdf")
    c2.Print(outfilename + ".C")
    
    return hban

def plot_mass_vs_width(M_fit, M_fit_Error, S_fit, S_fit_Error):
    massVSwidth = R.TGraphErrors(5, S_fit, M_fit, S_fit_Error, M_fit_Error)
    massVSwidth.SetMarkerStyle(20)
    massVSwidth.SetLineWidth(2)
    massVSwidth.GetYaxis().SetTitle("m_{Fit} (GeV)")
    massVSwidth.GetXaxis().SetTitle("#sigma_{Fit} (GeV)")
    massVSwidth.GetYaxis().SetRangeUser(165.0, 172.0)
    massVSwidth.GetXaxis().SetRangeUser(25.0, 35.0)

    c3 = R.TCanvas("c3", "", 600, 600)
    R.gStyle.SetOptFit()
    c3.cd()
    pad1 = R.TPad("pad1", "pad1", 0.0, 0.0, 1.0, 1.0)
    pad1.Draw()
    pad1.cd()
    pad1.SetLeftMargin(0.12)

    massVSwidth.SetTitle("")
    massVSwidth.Draw("Ap")

    text()

    pad1.Update()
    c3.Update()

# Example usage:
# M_fit = [...]  # Fill in your data
# detaM = [...]  # Fill in your data
# EM_Fit = [...]  # Fill in your data
# get_calib_hist(M_fit, detaM, EM_Fit)
# Plot_Mass_Vs_width(M_fit, M_fit_Error, S_fit, S_fit_Error)


if __name__ == '__main__':

    M_true = [169.5, 171.5, 172.5, 173.5, 175.5]
    Nomi_width = 1.322
    Width_true = [0.75, 0.9, 1.31, 1.5, 1.7, 1.9]
    
    M_fit_2018_AltMass_DNN_gt0p8 = [162.336,163.752,164.281,164.698,165.472]
    Error_M_fit_2018_AltMass_DNN_gt0p8 = [0.236, 0.243, 0.245, 0.248, 0.257]
    detaM_2018_AltMass_DNN_gt0p8 = [7.164,7.748,8.219,8.802,10.028]
    Error_detaM_2018_AltMass_DNN_gt0p8 = []

    gamma_fit_2018_AltWidth_DNN_gt0p8 = [0.11410,0.11424,0.11463,0.11466,0.11477,0.11471]
    Error_gamma_fit_2018_AltWidth_DNN_gt0p8 = [0.00111,0.00111,0.00111,0.00115,0.00111,0.00114]
    S_fit_2018_AltWidth_DNN_gt0p8 = [18.799, 18.823, 18.893,  18.898, 18.918, 18.908]
    Error_S_fit_2018_AltWidth_DNN_gt0p8 = [0.196, 0.196, 0.197,  0.203, 0.195, 0.202]
    Reso_2018_AltWidth_DNN_gt0p8 = [18.784, 18.801, 18.848, 18.839, 18.841, 18.812]
    Error_Reso_2018_AltWidth_DNN_gt0p8 = [0.196, 0.196, 0.196,  0.202, 0.195, 0.201]
    
    # remove top bkg from histogram results
 
    """M_fit_2018_AltMass_DNN_gt0p8 = [162.063,163.552,164.112,164.554,165.373]
    Error_M_fit_2018_AltMass_DNN_gt0p8 = [0.233,0.239,0.241,0.244,0.254]
    detaM_2018_AltMass_DNN_gt0p8 = [7.437,7.948,8.388,8.946,10.127]
    
    S_fit_2018_AltWidth_DNN_gt0p8 = [18.351,18.374,18.442,18.445,18.464,18.455]
    Error_S_fit_2018_AltWidth_DNN_gt0p8 = [0.183,0.186,0.183,0.185,0.184,0.188]
    Reso_2018_AltWidth_DNN_gt0p8 = [18.336,18.352,18.395,18.384,18.385,18.357]
    Error_Reso_2018_AltWidth_DNN_gt0p8 = [0.183,0.186,0.183,0.185,0.183,0.187]

    mass = 5.0943
    sigmaG = 0.112
    print(get_calibrated_mass(hband_mass,mass,sigmaG,0.7657,-117))
    print(get_calibrated_width(hband_width,mass,sigmaG,0.3879,11.22))"""
    
    
    get_linearity_plot(M_true, M_fit_2018_AltMass_DNN_gt0p8, Error_M_fit_2018_AltMass_DNN_gt0p8,len(M_true), variable="M", BDTCUT="gt0p7_UL2018")
    hband_mass = get_calib_hist(M_fit_2018_AltMass_DNN_gt0p8, detaM_2018_AltMass_DNN_gt0p8, Error_M_fit_2018_AltMass_DNN_gt0p8,len(M_fit_2018_AltMass_DNN_gt0p8), "M", "gt0p7_UL2018", "pol1")
    
    

    get_linearity_plot(Width_true, S_fit_2018_AltWidth_DNN_gt0p8, Error_S_fit_2018_AltWidth_DNN_gt0p8,len(Width_true), variable="S", BDTCUT="gt0p7_UL2018")
    hband_width = get_calib_hist(S_fit_2018_AltWidth_DNN_gt0p8, Reso_2018_AltWidth_DNN_gt0p8, Error_Reso_2018_AltWidth_DNN_gt0p8, len(S_fit_2018_AltWidth_DNN_gt0p8),"S", "gt0p7_UL2018", "pol1")


    mass = 5.095
    sigmaG = 0.11463
    print(get_calibrated_mass(hband_mass,mass,sigmaG,0.8633,-133.3))
    print(get_calibrated_width(hband_width,mass,sigmaG,0.4335,10.64))
    

