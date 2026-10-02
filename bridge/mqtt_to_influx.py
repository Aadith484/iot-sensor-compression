"""Subscribe to MQTT latent packets, decode, write to InfluxDB (Grafana reads from there)."""
import json, numpy as np, paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from tensorflow import keras

BROKER, TOPIC = "localhost", "iot/+/latent"
INFLUX = dict(url="http://localhost:8086", token="CHANGE_ME", org="my-org")
dec = keras.models.load_model("results/decoder.keras")
n = np.load("results/norm.npz"); mu, sd = n["mu"], n["sd"]
NAMES = ["temp","humidity","pressure","light","gas","sound","acc_x","acc_y","acc_z","gyro_z"]
write = InfluxDBClient(**INFLUX).write_api()

def on_msg(_, __, msg):
    node = msg.topic.split("/")[1]
    z = np.array(json.loads(msg.payload)["z"], dtype="float32")[None]
    w = dec.predict(z, verbose=0).reshape(-1, 10) * sd + mu
    for row in w:
        p = Point("sensors").tag("node", node)
        for k, v in zip(NAMES, row): p = p.field(k, float(v))
        write.write(bucket="iot", record=p)

c = mqtt.Client(); c.on_message = on_msg
c.connect(BROKER); c.subscribe(TOPIC); c.loop_forever()
