#ifndef MOTOR_DRIVER
#include <Adafruit_MotorShield.h>

Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x60);

Adafruit_DCMotor* motors[4];

// инверсия направления (из-за зеркальной установки)
int motorDir[4] = {
    1,   // M1 (левый передний)
   -1,   // M2 (левый задний)
   -1,   // M3 (правый передний)
    1    // M4 (правый задний)
};

void motors_init();
void setMotor(int i, int speed);
void stopAll();
void drive();

#endif

