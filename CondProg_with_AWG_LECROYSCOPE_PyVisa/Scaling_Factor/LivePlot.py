# Scaling_Factor/live_plot.py
import matplotlib.pyplot as plt

class LivePlot:
    def __init__(self, target_uS, lower_uS, upper_uS, max_attempts, iteration):
        plt.ion()
        self.plot_step = 0

        self.fig, (self.ax_g, self.ax_k) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)

        # --- G plot ---
        self.line_g, = self.ax_g.plot([], [], "o-", label="G")
        self.ax_g.axhline(target_uS, ls="--", color="r", label="Target")
        self.ax_g.fill_between(
            [0, max_attempts + 20],
            lower_uS,
            upper_uS,
            color="gray",
            alpha=0.15,
            label="Tolerance"
        )
        self.ax_g.set_ylabel("Conductance (µS)")
        self.ax_g.set_title(f"Live Programming | Iter {iteration}")
        self.ax_g.legend()
        self.ax_g.grid(True)

        # --- K plot ---
        self.line_k, = self.ax_k.plot([], [], "s-", color="tab:orange")
        self.ax_k.set_xlabel("Attempts")
        self.ax_k.set_ylabel("Scaling Factor K")
        self.ax_k.grid(True)

        self.x = []
        self.g = []
        self.k = []

    def update(self, G_uS, K):
        self.x.append(self.plot_step)
        self.g.append(G_uS)
        self.k.append(K)
        self.plot_step += 1

        self.line_g.set_data(self.x, self.g)
        self.ax_g.relim()
        self.ax_g.autoscale_view()

        self.line_k.set_data(self.x, self.k)
        self.ax_k.relim()
        self.ax_k.autoscale_view()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

    def closed(self):
        return not plt.fignum_exists(self.fig.number)

    def finalize(self, filename):
        self.fig.savefig(filename, dpi=300)
        plt.close(self.fig)
