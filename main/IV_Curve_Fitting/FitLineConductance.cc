#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <TGraph.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TLegend.h>

using namespace std;

void FitLineConductance() {
    // List of text files, Specifies the list of text files containing the I-V data.
    vector<string> file_names = {
        "File1IV.txt",
        //"File2IV.txt",
        //"File3IV.txt",
        //"File4IV.txt",
        //"File5IV.txt"
    };

    vector<double> voltage_all;
    vector<double> current_all;

    for (const auto& file_name : file_names) {
        ifstream file(file_name);
        if (!file.is_open()) {
            cerr << "Error opening file: " << file_name << endl;
            continue;
        }

        double v, i;
        while (file >> v >> i) {
            current_all.push_back(i);
            voltage_all.push_back(v);
        }
        file.close();
    }

    // Create a TGraph from the combined data
    TGraph* graph = new TGraph(voltage_all.size(), &voltage_all[0], &current_all[0]);
    graph->SetTitle("I-V Characteristics");
    graph->GetXaxis()->SetTitle("Voltage (V)");
    graph->GetYaxis()->SetTitle("Current (#mu A)");
    graph->SetMarkerStyle(kFullCircle);
    graph->SetMarkerSize(0.5);
    graph->SetMarkerColor(kBlue);
    gStyle->SetOptFit(1111);

    // Fit the combined data with a linear function
    //TF1* fit = new TF1("fit", "[0]*x + [1]", *min_element(voltage_all.begin(), voltage_all.end()), *max_element(voltage_all.begin(), voltage_all.end()));
    TF1* fit = new TF1("fit", "[0]*x + [1]", -0.1, 0.1);
    fit->SetParNames("Conductance #muS");
    graph->Fit(fit, "R");


    // Extract the conductance (slope)
    double conductance = fit->GetParameter(0);
    cout << "Combined Conductance: " << conductance <<  " S" << endl;

    // Draw the graph and fit
    TCanvas* c1 = new TCanvas("c1", "I-V Characteristics", 800, 600);
    graph->Draw("AP");
    fit->Draw("same");

    c1->Update();
}

