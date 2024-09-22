#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm> // For std::min_element and std::max_element
#include "TH1F.h"
#include "TF1.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TLatex.h"

using namespace std;

void plot_conductancecopy() {
    // List of filenames, corresponding fit ranges, and x-axis ranges
    vector<string> filenames = {"conductance1v1.dat", "conductance1v1.dat", "conductance1v1.dat", "conductance1v4.dat"};  // Add your filenames here
    vector<pair<double, double>> fit_ranges = {{6.5, 7.5}, {6.5,7.5 }, {6.5, 7.5}, {30, 35}};    // Define your fit ranges here
    vector<pair<double, double>> x_ranges = {{1.5, 3.0}, {1.5, 3.0}, {1.5, 3.0}, {20, 40}};      // Define your x-axis ranges here
    vector<string> text_labels = {"V= 1.0V, PW= 100#muSec, NoP= 1 ", "V= 1V, PW= 100#muSec, NoP= 25 ",
                                "V= 1V, PW= 100#muSec, NoP= 50 ", "V= 1V, PW= 100#muSec, NoP= 100 "};  // Custom text for each pad

    // Create a canvas and divide it into four pads
    TCanvas *c1 = new TCanvas("c1", "Conductance Histograms", 1200, 900);
    c1->Divide(2, 2);  // Divide the canvas into a 2x2 grid

    // Loop over each file
    for (size_t i = 0; i < filenames.size(); ++i) {
        const string& filename = filenames[i];
        const pair<double, double>& fit_range = fit_ranges[i];
        const pair<double, double>& x_range = x_ranges[i];
        const string& text_label = text_labels[i];

        // Switch to the correct pad
        c1->cd(i + 1);

        ifstream infile(filename);  
        vector<double> conductance;
        double value;

        while (infile >> value) {
            conductance.push_back(value);
        }

        // Manually set bin width and number of bins
        double bin_width = 0.1; // Set your desired bin width here
        double min_value = *min_element(conductance.begin(), conductance.end());
        double max_value = *max_element(conductance.begin(), conductance.end());

        // Calculate the number of bins based on the bin width
        int n_bins = static_cast<int>((max_value - min_value) / bin_width);

        // Adjust max_value to ensure consistent bin width
        max_value = min_value + n_bins * bin_width;

        // Create the histogram with specified bin width and number of bins
        TH1F *hist = new TH1F(("hist_" + filename).c_str(), ("Conductance Histogram for " + filename + ";Conductance (#muS);Frequency").c_str(), n_bins, min_value, max_value);

        for (auto &val : conductance) {
            hist->Fill(val);
        }

        // Fit the histogram with a Gaussian function using the specified fit range
        TF1 *gauss_fit = new TF1(("gauss_fit_" + filename).c_str(), "gaus", fit_range.first, fit_range.second);
        hist->Fit(gauss_fit, "R");

        double mean = gauss_fit->GetParameter(1);
        double sigma = gauss_fit->GetParameter(2);

        cout << "File: " << filename << " | Mean: " << mean << " | Sigma: " << sigma << endl;

        // Customize the histogram
        hist->SetTitle("");
        hist->GetXaxis()->SetTitle("Conductance (#muS)");
        hist->SetLineWidth(1);
        hist->SetLineColor(kBlue);

        // Set x-axis range
        hist->GetXaxis()->SetRangeUser(x_range.first, x_range.second);

        // Draw histogram and fit
        hist->Draw();
        gauss_fit->Draw("same");

        // Add text and legends
        TLatex *text = new TLatex(0.18, 0.78, text_label.c_str());
        text->SetNDC();
        text->SetTextColor(kBlack);
        text->SetTextSize(0.035);
        text->Draw();

        TLegend *leg = new TLegend(0.65, 0.70, 0.85, 0.85);  // Adjust position as needed
        leg->SetTextSize(0.040);
        leg->AddEntry(hist, "Conductance", "L");
        leg->AddEntry(gauss_fit, "Gauss Fit", "l");
        leg->SetBorderSize(0);
        leg->Draw();
    }

    // Save the canvas as a PNG file
    //c1->SaveAs("conductance_histograms.png");

    // Clean up to avoid memory leaks
    //delete c1;
}

