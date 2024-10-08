#include <TCanvas.h>
#include <TPad.h>
#include <TGraph.h>
#include <TF1.h>
#include <TAxis.h>
#include <TLegend.h>
#include <TStyle.h>

void IVPlot() {
    // Set style for publication quality
    gStyle->SetOptStat(0); // Disable statistics box
    gStyle->SetPadTickX(1); // Ticks on the upper axis
    gStyle->SetPadTickY(1); // Ticks on the right axis

    // Open the main data file and read data
    ifstream infile("M3IVData.dat"); // Replace with your actual main data file
    std::vector<double> voltage, current;
    double v, i;

    while (infile >> v >> i) {
        voltage.push_back(v);
        current.push_back(i);
    }

    // Create a TGraph for the main plot
    TGraph *graph = new TGraph(voltage.size(), &voltage[0], &current[0]);
    graph->SetTitle("Memristor I-V Characteristic Curve ");
    graph->SetMarkerStyle(20);
    graph->SetMarkerSize(0.0);
    graph->SetMarkerColor(kBlue); // Best color for publication
    graph->SetLineColor(kBlue);
    graph->SetLineWidth(2);

    // Create a canvas with a balanced aspect ratio
    TCanvas *c1 = new TCanvas("c1", "I-V Plot with Fits", 800, 1000); // Balanced width and height
    c1->SetGrid();

    // Create a pad within the canvas
    TPad *pad = new TPad("pad", "The pad", 0.02, 0.02, 0.98, 0.98);
    //pad->SetAspectRatio(1); // Maintain a 1:1 aspect ratio
    pad->Draw();
    pad->cd();

    // Draw the main graph
    graph->Draw("APL");

    // Customize the axes
    graph->GetXaxis()->SetTitle("Voltage (V)");
    graph->GetYaxis()->SetTitle("Current (#muA)");
    graph->GetXaxis()->SetTitleSize(0.045);
    graph->GetYaxis()->SetTitleSize(0.045);
    graph->GetXaxis()->SetTitleOffset(1.0);
    graph->GetYaxis()->SetTitleOffset(0.8);
    graph->GetXaxis()->SetLabelSize(0.04);
    graph->GetYaxis()->SetLabelSize(0.04);

    // Set the x and y axis limits
    graph->GetXaxis()->SetLimits(-1.0, 0.5);  // Set x-axis limits to [-1; 0.5]
    graph->GetYaxis()->SetRangeUser(-50, 70); // Set y-axis limits to [-50; 70]

    // Read the first selected data file
    ifstream infile1("MaxG.dat"); // Replace with your actual selected data file 1
    std::vector<double> voltage1, current1;
    while (infile1 >> v >> i) {
        voltage1.push_back(v);
        current1.push_back(i);
    }

    // Create a TGraph for the first selected data
    TGraph *graph1 = new TGraph(voltage1.size(), &voltage1[0], &current1[0]);
    graph1->SetMarkerStyle(1);  // Invisible marker
    graph1->SetLineColorAlpha(kRed, 0);  // Invisible line

    // Fit the first graph with a linear function
    TF1 *fit1 = new TF1("fit1", "pol1", voltage1.front(), voltage1.back());
    graph1->Fit(fit1, "R");  // "R" restricts fit to graph range
    double slope1 = fit1->GetParameter(1); // Get the slope (conductance)

    // Read the second selected data file
    ifstream infile2("MinG.dat"); // Replace with your actual selected data file 2
    std::vector<double> voltage2, current2;
    while (infile2 >> v >> i) {
        voltage2.push_back(v);
        current2.push_back(i);
    }

    // Create a TGraph for the second selected data
    TGraph *graph2 = new TGraph(voltage2.size(), &voltage2[0], &current2[0]);
    graph2->SetMarkerStyle(1);  // Invisible marker
    graph2->SetLineColorAlpha(kGreen, 0);  // Invisible line

    // Fit the second graph with a linear function
    TF1 *fit2 = new TF1("fit2", "pol1", voltage2.front(), voltage2.back());
    graph2->Fit(fit2, "R");
    double slope2 = fit2->GetParameter(1); // Get the slope (conductance)

    // Draw the fits
    fit1->SetLineColor(kRed); // Fit line color for graph1
    fit1->SetLineWidth(3);
    fit1->Draw("same");

    fit2->SetLineColor(kGreen); // Fit line color for graph2
    fit2->SetLineWidth(3);
    fit2->Draw("same");

    // Add a legend with conductance values (rounded to 2 significant digits)
    TLegend *legend = new TLegend(0.15, 0.60, 0.35, 0.85);
    legend->AddEntry(graph, "I-V Data", "lp");
    legend->AddEntry(fit1, Form("G_{max} = %.2f #muS", slope1), "l");
    legend->AddEntry(fit2, Form("G_{min} = %.2f #muS", slope2), "l");
    legend->SetTextSize(0.04);
    legend->Draw();

    // Save the plot as a high-resolution image
    // c1->SaveAs("IV_Curve_Plot_with_Fits.png"); // Change to desired format

    // Close the input files
    infile.close();
    infile1.close();
    infile2.close();
}

