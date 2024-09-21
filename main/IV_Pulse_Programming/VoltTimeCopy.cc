#include <TCanvas.h>
#include <TPad.h>
#include <TGraph.h>
#include <TAxis.h>
#include <TLegend.h>
#include <TStyle.h>
#include <fstream>
#include <vector>

void VolsTime() {
    // Set style for publication quality
    gStyle->SetOptStat(0); // Disable statistics box
    gStyle->SetPadTickX(1); // Ticks on the upper axis
    gStyle->SetPadTickY(1); // Ticks on the right axis

    // Read the first data file (time and voltage)
    std::ifstream infile1("VMem.dat"); // Replace with your actual data file
    std::vector<double> time1, voltage1;
    double t, v;

    while (infile1 >> t >> v) {
        time1.push_back(t);
        voltage1.push_back(v);
    }

    // Create a TGraph for the first data set
    TGraph *graph1 = new TGraph(time1.size(), &time1[0], &voltage1[0]);
    graph1->SetTitle("Voltage vs. Time");
    graph1->SetMarkerStyle(20);
    graph1->SetMarkerSize(1.0);
    graph1->SetMarkerColor(kBlue); // Best color for publication
    graph1->SetLineColor(kBlue);
    graph1->SetLineWidth(2);

    // Read the second data file (time and voltage)
    std::ifstream infile2("V2.dat"); // Replace with your actual data file
    std::vector<double> time2, voltage2;

    while (infile2 >> t >> v) {
        time2.push_back(t);
        voltage2.push_back(v);
    }

    // Create a TGraph for the second data set
    TGraph *graph2 = new TGraph(time2.size(), &time2[0], &voltage2[0]);
    graph2->SetMarkerStyle(21);
    graph2->SetMarkerSize(1.0);
    graph2->SetMarkerColor(kRed); // Best contrasting color for publication
    graph2->SetLineColor(kRed);
    graph2->SetLineWidth(2);

    // Create a canvas
    TCanvas *c1 = new TCanvas("c1", "Voltage vs. Time Plot", 800, 600);
    c1->SetGrid();

    // Create a pad within the canvas
    TPad *pad = new TPad("pad", "The pad", 0.02, 0.02, 0.98, 0.98);
    pad->Draw();
    pad->cd();
    pad->SetGrid(); // Enable grid for better readability

    // Draw the first graph
    graph1->Draw("AL");

    // Set axis ranges to accommodate negative values
    double minVoltage = std::min(*std::min_element(voltage1.begin(), voltage1.end()), *std::min_element(voltage2.begin(), voltage2.end())) - 0.5; // Add margin
    double maxVoltage = std::max(*std::max_element(voltage1.begin(), voltage1.end()), *std::max_element(voltage2.begin(), voltage2.end())) + 0.5; // Add margin

    graph1->GetYaxis()->SetRangeUser(minVoltage, maxVoltage);

    // Draw the second graph on the same canvas
    graph2->Draw("L same");

    // Customize the axes
    graph1->GetXaxis()->SetTitle("Time (#mus)"); // Change the unit as needed
    graph1->GetYaxis()->SetTitle("Voltage (V)");
    graph1->GetXaxis()->SetTitleSize(0.045);
    graph1->GetYaxis()->SetTitleSize(0.045);
    graph1->GetXaxis()->SetTitleOffset(1.2);
    graph1->GetYaxis()->SetTitleOffset(1.2);
    graph1->GetYaxis()->SetRangeUser(-0.65,0.65);

    graph1->GetXaxis()->SetLabelSize(0.04);
    graph1->GetYaxis()->SetLabelSize(0.04);

    // Add a legend
    TLegend *legend = new TLegend(0.15, 0.70, 0.35, 0.85);
    //legend->SetHeader("Legend", "C"); // Option "C" allows centering
    legend->AddEntry(graph1, "V_{Memristor}", "lp");
    legend->AddEntry(graph2, "V_{Applied}", "lp");
    legend->SetTextSize(0.035);
    legend->Draw();

    // Save the plot as a high-resolution image
    c1->SaveAs("Voltage_Time_Plot.png"); // Change to desired format

    // Close the input files
    infile1.close();
    infile2.close();
}

