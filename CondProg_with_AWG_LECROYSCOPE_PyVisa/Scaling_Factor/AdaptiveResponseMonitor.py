# class AdaptiveResponseMonitor:

#     def __init__(self, target_G, window=5):
#         self.target_G = target_G
#         self.window = window
#         self.G_window = []

#     def _base_threshold(self):
#         G_uS = self.target_G * 1e6
#         if G_uS < 50:
#             return 10e-6
#         elif G_uS < 150:
#             return 30e-6
#         else:
#             return 50e-6

#     def check(self, G_current):
#         self.G_window.append(G_current)

#         if len(self.G_window) < self.window:
#             return False

#         if len(self.G_window) > self.window:
#             self.G_window.pop(0)

#         G_old = self.G_window[0]
#         window_dG = abs(G_current - G_old)

#         err_start = abs(G_old - self.target_G)
#         err_end   = abs(G_current - self.target_G)
#         moving_toward_target = err_end < err_start

#         base_th = self._base_threshold()
#         dynamic_th = min(base_th, 0.4 * err_end)

#         if window_dG < dynamic_th and not moving_toward_target:
#             return True

#         return False

 

#     def initialize(self, G_initial):
#         self.G_initial = G_initial
#         self.G_window = [G_initial]


#     def reset(self):
#         self.G_window.clear()

class DirectionalResponseMonitor:

    def __init__(self, target_G,
                 max_wrong_direction=3,
                 max_weak_response=5):

        self.target_G = target_G
        self.max_wrong_direction = max_wrong_direction
        self.max_weak_response = max_weak_response

        self.prev_G = None
        self.wrong_dir_count = 0
        self.weak_count = 0

    def reset(self):
        self.prev_G = None
        self.wrong_dir_count = 0
        self.weak_count = 0

    def _delta_threshold_inc(self, G_current):
        error = abs(G_current - self.target_G)
        dynamic_th = 0.1 * error
        min_floor = 2e-6
        return max(dynamic_th, min_floor)   
    
    def _delta_threshold_dec(self, G_current):

        error = abs(G_current - self.target_G)

        # Error-based dynamic threshold
        delta_th = 0.1 * error

        # Minimum floor to avoid hypersensitivity
        min_floor = 2e-6

        return max(delta_th, min_floor)


    # Check if response is in expected direction and magnitude
    def check(self, G_current, is_increasing):

        if self.prev_G is None:
            self.prev_G = G_current
            return False

        dG = G_current - self.prev_G
        if is_increasing:
            delta_th = self._delta_threshold_inc(G_current)
        else:
            delta_th = self._delta_threshold_dec(G_current)

        # ---- INC mode ----
        if is_increasing:

            if dG > delta_th:
                # Strong correct move
                self.wrong_dir_count = 0
                self.weak_count = 0

            elif dG > 0:
                # Small correct move but below threshold
                self.wrong_dir_count = 0
                self.weak_count += 1
            
            elif dG < -delta_th:
                # Significant wrong direction
                self.wrong_dir_count += 1

            else:
                # Small fluctuation
                self.weak_count += 1

        # ---- DEC mode ----
        else:
            wrong_dir_th = 0.5 * delta_th
            if dG < -delta_th:
                # Strong correct decrease
                self.wrong_dir_count = 0
                
            elif dG > wrong_dir_th:
                # Significant wrong direction
                self.wrong_dir_count += 1

            else:
                # Small fluctuation
                self.weak_count += 1

        self.prev_G = G_current
        # Trigger if too many wrong direction moves or weak responses
        if (self.wrong_dir_count >= self.max_wrong_direction or
            self.weak_count >= self.max_weak_response):
            return True

        return False
