// ESP32 node: reads sensors, adapts transmission to WiFi/battery/change-rate, publishes via MQTT.
// NOTE: sensor reads are placeholders -- plug in your real sensor libraries.
#include <WiFi.h>
#include <PubSubClient.h>

const char* SSID = "YOUR_WIFI";  const char* PASS = "YOUR_PASS";
const char* BROKER = "192.168.1.10";  const char* NODE = "node1";
const int WINDOW = 16, CH = 10;
float buf[WINDOW][CH]; int idx = 0; float lastSent[CH] = {0}; int sinceLast = 0;
WiFiClient wifi; PubSubClient mqtt(wifi);

void readSensors(float* v) { for (int i = 0; i < CH; i++) v[i] = analogRead(34) / 4095.0f; }
float batteryLevel() { return analogRead(35) / 4095.0f; }

float changeRate() {
  float s = 0; for (int c = 0; c < CH; c++) s += fabs(buf[WINDOW-1][c] - lastSent[c]);
  return s / CH;
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(SSID, PASS);  while (WiFi.status() != WL_CONNECTED) delay(300);
  mqtt.setServer(BROKER, 1883);
}

void loop() {
  if (!mqtt.connected()) mqtt.connect(NODE);
  readSensors(buf[idx++]);
  if (idx == WINDOW) {
    idx = 0;
    int rssi = WiFi.RSSI(); float bat = batteryLevel();
    float thresh = 0.15; if (rssi < -75) thresh *= 1.5; if (bat < 0.3) thresh *= 1.5;
    if (changeRate() >= thresh || sinceLast >= 8) {
      // TODO: run TFLite Micro encoder here; send 20 latent values instead of raw
      String topic = String("iot/") + NODE + "/raw";
      mqtt.publish(topic.c_str(), (uint8_t*)buf, sizeof(buf));
      memcpy(lastSent, buf[WINDOW-1], sizeof(lastSent)); sinceLast = 0;
    } else sinceLast++;
  }
  delay(100);
}
