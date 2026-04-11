#include "telemetry.h"

#include <ArduinoJson.h>

#include "Encoders.h"
#include "sensors.h"

#define TELEMETRY_INTERVAL_MS 200

static unsigned long last_telemetry_ms = 0;

void telemetry_tick(unsigned long now_ms) {
  if (now_ms - last_telemetry_ms < TELEMETRY_INTERVAL_MS) return;
  last_telemetry_ms = now_ms;

  StaticJsonDocument<512> doc;

  JsonObject telemetry = doc.createNestedObject("telemetry");
  JsonObject ir = telemetry.createNestedObject("IRSensor");
  ir["ir1"] = sensors.ir1;
  ir["ir2"] = sensors.ir2;
  ir["ir3"] = sensors.ir3;
  ir["ir4"] = sensors.ir4;

  JsonObject ultrasonic = telemetry.createNestedObject("ultrasonicSensor");
  ultrasonic["distance"] = sensors.distance;

  JsonObject enc = doc.createNestedObject("encoders");
  enc["enc1"] = encoders.enc1;
  enc["enc2"] = encoders.enc2;
  enc["enc3"] = encoders.enc3;
  enc["enc4"] = encoders.enc4;

  serializeJson(doc, Serial);
  Serial.println();
}
