import ROOT
f = ROOT.TFile("higgsCombine_M1725.FitDiagnostics.mH120.root")
w = f.Get("w")
w.Print("v")
n_bins = 15
binning = ROOT.RooFit.Binning(n_bins,ROOT.TMath.Log(100.0),ROOT.TMath.Log(300))

can = ROOT.TCanvas()
plot = w.var("logM").frame()
w.data("data_obs").plotOn( plot, binning )

# Load the S+B model
sb_model = w.pdf("model_s").getPdf("eljets_UL18")

# Prefit
sb_model.Print()
sb_model.plotOn( plot, ROOT.RooFit.LineColor(2), ROOT.RooFit.Name("prefit") )

# Postfit
w.loadSnapshot("toyGenSnapshot")
sb_model.plotOn( plot, ROOT.RooFit.LineColor(4), ROOT.RooFit.Name("postfit") )
#r_bestfit = w.var("r").getVal()

plot.Draw()

#leg = ROOT.TLegend(0.55,0.6,0.85,0.85)
#leg.AddEntry("prefit", "Prefit S+B model (r=1.00)", "L")
#leg.AddEntry("postfit", "Postfit S+B model (r=%.2f)"%r_bestfit, "L")
#leg.Draw("Same")

can.Update()
can.SaveAs("part2_sb_model.png")