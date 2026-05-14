def stepped_pw_inc_dec(
    current_g: float,
    target_g: float,
    time_period: float,
    min_pw: float = 10e-6,
    is_increasing: bool = False, 
    mode: str = "aggressive",
    G_history: list | None = None,   
    G_history_dec: list | None = None
) -> float:
    """
    Adaptive pulse-width selection.
    INC  : original stepped logic (unchanged)
    DEC  : adaptive, history-aware PW with slow dynamics"""
    # what is this function doing? This function determines the pulse width to be used for programming the conductance based on whether we are increasing or decreasing the conductance, the current and target conductance values, and the history of conductance values. For increasing scenarios, it uses a stepped logic that reduces the pulse width as we get closer to the target. For decreasing scenarios, it includes an adaptive mechanism that detects if the device is "stuck" (not changing much) and increases the pulse width in that case, as well as damping for ping-pong behavior. The function ensures that the pulse width stays within specified bounds for effective programming.
    pw_nom = time_period / 2 # assume her we use 50 mus. 
    dG = abs(current_g - target_g)
  # ---------- Ping-pong detection ----------
    def pingpong(hist, tgt):
        if hist is None or len(hist) < 3:
            return False
        
        e1 = hist[-3] - tgt
        e2 = hist[-2] - tgt
        e3 = hist[-1] - tgt
        return (e1 * e2 < 0) or (e2 * e3 < 0)

    pingpong_detected = pingpong(G_history, target_g)

    # ==========================================================
    # ---------------- INCREASE CASE  ---------------
    # ==========================================================
    if is_increasing:
        # For increase case the PW adaption is optional, you can remove these following lines and keep the width 50mus"
        # But for PingPong case it is better to reduce the width to avoid overshoot

        pw_reduce_threshold = 0.1 * target_g #  when within 10% of target, reduce PW to be more gentle (tune this threshold as needed)

        if dG <= pw_reduce_threshold:
            PW_used = pw_nom /2 # what will be the PW here? 25 mus, more gentle to avoid overshoot when close to target.
        else:
            PW_used = pw_nom 

        # # ---------- NEW: slow-mode PW attenuation ----------
        if mode == "slow" or mode == "aggressive":
            if pingpong_detected:  #  pingpong damping in slow mode
                PW_used = PW_used /2 # what will be the PE here? 12.5 mus, more aggressive damping for pingpong in slow mode
            else:
                PW_used = PW_used * 1.0 # no damping if no pingpong in slow mode
        
    # ==========================================================
    # ---------------- DECREASE CASE (ADAPTIVE) ----------------
    # ==========================================================
    else:
        # Base conservative PW
        PW_used = pw_nom # 50 mus, more conservative for decrease to avoid overshoot and device stress

        # ---------- HISTORY-AWARE DEC EFFECTIVENESS ----------
        dec_stuck = False
        if target_g > 100e-06:
            DG_MIN_EFFECTIVE = 10e-6   # µS-level noise threshold
        else:
            DG_MIN_EFFECTIVE = 5e-6 
        if G_history_dec is not None and len(G_history_dec) >= 3:
            dG1 = G_history_dec[-3] - G_history_dec[-2]
            dG2 = G_history_dec[-2] - G_history_dec[-1]

            # ineffective if flat, increase, or tiny decrease
            if dG1 <= DG_MIN_EFFECTIVE and dG2 <= DG_MIN_EFFECTIVE:
                dec_stuck = True

        # ---------- ADAPT PW ONLY IF DEC IS STUCK ----------
        if dec_stuck:
            PW_used = max(PW_used / 2, pw_nom)   # escalate PW, bounded # what will be the PE here? 50 mus, more aggressive for stuck decrease to try to get it moving again, 
          
        # --------ping-pong damping (DEC gentle) ----------
        if pingpong_detected:
            PW_used = PW_used * 1.0  # dampening for pingpong in DEC mode

        PW_used = max(PW_used, min_pw)

    # ---------- Final formatting ----------
    PW_used = round(PW_used * 1e6) * 1e-6
    return PW_used
