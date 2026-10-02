"""Windowed autoencoder: 16 samples x 10 channels = 160 values -> 20 latent (8:1)."""
import numpy as np
from tensorflow import keras

WINDOW, CH, LATENT = 16, 10, 20

def make_windows(data):
    n = (len(data) // WINDOW) * WINDOW
    return data[:n].reshape(-1, WINDOW * CH)

def build():
    inp = keras.Input(shape=(WINDOW * CH,))
    x = keras.layers.Dense(96, activation="relu")(inp)
    z = keras.layers.Dense(LATENT, activation="linear", name="latent")(x)
    d1 = keras.layers.Dense(96, activation="relu")
    d2 = keras.layers.Dense(WINDOW * CH, activation="linear")
    out = d2(d1(z))
    ae = keras.Model(inp, out)
    enc = keras.Model(inp, z)
    dec_in = keras.Input(shape=(LATENT,))
    dec = keras.Model(dec_in, d2(d1(dec_in)))
    ae.compile(optimizer=keras.optimizers.Adam(1e-3), loss="mse")
    return ae, enc, dec

def accuracy(x, xr, scale):
    """Reconstruction accuracy = 1 - mean abs error / signal range (per channel, original units)."""
    err = np.abs(x - xr).reshape(-1, WINDOW, CH).mean(axis=(0, 1))
    return float(1 - (err / scale).mean())
