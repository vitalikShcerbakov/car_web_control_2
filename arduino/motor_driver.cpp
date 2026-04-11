#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <ArduinoJson.h>
#include <INA226_WE.h>
#include "Encoders.h"
#include "sensors.h"


void motors_init() {
    motors[0] = AFMS.getMotor(1); // M1
    motors[1] = AFMS.getMotor(2); // M2
    motors[2] = AFMS.getMotor(3); // M3
    motors[3] = AFMS.getMotor(4); // M4
}

void setMotor(int i, int speed) {
    if (!motors[i]) return;  // если мотор не инициализирован — выходим
    speed *= motorDir[i];  // учитываем инверсию

    int pwm = constrain(abs(speed), 0, 255);

    motors[i]->setSpeed(pwm);

    if (speed > 0)
        motors[i]->run(FORWARD);
    else if (speed < 0)
        motors[i]->run(BACKWARD);
    else
        motors[i]->run(RELEASE);
}

void stopAll() {
    for (int i = 0; i < 4; i++) {
        motors[i]->run(RELEASE);
    }
  }

void drive() {
    // левая сторона (M1, M2)
    setMotor(0, targetM1);
    setMotor(1, targetM2);

    // правая сторона (M3, M4)
    setMotor(2, targetM3);
    setMotor(3, targetM4);
}
