// Caustic Bench Rig firmware
// Board: ESP32 DevKit V1 (Arduino board "DOIT ESP32 DEVKIT V1"), ESP32 Arduino core 3.x
//
// One DRV8833 drives both loads:
//   Channel A (AIN1/AIN2 -> AOUT1/AOUT2): speaker (4 ohm 3 W), wired directly. SPK_LIMIT caps its current.
//   Channel B (BIN1 -> BOUT1/BOUT2):      LED star, through one 3 ohm resistor. BIN2 is wired to GND.
//
// Control it from a web page or the Serial Monitor.
//   Web: join the Wi-Fi network "Caustic-Rig" (password "causticrig") and open http://192.168.4.1
//        If you save your home Wi-Fi on the page, it is also at http://caustic.local on your network.
//   Serial (115200 baud, "New Line"): led <0-100>, amp <0-100>, freq <hz>,
//        sweep <from> <to> <sec>, pattern <1-30>, patterns, comp <0-100>, stop, off, status, diag

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include "page.h"
#include "patterns.h"

const char *AP_SSID = "Caustic-Rig";
const char *AP_PASS = "causticrig";  // at least 8 characters
const char *HOSTNAME = "caustic";    // http://caustic.local

const int PIN_SPK_A = 25;  // DRV8833 AIN1 (IN1)
const int PIN_SPK_B = 26;  // DRV8833 AIN2 (IN2)
const int PIN_LED   = 27;  // DRV8833 BIN1 (IN3)

const int PWM_FREQ = 20000;
const int PWM_BITS = 10;
const int PWM_MAX  = (1 << PWM_BITS) - 1;

const int LED_START = 100;     // percent at power-up; needs the heatsink
const float FREQ_START = 10.0; // Hz
const float FREQ_MIN = 0.5, FREQ_MAX = 40.0;

// The speaker has no series resistor, so 100% on the slider is limited to 60% PWM duty:
// about 0.75 A peak and about 1.1 W into the 4 ohm 3 W speaker. Use the 5 V 2 A charger at high settings:
// all power passes through the ESP32 board's USB diode (about 1 A), so a PC port may brown out.
const float SPK_LIMIT = 0.60;

// Flicker fix. The speaker and LED share one 5 V supply, so the supply sags as the speaker pulls current and the
// LED dims with it. compPercent dims the LED by the same amount when the speaker is NOT pulling, so its brightness
// stays level. 0 = off. Raise it until slow ripples (1-3 Hz) stop flickering. Saved in flash.
const int COMP_START = 30;
int compPercent = COMP_START;

int ledPercent = LED_START;
int ampPercent = 0;  // speaker starts off
float freqHz = FREQ_START;

bool sweeping = false;
float sweepFrom, sweepTo;
unsigned long sweepStartMs, sweepMs;

float phase = 0;  // radians, accumulated so frequency changes never jump

// Patterns (patterns.h) are played by the waveform task. Other code only posts a request.
PatternPlayer player;
const int PAT_NO_REQ = -100;
volatile int patReq = PAT_NO_REQ;  // pattern index to start, -1 to stop
volatile uint32_t maxWaveGapUs = 0, maxLoopGapUs = 0;  // for the "diag" command

WebServer server(80);
Preferences prefs;
String homeSsid;

// ---------- controls shared by serial and web ----------

void writeLed(float spkNow) {  // spkNow: speaker duty right now, 0..1
  float spkPeak = ampPercent * SPK_LIMIT / 100;
  float level = ledPercent / 100.0f * (1 - compPercent / 100.0f * (spkPeak - spkNow));
  ledcWrite(PIN_LED, (int)(constrain(level, 0.0f, 1.0f) * PWM_MAX));
}

void setLed(int p) {
  ledPercent = constrain(p, 0, 100);
  writeLed(0);
}

void setComp(int p) {
  compPercent = constrain(p, 0, 100);
  prefs.putInt("comp", compPercent);
}

void setAmp(int p) { ampPercent = constrain(p, 0, 100); }

void stopPattern() { patReq = -1; }

void startPattern(int i) {  // i counts from 0
  if (i < 0 || i >= PATTERN_COUNT) return;
  sweeping = false;
  if (ampPercent == 0) ampPercent = 60;
  patReq = i;
}

int patternShown() { return patReq >= 0 ? patReq : (patReq == -1 ? -1 : player.shown()); }

void setFreq(float f) {
  stopPattern();
  sweeping = false;
  freqHz = constrain(f, FREQ_MIN, FREQ_MAX);
}

void startSweep(float a, float b, float sec) {
  sweepFrom = constrain(a, FREQ_MIN, FREQ_MAX);
  sweepTo = constrain(b, FREQ_MIN, FREQ_MAX);
  sweepMs = (unsigned long)(sec * 1000);
  sweepStartMs = millis();
  stopPattern();
  sweeping = true;
}

void stopSpeaker() { ampPercent = 0; sweeping = false; stopPattern(); }

void allOff() { stopSpeaker(); setLed(0); }

String statusJson() {
  String ip = WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "";
  char buf[300];
  snprintf(buf, sizeof(buf),
           "{\"led\":%d,\"amp\":%d,\"freq\":%.2f,\"comp\":%d,\"pattern\":%d,\"sweeping\":%s,\"home_ssid\":\"%s\",\"home_ip\":\"%s\"}",
           ledPercent, ampPercent, freqHz, compPercent, patternShown() + 1, sweeping ? "true" : "false", homeSsid.c_str(), ip.c_str());
  return String(buf);
}

void printStatus() {
  int p = patternShown();
  Serial.printf("led %d%%  amp %d%%  freq %.2f Hz  comp %d%s%s\n", ledPercent, ampPercent, freqHz, compPercent,
                sweeping ? "  (sweeping)" : "", p >= 0 ? (String("  pattern ") + (p + 1) + " " + PATTERNS[p].name).c_str() : "");
}

String patternsJson() {
  String j = "[";
  for (int i = 0; i < PATTERN_COUNT; i++) j += String(i ? ",\"" : "\"") + PATTERNS[i].name + "\"";
  return j + "]";
}

// ---------- serial ----------

void handleLine(String s) {
  s.trim();
  s.toLowerCase();
  if (!s.length()) return;
  int sp = s.indexOf(' ');
  String cmd = sp < 0 ? s : s.substring(0, sp);
  String arg = sp < 0 ? "" : s.substring(sp + 1);

  if (cmd == "led") setLed(arg.toInt());
  else if (cmd == "amp") setAmp(arg.toInt());
  else if (cmd == "freq") setFreq(arg.toFloat());
  else if (cmd == "sweep") {
    float a, b, sec;
    if (sscanf(arg.c_str(), "%f %f %f", &a, &b, &sec) == 3 && sec > 0) startSweep(a, b, sec);
    else { Serial.println("usage: sweep <from Hz> <to Hz> <seconds>"); return; }
  }
  else if (cmd == "comp") setComp(arg.toInt());
  else if (cmd == "pattern") startPattern(arg.toInt() - 1);
  else if (cmd == "patterns") {
    for (int i = 0; i < PATTERN_COUNT; i++) Serial.printf("%2d  %s\n", i + 1, PATTERNS[i].name);
    return;
  }
  else if (cmd == "diag") {
    Serial.printf("longest gap since last diag: waveform %.1f ms, web/serial loop %.1f ms\n",
                  maxWaveGapUs / 1000.0, maxLoopGapUs / 1000.0);
    maxWaveGapUs = maxLoopGapUs = 0;
    return;
  }
  else if (cmd == "stop") stopSpeaker();
  else if (cmd == "off") allOff();
  else if (cmd != "status") { Serial.println("commands: led, amp, freq, sweep, pattern, patterns, comp, stop, off, status, diag"); return; }
  printStatus();
}

// ---------- web ----------

void sendStatus() { server.send(200, "application/json", statusJson()); }

void setupWeb() {
  server.on("/", HTTP_GET, []() { server.send_P(200, "text/html", PAGE_HTML); });

  server.on("/api/status", HTTP_GET, sendStatus);

  server.on("/api/set", HTTP_POST, []() {
    if (server.hasArg("led")) setLed(server.arg("led").toInt());
    if (server.hasArg("amp")) setAmp(server.arg("amp").toInt());
    if (server.hasArg("freq")) setFreq(server.arg("freq").toFloat());
    if (server.hasArg("comp")) setComp(server.arg("comp").toInt());
    sendStatus();
  });

  server.on("/api/sweep", HTTP_POST, []() {
    float sec = server.arg("sec").toFloat();
    if (sec <= 0) { server.send(400, "text/plain", "seconds must be above 0"); return; }
    startSweep(server.arg("from").toFloat(), server.arg("to").toFloat(), sec);
    sendStatus();
  });

  server.on("/api/patterns", HTTP_GET, []() { server.send(200, "application/json", patternsJson()); });
  server.on("/api/pattern", HTTP_POST, []() {
    startPattern(server.arg("n").toInt() - 1);
    sendStatus();
  });

  server.on("/api/stop", HTTP_POST, []() { stopSpeaker(); sendStatus(); });
  server.on("/api/off", HTTP_POST, []() { allOff(); sendStatus(); });

  server.on("/api/wifi", HTTP_POST, []() {
    prefs.putString("ssid", server.arg("ssid"));
    prefs.putString("pass", server.arg("pass"));
    server.send(200, "text/plain", "saved, restarting");
    delay(500);
    ESP.restart();
  });

  server.on("/api/wifi/forget", HTTP_POST, []() {
    prefs.remove("ssid");
    prefs.remove("pass");
    server.send(200, "text/plain", "forgotten, restarting");
    delay(500);
    ESP.restart();
  });

  server.onNotFound([]() { server.send(404, "text/plain", "not found"); });
  server.begin();
}

void setupWifi() {
  prefs.begin("caustic", false);
  homeSsid = prefs.getString("ssid", "");
  String homePass = prefs.getString("pass", "");
  compPercent = prefs.getInt("comp", COMP_START);

  WiFi.mode(WIFI_AP_STA);
  WiFi.setSleep(false);  // Wi-Fi power saving adds 100+ ms lag to every request
  WiFi.setHostname(HOSTNAME);
  if (homeSsid.length()) {
    WiFi.begin(homeSsid.c_str(), homePass.c_str());
    Serial.printf("Joining home Wi-Fi \"%s\"", homeSsid.c_str());
    for (int i = 0; i < 20 && WiFi.status() != WL_CONNECTED; i++) { delay(500); Serial.print("."); }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED)
      Serial.printf("Home Wi-Fi: http://%s.local or http://%s\n", HOSTNAME, WiFi.localIP().toString().c_str());
    else {
      // Stop retrying. Endless retries hop across channels and make the Caustic-Rig network unreachable.
      WiFi.setAutoReconnect(false);
      WiFi.disconnect();
      WiFi.mode(WIFI_AP);
      Serial.println("Could not join home Wi-Fi. Check the name and password on the page. The Caustic-Rig network still works.");
    }
  }
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.printf("Rig Wi-Fi: join \"%s\" (password %s), open http://%s\n", AP_SSID, AP_PASS,
                WiFi.softAPIP().toString().c_str());
  MDNS.begin(HOSTNAME);
  MDNS.addService("http", "tcp", 80);
}

// ---------- speaker waveform ----------
// Runs in its own task at a higher priority than loop(), so serving the web page never stalls the
// waveform. A stall used to freeze the cone and then jump it to catch up, which clicked.

void waveTask(void *) {
  int64_t last = esp_timer_get_time();
  for (;;) {
    vTaskDelay(1);  // 1 ms
    int64_t now = esp_timer_get_time();
    uint32_t gap = (uint32_t)(now - last);
    if (gap > maxWaveGapUs) maxWaveGapUs = gap;
    last = now;

    int req = patReq;
    if (req != PAT_NO_REQ) {
      patReq = PAT_NO_REQ;
      if (req >= 0) player.start(req, millis());
      else player.stop();
    }
    float pf, pa, scale = 1.0f;
    if (player.tick(millis(), pf, pa)) {
      freqHz = constrain(pf, FREQ_MIN, FREQ_MAX);
      scale = pa;
    }

    phase += TWO_PI * freqHz * gap * 1e-6f;
    if (phase > TWO_PI) phase -= TWO_PI;

    int duty = (int)(sinf(phase) * ampPercent * scale * SPK_LIMIT * PWM_MAX / 100);
    // Positive half drives AIN1, negative half drives AIN2. The other input stays low.
    ledcWrite(PIN_SPK_A, duty > 0 ? duty : 0);
    ledcWrite(PIN_SPK_B, duty < 0 ? -duty : 0);
    writeLed(fabsf((float)duty) / PWM_MAX);
  }
}

// ---------- main ----------

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  ledcAttach(PIN_SPK_A, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_SPK_B, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_LED, PWM_FREQ, PWM_BITS);
  ledcWrite(PIN_SPK_A, 0);
  ledcWrite(PIN_SPK_B, 0);
  setLed(LED_START);

  setupWifi();
  setupWeb();

  xTaskCreatePinnedToCore(waveTask, "wave", 4096, NULL, 5, NULL, 1);
  Serial.println("Caustic rig ready. Type: led 20, amp 30, freq 10, sweep 5 25 20, stop, off, status");
  printStatus();
}

void loop() {
  static uint32_t lastLoopUs = micros();
  uint32_t nowUs = micros();
  if (nowUs - lastLoopUs > maxLoopGapUs) maxLoopGapUs = nowUs - lastLoopUs;
  lastLoopUs = nowUs;

  server.handleClient();
  if (Serial.available()) handleLine(Serial.readStringUntil('\n'));

  if (sweeping) {
    unsigned long t = millis() - sweepStartMs;
    if (t >= sweepMs) {
      freqHz = sweepTo;
      sweeping = false;
      printStatus();
    } else {
      freqHz = sweepFrom + (sweepTo - sweepFrom) * (float)t / sweepMs;
    }
  }
}

