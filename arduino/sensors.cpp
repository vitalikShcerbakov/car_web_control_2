#include "sensors.h"

#include <NewPing.h>

#define PIN_TRIG 12
#define PIN_ECHO 11
/** Макс. дальность поиска эха (см); влияет на таймаут NewPing */
#define MAX_DISTANCE_CM 200

NewPing sonar(PIN_TRIG, PIN_ECHO, MAX_DISTANCE_CM);

SensorData sensors;

void ir_init() {
  pinMode(IR1_PIN, INPUT);
  pinMode(IR2_PIN, INPUT);
  pinMode(IR3_PIN, INPUT);
  pinMode(IR4_PIN, INPUT);
}

void sensors_init() {
  ir_init();
}

static void ir_read_all() {
  sensors.ir1 = !digitalRead(IR1_PIN);
  sensors.ir2 = !digitalRead(IR2_PIN);
  sensors.ir3 = !digitalRead(IR3_PIN);
  sensors.ir4 = !digitalRead(IR4_PIN);
}

void sensors_update() {
  sensors.timestamp = millis();

  unsigned int cm = sonar.ping_cm();
  // NewPing: 0 = нет эха / вне диапазона — не «0 см», иначе ломается safety и UI
  if (cm == 0) {
    sensors.distance = 400.0f;
  } else {
    sensors.distance = static_cast<float>(cm);
  }

  ir_read_all();
}

bool obstacle_ahead() {
  return sensors.distance > 0.5f && sensors.distance < OBSTACLE_DISTANCE;
}

bool obstacle_ir(int num) {
  switch (num) {
    case 0: return sensors.ir1;
    case 1: return sensors.ir2;
    case 2: return sensors.ir3;
    case 3: return sensors.ir4;
    default: return false;
  }
}
