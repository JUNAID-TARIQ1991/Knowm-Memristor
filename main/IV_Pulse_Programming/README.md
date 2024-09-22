# Analog Dicovery Board v2
f you're wondering where to buy an oscilloscope or how to buy an oscilloscope, you've come to the right place. Digilent Analog Discovery 2 is a USB oscilloscope, logic analyzer, and multi-function instrument that allows users to measure, visualize, generate, record, and control mixed-signal circuits of all kinds. Despite our competitive oscilloscope price, we never compromise on quality. Developed in conjunction with Analog Devices and supported by Xilinx University Program, this compact oscilloscope is small enough to be a pocket oscilloscope, but powerful enough to replace a stack of lab oscilloscopes and equipment, providing engineering professionals, students, hobbyists, and electronic enthusiasts the freedom to work with analog and digital circuits in virtually any environment, in or out of the lab. The analog and digital inputs and outputs can be connected to a circuit using simple wire probes; alternatively, the Analog Discovery BNC Adapter and BNC probes can be used to connect and utilize the inputs and outputs. 

Driven by the free WaveForms software (Mac, Linux, and Windows compatible), this small oscilloscope can be configured to work as any one of several traditional test and measurement instruments including an Oscilloscope, Waveform Generator, Power Supply, Voltmeter, Data Logger, Logic Analyzer, Pattern Generator, Static I/O, Spectrum Analyzer, Network Analyzer, Impedance Analyzer, Protocol Analyzer, and Curve Tracer. 

When you buy an oscilloscope from Digilent, you can be confident that you're getting an excellent product from a trusted brand. We're committed to providing our customers with the best possible experience, whether you're a student just starting out or a seasoned professional. We also offer the best oscilloscope price on the market for verified academic accounts, so if you're looking to reduce the oscilloscope cost, head over to our academic verification page for more information. If you're an international customer, we have a network of authorized oscilloscope distributors that may have better shipping options.
# USB Oscilloscope
Analog Discovery 2 among compatible add-on boardsThe Analog Discovery 2 oscilloscope is designed to be a portable alternative to a stack of benchtop equipment. It's durable enclosure measures (3.23 inch x 3.25 inch x7/8 inch) and fits in a pocket. The Digilent Discovery 2 can be connected to circuits and designs via the included female flywires, or used in conjunction with the included gender changers when a male connection is necessary.

Accessories can be purchased separately to provide additional functionality, such as the BNC Adapter for higher bandwidth and BNC connectors, or the Breadboard Adapter and Breadboard Breakout for a direct connection to the breadboard, or the Impedance Analyzer for additional Impedance measurement functionality. The Analog Discovery 2 comes packaged in a durable project box that will fit all the included accessories and some additional adapter boards. The project box measures (7" x 5.75" x 1.5") and provides even more durability when stashing your portable Oscilloscope and multi-function instrument in your backpack or briefcase.
# How to Measure Conductance from IV curve of Memristor using AD2? 
To know about what is memristor and how it work. see Knowm Memristor Discovery Manual by Alex Nugent. Working with AD2 you must have Digilent waveform sotware available at  https://reference.digilentinc.com/reference/software/waveforms/waveforms-
3/start.
# DC response of Memristor
Depending on your board version, vo, v1, v2 or v3. place a discrete memristor chip into the socket of the Memristor Discovery board. Open the ”DC” experiment. Make 2 sure your V2 board is in ’Mode 1’.  The DC app allows you to drive a memristor in series with a resistor, as in Figure 18 of the manual , with various ramping functions including sawtooth, sawtoothupdown, triangle and triangleupdown at time scales from 10 to 1000ms. The number of applied ramping signals can be selected and the response can be observed as either a time series (V1+ vs T and V2+ vs T), I vs V or G vs V plot, revealing the behavior of the memristor at slow timescales.
1. select the Dc experiment from the top menu
2. select square waveform of amplitude 1v, pulse width 100ms, number of pulses 5.
3. select the desired memristor from m1 to m16 (( only one memristor at a time)
4. press start or s.
5. you will seee the Pnched IV curve in IV plane, That is charateristic curve of a meristor. See IVPlot.pdf
# How to fit IV curve to get conductance value using  Digilent waveform software with AD2
1. Run the Dc experiment, and select IV responce of the memristor
2. Export the IV values to a csv file
3. In the file first column represent voltage and second current in milli ampares.
4. Plot these values using python or root (c++), see code in IV_fitting branch.
# Pulse Programming experiment
In the Pulse experiment we apply pulses of various magnitudes, durations,
shapes, etc, to a memristor while we measure its resistance. We use the same
basic circuit as the prior experiments (See figure 18). Pulse properties can be
selected on the left controls. When a selection or change is made, a preview
of the pulse shape is displayed in the main plot. When you are satisfied with
your pulse (or pulse train), you can apply the pulse by clicking on the ’Start’
button. Immediately after clicking the ’Start’ button, the captured waveform
will display in the main plot area. At the same time, a series of ’read’ pulses
will be fired at an interval set by the ’Sample Period [s]’ value, which is set
38to 1 second by default. The measured conductance of the memristor over time
will be displayed in the lower plot. These measurements will continue until the
’Stop’ button (previously the ’Start’ button) is pressed.
You can select three plots to display in the main plot area via the radio
button at the bottom of the screen, below the conductance-vs-time plot. ’Write-
Erase Pulse Capture’ displays V1 (Blue), V2(Yellow) and V1-V2(Purple), which
is the voltage drop across the memristor. ’Read Pulse Capture’ displays the
same voltages, but will update for every new read pulse. The conductance
of the memristor is calculated from this information. Due to RC effects, it is
important to understand how this occurs and helpful to see the raw data to make
sure you are not operating outside the optimal parameters for measurement. We
will discuss this in more detail below. Finally, the ’I-T’ plot converts the data
gathered in the ’Write-Erase Pulse Capture’ data and, using the value of the
series resistor, computes the current.
The pulse can be applied again by clicking ’Stop’ and then ’Start’ again or by
pressing the ’S’ key on the keyboard to toggle between the two. Each time the
’Start’ button is pressed, a pulse will be generated, waveforms captured, and
measurement pulses will commence. While the main pulse capture plots will
update, the Conductance vs Time plot will simply add the new measurements
and grow in size. If you would like to reset all plots, select the Pulse experiment
from the main menu.
# How to program Memristor conductance
1 In the pulse experiment first reset the device by applying large negative pulse i.e. -2v
2 Apply several reset pulses by pressing start and stop button
3 Now apply the pulses of +ve voltage, until you achieve the desired conductance state.
4 Let few read pulses pass.
5 Now you can read the memristor conductance by applying small +ve voltage i.e., 0.1v using DC or AC experiment via method describe in previous section
   

