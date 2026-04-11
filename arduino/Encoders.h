#ifndef ENCODERS_H
#define ENCODERS_H

#include <Arduino.h>
#include <Encoder.h>

struct EncodersData {
  long enc1, enc2, enc3, enc4;
  unsigned long timestamp;
};

extern Encoder myEnc1;
extern Encoder myEnc2;
extern Encoder myEnc3;
extern Encoder myEnc4;

extern EncodersData encoders;

void updateEncoders();

#endif
