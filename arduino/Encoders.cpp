#include "Encoders.h"

Encoder myEnc1(2, 22);
Encoder myEnc2(3, 24);
Encoder myEnc3(18, 26);
Encoder myEnc4(19, 28);

EncodersData encoders;

void updateEncoders() {
  encoders.enc1 = myEnc1.read();
  encoders.enc2 = myEnc2.read();
  encoders.enc3 = myEnc3.read();
  encoders.enc4 = myEnc4.read();
  encoders.timestamp = millis();
}
