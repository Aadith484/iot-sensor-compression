"""Synthetic 10-channel sensor stream (stand-in for real Arduino/ESP32 logs).

Channels: temp, humidity, pressure, light, gas, sound, acc_x, acc_y, acc_z, gyro_z
Replace `generate()` output with your own CSV logs if you have real data:
    data = np.loadtxt("my_log.csv", delimiter=",")  # shape (N, 10)
"""
import numpy as np

CHANNELS = ["temp", "humidity", "pressure", "light", "gas",
            "sound", "acc_x", "acc_y", "acc_z", "gyro_z"]

def generate(n=60000, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    day = np.sin(2 * np.pi * t / 5000)
    temp = 27 + 3 * day + rng.normal(0, 0.05, n)
    hum = 60 - 8 * day + rng.normal(0, 0.2, n)
    pres = 1009 + 0.5 * np.sin(2 * np.pi * t / 12000) + rng.normal(0, 0.02, n)
    light = np.clip(300 + 280 * day + rng.normal(0, 5, n), 0, None)
    gas = 120 + 0.4 * hum + rng.normal(0, 1, n)
    sound = 40 + 5 * np.abs(np.sin(2 * np.pi * t / 700)) + rng.normal(0, 0.5, n)
    motion = np.sin(2 * np.pi * t / 90)
    acc_x = 0.3 * motion + rng.normal(0, 0.02, n)
    acc_y = 0.2 * np.sin(2 * np.pi * t / 90 + 1) + rng.normal(0, 0.02, n)
    acc_z = 1.0 + 0.1 * motion + rng.normal(0, 0.02, n)
    gyro = 15 * np.cos(2 * np.pi * t / 90) + rng.normal(0, 0.5, n)
    return np.stack([temp, hum, pres, light, gas, sound,
                     acc_x, acc_y, acc_z, gyro], axis=1).astype("float32")

if __name__ == "__main__":
    d = generate()
    np.save("results/sensor_data.npy", d)
    print("saved", d.shape)
