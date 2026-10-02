import json, numpy as np, tensorflow as tf
from generate_data import generate
from autoencoder import make_windows, build, accuracy, WINDOW, CH, LATENT

data = generate()
mu, sd = data.mean(0), data.std(0)
rng_ = data.max(0) - data.min(0)
X = make_windows((data - mu) / sd)
split = int(0.8 * len(X))
ae, enc, dec = build()
ae.fit(X[:split], X[:split], epochs=40, batch_size=64, validation_split=0.1, verbose=2)

xr = ae.predict(X[split:], verbose=0)
xt = (X[split:].reshape(-1, CH) * sd + mu).reshape(-1, WINDOW * CH)
xrt = (xr.reshape(-1, CH) * sd + mu).reshape(-1, WINDOW * CH)
acc = accuracy(xt, xrt, rng_)
ratio = (WINDOW * CH) / LATENT
print(f"compression ratio {ratio:.1f}:1 | reconstruction accuracy {acc*100:.2f}%")

enc.save("results/encoder.keras"); dec.save("results/decoder.keras")
np.savez("results/norm.npz", mu=mu, sd=sd, rng=rng_)
json.dump({"compression_ratio": ratio, "reconstruction_accuracy": acc},
          open("results/ae_metrics.json", "w"), indent=2)

conv = tf.lite.TFLiteConverter.from_keras_model(enc)   # edge deployment
open("results/encoder.tflite", "wb").write(conv.convert())
print("exported encoder.tflite")
