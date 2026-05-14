import sys
import time

class InitialReset:
    def __init__(self,reset_pulses=5,stuck_high_g= 800e-06, reset_attempts =2, stuck_attempts = 3):
        
        self.reset_pulses = reset_pulses
        self.stuck_high_g = stuck_high_g
        self.reset_attempts = reset_attempts
        self.stuck_attempts = stuck_attempts
        self.stuck_counter = 0


    def initial_reset_check(self, awg_handle, oscilloscope, channel, do_initial_reset=True):

        from Read_write_reset.ResetMemristor import ResetMemristor
        from Read_write_reset.ReadMemristor import ReadMemristor
        from Read_write_reset.Stuck_High_check import Pulse4StuckHigh
        from Read_write_reset.Stuck_low_check import Pulse4StuckLow
        import time

        NORMAL_RESET_G = 20e-6     # success threshold
        STRONG_RESET_G = self.stuck_high_g

        def adaptive_reset_pulses(g, base):
            if g > 200e-6:
                return base * 5
            elif g > 100e-6:
                return base * 2
            else:
                return base 

        # ---------- NO INITIAL RESET ----------
        if not do_initial_reset:
            print("[INIT] Initial reset disabled")
            return ReadMemristor(awg_handle, oscilloscope, channel), False

        # ---------- INITIAL READ ----------
        g = ReadMemristor(awg_handle, oscilloscope, channel)
        time.sleep(0.1)
        print(f"[INIT] Initial G = {g*1e6:.2f} µS")

        # ==================================================
        # PHASE 1: STUCK-HIGH RECOVERY
        # ==================================================
        if g > STRONG_RESET_G:
            print("[INIT] Entering STUCK-HIGH recovery")

            for i in range(self.stuck_attempts):
                print(f"[STUCK] Attempt {i+1}/{self.stuck_attempts}")

                Pulse4StuckHigh(awg_handle,channel,Time_Period=100e-3,Amplitude=1.0,No_pulses=10)
                time.sleep(0.5)
                ResetMemristor(awg_handle,channel,50, Amplitude= -2.0)
                time.sleep(0.2)
                g = ReadMemristor(awg_handle, oscilloscope, channel)
                print(f"[STUCK] Final G = {g*1e6:.2f} µS (R = {(1 / g) / 1e3:.1f} kΩ)")

                if g <= STRONG_RESET_G:
                    print("[STUCK] Recovery successful")
                    break
            else:
                print("[ERROR] Memristor permanently STUCK HIGH (Required hardware reset)")
                return g, True   # HARD FAILURE

        # ==================================================
        # PHASE 2: NORMAL RESET
        # ==================================================
        for j in range(self.reset_attempts):
            if g <= NORMAL_RESET_G:
                print("[INIT] Normal reset successful")
                return g, False
            print(f"[INIT] Normal reset {j+1}/{self.reset_attempts} with {self.reset_pulses} pulses")
            
            ResetMemristor(awg_handle, channel, self.reset_pulses, -1.0)
            time.sleep(0.5)
            g = ReadMemristor(awg_handle, oscilloscope, channel)
            time.sleep(0.1)

            # ---------- FINAL STATUS ----------
        if g > NORMAL_RESET_G:
            print("[WARNING] Reset incomplete: G still high")
            
            
        r_kohm = (1 / g) / 1e3
        print(f"[INIT] Final G = {g*1e6:.2f} µS (R = {r_kohm:.1f} kΩ)")

        return g, False

    