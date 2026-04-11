#ifndef BATTERY_INA_H
#define BATTERY_INA_H

#include <Arduino.h>

extern float telemetryPower;

struct INAData {
  float busVoltage_V;
  float current_mA;
  float power_mW;
  bool overflow;
};

void battery_ina_begin();
void battery_ina_tick(unsigned long now_ms);
float readVoltage(byte pin, float R1, float R2);

#endif
