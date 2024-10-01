"""
Test Memristor with  dwfpy library 
Created : Valerio Bocci Jun 2024

Reproduce DC experiment of Mem-Disc
Davide: debug, implemented waited Rmeasurment 24-06-2024
Davide: implemented R-measurement and G estimation vs cycles 20-06-2024
Davide: debug and added plotting part V-time I-V e G-V
"""

#import matplotlib.pyplot as plt
import dwfpy as dwf
import time
from datetime import datetime
import threading
from sklearn.linear_model import LinearRegression
from utils import plot_Capture, plot_IV, plot_GV, plot_Gmean_byCycles, SaveCSV_and_upload, step_seconds_converter, extract_cycles, plot_IV_byCycles, plot_GV_byCycles, estimate_R_byCycles

DO_RESET_STEP = False
DO_PROG_STEP = False
DO_2ND_MEASUREMENT = False
DO_WAITING_LOOPS = False
R = 10000 #Ohm
sample_rate = 5000
sample_rate_waitingMode = 1000

# Memristors on which execute the experiment
memristors = [ 5] #

#Create directory for saving
impose_dir = datetime.now().strftime("%Y%m%d_%H%M%S")

def disabling_wavegen0(): #It cannot has arguments
    wavegen[0].setup(enabled=False) #If no offset is given, it remains the one setted by wavegen
    print("Spento wavegen[0] al tempo", time.time())

def login():
    for i in range(0,16):
        pattern[i].setup_constant('low', start=True)
    # Set the positive power supply to 3.3V and enable it.
    device.supplies.positive.setup(voltage=5.0) #this step seems give a spike of 0.004V (negligible)
    device.supplies.negative.setup(voltage=-5.0)
    device.supplies.master_enable = True

print(f'DWF Version: {dwf.Application.get_version()}')

with dwf.AnalogDiscovery2() as device:
    print(f'Found device: {device.name} ({device.serial_number})')

    scope = device.analog_input
    wavegen = device.analog_output #link: https://github.com/mariusgreuel/dwfpy/blob/main/src/dwfpy/analog_output.py
    pattern = device.digital_output

    #print("Starting oscilloscope on 1+ (V memristor) ")
    scope.channels[0].setup(range = 0.9, enabled = True)  #
    #print("Starting oscilloscope on 2+ (V Generator)")
    scope.channels[1].setup(range = 0.9, enabled = True)  # 


    # Creare un thread che esegue la funzione dopo 5 secondi
    timer_thread = threading.Timer(0.2, login) #-0.1 to disable before of the 0V
    # Avviare il thread
    timer_thread.start()
    recorder = scope.record(sample_rate=sample_rate, length=1, configure=True, start=True)
    t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate)
    plot_Capture(t, recorder, title='Capture plot V(t)', memNumber="no-mem")


    # Repeat the experiment for each memristor
    for m in memristors:
        print(f"Working on Memristor {m}")
        # Output a high level on pin DIO-0 to select the righ Memristor.
        for i in range(0):
            pattern[i].setup_constant('low', start=True)

        # Set the positive power supply to 3.3V and enable it.
        #device.supplies.positive.setup(voltage=5.0) #this step seems give a spike of 0.004V (negligible)
        #device.supplies.negative.setup(voltage=-5.0)
        #device.supplies.master_enable = True
        
        time.sleep(1)
        #E' IMPORTANTE CHE LO SLEEP SIA PRIMA
        pattern[m].setup_constant('high', start=True) #E' IMPORTANTE CHE LO SLEEP SIA PRIMA

        #recorder = scope.record(sample_rate=100000, length=1, configure=True, start=True)
        #plot_Capture(recorder, title='Voltage on the board Before enabling W1 and switch 1')

        if DO_RESET_STEP:
            frequency = 1
            NumCycles = 0.5
            Tensione_Prog = 0.5
            Offset = -0.1
            TimeSleep0 = NumCycles/frequency

            time.sleep(1)
            wavegen[0].setup('triangle', frequency=frequency, amplitude=Tensione_Prog, start=True, offset=Offset)
            wavegen[1].setup(enabled=False)

            # Creare un thread che esegue la funzione dopo 5 secondi
            timer_thread = threading.Timer(TimeSleep0, disabling_wavegen0) #-0.1 to disable before of the 0V

            # Avviare il thread
            timer_thread.start()

            #start recording
            recorder = scope.record(sample_rate=sample_rate, length=TimeSleep0+0.1, configure=True, start=True)
            #print("End first recording", time.time())

            # Check for lost or corrupted samples
            if recorder.lost_samples > 0:
                print('Samples lost, reduce sample rate.')
            if recorder.corrupted_samples > 0:
                print('Samples corrupted, reduce sample rate.')

            #Plotting and Saving
            voltage_diff = (recorder.channels[0].data_samples - recorder.channels[1].data_samples)
            t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate)
            # Plot current vs. voltage difference
            I = (voltage_diff) / R #Ohm
            G = I / (-1 * recorder.channels[0].data_samples)

            #print("Saving csv and plots...")
            csvfilename = SaveCSV_and_upload(t, -1 * recorder.channels[0].data_samples, I, G,
                                dirsuffix='DC_exp', memNumber=str(m+1), impose_dir=impose_dir, suffix='_resetStep')
            plot_Capture(t, recorder, title='Capture plot V(t)', plotDV=True, voltage_diff=voltage_diff, csvfilename=csvfilename, memNumber=str(m+1))
            plot_IV(-1 * recorder.channels[0].data_samples, I, title='I-V curve', csvfilename=csvfilename, memNumber=str(m+1))
            time.sleep(0.1)
            plot_GV(-1 * recorder.channels[0].data_samples, G, title='G-V curve', csvfilename=csvfilename, memNumber=str(m+1))
            print(f" - Reset step executed and saved in {impose_dir}_DC_exp/mem{m}")
        else: TimeSleep0 = 0

        #print('Starting the second part of the experiment')
        #Test of resistance measurement
        frequency = 1
        NumCycles = 60
        amplitude = 0.0
        Offset = -0.1
        sample_rate = 10000
        TimeSleep1 = NumCycles/frequency

        time.sleep(1)
        wavegen[0].setup('triangle', frequency=frequency, amplitude=amplitude, start=True, offset=Offset)
        wavegen[1].setup(enabled=False)

        timer_thread = threading.Timer(TimeSleep1, disabling_wavegen0)
        timer_thread.start()

        # recording
        recorder = scope.record(sample_rate=sample_rate, length=TimeSleep1+0.1, configure=True, start=True)
        #print("End second recording", time.time())
        time.sleep(0.1)
        # computing variables
        t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate)
        voltage_diff = (recorder.channels[0].data_samples - recorder.channels[1].data_samples)
        # Plot current vs. voltage difference
        I = (voltage_diff) / R #Ohm
        G = I / (-1 * recorder.channels[0].data_samples)

        #print("Saving csv and plots...")
        csvfilename = SaveCSV_and_upload(t, -1 * recorder.channels[0].data_samples, I, G,
                                dirsuffix='R_meas', memNumber=str(m+1), impose_dir=impose_dir, suffix='_1stRead')#The suffix is used also for following plots
        plot_Capture(t, recorder, title='R-measurement '+str(TimeSleep1), csvfilename=csvfilename, memNumber=str(m+1) )
        time.sleep(0.1)

        #split data in periods and extract many R_measurements
        cycles_data_1 = extract_cycles(csvfilename, NumCycles, frequency) #from 1 to NumCycles

        plot_IV_byCycles(cycles_data_1, csvfilename=csvfilename, N=2, memNumber=str(m+1))
        plot_GV_byCycles(cycles_data_1, csvfilename=csvfilename, N=2, memNumber=str(m+1))
        plot_Gmean_byCycles(cycles_data_1, csvfilename=csvfilename, N=1, memNumber=str(m+1))
        # Creare il modello di regressione lineare
        estimate_R_byCycles(cycles_data_1, title="R vs Cycles", csvfilename=csvfilename, memNumber=str(m+1))
        print(f" - First R measurement and saved in {impose_dir}_R_meas/mem{m}")

        if DO_PROG_STEP:
            frequency = 1
            NumCycles = 1
            Tensione_Prog = 0.5
            Offset = -0.1
            TimeSleep2 = NumCycles/frequency

            time.sleep(1)
            wavegen[0].setup('triangle', frequency=frequency, amplitude=Tensione_Prog, start=True, offset=Offset)
            wavegen[1].setup(enabled=False)

            timer_thread = threading.Timer(TimeSleep2-0.1, disabling_wavegen0 ) #-0.1 to disable before of the 0V
            timer_thread.start()

            #start recording
            recorder = scope.record(sample_rate=sample_rate, length=TimeSleep2, configure=True, start=True)
            # Check for lost or corrupted samples
            if recorder.lost_samples > 0:
                print('Samples lost, reduce sample rate.')
            if recorder.corrupted_samples > 0:
                print('Samples corrupted, reduce sample rate.')

            #Plotting and Saving
            voltage_diff = (recorder.channels[0].data_samples - recorder.channels[1].data_samples)
            t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate)
            # Plot current vs. voltage difference
            I = (voltage_diff) / R #Ohm
            G = I / (-1 * recorder.channels[0].data_samples)

            #print("Saving csv and plots...")
            csvfilename = SaveCSV_and_upload(t, -1 * recorder.channels[0].data_samples, I, G,
                                dirsuffix='DC_exp', memNumber=str(m+1), impose_dir=impose_dir, suffix='_ProgStep') #The suffix is used also for following plots
            plot_Capture(t, recorder, title='Capture plot V(t)', plotDV=True, voltage_diff=voltage_diff, csvfilename=csvfilename, memNumber=str(m+1))
            plot_IV(-1 * recorder.channels[0].data_samples, I, title='I-V curve', csvfilename=csvfilename, memNumber=str(m+1))
            time.sleep(0.1)
            plot_GV(-1 * recorder.channels[0].data_samples, G, title='G-V curve', csvfilename=csvfilename, memNumber=str(m+1))
            print(f" - Programming step executed and saved in {impose_dir}_DC_exp/mem{m}")
        else: TimeSleep2 = 0

        #Test of resistance measurement
        if DO_2ND_MEASUREMENT:
            frequency = 1
            NumCycles = 240
            amplitude = 0.0
            Offset = -0.1
            sample_rate = 10000
            TimeSleep3 = NumCycles/frequency

            time.sleep(1)
            wavegen[0].setup('triangle', frequency=frequency, amplitude=amplitude, start=True, offset=Offset)
            wavegen[1].setup(enabled=False)

            # recording
            recorder = scope.record(sample_rate=sample_rate, length=TimeSleep3+0.1, configure=True, start=True)
            #print("End second recording", time.time())
            time.sleep(0.1)
            # computing variables
            t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate)
            voltage_diff = (recorder.channels[0].data_samples - recorder.channels[1].data_samples)
            # Plot current vs. voltage difference
            I = (voltage_diff) / R #Ohm
            G = I / (-1 * recorder.channels[0].data_samples)

            #print("Saving csv and plots...")
            csvfilename = SaveCSV_and_upload(t, -1 * recorder.channels[0].data_samples, I, G,
                                    dirsuffix='R_meas', memNumber=str(m+1), impose_dir=impose_dir, suffix='_2ndRead')#The suffix is used also for following plots
            plot_Capture(t, recorder, title='R-measurement '+str(TimeSleep3), csvfilename=csvfilename, memNumber=str(m+1))
            time.sleep(0.1)

            #split data in periods and extract many R_measurements
            cycles_data = extract_cycles(csvfilename, NumCycles, frequency) #from 1 to NumCycles
            plot_IV_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), N=2)
            plot_GV_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), N=2)
            plot_Gmean_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), N=2)
            # Creare il modello di regressione lineare
            estimate_R_byCycles(cycles_data, title="R vs Cycles", csvfilename=csvfilename, memNumber=str(m+1), suffix='_2ndRead')
            print(f" - R measured and saved in {impose_dir}_R_meas/mem{m}")
        else: TimeSleep3 = 0

        if DO_WAITING_LOOPS:
            NwaitingLoops = 6
            WaitRecording = 240
            integral_t = TimeSleep0 + TimeSleep1 + TimeSleep2 + TimeSleep3
            for l in range(0,NwaitingLoops):
                print('waiting...')
                #time.sleep(wait)
                # recording
                recorder = scope.record(sample_rate=sample_rate_waitingMode, length=WaitRecording, configure=True, start=True)
                t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate_waitingMode)
                voltage_diff = (recorder.channels[0].data_samples - recorder.channels[1].data_samples)
                # Plot current vs. voltage difference
                I = (voltage_diff) / R #Ohm
                G = I / (-1 * recorder.channels[0].data_samples)

                csvfilename = SaveCSV_and_upload(t, -1 * recorder.channels[0].data_samples, I, G,
                                        dirsuffix='R_meas', memNumber=str(m+1), impose_dir=impose_dir, suffix=f'_2ndRead_{integral_t}')#The suffix is used also for following plots
                plot_Capture(t, recorder, title=f'R-measurement intg-t({integral_t})', csvfilename=csvfilename, memNumber=str(m+1))
                time.sleep(0.1)

                #split data in periods and extract many R_measurements
                cycles_data = extract_cycles(csvfilename, NumCycles, frequency) #from 1 to NumCycles
                plot_IV_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), N=1, title=f'R-measurement intg-t({integral_t})')
                plot_GV_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), N=1, title=f'R-measurement intg-t({integral_t})')
                plot_Gmean_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), N=1, title=f'R-measurement intg-t({integral_t})')
                # Creare il modello di regressione lineare
                estimate_R_byCycles(cycles_data, csvfilename=csvfilename, memNumber=str(m+1), suffix=f'_2ndRead_{integral_t}', title=f'R-measurement intg-t({integral_t})')
                integral_t += WaitRecording


        # Start recording on channels 0 and 1, lenght set number of seconds of recording
        print("   Disabling wavegen...", time.time())
        wavegen[0].setup(enabled=False, offset=0.0)
        recorder = scope.record(sample_rate=10000, length=1, configure=True, start=True)
        #print("End final recording", time.time())
        t = step_seconds_converter(recorder.channels[0].data_samples, sample_rate)
        plot_Capture(t, recorder, title='Voltage on the board after diseabling W1', memNumber=str(m+1))

    #while True:
    #    time.sleep(1)
    #    pass
