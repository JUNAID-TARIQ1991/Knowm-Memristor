#include <TCanvas.h>
#include <TGraph.h>
#include <TAxis.h>
#include <TLegend.h>
#include <TStyle.h>
#include <fstream>
#include <vector>

void ConductancePlot() {
    // Set style for publication-quality plots
    gStyle->SetOptStat(0); // Disable statistics box
    gStyle->SetPadTickX(1); // Ticks on the upper axis
    gStyle->SetPadTickY(1); // Ticks on the right axis

    // Read the data file (pulse number and conductance)
    std::ifstream infile("ConductanceData.dat"); // Replace with your actual data file
    std::vector<double> pulseNumber, conductance;
    double pulse, cond;

    while (infile >> pulse >> cond) {
        pulseNumber.push_back(pulse);
        conductance.push_back(cond*1000);
    }

    // Create a TGraph for the data set
    TGraph *graph = new TGraph(pulseNumber.size(), &pulseNumber[0], &conductance[0]);
    graph->SetTitle("Conductance vs. Pulse Number");
    graph->SetMarkerStyle(20);
    graph->SetMarkerSize(1.0);
    graph->SetMarkerColor(kBlue); // Set color for the graph
    graph->SetLineColor(kBlue);
    graph->SetLineWidth(2);

    // Create a canvas with high resolution
    TCanvas *c1 = new TCanvas("c1", "Conductance vs. Pulse Number Plot", 1600, 800);

    // Draw the graph on the canvas
    graph->Draw("ALP"); // "A" for axis, "L" for line, "P" for points

    // Customize the axes
    graph->GetXaxis()->SetTitle("Read Pulse Number");
    graph->GetYaxis()->SetTitle("Conductance (#muS)"); // Assuming conductance is in Siemens (S)
    graph->GetXaxis()->SetTitleSize(0.045);
    graph->GetYaxis()->SetTitleSize(0.045);
    graph->GetXaxis()->SetTitleOffset(1.0);
    graph->GetYaxis()->SetTitleOffset(1.0);
    graph->GetXaxis()->SetLabelSize(0.04);
    graph->GetYaxis()->SetLabelSize(0.04);

    // Add a legend
    TLegend *legend = new TLegend(0.15, 0.75, 0.35, 0.85);
    //legend->SetHeader("Legend", "C"); // Option "C" allows centering
    legend->AddEntry(graph, "Conductance ", "lp");
    legend->SetTextSize(0.035);
    legend->Draw();

    // Save the plot as a high-resolution image
    c1->SaveAs("Conductance_PulseNumber_Plot.png"); // Change to desired format

    // Close the input file
    infile.close();
}

