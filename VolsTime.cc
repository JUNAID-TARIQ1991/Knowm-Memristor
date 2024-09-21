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
        voltage2.push_back(v*-1);
    }

    // Create a TGraph for the second data set
    TGraph *graph2 = new TGraph(time2.size(), &time2[0], &voltage2[0]);
    graph2->SetMarkerStyle(21);
    graph2->SetTitle("");
    graph2->SetMarkerSize(1.0);
    graph2->SetMarkerColor(kRed); // Best contrasting color for publication
    graph2->SetLineColor(kRed);
    graph2->SetLineWidth(2);

    // Create a canvas with high resolution
    TCanvas *c1 = new TCanvas("c1", "Voltage vs. Time Plot", 1000, 1000); // Increased width for side-by-side layout

    // Create two pads within the canvas, one next to the other
    TPad *pad1 = new TPad("pad1", "Left Pad", 0.01, 0.01, 0.49, 0.99); // Left pad
    TPad *pad2 = new TPad("pad2", "Right Pad", 0.49, 0.01, 0.99, 0.99); // Right pad

    pad1->Draw();
    pad2->Draw();

    // Draw on the first pad (left pad)
    pad1->cd();
    //pad1->SetGrid(); // Enable grid for better readability
    //pad1->SetRightMargin(0); // Remove right margin to join with the second pad

    // Set axis ranges to accommodate negative values for pad1
    double minVoltage = std::min(*std::min_element(voltage1.begin(), voltage1.end()), *std::min_element(voltage2.begin(), voltage2.end())) - 0.5; // Add margin
    double maxVoltage = std::max(*std::max_element(voltage1.begin(), voltage1.end()), *std::max_element(voltage2.begin(), voltage2.end())) + 0.5; // Add margin

    graph2->GetYaxis()->SetRangeUser(-0.1, 0.8);
    graph2->GetXaxis()->SetRangeUser(0, 2800);

    // Draw the second graph on the first pad
    graph2->Draw("AL");
    graph1->Draw("Lsame");

    // Customize the y-axis for pad1
    graph2->GetYaxis()->SetTitle("Voltage (V)");
    graph2->GetXaxis()->SetTitle("Time (#mus)");
    graph2->GetYaxis()->SetTitleSize(0.045);
    graph2->GetYaxis()->SetTitleOffset(1.2);
    graph2->GetYaxis()->SetLabelSize(0.04);

    // Add a legend for pad1
    TLegend *legend1 = new TLegend(0.15, 0.68, 0.45, 0.88);
    legend1->SetHeader("Set", "C"); // Option "C" allows centering
    legend1->AddEntry(graph1, "V_{Memristor}", "lp");
    legend1->AddEntry(graph2, "-V_{set} ", "lp");
    legend1->SetTextSize(0.045);
    legend1->Draw();

    // Draw on the second pad (right pad)
    pad2->cd();
    //pad2->SetGrid(); // Enable grid for better readability
    //pad2->SetLeftMargin(0); // Remove left margin to join with the first pad
 // 
 // Read the first data file (time and voltage)
    std::ifstream infile1C("VMemReset.dat"); // Replace with your actual data file
    std::vector<double> time1C, voltage1C;
    double t1C, v1C;

    while (infile1C >> t1C >> v1C) {
        time1C.push_back(t1C);
        voltage1C.push_back(v1C);
    }
    // Create a TGraph for the first data set
    TGraph *graph1_copy = new TGraph(time1C.size(), &time1C[0], &voltage1C[0]);
    graph1_copy->SetMarkerStyle(20);
    graph1_copy->SetMarkerSize(1.0);
    graph1_copy->SetMarkerColor(kBlue); // Best color for publication
    graph1_copy->SetLineColor(kBlue);
    graph1_copy->SetLineWidth(2);
    
    std::ifstream infile2C("V2Reset.dat"); // Replace with your actual data file
    std::vector<double> time2C, voltage2C;
        double t2C, v2C;


    while (infile2C >> t2C >> v2C) {
        time2C.push_back(t2C);
        voltage2C.push_back(v2C*-1);
    }
    // Create a TGraph for the second data set
    TGraph *graph2_copy = new TGraph(time2C.size(), &time2C[0], &voltage2C[0]);
    graph2_copy->SetMarkerStyle(21);
    graph2_copy->SetMarkerSize(1.0);
    graph2_copy->SetTitle("");
    graph2_copy->SetMarkerColor(kRed); // Best contrasting color for publication
    graph2_copy->SetLineColor(kRed);
    graph2_copy->SetLineWidth(2);



    graph2_copy->GetYaxis()->SetRangeUser(-3, 2);
    graph2_copy->GetXaxis()->SetRangeUser(0, 2800);


    // Draw the same graphs again on the second pad
    //TGraph *graph1_copy = (TGraph*)graph1->Clone(); // Create a copy of the first graph
    //TGraph *graph2_copy = (TGraph*)graph2->Clone(); // Create a copy of the second graph

    graph2_copy->Draw("AL");
    graph1_copy->Draw("L same");

    // Customize the axes for pad2
    graph2_copy->GetXaxis()->SetTitle("Time (#mus)"); // Set x-axis title only on the second pad
    //graph1_copy->GetYaxis()->SetTitle("Voltage (V)");
    graph1_copy->GetXaxis()->SetTitleSize(0.045);
    graph1_copy->GetYaxis()->SetTitleSize(0.045);
    graph1_copy->GetXaxis()->SetTitleOffset(1.2);
    graph1_copy->GetYaxis()->SetTitleOffset(1.2);
    graph1_copy->GetXaxis()->SetLabelSize(0.04);
    graph1_copy->GetYaxis()->SetLabelSize(0.04);

    // Add a legend for pad2
    TLegend *legend2 = new TLegend(0.15, 0.68, 0.43, 0.88);
    legend2->SetHeader("Reset", "C"); // Option "C" allows centering
    legend2->AddEntry(graph1_copy, "V_{Memristor}", "lp");
    legend2->AddEntry(graph2_copy, "-V_{set} ", "lp");
    legend2->SetTextSize(0.045);
    legend2->Draw();

    // Save the plot as a high-resolution image
    c1->SaveAs("Voltage_Time_Plot_SideBySide.png"); // Change to desired format

    // Close the input files
    infile1.close();
    infile2.close();
}

