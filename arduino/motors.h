#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>

bool motors_begin();
void motors_drive();
void motors_stop_all();
void motors_parse_command(char *cmd);
void motors_set_targets(int m1, int m2, int m3, int m4);

#endif
