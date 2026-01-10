            # ===================== SCALING LOGIC =====================
def init_alpha_beta(G_init, G_target, G_max, is_increasing):
    """
    Smooth gain scheduling:
    Choose K_des that is linear in G_target, then solve alpha so that
    K = alpha*(er + gt*ea) matches K_des. Keep beta = alpha*gt.
    """
    g0 = G_init / max(G_max, 1e-12) # Current normalized conductance or current G value
    gt = G_target / max(G_max, 1e-12) # target normalized conductance

    # apply the same K shaping in both directions, for absolute error:
    dG = abs(G_target - G_init)

    # Errors at initialization (same definitions used later) # relative error
    if is_increasing:
        er = (G_target - G_init) / max(G_target, 1e-12)
    else:
        er = (G_init - G_target) / max(G_init, 1e-12) 

    ea = dG / max(G_max, 1e-12)

    # ----- Desired linear K vs target (tune these 4 numbers, Gmin, Gmax, Kmin, Kmax) -----
    Gmin = 40e-6 #  Minimum target conductance
    Gmax_lin = 250e-6 # Maximum target conductance
    # ---- Direction-aware K range, Constarint on scaling factor, and it should be linear in this range----
    if is_increasing:
        Kmin = 0.10
        Kmax = 2.0
    else:
        Kmin = 0.10
        Kmax = 1.00

    # ---- Linear mapping of target K, t is just a factor b/w 0 and 1, k_des is the desired factor i.e., 
    # 0.1 and 2.0 or 3.0 ----
    if is_increasing:
        t = (min(max(G_target, Gmin), Gmax_lin) - Gmin) / (Gmax_lin - Gmin)
    else:
        # Use distance to go for RESET
        dGmax = max(1e-12, (G_max - Gmin))   # scale reference
        t = min(1.0, max(0.0, dG / dGmax))   # larger drop => larger K_des

    K_des = Kmin + (Kmax - Kmin) * t # desired K, what we want to achieve

    # ---- Solve alpha to hit K_desired smoothly ----
    denom = er + gt * ea #
    if abs(denom) < 1e-9:   # Very rare case, avoid div by zero 
        alpha = 1.0 # arbitrary
    else:
        alpha = K_des / denom # solve for alpha, real definition of K

    # ---- Safety limits ----
    alpha = max(0.1, min(3.0, alpha)) # alpha non-negative
    beta  = alpha * gt
    beta  = max(0.0, min(3.0, beta)) # beta non-negative
    return alpha, beta
