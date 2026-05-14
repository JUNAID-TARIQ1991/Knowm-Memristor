def update_scaling(
    IntendedG_value,
    G_current,
    G_target,
    G_max,
    alpha,
    beta,
    G_history,
    attempt,
    max_attempts,
    is_increasing=True
):
    """
    Compute scaling factor K and update alpha/beta.

    INC (SET):
        - Adaptive gain (alpha/beta)
        - Stuck detection accelerates convergence

    DEC (RESET):
        - Bounded, distance-based scaling
        - No alpha/beta adaptation
        - Authority handled via PW, not K
    """

    # =========================
    # ---- INCREASING CASE ----
    # =========================
    if is_increasing:

        # Relative error (toward target)
        er = (G_target - G_current) / max(G_target, 1e-12)

        # Absolute/global error
        ea = abs(G_target - G_current) / max(G_max, 1e-12)

        # ---- Stuck detection ----
        stuck = False
        if G_history is not None and len(G_history) >= 2:
            dG = abs(G_history[-1] - G_history[-2])
            if dG < 0.15 * G_current:
                stuck = True

        # ---- Adaptive alpha/beta update ----
        if stuck:
            gain = 0.2 + 0.1 * (attempt / max_attempts)
            alpha *= (1.0 + gain)
            beta  *= (1.0 + 0.5 * gain)

        # ---- Scaling factor ----
        K = alpha * er + beta * ea

        # ---- Clamp ----
        K = max(0.1, min(3.0, K))

        return K, alpha, beta, stuck


    # =========================
    # ---- DECREASING CASE ----
    # =========================
    else:
        # Distance above target
        dG = max(G_current - G_target, 0.0)

        # Normalized distance (geometry, NOT gain)
        er = dG / max(G_target, 1e-12)

        # ---- Bounded DEC scaling ----
        # No alpha/beta adaptation here
        # No stuck-driven gain escalation
        K = max(0.1, min(1.0, er))

        return K, alpha, beta, 
