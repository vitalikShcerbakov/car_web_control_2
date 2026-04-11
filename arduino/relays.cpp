#include "relays.h"

static const int drive_bat_pin = 53;
static const int telemetry_bat_pin = 51;

static int command_drive_bat = 0;
static int command_telemetry_bat = 1;

void relays_begin() {
  pinMode(drive_bat_pin, OUTPUT);
  pinMode(telemetry_bat_pin, OUTPUT);
}

void relays_parse_command(char *cmd) {
  char *ptr = strstr(cmd, "driverBat:");
  if (ptr) command_drive_bat = atoi(ptr + 10);

  ptr = strstr(cmd, "telemetryBat:");
  if (ptr) command_telemetry_bat = atoi(ptr + 13);
}

void relays_apply() {
  digitalWrite(drive_bat_pin, command_drive_bat);
  digitalWrite(telemetry_bat_pin, command_telemetry_bat);
}
