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
    if variable == "M":    constant_array = np.full((len(M_true)), 172.5)  
    elif variable == "S":  constant_array = np.full((len(M_true)), 1.4)
    print(f'{constant_array = }')
    print(f'{np.array(M_true) = }')
    M_true_ori_shift = np.subtract(np.array(M_true),constant_array)
    print(f'{M_true_ori_shift = }')
    masspoint = R.TGraphErrors(Num_points, M_true_ori_shift, np.array(M_fit), np.zeros(Num_points), np.array(Ey1))
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
    
    masspoint.Fit("f1", "C", "", M_true_ori_shift[0] - 0.5, M_true_ori_shift[Num_points - 1] + 0.5)
    
    grint = R.TGraphErrors(Num_points)
    grint.SetTitle("")
    
    for i in range(Num_points):
        grint.SetPoint(i, masspoint.GetX()[i], 0)
    
    R.TVirtualFitter.GetFitter().GetConfidenceIntervals(grint)
    grint.Print()
    grint.SetLineColor(R.kRed)
    
    if variable == "M":
        grint.GetXaxis().SetTitle("m_{True}-172.5 (GeV)")
        if("closer" in BDTCUT):
            grint.GetYaxis().SetTitle("m_{Calibrated} (GeV)")
        else:
            grint.GetYaxis().SetTitle("m_{Fit} (GeV)")
        grint.GetYaxis().SetTitleOffset(1.4)
        grint.SetMaximum(M_fit[Num_points - 1] + 1)
        grint.SetMinimum(M_fit[0] - 2)
    elif variable == "S":
        grint.GetXaxis().SetTitle("#Gamma_{t}-1.4 (GeV)")
        if("closer" in BDTCUT):
            grint.GetYaxis().SetTitle("#sigma_{Calibrated} (GeV)")
        else:
            grint.GetYaxis().SetTitle("#sigma_{Fit} (GeV)")
        grint.GetYaxis().SetTitleOffset(1.7)
        grint.SetMaximum(M_fit[0] + 1.5)
        grint.SetMinimum(M_fit[Num_points - 1] - 1.5)
        print(M_fit[0],M_fit[Num_points - 1])
    
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
    #print(lnsigma*lnsigma-resolution*resolution)
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

    M_true = [169.5, 170.5,171.5, 172.5, 173.5, 174.5,175.5]
    Width_true = [0.75, 0.9,1.1, 1.3, 1.4,1.5, 1.7, 1.9]
    
    M_fit_2018_AltMass_DNN_gt0p7 = []
    Error_M_fit_2018_AltMass_DNN_gt0p7 = []
    detaM_2018_AltMass_DNN_gt0p7 = []
    Error_detaM_2018_AltMass_DNN_gt0p7 = []

    gamma_fit_2018_AltWidth_DNN_gt0p7 = []
    Error_gamma_fit_2018_AltWidth_DNN_gt0p7 = []
    S_fit_2018_AltWidth_DNN_gt0p7 = []
    deltaS_fit_2018_AltWidth_DNN_gt0p7 = []
    Error_S_fit_2018_AltWidth_DNN_gt0p7 = []
    Reso_2018_AltWidth_DNN_gt0p7 = []
    Error_Reso_2018_AltWidth_DNN_gt0p7 = []
    
    LnM_AltMassfit_Run2_AltMass_DNN_gt0p7 = [5.093911,5.097217,5.098843,5.102156,5.104430,5.106490,5.110750]
    M_AltMassfit_Run2_AltMass_DNN_gt0p7 = [164.170,164.652,164.918,165.484,165.869,166.237,166.940]
    Error_M_AltMassfit_Run2_AltMass_DNN_gt0p7 = [0.381,0.386,0.389,0.401,0.405,0.402,0.413]
    detaM_Run2_AltMass_DNN_gt0p7 = [5.330,5.848,6.582,7.016,7.631,8.263,8.560]
    gamma_AltMassfit_Run2_AltWidth_DNN_gt0p7 = [0.118247,0.115034,0.114924,0.115910,0.116368,0.117685,0.117314]
    Error_detaM_2018_AltMass_DNN_gt0p7 = []

    LnM_AltWidthfit_Run2_AltMass_DNN_gt0p7 = [5.101839,5.101905,5.101990,5.102077,5.102156,5.102165,5.102252,5.102339]
    gamma_AltWidthfit_Run2_AltWidth_DNN_gt0p7 = [0.115473,0.115559,0.115672, 0.115793,0.115910,0.115917,0.116041,0.116167]
    Error_gamma_AltWidthfit_Run2_AltWidth_DNN_gt0p7 = [0.001455,0.001440,0.001401,0.001419,0.001451,0.001387,0.001528,0.001501]
    S_AltWidthfit_Run2_AltWidth_DNN_gt0p7 = [19.1657,19.1815,19.2024,19.2245,19.2458,19.2471,19.2698,19.2929]
    Error_S_AltWidthfit_Run2_AltWidth_DNN_gt0p7 = [0.264,0.261,0.255,0.258,0.264,0.253,0.277,0.272]
    deltaS_AltWidthfit_Run2_AltWidth_DNN_gt0p7 = [18.416,18.282,18.102,17.925,17.936,17.747,17.570,17.393]
    Reso_Run2_AltWidth_DNN_gt0p7 = [19.151,19.160,19.171,19.181,19.195,19.189,19.195,19.199]
    Error_Reso_Run2_AltWidth_DNN_gt0p7 = [0.264,0.261,0.254,0.257,0.263,0.252,0.276,0.271]

    get_linearity_plot(M_true, M_AltMassfit_Run2_AltMass_DNN_gt0p7, Error_M_AltMassfit_Run2_AltMass_DNN_gt0p7,len(M_true), variable="M", BDTCUT="gt0p7_Run2")
    hband_mass = get_calib_hist(M_AltMassfit_Run2_AltMass_DNN_gt0p7, detaM_Run2_AltMass_DNN_gt0p7, Error_M_AltMassfit_Run2_AltMass_DNN_gt0p7,len(M_AltMassfit_Run2_AltMass_DNN_gt0p7), "M", "gt0p7_Run2", "pol1")
    
    

    get_linearity_plot(Width_true, S_AltWidthfit_Run2_AltWidth_DNN_gt0p7, Error_S_AltWidthfit_Run2_AltWidth_DNN_gt0p7,len(Width_true), variable="S", BDTCUT="gt0p7_Run2")
    hband_width = get_calib_hist(S_AltWidthfit_Run2_AltWidth_DNN_gt0p7, Reso_Run2_AltWidth_DNN_gt0p7, Error_Reso_Run2_AltWidth_DNN_gt0p7, len(S_AltWidthfit_Run2_AltWidth_DNN_gt0p7),"S", "gt0p7_Run2", "pol1")

    calibrated_mass = []
    Error_calibrated_mass = []
    calibrated_width = []
    Error_calibrated_width = []

    # =====  Closer mass =========

    for mass, sigmaG in zip(LnM_AltMassfit_Run2_AltMass_DNN_gt0p7,gamma_AltMassfit_Run2_AltWidth_DNN_gt0p7):
        #print(mass,sigmaG)
        cali_mass, Error_cali_mass = get_calibrated_mass(hband_mass,mass,sigmaG,1.238,-197.8)
        calibrated_mass.append(cali_mass)
        Error_calibrated_mass.append(Error_cali_mass)
    print(f'{calibrated_mass = }')
    print(f'{Error_calibrated_mass = }')

    get_linearity_plot(M_true, calibrated_mass, Error_calibrated_mass,len(M_true), variable="M", BDTCUT="gt0p7_Run2_closer")

   # ======= closer width =======

    for mass, sigmaG in zip(LnM_AltWidthfit_Run2_AltMass_DNN_gt0p7,gamma_AltWidthfit_Run2_AltWidth_DNN_gt0p7):
        #print(mass,sigmaG)
        cali_width, Error_cali_width = get_calibrated_width(hband_width,mass,sigmaG,0.3964,11.56)
        calibrated_width.append(cali_width)
        Error_calibrated_width.append(Error_cali_width)
    print(f'{calibrated_width = }')
    print(f'{Error_calibrated_width = }')
   
    get_linearity_plot(Width_true, calibrated_width, Error_calibrated_width,len(Width_true), variable="S", BDTCUT="gt0p7_Run2_closer")

    """systs = ["PSWeight_ISR_Up", "PSWeight_ISR_Down", "PSWeight_FSR_Up", "PSWeight_FSR_Down","hdamp_Up", "hdamp_Down"]
    masses = [5.09500,5.09502,5.09545,5.09438,5.09504,5.09498]
    sigmaGs = [0.11466,0.11458,0.11473,0.11447,0.11461,0.11464]
    for i,sys in enumerate(systs):
        print("\n===="+sys+"====")
        print("M = ",get_calibrated_mass(hband_mass,masses[i],sigmaGs[i],0.8633,-133.3)[0])
        print("W = ",get_calibrated_width(hband_width,masses[i],sigmaGs[i],0.4335,10.64)[0])

        
    print("PEs")
    mass = 5.107
    error_mass = 0.001594
    sigmaG = 0.1351
    error_sigmaG = 0.00172
    print("M = ",get_calibrated_mass(hband_mass,mass,sigmaG,0.8633,-133.3)[0],get_calibrated_mass(hband_mass,mass+error_mass,sigmaG,0.8633,-133.3)[0],get_calibrated_mass(hband_mass,mass-error_mass,sigmaG,0.8633,-133.3)[0])
    print("Sigma = ",get_calibrated_width(hband_width,mass,sigmaG,0.4335,10.64)[0], get_calibrated_width(hband_width,mass,sigmaG+error_sigmaG,0.4335,10.64)[0], get_calibrated_width(hband_width,mass,sigmaG-error_sigmaG,0.4335,10.64)[0])"""
