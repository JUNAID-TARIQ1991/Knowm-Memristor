#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <TGraph.h>
#include <TCanvas.h>
#include <TF1.h>
#include <TLegend.h>
#include <TStyle.h>
#include <TColor.h>

using namespace std;

void FitLineConductanceNEW() {
    // List of text files, Specifies the list of text files containing the I-V data.
    vector<string> file_names = {
        "File1IV.txt",
        "File2IV.txt",
        "File3IV.txt",
         "File4IV.txt",
         "File5IV.txt",
         "File6IV.txt"
    };

    // Define corresponding voltages for each file
    vector<string> voltages = {
        "0.15V",
        "0.30V",
	"0.50V",
	"0.70V",
	"0.90V",
	"1.00V"
        // Add more voltages as needed
    };

    // Define colors for each file
    vector<int> colors = {kRed, kBlue, kGreen, kMagenta, kCyan, 9};

    TCanvas* c1 = new TCanvas("c1", "I-V Characteristics", 900, 600);
    TLegend* legend_voltages = new TLegend(0.1, 0.7, 0.3, 0.9);
    legend_voltages->SetHeader("Voltages", "C");
    legend_voltages->SetBorderSize(1);

    TLegend* legend_conductance = new TLegend(0.1, 0.7, 0.3, 0.9);
    legend_conductance->SetHeader("Conductance", "C");
    legend_conductance->SetBorderSize(1);

    for (size_t idx = 0; idx < file_names.size(); ++idx) {
        const auto& file_name = file_names[idx];
        ifstream file(file_name);
        if (!file.is_open()) {
            cerr << "Error opening file: " << file_name << endl;
            continue;
        }

        vector<double> voltage;
        vector<double> current;

        double v, i;
        while (file >> v >> i) {
            current.push_back(i);
            voltage.push_back(v);
        }
        file.close();

        // Create a TGraph for the current file
        TGraph* graph = new TGraph(voltage.size(), &voltage[0], &current[0]);
        graph->SetTitle("Memristor 3 Conductance");
        graph->GetXaxis()->SetTitle("Voltage (V)");
        graph->GetXaxis()->SetTitleSize(0.05);
	

        graph->GetYaxis()->SetTitle("Current (#muA)");
        graph->GetYaxis()->SetTitleSize(0.05);
	graph->SetLineWidth(2);

	if(idx == 0){
		graph->SetMarkerStyle(kFullCircle);
		graph->SetMarkerSize(1.0);
		graph->GetXaxis()->SetLimits(-0.1,0.1);
		graph->GetYaxis()->SetRangeUser(-2,2.1);

	}
	else
	{graph->SetMarkerStyle(kFullCircle);
	graph->SetMarkerSize(1.0);}
       
        graph->SetMarkerColor(colors[idx]);

        // Fit the data with a linear function
        TF1* fit = new TF1(("fit_" + to_string(idx)).c_str(), "[0]*x + [1]", -0.1, 0.1);
        fit->SetParNames("Conductance #muS");
        fit->SetLineColor(colors[idx]);
        graph->Fit(fit, "R");

        // Extract the conductance (slope)
        double conductance = fit->GetParameter(0);
        cout << "Conductance for " << file_name << ": " << conductance << " S" << endl;

        // Draw the graph and fit
        if (idx == 0) {
            graph->Draw("AP");
        } else {
            graph->Draw("P same");
        }
        fit->Draw("same");

        // Add the voltage to the legend
        //legend_voltages->AddEntry(graph, voltages[idx].c_str(), "P");

        // Add the conductance to the legend
        stringstream ss;
        ss << "Conductance " << voltages[idx] << ": " << conductance << " #mu S";
        legend_conductance->AddEntry(fit, ss.str().c_str(), "L");
    }

    //legend_voltages->Draw();
    legend_conductance->Draw();
    c1->Update();
}

