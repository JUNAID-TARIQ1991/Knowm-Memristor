# ===================== SCALING LOGIC =====================
def init_alpha_beta(G_init, G_target, G_max, mode, is_increasing):
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
    #what is er and ea here? er is the relative error between the current conductance and the target conductance, normalized by the target conductance for increasing case, and by the current conductance for decreasing case. ea is the absolute error normalized by the maximum conductance. These errors are used to compute the desired scaling factor K_des, which in turn is used to solve for the initial alpha and beta values that will guide the scaling of updates in subsequent iterations.
    # ----- Desired linear K vs target (tune these 4 numbers, Gmin, Gmax, Kmin, Kmax) -----
    Gmin = 40e-6 #  Minimum target conductance
    Gmax_lin = 250e-6 # maximum target conductance for linear K scaling, above this K is maxed out
    # ---- Direction-aware K range, Constarint on scaling factor, and it should be linear in this range----
    if is_increasing:
        Kmin = 0.10
        if mode == "slow":
            Kmax = 1.00     # start stays conservative
        else:
            Kmax = 2.00     # aggressive  allow wider K for slow start
    else:
        Kmin = 0.10
        Kmax = 1.00

    # ---- Linear mapping of target K, t is just a factor b/w 0 and 1, k_des is the desired factor i.e., 
     # what is t here? here t is a normalized position of G_target between Gmin and Gmax_lin, so K_des will be Kmin when G_target is at Gmin, and Kmax when G_target is at or above Gmax_lin. This creates a smooth scaling factor that increases as the target conductance increases, but caps it at Kmax for very high targets. The logic is the same for both increasing and decreasing cases, but the interpretation of t differs slightly based on the direction of change.
    if is_increasing:
        t = (min(max(G_target, Gmin), Gmax_lin) - Gmin) / (Gmax_lin - Gmin)
    else:
        # Use distance to go for RESET
        dGmax = max(1e-12, (G_max - Gmin))   # scale reference
        t = min(1.0, max(0.0, dG / dGmax))   # larger drop => larger K_des      
    K_des = Kmin + (Kmax - Kmin) * t

    # ---- Distance-aware soft start (INCREASE only) ----
    if is_increasing:
        # normalized distance to target (0 = at target, 1 = far)
        dist = abs(G_target - G_init) / max(G_target, 1e-12)

        # If already moderately close, start very gently
        if dist < 0.4:
            K_des *= 0.6  # strong attenuation


    # ---- Small aggressive boost if starting from very low G < 5 mu or  > 200 k ohm (INCREASE only) ----
    if is_increasing and G_init <= 5e-6:
        K_des *= 1.25
        K_des = min(K_des, Kmax)

    # -------- FIX: distance-aware attenuation (INCREASE only) As approaching to the target soften the K --------
    #           For the linear fixed  K_init remove the following logic
    # if is_increasing:
    #     d = abs(G_target - G_init) / max(G_max, 1e-12)   # normalized distance
    #     d_ref = 0.2   # distance below which we soften k (≈ 20% of range)

    #     w = min(1.0, d / d_ref)   # 0 → close, 1 → far
    #     K_des = Kmin + (K_des - Kmin) * w


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
# This function initializes the alpha and beta parameters that are used to compute the scaling factor K for adjusting the conductance updates. The initialization is based on the initial conductance, target conductance, maximum conductance, and whether we are increasing or decreasing the conductance. The logic includes a desired linear scaling factor K_des that depends on the target conductance, as well as adjustments for being close to the target or starting from a very low conductance. Finally, it solves for alpha to achieve the desired K_des and applies safety limits to ensure reasonable values.