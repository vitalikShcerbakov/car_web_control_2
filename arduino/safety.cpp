#include "safety.h"

#include <math.h>

#include "sensors.h"

static bool g_safety_enabled = true;

static constexpr float US_HARD_CM = 20.0f;
static constexpr float US_SOFT_CM = 30.0f;
static constexpr float FWD_CAP_SOFT = 100.0f;
/** Выше — «нет достоверного эха» (NewPing: 0 см или запасной дальний предел) */
static constexpr float US_TRUST_MAX_CM = 350.0f;

static inline bool ir_front_blocked() {
  return sensors.ir1 || sensors.ir2;
}

static inline bool ir_rear_blocked() {
  return sensors.ir3 || sensors.ir4;
}

static inline bool ultrasonic_valid_cm(float d) {
  return d > 0.5f && d < US_TRUST_MAX_CM;
}

void safety_parse_command(char *cmd) {
  char *p = strstr(cmd, "safety:");
  if (p) g_safety_enabled = atoi(p + 7) != 0;
}

void safety_filter_targets(int *m1, int *m2, int *m3, int *m4) {
  if (!g_safety_enabled) return;

  float a = static_cast<float>(*m1);
  float b = static_cast<float>(*m2);
  float c = static_cast<float>(*m3);
  float d = static_cast<float>(*m4);

  float L = (a + b) / 2.0f;
  float R = (c + d) / 2.0f;
  float F = (L + R) / 2.0f;
  float T = (L - R) / 2.0f;

  const bool front_ir = ir_front_blocked();
  const bool rear_ir = ir_rear_blocked();
  const float dist = sensors.distance;

  if (front_ir && F > 0.0f) F = 0.0f;
  if (rear_ir && F < 0.0f) F = 0.0f;

  if (F > 0.0f && ultrasonic_valid_cm(dist)) {
    if (dist <= US_HARD_CM) {
      F = 0.0f;
    } else if (dist <= US_SOFT_CM) {
      if (F > FWD_CAP_SOFT) F = FWD_CAP_SOFT;
    }
  }

  L = F + T;
  R = F - T;

  int iL = static_cast<int>(round(L));
  int iR = static_cast<int>(round(R));

  iL = constrain(iL, -255, 255);
  iR = constrain(iR, -255, 255);

  *m1 = iL;
  *m2 = iL;
  *m3 = iR;
  *m4 = iR;
}
