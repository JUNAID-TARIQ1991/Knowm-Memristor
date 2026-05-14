# stuck_monitor.py
# ------------------------------------------------
# Generic stuck / ineffective programming detector
# Includes stuck-low detection
# ------------------------------------------------

class StuckMonitor:
    def __init__(
        self,
        min_effective_dG=10e-6,     # 1 µS 
        min_error_reduction=0.1,  # 10 %
        stuck_low_threshold=20e-6,  # 20 µS
        max_hard_stuck_iter=3, 
        max_iter_failures=2,              # if you fail to reach target for N consecutive iterations, consider it a global stuck condition
        plateau_threshold=10e-6,           # NEW: if final G stays within 5 µS for N iterations, consider it a plateau
        plateau_window=3):                # store last N iteration results for plateau detection
   

        self.min_effective_dG = min_effective_dG
        self.min_error_reduction = min_error_reduction
        self.stuck_low_threshold = stuck_low_threshold
        self.max_hard_stuck_iter = max_hard_stuck_iter
        self.hard_stuck_count = 0   
        self.G_history = []
        self.iteration_fail_count = 0
        self.max_iter_failures = max_iter_failures
        self.iteration_final_G = []
        self.plateau_threshold = plateau_threshold
        self.plateau_window = plateau_window


    def reset(self):
        """Clear history (call after reset / restart)."""
        self.G_history.clear() 
    # Log each attempt output
    def update(self, G_current):
        """Append new conductance value."""
        self.G_history.append(G_current)
    # If meristor consistently stuck high after hard reset
    def check_stuck_high(self, G_target, factor=2.0):
        if len(self.G_history) < 2: # wait untill final attempt
            return False

        G_start = self.G_history[0]
        G_end   = self.G_history[-1]

        # Always far above target
        if G_start > factor * G_target and G_end > factor * G_target: # factor i defined 2
            # No meaningful decrease
            if abs(G_end - G_start) / G_start < 0.05:
                return True

        return False

    def is_stuck(self, G_target):
        """
        Detect ineffective programming.
        Returns (stuck: bool, reason: str)
        """

        # ---------- --------------------------STUCK-LOW CHECK  and Hard Stuck Low-----------------------------------------
        if len(self.G_history) >= 2: # see all the attempts
            G_start = self.G_history[0]
            G_end   = self.G_history[-1]
            G_max   = max(self.G_history)

            # If the device EVER escaped low-G, forgive past hard-stuck failures
            if G_max > self.stuck_low_threshold:
                self.hard_stuck_count = 0
            
            # ---- HARD STUCK LOW (highest priority) ----
            if (G_start < 0.5 * self.stuck_low_threshold and
                G_end   < 0.5 * self.stuck_low_threshold and
                G_max   < 0.8 * self.stuck_low_threshold):
                
                self.hard_stuck_count += 1
                if self.hard_stuck_count >= self.max_hard_stuck_iter:
                    return True, "PERMANENT_HARD_STUCK"

                return True, "HARD_STUCK_LOW"
                
            # ---- STUCK LOW ----
            if (G_start < self.stuck_low_threshold and
                G_end   < self.stuck_low_threshold and 
                G_max   < 2 * self.stuck_low_threshold): # if you never escaped (2* low threshold = 40 muS)
                return True, "STUCK_LOW"

        # ---------- -----------------------GENERAL STUCK CHECK -------------------------------------------
        if len(self.G_history) < 2 :
            return False, None

        if self.check_stuck_high(G_target):
            return True, "STUCK_HIGH"

        recent = self.G_history

        # Net conductance change
        delta_G = abs(recent[-1] - recent[0])

        # Error reduction toward target
        err_start = abs(G_target - recent[0])
        err_end   = abs(G_target - recent[-1])

        error_reduction = (err_start - err_end) / max(err_start, 1e-12)

        if delta_G < self.min_effective_dG:
            return True, "NO_EFFECTIVE_RESPONSE"

        if error_reduction < self.min_error_reduction:
            return True, "NO_PROGRESS_TOWARD_TARGET"

        return False, None

    def register_iteration_result(self, target_reached, final_G):
        """
        Call this once per iteration at the end.
        """

        # Store final conductance history
        self.iteration_final_G.append(final_G)

        if target_reached:
            self.iteration_fail_count = 0
            return False, None

        # Increment failure counter
        self.iteration_fail_count += 1

        if self.iteration_fail_count >= self.max_iter_failures:
            return True, "CONSECUTIVE_ITERATION_FAILURE"

        # Plateau detection
        if len(self.iteration_final_G) >= self.plateau_window:
            recent = self.iteration_final_G[-self.plateau_window:]
            if max(recent) - min(recent) < self.plateau_threshold:
                return True, "PLATEAU_BELOW_TARGET"

        return False, None

