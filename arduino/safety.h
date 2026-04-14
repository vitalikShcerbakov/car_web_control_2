#ifndef SAFETY_H
#define SAFETY_H

#include <Arduino.h>

void safety_parse_command(char *cmd);
void safety_filter_targets(int *m1, int *m2, int *m3, int *m4);

#endif
