// Ripple patterns: each one plays the ripple speed (and sometimes strength) in a loop.
// A pattern is a list of segments. Each segment glides the frequency from f0 to f1 over ms milliseconds,
// and the strength from a0 to a1 (percent of the Ripple strength slider).
//   LIN  straight line          EXP  even steps per octave (sounds and looks like a steady speed-up)
//   EASE slow in, slow out      (two EASE segments back and forth make a smooth wobble)
// A few patterns are generated on the fly (raindrops, drift, shuffle).
#pragma once
#include <Arduino.h>

enum Curve : uint8_t { LIN, EXP, EASE };
struct Seg { float f0, f1; uint16_t ms; uint8_t a0, a1; Curve c; };
enum Special : uint8_t { NONE, RAIN, DRIFT, SHUFFLE };
struct Pattern { const char *name; const Seg *segs; uint8_t n; Special sp; };

#define H(f, ms, a) {f, f, ms, a, a, LIN}                   // hold one speed
#define G(f0, f1, ms, a, c) {f0, f1, ms, a, a, c}           // glide

// ---- quick flicks: slow, then a split second fast, then slow again
static const Seg P_FLICK[]   = { H(2, 1400, 70), H(20, 120, 100) };
static const Seg P_DOUBLE[]  = { H(2, 1500, 70), H(20, 100, 100), H(2, 200, 70), H(20, 100, 100) };
static const Seg P_PING[]    = { H(1, 1000, 60), H(30, 80, 100) };
static const Seg P_HEART[]   = { H(1.5, 900, 60), H(18, 100, 100), H(1.5, 150, 60), H(12, 120, 100) };
static const Seg P_SHIVER[]  = { H(3, 450, 70), H(40, 50, 100) };
static const Seg P_STUTTER[] = { H(4, 1200, 70), H(25, 60, 100), H(4, 80, 70), H(25, 60, 100), H(4, 80, 70), H(25, 60, 100) };
static const Seg P_THUNDER[] = { H(1, 3000, 50), H(10, 400, 100), H(6, 300, 85), H(3, 300, 70) };
static const Seg P_LADDER[]  = { H(2, 1000, 70), H(10, 100, 100), H(2, 1000, 70), H(15, 100, 100), H(2, 1000, 70), H(20, 100, 100),
                                 H(2, 1000, 70), H(25, 100, 100), H(2, 1000, 70), H(30, 100, 100) };
static const Seg P_STORM[]   = { H(3, 320, 70), H(25, 80, 100) };
static const Seg P_CHIRP[]   = { G(3, 30, 300, 100, EXP), H(3, 1200, 70) };
static const Seg P_DCHIRP[]  = { G(30, 3, 400, 100, EXP), H(3, 1500, 70) };

// ---- slow evolutions: start slow and speed up
static const Seg P_RISE[]    = { G(1, 25, 20000, 80, EXP) };
static const Seg P_RISEFALL[]= { G(1, 25, 15000, 80, EXP), G(25, 1, 15000, 80, EXP) };
static const Seg P_SWEEP[]   = { G(0.5, 40, 30000, 80, EXP) };
static const Seg P_CLIMB[]   = { G(2, 30, 4000, 85, EXP), H(2, 1000, 70) };
static const Seg P_FALL[]    = { G(30, 1, 10000, 80, EXP) };
static const Seg P_TIDE[]    = { {2, 8, 4000, 40, 100, EASE}, {8, 2, 4000, 100, 40, EASE} };
static const Seg P_STAIRS[]  = { H(2, 2000, 80), H(4, 2000, 80), H(6, 2000, 80), H(8, 2000, 80), H(10, 2000, 80), H(12, 2000, 80),
                                 H(14, 2000, 80), H(16, 2000, 80), H(14, 2000, 80), H(12, 2000, 80), H(10, 2000, 80), H(8, 2000, 80),
                                 H(6, 2000, 80), H(4, 2000, 80) };
static const Seg P_EVOLVE[]  = { G(0.5, 12, 60000, 80, EXP), G(12, 0.5, 60000, 80, EXP) };

// ---- wobbles
static const Seg P_WOBBLE[]  = { G(6, 14, 1000, 80, EASE), G(14, 6, 1000, 80, EASE) };
static const Seg P_DEEP[]    = { G(2, 22, 2500, 80, EASE), G(22, 2, 2500, 80, EASE) };
static const Seg P_WARBLE[]  = { G(15, 25, 170, 80, EASE), G(25, 15, 170, 80, EASE) };
static const Seg P_SIREN[]   = { G(5, 25, 500, 85, EASE), G(25, 5, 500, 85, EASE) };

// ---- strength patterns
static const Seg P_PULSE[]   = { H(8, 300, 100), H(8, 700, 0) };
static const Seg P_SWELL[]   = { {6, 6, 3000, 20, 100, EASE}, {6, 6, 3000, 100, 20, EASE} };
static const Seg P_TAPS[]    = { H(15, 150, 100), H(15, 850, 0) };
static const Seg P_KNOCK[]   = { H(25, 40, 100), H(25, 560, 0) };

#define PAT(name, arr) {name, arr, sizeof(arr) / sizeof(Seg), NONE}
#define GEN(name, sp) {name, nullptr, 0, sp}

const Pattern PATTERNS[] = {
  PAT("Flick", P_FLICK),        PAT("Double flick", P_DOUBLE), PAT("Ping", P_PING),
  GEN("Raindrops", RAIN),       PAT("Heartbeat", P_HEART),     PAT("Shiver", P_SHIVER),
  PAT("Stutter", P_STUTTER),    PAT("Thunder", P_THUNDER),     PAT("Flick ladder", P_LADDER),
  PAT("Flick storm", P_STORM),  PAT("Chirp", P_CHIRP),         PAT("Down chirp", P_DCHIRP),
  PAT("Slow rise", P_RISE),     PAT("Rise and fall", P_RISEFALL), PAT("Full sweep", P_SWEEP),
  PAT("Fast climb", P_CLIMB),   PAT("Long fall", P_FALL),      PAT("Tide", P_TIDE),
  PAT("Stairs", P_STAIRS),      PAT("Evolve (2 min)", P_EVOLVE), PAT("Wobble", P_WOBBLE),
  PAT("Deep wobble", P_DEEP),   PAT("Warble", P_WARBLE),       PAT("Siren", P_SIREN),
  GEN("Drift", DRIFT),          PAT("Pulse", P_PULSE),         PAT("Swell", P_SWELL),
  PAT("Taps", P_TAPS),          PAT("Knock", P_KNOCK),         GEN("Shuffle", SHUFFLE),
};
const int PATTERN_COUNT = sizeof(PATTERNS) / sizeof(Pattern);

class PatternPlayer {
 public:
  // Index of the pattern shown as playing (Shuffle shows as Shuffle), or -1.
  int shown() const { return shuffling ? shuffleIdx : idx; }

  void start(int i, uint32_t now) {
    if (i < 0 || i >= PATTERN_COUNT) { stop(); return; }
    shuffling = PATTERNS[i].sp == SHUFFLE;
    if (shuffling) { shuffleIdx = i; shuffleStart = now; i = pickOther(i); }
    begin(i, now);
  }

  void stop() { idx = -1; shuffling = false; }

  // Fills in the frequency and strength (0..1) for this moment. Returns false when nothing is playing.
  bool tick(uint32_t now, float &f, float &a) {
    if (idx < 0) return false;
    if (shuffling && now - shuffleStart >= 20000) { shuffleStart = now; begin(pickOther(idx), now); }
    for (int guard = 0; now - segStart >= cur().ms && guard < 50; guard++) {  // move to the next segment
      segStart += cur().ms;
      next();
    }
    if (now - segStart > 60000) segStart = now;  // never try to catch up after a long stall
    const Seg &s = cur();
    float u = s.ms ? (now - segStart) / (float)s.ms : 1.0f;
    u = constrain(u, 0.0f, 1.0f);
    float e = s.c == EASE ? (1 - cosf(PI * u)) / 2 : u;
    f = s.c == EXP ? s.f0 * powf(s.f1 / s.f0, u) : s.f0 + (s.f1 - s.f0) * e;
    a = (s.a0 + (s.a1 - s.a0) * e) / 100.0f;
    lastF = f;
    return true;
  }

 private:
  int idx = -1, shuffleIdx = -1;
  bool shuffling = false, rainBurst = false;
  uint8_t seg = 0;
  uint32_t segStart = 0, shuffleStart = 0;
  float lastF = 2;
  Seg dyn = H(2, 1000, 70);

  static float rnd(float lo, float hi) { return lo + (hi - lo) * (esp_random() / 4294967295.0f); }

  int pickOther(int not_this) {
    int j;
    do { j = esp_random() % PATTERN_COUNT; } while (j == not_this || PATTERNS[j].sp == SHUFFLE);
    return j;
  }

  const Seg &cur() const { return PATTERNS[idx].sp == NONE ? PATTERNS[idx].segs[seg] : dyn; }

  void begin(int i, uint32_t now) {
    seg = 0;
    segStart = now;
    rainBurst = true;  // so the first raindrop segment is a rest
    idx = i;
    if (PATTERNS[i].sp != NONE) makeDyn();
  }

  void next() {
    if (PATTERNS[idx].sp == NONE) seg = (seg + 1) % PATTERNS[idx].n;
    else makeDyn();
  }

  void makeDyn() {
    if (PATTERNS[idx].sp == RAIN) {
      rainBurst = !rainBurst;
      if (rainBurst) dyn = Seg{0, 0, (uint16_t)rnd(60, 150), 100, 100, LIN};
      else dyn = Seg{1.5, 1.5, (uint16_t)rnd(300, 2000), 65, 65, LIN};
      if (rainBurst) dyn.f0 = dyn.f1 = rnd(15, 35);
    } else {  // DRIFT
      float target = rnd(3, 20);
      dyn = Seg{lastF, target, (uint16_t)rnd(2000, 5000), 80, 80, EASE};
    }
  }
};
