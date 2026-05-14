def init_base_np(
    target_g: float, current_g: float,
    is_increasing: bool,
    mode: str = "slow"   # only used for INC
) -> int:
    """
    Initialize base number of pulses.

    INC  : supports 'slow' and 'aggressive' start
    DEC  : fixed, trusted logic (unchanged)
    """
    
    # what is this function doing? This function initializes the base number of pulses (NP) to be applied for the first
    #  update based on the target conductance, current conductance, whether we are increasing or decreasing the conductance, 
    # and a mode that can be "slow" or "aggressive" for increasing scenarios. The logic uses predefined thresholds to determine 
    # the appropriate NP, with more aggressive settings for higher target conductances in the increasing case, and a fixed logic for the decreasing
    #  case based on the distance to the target. This initial NP will then be refined in subsequent iterations as we get closer to the target conductance.
    dG = abs(current_g - target_g)
    # ---------------- INC logic ----------------
    if is_increasing:
        if mode == "very slow":
            if target_g <= 50e-6:
                return 1
            elif target_g <= 150e-6:
                return 2
            elif target_g <= 250e-6:
                return 5
            else:
                return 10
        elif mode == "slow":
            if target_g <= 50e-6:
                return 2
            elif target_g <= 150e-6:
                return 10
            elif target_g <= 250e-6:
                return 15
            else:
                return 20
        elif mode == "aggressive":
            if target_g <= 50e-6:
                return 5
            elif target_g <= 150e-6:
                return 15
            elif target_g <= 250e-6:
                return 20
            else:
                return 30
        else:
            raise ValueError(f"Unknown init mode: {mode}")

    # ---------------- DEC logic (UNCHANGED) ----------------
    else:
        if dG > 150e-06:
            return 20
        elif  dG > 80e-06:
            return 15
        else:
            return 10


  

def refine_np_near_target(
    base_np: int,
    current_g: float,
    target_g: float
) -> int:
    """
    Reduce NP aggressively when close to target,
    especially for low target conductance.
    """

    rel_error = abs(current_g - target_g) / target_g

    # ---- Very close to target (within 20%) ----
    if rel_error <= 0.20:
        if target_g < 100e-6:
            return min(base_np, 2)
        else:
            return base_np

    # ---- Moderately close (20–40%) ----
    if rel_error <= 0.40:
        if target_g < 100e-6:
            return min(base_np, 5)
        else:
            return base_np

    # ---- Far from target ----
    return base_np
