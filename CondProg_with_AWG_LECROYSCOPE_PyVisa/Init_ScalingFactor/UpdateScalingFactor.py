def update_scaling(G_current,G_target,G_max,alpha,beta,G_history,attempt,max_attempts,is_increasing):
    """
    Compute scaling factor K and update alpha/beta.
    Fully symmetric increasing/decreasing logic.
    """

    # --- Relative error (asymmetric, IMPORTANT) ---
    if is_increasing:
        er = (G_target - G_current) / max(G_target, 1e-12)
    else:
        er = (G_current - G_target) / max(G_current, 1e-12)

    # --- Absolute error ---
    ea = abs(G_target - G_current) / G_max

    # --- Stuck detection ---
    stuck = False
    if len(G_history) >= 2:
        dG = abs(G_history[-1] - G_history[-2])
        if dG < 0.1 * G_current:  # less than 5% change
            stuck = True
    # --- Adaptive update in case of stuck ---
    if stuck:
        # Very mild gain, slowly increases with attempts
        gain = 0.05 + 0.20 * (attempt / max_attempts)
        alpha *= (1.0 + gain)  
        beta  *= (1.0 + 0.5 * gain)

    # --- Real Scaling factor ---
    K = alpha * er + beta * ea # combined effect Define K (scaling factor) ********

    # --- Safety clamps ---
    K = max(0.1, min(3.0, K))
    alpha = min(alpha, 5.0)
    beta  = min(beta, 5.0)

    return K, alpha, beta, stuck
