# Distributed IoT Sensor Data Compression and Transmission Optimization System

Multi-node IoT pipeline: Arduino + ESP32 nodes read 10 sensor channels, a TensorFlow/Keras autoencoder
compresses 16-sample windows (160 values -> 20 latent values, **8:1**), and an adaptive policy decides
*whether* to transmit based on WiFi strength, battery level and data change rate. Data travels over MQTT
into InfluxDB and is visualised in Grafana.

```
Sensors -> ESP32 (encoder + adaptive policy) --MQTT--> bridge (decoder) -> InfluxDB -> Grafana
```

## Structure
- `src/generate_data.py` – synthetic 10-channel stream (swap in real logs if you have them)
- `src/autoencoder.py`, `src/train.py` – model, training, TFLite export
- `src/adaptive_policy.py`, `src/simulate.py`, `src/sweep.py` – policy, energy simulation, threshold sweep
- `bridge/mqtt_to_influx.py` – MQTT subscriber -> decode -> InfluxDB
- `firmware/esp32_node/esp32_node.ino` – ESP32 sketch (sensor reads + TFLite Micro hook are TODO placeholders)

## Run
```bash
pip install -r requirements.txt
python src/train.py      # trains, prints compression ratio + accuracy
python src/simulate.py   # baseline vs adaptive, writes results/system_metrics.json
python src/sweep.py      # threshold trade-off table
```

## Results (simulation on synthetic data)
Accuracy = 1 - mean absolute error / signal range. Energy uses a simple radio model (see `tx_energy_mj`),
not hardware measurements.

| threshold | windows sent | energy saved | accuracy |
|---|---|---|---|
| 0.0 | 3750/3750 | 66.9% | 97.5% |
| 0.5 | 3355/3750 | 70.5% | 96.2% |
| 0.6 | 2737/3750 | 76.0% | 93.7% |
| 0.7 | 2415/3750 | 78.8% | 92.8% |
| 0.75 | 1884/3750 | 83.5% | 91.0% |
| 0.85 | 799/3750 | 93.0% | 86.6% |

Higher threshold = fewer transmissions = more energy saved, but the receiver holds stale data longer.
Default threshold is 0.6.

## Limitations
- Data is synthetic and the energy model is a toy; replace both with real logs / measured current draw.
- The firmware is a skeleton: add your sensor libraries and run the encoder on-device via TFLite Micro.
