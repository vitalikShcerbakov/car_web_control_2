#include <Wire.h>

#include "battery_ina.h"
#include "Encoders.h"
#include "motors.h"
#include "relays.h"
#include "sensors.h"
#include "telemetry.h"

#define SERIAL_LINE_BUFFER 128
static char serial_line[SERIAL_LINE_BUFFER];
static uint8_t serial_line_len = 0;

static void handle_serial_line(char *line) {
  motors_parse_command(line);
  relays_parse_command(line);
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("Starting setup..."));

  relays_begin();

  Wire.begin();

  sensors_init();
  battery_ina_begin();

  if (!motors_begin()) {
    Serial.println(F("Motor Shield not found."));
    while (1) {}
  }
  Serial.println(F("Motor Shield OK. Setup done."));
}

void loop() {
  unsigned long now = millis();

  while (Serial.available()) {
    char c = static_cast<char>(Serial.read());
    if (c == '\n') {
      serial_line[serial_line_len] = '\0';
      handle_serial_line(serial_line);
      serial_line_len = 0;
    } else if (serial_line_len < SERIAL_LINE_BUFFER - 1) {
      serial_line[serial_line_len++] = c;
    }
  }

  battery_ina_tick(now);
  telemetry_tick(now);

  motors_drive();

  sensors_update();
  updateEncoders();

  relays_apply();
}
