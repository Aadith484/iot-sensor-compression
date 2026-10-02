"""Baseline (raw every window) vs compressed+adaptive. All numbers are MEASURED here."""
import json, numpy as np
from tensorflow import keras
from generate_data import generate
from autoencoder import make_windows, accuracy, WINDOW, CH, LATENT
from adaptive_policy import Policy, tx_energy_mj

enc = keras.models.load_model("results/encoder.keras")
dec = keras.models.load_model("results/decoder.keras")
n = np.load("results/norm.npz"); mu, sd, rng_ = n["mu"], n["sd"], n["rng"]

data = generate(seed=7)
X = make_windows((data - mu) / sd)
Z = enc.predict(X, verbose=0); R = dec.predict(Z, verbose=0)

rs = np.random.default_rng(1)
rssi = -60 + 12 * np.sin(np.arange(len(X)) / 200) + rs.normal(0, 3, len(X))
pol = Policy()
raw_b, lat_b = WINDOW * CH * 4, LATENT * 4
e_base = e_adapt = 0.0; since = 0; sent = 0
recon = np.zeros_like(X); cur = R[0]
for i in range(len(X)):
    battery = max(0.05, 1 - i / len(X))
    change = float(np.abs(Z[i] - Z[i - 1]).mean()) if i else 1.0
    e_base += tx_energy_mj(raw_b, rssi[i])
    if pol.decide(rssi[i], battery, change, since) == "LATENT":
        e_adapt += tx_energy_mj(lat_b, rssi[i]); cur = R[i]; since = 0; sent += 1
    else:
        since += 1
    recon[i] = cur

xt = (X.reshape(-1, CH) * sd + mu).reshape(-1, WINDOW * CH)
xr = (recon.reshape(-1, CH) * sd + mu).reshape(-1, WINDOW * CH)
out = {"windows": len(X), "windows_transmitted": sent,
       "energy_baseline_mJ": e_base, "energy_adaptive_mJ": e_adapt,
       "energy_reduction_pct": 100 * (1 - e_adapt / e_base),
       "end_to_end_accuracy_pct": 100 * accuracy(xt, xr, rng_),
       "compression_ratio": (WINDOW * CH) / LATENT}
json.dump(out, open("results/system_metrics.json", "w"), indent=2)
print(json.dumps(out, indent=2))
