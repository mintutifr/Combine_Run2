import ROOT as R

fitfile = R.TFile.Open("fitDiagnostics_M1725_DNNfit_mu.root")

postfitHist = fitfile.Get("shapes_fit_s/mujets/total");
postfitHist.SetLineColor(R.kRed)
prefitHist = fitfile.Get("shapes_prefit/mujets/total");
prefitHist.SetLineColor(R.kBlue)
postfitHist.Draw("hist")
prefitHist.Draw("hist;same")

raw_input()
