#include "battery_ina.h"

#include <ArduinoJson.h>
#include <INA226_WE.h>
#include <Wire.h>

#define I2C_ADDRESS_DRIVE 0x44
#define I2C_ADDRESS_RASP 0x40

#define BATTERY_INTERVAL_MS 1000
#define DRIVE_CALIBRATION 0.949f
#define RASPBERRY_CALIBRATION 0.986f

static INA226_WE ina_drive(I2C_ADDRESS_DRIVE);
static INA226_WE ina_rasp(I2C_ADDRESS_RASP);

static unsigned long last_battery_ms = 0;

const int telemetryPowerPin = A7;
const float referenceVoltage = 4.9;  // Напрежение на 5v+ факт
const float analogMax = 1023.0;
const float R1_BAT = 6960.0;
const float R2_BAT = 10050.0;

static INAData read_voltage(INA226_WE &ina, float calibration) {
  INAData data{};
  ina.readAndClearFlags();
  data.busVoltage_V = ina.getBusVoltage_V() * calibration;
  data.current_mA = ina.getCurrent_mA();
  data.power_mW = ina.getBusPower();
  data.overflow = ina.overflow;
  return data;
}

static void send_battery_json(const INAData &drive, const INAData &rasp, float telemetryPower_V) {
  StaticJsonDocument<192> doc;
  JsonObject battery = doc.createNestedObject("battery");
  JsonObject bat_drive = battery.createNestedObject("drive");
  bat_drive["bus_V"] = drive.busVoltage_V;
  bat_drive["current_mA"] = drive.current_mA;
  bat_drive["power_mW"] = drive.power_mW;

  JsonObject bat_rasp = battery.createNestedObject("raspberry");
  bat_rasp["bus_V"] = rasp.busVoltage_V;
  bat_rasp["current_mA"] = rasp.current_mA;
  bat_rasp["power_mW"] = rasp.power_mW;

  battery["telemetryPower_V"] = telemetryPower_V;
  doc["overflow"] = drive.overflow || rasp.overflow;

  serializeJson(doc, Serial);
  Serial.println();
}

void battery_ina_begin() {
  ina_drive.init();
  ina_rasp.init();
}

void battery_ina_tick(unsigned long now_ms) {
  if (now_ms - last_battery_ms < BATTERY_INTERVAL_MS) return;
  last_battery_ms = now_ms;

  INAData bat_drive = read_voltage(ina_drive, DRIVE_CALIBRATION);
  INAData bat_rasp = read_voltage(ina_rasp, RASPBERRY_CALIBRATION);
  float telemetryPower_V = readVoltage(telemetryPowerPin, R1_BAT, R2_BAT);


  if (bat_drive.overflow || bat_rasp.overflow)
    Serial.println(F("Warning: INA226 overflow"));

  send_battery_json(bat_drive, bat_rasp, telemetryPower_V);
}

float readVoltage(byte pin, float R1, float R2) {
  int raw = analogRead(pin);
  float vOut = raw * referenceVoltage / analogMax;
  float vIn = vOut * (R1 + R2) / R2;
  return vIn;
}
