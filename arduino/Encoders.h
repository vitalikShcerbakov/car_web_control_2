#ifndef ENCODERS_H
#define ENCODERS_H

#include <Encoder.h>

// Объявляем внешние переменные, чтобы они были доступны в основном файле
extern Encoder myEnc1;
extern Encoder myEnc2;
extern Encoder myEnc3;
extern Encoder myEnc4;

extern long lastPosition1;
extern long lastPosition2;
extern long lastPosition3;
extern long lastPosition4;

// Прототипы функций
void initEncoders();
void updateEncoders();
void encoders_to_json();

#endif
