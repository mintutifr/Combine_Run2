#create workspace
text2workspace.py datacard_DNN_hist_mu.txt -m 172.5 -o workspace_DNN_mu.root

# Run fit
combine -M FitDiagnostics workspace_DNN_mu.root --rMin -2 --rMax 2 -n _M1725_DNNfit_mu  --plots --saveShapes

