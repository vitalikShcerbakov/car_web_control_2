#include "motors.h"

#include <Adafruit_MotorShield.h>

static Adafruit_MotorShield AFMS(0x60);
static Adafruit_DCMotor *motors[4];

// инверсия направления (из-за зеркальной установки)
static const int motorDir[4] = {
    1,   // M1 (левый передний)
    -1,  // M2 (левый задний)
    -1,  // M3 (правый передний)
    1    // M4 (правый задний)
};

static int targetM1 = 0;
static int targetM2 = 0;
static int targetM3 = 0;
static int targetM4 = 0;

static void set_motor(int i, int speed) {
  if (!motors[i]) return;
  speed *= motorDir[i];

  int pwm = constrain(abs(speed), 0, 255);
  motors[i]->setSpeed(pwm);

  if (speed > 0)
    motors[i]->run(FORWARD);
  else if (speed < 0)
    motors[i]->run(BACKWARD);
  else
    motors[i]->run(RELEASE);
}

bool motors_begin() {
  if (!AFMS.begin()) return false;

  motors[0] = AFMS.getMotor(1);
  motors[1] = AFMS.getMotor(2);
  motors[2] = AFMS.getMotor(3);
  motors[3] = AFMS.getMotor(4);
  return true;
}

void motors_set_targets(int m1, int m2, int m3, int m4) {
  targetM1 = constrain(m1, -255, 255);
  targetM2 = constrain(m2, -255, 255);
  targetM3 = constrain(m3, -255, 255);
  targetM4 = constrain(m4, -255, 255);
}

void motors_parse_command(char *cmd) {
  int M1 = 0, M2 = 0, M3 = 0, M4 = 0;

  char *ptr = strstr(cmd, "M1:");
  if (ptr) M1 = atoi(ptr + 3);

  ptr = strstr(cmd, "M2:");
  if (ptr) M2 = atoi(ptr + 3);

  ptr = strstr(cmd, "M3:");
  if (ptr) M3 = atoi(ptr + 3);

  ptr = strstr(cmd, "M4:");
  if (ptr) M4 = atoi(ptr + 3);

  motors_set_targets(M1, M2, M3, M4);
}

void motors_drive() {
  static int prev1 = 0, prev2 = 0, prev3 = 0, prev4 = 0;
  static bool synced = false;
  if (synced && targetM1 == prev1 && targetM2 == prev2 && targetM3 == prev3 && targetM4 == prev4)
    return;
  synced = true;
  prev1 = targetM1;
  prev2 = targetM2;
  prev3 = targetM3;
  prev4 = targetM4;

  set_motor(0, targetM1);
  set_motor(1, targetM2);
  set_motor(2, targetM3);
  set_motor(3, targetM4);
}

void motors_stop_all() {
  for (int i = 0; i < 4; i++) {
    if (motors[i]) motors[i]->run(RELEASE);
  }
}
