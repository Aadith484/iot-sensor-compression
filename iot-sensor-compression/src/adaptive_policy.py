"""Adaptive transmission policy: per window decide SKIP or send LATENT.

Inputs: wifi RSSI (dBm), battery (0-1), data change rate, windows since last send.
"""
from dataclasses import dataclass

@dataclass
class Policy:
    base_thresh: float = 0.6   # tuned on latent change-rate distribution (see README)
    heartbeat: int = 8            # force a send at least every N windows

    def decide(self, rssi, battery, change, since_last):
        thresh = self.base_thresh
        if rssi < -75: thresh *= 1.5      # weak wifi -> pickier
        if battery < 0.3: thresh *= 1.5   # low battery -> pickier
        if since_last >= self.heartbeat: return "LATENT"
        return "SKIP" if change < thresh else "LATENT"

def tx_energy_mj(n_bytes, rssi):
    """Toy radio model: cost per byte rises as signal weakens, plus fixed wake overhead.
    Calibrate these constants against real current measurements for a credible report."""
    per_byte = 0.002 * (1 + max(0, (-rssi - 55)) / 25)
    return n_bytes * per_byte + 0.5
