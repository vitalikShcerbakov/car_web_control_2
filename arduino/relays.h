#ifndef RELAYS_H
#define RELAYS_H

#include <Arduino.h>

void relays_begin();
void relays_apply();
void relays_parse_command(char *cmd);

#endif
