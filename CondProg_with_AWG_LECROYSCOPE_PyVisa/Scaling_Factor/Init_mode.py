from Read_write_reset.Set_G_Channel import SendWritePulse
from Read_write_reset.ReadMemristor import ReadMemristor
from Read_write_reset.ResetMemristor import ResetMemristor
from Read_write_reset.Stuck_low_check import Pulse4StuckLow

import time
def detect_init_mode(
    awg_handle,
    oscilloscope,
    channel: int,
    current_g_value: float,
    probe_amp: float = 1.0,
    probe_pw: float = 50e-6,
    probe_np: int = 5,
    probe_g_threshold: float = 100e-6,  # <-- key threshold
    abs_jump_limit: float = 100e-6,      # optional safety
    settle_time: float = 0.2
) -> str:
    """
    Decide initial programming mode using a single INC probe pulse.
    """

    probe_g0 = current_g_value

    # --- Probe pulse ---
    SendWritePulse(
        awg_handle,
        probe_amp,
        probe_pw,
        probe_np,
        channel
    )
    time.sleep(settle_time)
    probe_g1 = ReadMemristor(awg_handle, oscilloscope, channel)
    time.sleep(0.1)
    probe_g1 = ReadMemristor(awg_handle, oscilloscope, channel)
    delta_g = probe_g1 - probe_g0 
    # --- Decision based on crossing threshold ---
    #if probe_g1 > probe_g_threshold or delta_g > abs_jump_limit:
    if probe_g1 > 350e-6: 
        mode = "very slow"
    elif probe_g1 > probe_g_threshold or delta_g > abs_jump_limit:
        mode = "slow"
    else:
        mode = "aggressive"

    print(
        f"[INIT-PROBE] G0={probe_g0*1e6:.2f} µS --> "
        f"G1={probe_g1*1e6:.2f} µS | "
        f"ΔG={delta_g*1e6:.2f} µS --> {mode.upper()} START"
    )
    ResetMemristor(awg_handle,channel,No_Pulses=5,Amplitude=-1.0)
    time.sleep(settle_time)

    new_g = ReadMemristor(awg_handle, oscilloscope, channel)

    return mode, new_g
