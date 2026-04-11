#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

#define TRIG_PIN 9
#define ECHO_PIN 10

#define IR1_PIN 46
#define IR2_PIN 48
#define IR3_PIN 50
#define IR4_PIN 52

#define OBSTACLE_DISTANCE 30

struct SensorData {
  float distance;
  bool ir1, ir2, ir3, ir4;
  unsigned long timestamp;
};

extern SensorData sensors;

void sensors_init();
void sensors_update();
bool obstacle_ahead();
bool obstacle_ir(int num);

#endif
