#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm> // For std::min_element and std::max_element
#include "TH1F.h"
#include "TF1.h"
#include "TCanvas.h"

using namespace std;

void plot_conductance() {
	    TCanvas *c1 = new TCanvas("c1", "Conductance Histogram", 800, 600);
    ifstream infile("conductance0_450p.dat");  // Change this to your actual file name
    vector<double> conductance;
    double value;

    while (infile >> value) {
        conductance.push_back(value);
    }

    int n_bins = 10;  // Number of bins for the histogram
    double min_value = *min_element(conductance.begin(), conductance.end());
    double max_value = *max_element(conductance.begin(), conductance.end());

    // Calculate bin width
    double bin_width = (max_value - min_value) / n_bins;

    // Adjust max_value to ensure consistent bin width
    max_value = min_value + n_bins * bin_width;

    TH1F *hist = new TH1F("hist", "Conductance Histogram;Conductance;Frequency", n_bins, min_value, max_value);

    for (auto &val : conductance) {
        hist->Fill(val);
    }

    // Fit the histogram with a Gaussian function
    TF1 *gauss_fit = new TF1("gauss_fit", "gaus", min_value, max_value);
    //TF1 *gauss_fit = new TF1("gauss_fit", "gaus", 42, 48);
    hist->Fit("gauss_fit","R");

    double mean = gauss_fit->GetParameter(1);
    double sigma = gauss_fit->GetParameter(2);

    cout << "Mean: " << mean << endl;
    cout << "Sigma: " << sigma << endl;

    hist->Draw();

   	hist->SetTitle("");
	//hist->GetXaxis()->SetRangeUser(7,15);
	//hist->GetYaxis()->SetRangeUser(30,230);
	hist->GetXaxis()->SetTitle("Conductance #muS");

	//hist->SetMarkerStyle(20);
	//hist->SetMarkerColor(1);
	//hist->SetMarkerSize(2);
	hist->SetLineWidth(1);
	hist->SetLineColor(kBlue);


	TLatex *text8 =new TLatex(0.18 ,0.78,"V= 0.5, PW= 100#mus, NoP= 50 ");
   //TLatex *text =new TLatex(0.2 ,0.80,"pp at #sqrt{S}= 0.9 TeV ");
   text8->SetNDC();
   text8->SetTextColor(kBlack);
   text8->SetTextSize(0.035);
   text8->Draw();

   TLegend *leg2=new TLegend(0.15,0.70,0.30,0.94);
leg2->SetTextSize(0.040);
leg2->SetNColumns(2);

TLegendEntry *le11 = leg2->AddEntry(hist,"Conductance","L");


leg2->SetBorderSize(0);
//leg2->Draw();

TLegend *lega=new TLegend(0.10,0.22,0.40,0.30);
lega->SetTextSize(0.04);
lega->SetTextFont(62);
   lega->SetLineColor(kRed);
   lega->SetLineStyle(1);
   lega->SetLineWidth(1);
   lega->SetFillColor(19);
   lega->SetFillStyle(1001);
   TLegendEntry *le101 = lega->AddEntry(gauss_fit,"Gauss Fit","l");
lega->Draw();

    //c1->SaveAs("conductance_histogram.png");  // Save the histogram as a PNG file
}












































