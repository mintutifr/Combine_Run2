void text(){

    TPaveText* lumitext = new TPaveText(0.80555, 0.93,0.89555, 0.95, "brNDC");
    lumitext->SetFillStyle(0);
    lumitext->SetBorderSize(0);
    lumitext->SetMargin(0);
    lumitext->SetTextFont(42);
    lumitext->SetTextSize(0.03);
    lumitext->SetTextAlign(33);
    lumitext->AddText("59.2 fb^{-1} (13 TeV, 2018)");((TText*)lumitext->GetListOfLines()->Last())->SetTextFont(42);

    TPaveText* cmstext = new TPaveText(0.36, 0.86, 0.48, 0.88, "brNDC");
    cmstext->SetFillStyle(0);
    cmstext->SetBorderSize(0);
    cmstext->SetMargin(0);
    cmstext->SetTextFont(42);
    cmstext->SetTextSize(0.05);
    cmstext->SetTextAlign(33);
    cmstext->AddText("#bf{CMS} #it{Preliminary}");((TText*)cmstext->GetListOfLines()->Last())->SetTextFont(42);

    TPaveText* finalstat = new TPaveText(0.24, 0.80, 0.35, 0.825, "brNDC");
    finalstat->SetFillStyle(0);
    finalstat->SetBorderSize(0);
    finalstat->SetMargin(0);
    finalstat->SetTextFont(42);
    finalstat->SetTextSize(0.05);
    finalstat->SetTextAlign(33);
    finalstat->AddText(Form("#it{l^{#pm}, 2J1T}"));((TText*)cmstext->GetListOfLines()->Last())->SetTextFont(42);

    TPaveText* cntrl0 = new TPaveText(0.24, 0.72, 0.33, 0.75, "brNDC");
    cntrl0->SetFillStyle(0);
    cntrl0->SetBorderSize(0);
    cntrl0->SetMargin(0);
    cntrl0->SetTextFont(42);
    cntrl0->SetTextSize(0.03);
    cntrl0->SetTextAlign(33);
    //cntrl0->AddText("2J1T, m_{T}^{W}> 50 GeV, BDT > 0.82 ");
    cntrl0->AddText(" BDT > 0.82 ");

    lumitext->Draw(); 
    cmstext->Draw();
    finalstat->Draw();
      	//cntrl0->Draw();	


}
void get_liniority_plot(Float_t M_true[],Float_t M_fit[],Float_t Ey1[],Int_t Size,TString variable = "S",TString BDTCUT="0p8"){

    int Num_points = Size;
    cout<<"size of the array : "<<Num_points<<endl;
    TGraphErrors *masspoint = new TGraphErrors(Num_points,M_true,M_fit,0,Ey1);   
        
    masspoint->SetMarkerStyle(20);
    masspoint->SetLineWidth(2);
    
    TF1 *f1 = new TF1("f1", "pol1");    
    f1->SetLineWidth(2);

    TCanvas *c1 = new TCanvas("c1","", 600,600,600,600);gStyle->SetOptFit();
    c1->cd();//TGaxis::SetMaxDigits(2);

    TPad* pad1 = new TPad("pad1", "pad1", 0.0, 0.0, 1.0, 1.0); 
    pad1->Draw();pad1->cd();
    pad1->SetLeftMargin(0.12);
    masspoint->Fit("f1","C","",M_true[0]-0.5,M_true[Num_points-1]+0.5);
    TGraphErrors *grint = new TGraphErrors(Num_points);
    grint->SetTitle("");
    
    for (int i=0; i<Num_points; i++) grint->SetPoint(i, masspoint->GetX()[i], 0);
    (TVirtualFitter::GetFitter())->GetConfidenceIntervals(grint);
    grint->Print();
    grint->SetLineColor(kRed);
    if(variable=="M"){
        grint->GetXaxis()->SetTitle("m_{True} (GeV)");
        grint->GetYaxis()->SetTitle("m_{Fit} (GeV)");
        grint->GetYaxis()->SetTitleOffset(1.4);
    }
    else if(variable=="S"){
        grint->GetXaxis()->SetTitle("#Gamma (GeV)");
        grint->GetYaxis()->SetTitle("#sigma_{Fit} (GeV)");
        grint->GetYaxis()->SetTitleOffset(1.7);
    }
    grint->Draw("ap");
    masspoint->Draw("psame");
    pad1->Update();
    c1->Update();
    TPaveStats *ps = (TPaveStats*)pad1->GetPrimitive("stats");
    ps->SetX1NDC(0.5);ps->SetX2NDC(0.85);
    ps->SetY1NDC(0.2);ps->SetY2NDC(0.33);
    ps->SetBorderSize(0);

    text();
    if(variable=="S") variable = "fit_Sigma";
    if(variable=="M") variable = "fit_Mass";
    TString outfilename	= "Plots/Linearity_"+variable+"_"+BDTCUT;
    c1->Print(outfilename+".png");
    c1->Print(outfilename+".pdf");
    c1->Print(outfilename+".C");
}


double offset_truemass(TH1D *h1,double fitvalue,double par0,double par1,TString Variable="M"){
    double offset = 0 ;
    offset = fitvalue* par1+par0;
    int bin = h1->FindBin(fitvalue);
    float res = 0;
    if(Variable == "M"){
        cout<<"offset = Mfitmass*"<<par1<<"+("<<par0<<")"<<endl;
        cout<< "#Delta M coressponding to mfit("<<fitvalue<<")= "<<offset<<endl;	
        cout<<"coresponding uncertainty = "<<h1->GetBinError(bin)<<endl;
        cout<<"true mass = "<<fitvalue+offset<<endl;
        res = (fitvalue+offset);
    }
    if(Variable == "S"){
        cout<<"offset = FitSigma*"<<par1<<"+("<<par0<<")"<<endl;
        cout<< "Resolution coressponding to FitSigma("<<fitvalue<<")= "<<offset<<endl;
        cout<<"coresponding uncertainty = "<<h1->GetBinError(bin)<<endl;
        float True_Width_Squre = fitvalue*fitvalue-offset*offset;
        cout<<"True Width Squre = "<<True_Width_Squre<<endl;
        if(True_Width_Squre){
            cout<<"True Width = "<<sqrt(True_Width_Squre)<<endl;
            res = sqrt(True_Width_Squre);
        }
        else cout<<"True Width is negative = "<<True_Width_Squre<<endl;

   }

    return res ;
}

double get_realWidth(TH1D *h1,double fitvalue,double par0,double par1,double par2,TString Variable="M"){
        double offset = 0 ;
        offset = fitvalue*fitvalue*par2+fitvalue*par1+par0;
        int bin = h1->FindBin(fitvalue);
        float res = 0;
        if(Variable == "M"){
                cout<<"offset = Mfitmass*"<<par1<<"+("<<par0<<")"<<endl;
                cout<< "#Delta M coressponding to mfit("<<fitvalue<<")= "<<offset<<endl;
                cout<<"coresponding uncertainty = "<<h1->GetBinError(bin)<<endl;
                cout<<"true mass = "<<fitvalue+offset<<endl;
                res = (fitvalue+offset);
        }
        if(Variable == "S"){
                cout<<"Resolution = FitSigma*FitSigma"<<par2<<"+(FitSigma*"<<par1<<")+"<<par0<<endl;
                cout<< "Resolution coressponding to FitSigma("<<fitvalue<<")= "<<offset<<endl;
                cout<<"coresponding uncertainty = "<<h1->GetBinError(bin)<<endl;
                float True_Width_Squre = fitvalue*fitvalue-offset*offset;
                cout<<"True Width Squre = "<<True_Width_Squre<<endl;
                if(True_Width_Squre){
                        cout<<"True Width = "<<sqrt(True_Width_Squre)<<endl;
                        res = sqrt(True_Width_Squre);
                }
                else cout<<"True Width is negative = "<<True_Width_Squre<<endl;

        }

        return res ;
}

TH1D *get_calib_hist(Float_t M_fit[],Float_t detaM[],Float_t EM_Fit[],Int_t Size,TString variable="S",TString BDTCUT="0p8",TString poli = "pol1"){

    int Num_points = Size;
    float mini = M_fit[0];
    float maxi = M_fit[0];
        
    for(int i=0;i<Num_points;i++){
            if(M_fit[i]<mini) mini=M_fit[i];
            if(M_fit[i]>maxi) maxi=M_fit[i];
    }
         
        
    TGraphErrors *deltamass = new TGraphErrors(Num_points,M_fit,detaM,0,EM_Fit);
    deltamass->SetMarkerStyle(20);
    deltamass->SetLineWidth(2);
    if(variable=="M"){
        deltamass->GetYaxis()->SetTitle("#Delta m (GeV)");
        deltamass->GetXaxis()->SetTitle("m_{Fit} (GeV)");
        deltamass->GetYaxis()->SetTitleOffset(1.25);
    }
    else{
        deltamass->GetYaxis()->SetTitle("Resolution (GeV)");
        deltamass->GetXaxis()->SetTitle("#sigma (GeV)");
    }
    TCanvas *c2 = new TCanvas("c2","", 600,600,600,600);gStyle->SetOptFit();
    c2->cd();
    pad1 = rt.TPad('pad1', 'pad1', 0.0, 0.195259, 1.0, 0.990683)
    pad1.SetBottomMargin(0.089)
    pad1.SetTicky()
    pad1.SetTickx()
    #pad1.GetGridy().SetMaximum(Data.GetMaximum() * 1.2)
    #pad1.SetRightMargin(0.143)
    pad1.Draw()
    pad1.cd()
    pad1.cd()

   
    TF1 *f1 = new TF1("f1", poli); //gStyle->SetErrorY(0);
    f1->SetLineWidth(2);

    if(variable=="M"){
        deltamass->Fit("f1","C","",M_fit[0]-0.2,M_fit[Num_points-1]+0.2);
        deltamass->SetMaximum(detaM[Num_points-1]+1);
        deltamass->SetMinimum(detaM[0]-2);
        deltamass->SetTitle("");
        deltamass->Draw("Ap");
        //deltamass->SetLineColor(0);
        //deltamass->SetMarkerStyle(0);   //deltamass->SetErrorY(0);
    }
    else{
        deltamass->Fit("f1","C","",M_fit[0]-0.0001,M_fit[Num_points-1]+0.0001);
        deltamass->SetMaximum(detaM[Num_points-1]+0.3);
        deltamass->SetMinimum(detaM[0]-0.3);
        deltamass->SetTitle("");
        deltamass->Draw("Ap");
        //deltamass->SetLineColor(0);
        //deltamass->SetMarkerStyle(0);   //deltamass->SetErrorY(0);
    }

    cout<<M_fit[0]<<":"<<M_fit[Num_points-1]<<endl;
    TH1D *hban = new TH1D("hban","", 100,M_fit[0]-0.0001,maxi+0.0001);
    Double_t cl=0.68;
    (TVirtualFitter::GetFitter())->GetConfidenceIntervals(hban,cl);
    hban->SetStats(kFALSE);
    hban->SetLineColor(2);
    hban->Print();

    c2->Update();
    TPaveStats *ps1 = (TPaveStats*)c2->GetPrimitive("stats");
    ps1->SetX1NDC(0.5);ps1->SetX2NDC(0.85);
    ps1->SetY1NDC(0.2);ps1->SetY2NDC(0.33);
    ps1->SetBorderSize(0);
    hban->Draw("e1 same");
    text();
    c2->Update();
    /*if(variable=="M"){
        //c2->Print("Calibration_MFit_VS_DelatM_ALtMass_2016_pol_BDT"+BDTCUT+"_combine.png");
        offset_truemass(hban,M_fit[1],f1->GetParameter(0),f1->GetParameter(1),"M");
        //get_realWidth(hban,M_fit[2],f1->GetParameter(0),f1->GetParameter(1),f1->GetParameter(2),"M");
    }
    if(variable=="S"){
                //c2->Print("Calibration_Fit_Width_VS_Resolution_ALtWidth_2016_pol2_BDT"+BDTCUT+".png");

        for (int i=0; i<Num_points; i++)   get_realWidth(hban,M_fit[i],f1->GetParameter(0),f1->GetParameter(1),f1->GetParameter(2),"S");
    
    }*/
    if(variable=="S") variable = "fit_Sigma";
    if(variable=="M") variable = "fit_Mass";
    TString outfilename = "Plots/Calibration_"+poli+"_"+variable+"_"+BDTCUT;
    c2->Print(outfilename+".png");
    c2->Print(outfilename+".pdf");
    c2->Print(outfilename+".C");
    return hban;
}

void Plot_Mass_Vs_width(Float_t M_fit[],Float_t M_fit_Error[],Float_t S_fit[],Float_t S_fit_Error[]){
    TGraphErrors *massVSwidth = new TGraphErrors(5,S_fit,M_fit,S_fit_Error,M_fit_Error);         
    massVSwidth->SetMarkerStyle(20);
    massVSwidth->SetLineWidth(2);
    massVSwidth->GetYaxis()->SetTitle("m_{Fit} (GeV)");
    massVSwidth->GetXaxis()->SetTitle("#sigma_{Fit} (GeV)");
    massVSwidth->GetYaxis()->SetRangeUser(165.0,172.0);
    massVSwidth->GetXaxis()->SetRangeUser(25.0,35.0);

    TCanvas *c3 = new TCanvas("c3","", 600,600,600,600);gStyle->SetOptFit();
    c3->cd();
    TPad* pad1 = new TPad("pad1", "pad1", 0.0, 0.0, 1.0, 1.0);
    pad1->Draw();pad1->cd();
    pad1->SetLeftMargin(0.12);

    massVSwidth->SetTitle("");
    massVSwidth->Draw("Ap");
    text();
    pad1->Update();
    c3->Update();
}

void Plot_Resol_Vs_width(Float_t Reso_fit[],Float_t Reso_fit_Error[],Float_t Sigma_fit[],Float_t Sigma_Error_fit[]){
        TGraphErrors *massVSwidth = new TGraphErrors(5,Sigma_fit,Reso_fit,Sigma_Error_fit,Reso_fit_Error);
        massVSwidth->SetMarkerStyle(20);
        massVSwidth->SetLineWidth(2);
        massVSwidth->GetXaxis()->SetTitle("#sigma (GeV)");
        massVSwidth->GetYaxis()->SetTitle("Resolution (GeV)");
        massVSwidth->GetYaxis()->SetRangeUser(30.0,35.0);
        massVSwidth->GetXaxis()->SetRangeUser(30.0,35.0);

        TCanvas *c3 = new TCanvas("c3","", 600,600,600,600);gStyle->SetOptFit();
        c3->cd();
        TPad* pad1 = new TPad("pad1", "pad1", 0.0, 0.0, 1.0, 1.0);
        pad1->Draw();pad1->cd();
        pad1->SetLeftMargin(0.12);

        massVSwidth->SetTitle("");
        massVSwidth->Draw("Ap");
        text();
        pad1->Update();
        c3->Update();
}

void Linearity_Calibration(){
        Float_t M_true[] = {169.5, 171.5, 172.5, 173.5, 175.5};
        Float_t M_true3[] = {};
        Float_t Nomi_width = 1.322;
        Float_t Width_true[] = {0.75,0.9,1.31,1.3,1.5,1.7,1.9};

        Float_t M_fit[] = {163.2838341,164.5920519,165.3591872,166.0534958,167.3320229,170.2741866};
        Float_t E_M_fit[] = {0.2704993767,0.2606648828,0.2507255937,0.2628180484,0.2967902964,0.2871214569};
        Float_t detaM[] = {6.216165896,6.907948053,7.140812804,7.446504249,8.167977053,8.225813423};
        Float_t EdeltaM[]={0.4577,0.322229,0.281654,0.271497,0.345145,0.573479};


        Float_t LN_S_fit_2016_AltWidth_BDT_M0p2_8p2_stat0p25[] = {0.186,0.186,0.187,0.189,0.191};
        Float_t Error_LN_S_fit_2016_AltWidth_BDT_M0p2_8p2_stat0p25[] = {0.0006,0.0006,0.0016,0.0016, 0.0022};
        Float_t S_fit_2016_AltWidth_BDT_M0p2_8p2_stat0p25[] = {32.352,32.449,32.600,32.954, 33.345};
        Float_t Error_S_fit_2016_AltWidth_BDT_M0p2_8p2_stat0p25[] = {0.124,0.118,0.304,0.457,0.457};
        Float_t Reso_2016_AltWidth_BDT_M0p2_8p2_stat0p25[]={32.35,32.44,32.57,32.749,32.92};
        Float_t Error_Reso_2016_AltWidth_BDT_M0p2_8p2_stat0p25[]={0.124,0.118,0.304,0.451,0.451};

        Float_t M_fit_2018_AltMass_DNN_gt0p8[] = {161.272,162.686,163.205,163.609,164.372};
        Float_t Error_M_fit_2018_AltMass_DNN_gt0p8[] = {0.236,0.243,0.245,0.248,0.257};
        Float_t detaM_2018_AltMass_DNN_gt0p8[] = {8.2278,8.8137,9.2947,9.8906,11.1277};
        Float_t EdeltaM_2018_AltMass_DNN_gt0p8[]={};
    
        Float_t S_fit_2018_AltWidth_DNN_gt0p8[] = {18.799,18.823,18.893,18.875,18.898,18.918,18.908};
        Float_t Error_S_fit_2018_AltWidth_DNN_gt0p8[] = {0.196,0.196,0.197,0.199,0.203,0.195,0.202};
        Float_t Reso_2018_AltWidth_DNN_gt0p8[]={18.784,18.801,18.848,18.830,18.839,18.841,18.812};
        Float_t Error_Reso_2018_AltWidth_DNN_gt0p8[]={0.196,0.196,0.196,0.199,0.202,0.195,0.201};

        //get_liniority_plot(Width_true,S_fit_2018_AltWidth_DNN_gt0p8,Error_S_fit_2018_AltWidth_DNN_gt0p8,sizeof(Width_true)/sizeof(Width_true[0]),"S","gt0p7_UL2018");
    
        TH1D *hband_width = new TH1D("hband_width","", 100, S_fit_2018_AltWidth_DNN_gt0p8[0]-1, S_fit_2018_AltWidth_DNN_gt0p8[6]+1);
        
        hband_width = get_calib_hist(S_fit_2018_AltWidth_DNN_gt0p8, Reso_2018_AltWidth_DNN_gt0p8, Error_Reso_2018_AltWidth_DNN_gt0p8,sizeof(Width_true)/sizeof(Width_true[0]),"S","gt0p7_UL2018","pol1");
       

        //Float_t M_fit_2016_AltMass_BDT_M0p2_8p2[] = {167.700,169.676,170.976};
        //Float_t Error_M_fit_2016_AltMass_BDT_M0p2_8p2[] = {0.120,0.099,0.155};
        //Float_t deltaM_2016_AltMass_BDT_M0p2_8p2[] = {1.800,2.824,4.525};


        //get_liniority_plot(M_true,M_fit_2018_AltMass_DNN_gt0p8,Error_M_fit_2018_AltMass_DNN_gt0p8,sizeof(M_true)/sizeof(M_true[0]),"M","gt0p7_UL2018");
        TH1D *hband_mass = new TH1D("hband_mass","", 100, M_fit_2018_AltMass_DNN_gt0p8[0]-1, M_fit_2018_AltMass_DNN_gt0p8[4]+1);
        hband_mass = get_calib_hist( M_fit_2018_AltMass_DNN_gt0p8, detaM_2018_AltMass_DNN_gt0p8,Error_M_fit_2018_AltMass_DNN_gt0p8,sizeof(M_true)/sizeof(M_true[0]),"M","gt0p7_UL2018","pol2");
        

}
