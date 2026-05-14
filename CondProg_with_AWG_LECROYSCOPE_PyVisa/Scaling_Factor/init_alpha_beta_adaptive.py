def init_alpha_beta(G_init, G_target, G_max, is_increasing):
    """
    Distance-aware initialization of alpha/beta.
    Aggressive far from target, gentle near target.
    """

    # -------- Normalizations --------
    gt = G_target / max(G_max, 1e-12)
    dG = abs(G_target - G_init)
    d  = dG / max(G_max, 1e-12)   # normalized distance [0, 1]

    # -------- Errors (same as before) --------
    if is_increasing:
        er = (G_target - G_init) / max(G_target, 1e-12)
    else:
        er = (G_init - G_target) / max(G_init, 1e-12)

    ea = dG / max(G_max, 1e-12)

    # -------- K range --------
    if is_increasing:
        Kmin, Kmax = 0.15, 2.0
    else:
        Kmin, Kmax = 0.10, 1.0

    # -------- DISTANCE-AWARE K_des --------
    # d = 1 → far → K ≈ Kmax
    # d = 0 → near → K ≈ Kmin
    K_des = Kmin + (Kmax - Kmin) * min(1.0, d / 0.5)
    # 0.5 = distance where K saturates (tunable)

    # -------- Safety attenuation near target --------
    if d < 0.15:
        K_des *= 0.5
    if d < 0.05:
        K_des *= 0.25

    # -------- Solve for alpha --------
    denom = er + gt * ea
    if abs(denom) < 1e-9:
        alpha = Kmin
    else:
        alpha = K_des / denom

    # -------- Clamp --------
    alpha = max(0.05, min(3.0, alpha))
    beta  = alpha * gt
    beta  = max(0.0, min(3.0, beta))

    return alpha, beta
