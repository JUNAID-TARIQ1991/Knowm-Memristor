def update_scaling(IntendedG_value,G_current,G_target,G_max,alpha,beta,G_history,attempt,max_attempts,is_increasing):
    """
    Compute scaling factor K and update alpha/beta.
    Fully symmetric increasing/decreasing logic.
    """
# what is this function doing? This function computes the scaling factor K that will be used to adjust the conductance updates based on the current conductance, target conductance, and the history of conductance values. It also updates the alpha and beta parameters that contribute to K, and includes logic to detect if the device is "stuck" (not changing much) and adaptively increase the gain in that case. The function ensures that K, alpha, and beta stay within reasonable bounds to maintain stable and effective programming of the conductance.
# in the very initial iterations, the alpha and beta values are initialized based on the initial conditions and the desired scaling factor K_des. As the iterations progress, this function is called to compute the actual scaling factor K for each update, and it adjusts alpha and beta based on the observed errors and whether the device is making progress towards the target conductance. The logic is designed to be symmetric for both increasing and decreasing conductance scenarios, with specific adjustments to ensure smooth convergence and avoid overshooting or getting stuck.
    # --- Relative error (asymmetric, IMPORTANT) ---
    if is_increasing:
        er = (G_target - G_current) / max(G_target, 1e-12)
    else:                                         # old logic 04/02/2026
        er = (G_current - G_target) / max(G_current, 1e-12)

    # --- Absolute error ---
    ea = abs(G_target - G_current) / G_max

    # --- Stuck detection ---
    # what is stuck and how it boost the alpha and beta and what is gain??

    # Stuck is defined as a situation where the change in conductance (dG) between the last two attempts is less than 15% of the current conductance, indicating that the device is not responding effectively to the programming pulses. When stuck is detected, we apply a gain to alpha and beta to increase the scaling factor K, which in turn increases the magnitude of the updates in an attempt to "unstick" the device. The gain starts at 0.2 and can increase up to 0.3 as the number of attempts approaches the maximum allowed attempts, providing a gradual increase in aggressiveness to try to overcome the stuck condition without causing instability.
    stuck = False
    if len(G_history) >= 2:
        dG = abs(G_history[-1] - G_history[-2])
        if dG < 0.15 * G_current:  # less than 15% change
            stuck = True
    # --- Adaptive update in case of stuck ---
    if stuck:
        # Very mild gain, slowly increases with attempts
        gain = 0.2 + 0.1 * (attempt / max_attempts)
        alpha *= (1.0 + gain)  
        beta  *= (1.0 + 0.5 * gain)

    # --- Real Scaling factor ---
    # in each attempt we compute the scaling factor K based on the current alpha and beta, which are adjusted based on the observed errors and whether the device is stuck. The computed K is then clamped to ensure it stays within reasonable bounds for stable programming. The function returns the computed K along with the updated alpha, beta, and stuck status for use in the next iteration.
    # K is always positive, and we allow it to be larger for increasing case to speed up when far, but more conservative for decreasing case to avoid overshooting. The exact bounds can be tuned based on the specific device characteristics and desired programming behavior.
    K = alpha * er + beta * ea # combined effect Define K (scaling factor) ********

    # --- Safety clamps ---
    #if IntendedG_value <= 50e-6 and is_increasing:
        #K = max(0.1, min(0.1, K)) # K non-negative 
    #elif IntendedG_value<= 150e-6 and is_increasing:
        #K = max(0.1, min(0.5, K)) # K non-negative
    #else:
    if is_increasing:
        K = max(0.1, min(3.0, K)) # K non-negative default values
    else:
        K = max(0.1, min(2.0, K)) # K non-negative default values
    alpha = min(alpha, 5.0)
    beta  = min(beta, 5.0)

    return K, alpha, beta, stuck 
