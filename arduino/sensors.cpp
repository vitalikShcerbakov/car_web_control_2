#include "sensors.h"

enum US_State {
  US_IDLE,
  US_TRIG,
  US_WAIT
};

static US_State us_state = US_IDLE;

static unsigned long trig_time = 0;
static unsigned long echo_start = 0;
static unsigned long echo_end = 0;

static bool last_echo_state = LOW;
static bool new_data = false;

static float distance = 300;
static unsigned long last_measure = 0;

SensorData sensors;

static void ultrasonic_init() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);
}

static void ultrasonic_poll() {
  bool state = digitalRead(ECHO_PIN);
  unsigned long now = micros();

  if (state && !last_echo_state) {
    echo_start = now;
  }

  if (!state && last_echo_state) {
    echo_end = now;
    new_data = true;
  }

  last_echo_state = state;
}

static void ultrasonic_update() {
  unsigned long now = micros();

  ultrasonic_poll();

  switch (us_state) {

    case US_IDLE:
      if (millis() - last_measure >= 60) {
        digitalWrite(TRIG_PIN, LOW);
        trig_time = now;
        us_state = US_TRIG;
      }
      break;

    case US_TRIG:
      if (now - trig_time >= 2) {
        digitalWrite(TRIG_PIN, HIGH);
      }
      if (now - trig_time >= 12) {
        digitalWrite(TRIG_PIN, LOW);
        trig_time = now;
        us_state = US_WAIT;
      }
      break;

    case US_WAIT:
      if (new_data) {
        unsigned long duration = echo_end - echo_start;
        distance = duration * 0.0343f / 2.0f;

        new_data = false;
        last_measure = millis();
        us_state = US_IDLE;
      }

      if (now - trig_time > 50000) {
        distance = 400;
        last_measure = millis();
        us_state = US_IDLE;
      }
      break;
  }

  sensors.distance = distance;
}

static void ir_init() {
  pinMode(IR1_PIN, INPUT);
  pinMode(IR2_PIN, INPUT);
  pinMode(IR3_PIN, INPUT);
  pinMode(IR4_PIN, INPUT);
}

static void ir_read_all() {
  sensors.ir1 = !digitalRead(IR1_PIN);
  sensors.ir2 = !digitalRead(IR2_PIN);
  sensors.ir3 = !digitalRead(IR3_PIN);
  sensors.ir4 = !digitalRead(IR4_PIN);
}

void sensors_init() {
  ultrasonic_init();
  ir_init();
}

void sensors_update() {
  sensors.timestamp = millis();
  ultrasonic_update();
  ir_read_all();
}

bool obstacle_ahead() {
  return sensors.distance < OBSTACLE_DISTANCE;
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
