from Read_write_reset.ReadMemristor import ReadMemristor
from Read_write_reset.ResetMemristor import ResetMemristor
import time
def handle_runaway(
    current_g_value,
    is_increasing,
    intended_g_value,
    max_conductance,
    awg_handle,
    oscilloscope,
    channel,
    runaway_counter,
    RUNAWAY_LIMIT,
    reset_pulses=10,
    extra_reset_pulses=20,
    extra_reset_limit=3,
    recovery_threshold=350e-6,
    sleep_after_reset=0.5
):
    """
    Handle runaway conductance safely.

    Returns:
        recovered (bool): True if device recovered
        abort (bool): True if persistent runaway detected
        current_g_value (float): Updated conductance
        runaway_counter (int): Updated runaway counter
    """

    runaway = False

    # ---------- RUNAWAY DETECTION ----------
    if current_g_value >= recovery_threshold:
        runaway = True
    #elif is_increasing and current_g_value > intended_g_value + max_conductance:
        #runaway = True

    if not runaway:
        return True, False, current_g_value, runaway_counter

    print(f"[SAFETY] Runaway conductance detected: {current_g_value*1e6:.2f} µS")
    print("[SAFETY] Performing safety reset sequence")

    # ---------- FIRST RESET ----------
    ResetMemristor(awg_handle, channel, reset_pulses)
    time.sleep(sleep_after_reset)
    current_g_value = ReadMemristor(awg_handle, oscilloscope, channel)

    print(f"[SAFETY] G after reset: {current_g_value*1e6:.2f} µS")

    # ---------- EXTRA RESET LOOP ----------
    safety_resets = 0
    while current_g_value > 100e-6 and safety_resets < extra_reset_limit:
        print(
            f"[SAFETY] G still high ({current_g_value*1e6:.2f} µS) "
            f"--> extra reset {safety_resets+1}/{extra_reset_limit}"
        )
        ResetMemristor(awg_handle, channel, extra_reset_pulses)
        time.sleep(sleep_after_reset)
        current_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
        safety_resets += 1

    print(f"[SAFETY] Final G after safety loop: {current_g_value*1e6:.2f} µS")

    # ---------- RECOVERY DECISION ----------
    if current_g_value <= recovery_threshold:
        print("[RECOVERY] Runaway recovered --> continuing programming")
        runaway_counter = 0
        return True, False, current_g_value, runaway_counter

    # ---------- UNRECOVERED RUNAWAY ----------
    runaway_counter += 1
    print(f"[FAIL] Runaway not recovered ({runaway_counter}/{RUNAWAY_LIMIT})")

    if runaway_counter >= RUNAWAY_LIMIT:
        print("[FATAL] Persistent runaway —> device not recoverable")
        return False, True, current_g_value, runaway_counter

    return False, False, current_g_value, runaway_counter
