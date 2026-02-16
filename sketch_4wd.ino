// ================= 4WD Arduino + L293D Motor Shield =================

// PWM пины для скорости моторов
#define M1_PWM 11 // левый передний
#define M2_PWM 3  // левый задний
#define M3_PWM 5  // правый передний
#define M4_PWM 6  // правый задний

// 74HC595 (драйвер направлений) пины
#define MOTORLATCH 12
#define MOTORDATA 8
#define MOTORCLK 4
#define MOTORENABLE 7

// биты направления для каждого мотора
#define M1_A 2
#define M1_B 3
#define M2_A 1
#define M2_B 4
#define M3_A 5
#define M3_B 7
#define M4_A 0
#define M4_B 6

String input = "";
byte latch_state = 0;

void setup() {
  Serial.begin(115200);

  pinMode(MOTORLATCH, OUTPUT);
  pinMode(MOTORDATA, OUTPUT);
  pinMode(MOTORCLK, OUTPUT);
  pinMode(MOTORENABLE, OUTPUT);
  digitalWrite(MOTORENABLE, LOW); // активируем моторы

  pinMode(M1_PWM, OUTPUT);
  pinMode(M2_PWM, OUTPUT);
  pinMode(M3_PWM, OUTPUT);
  pinMode(M4_PWM, OUTPUT);

  stopAll();
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      parseCommand(input);
      input = "";
    } else {
      input += c;
    }
  }
}

// ================= Обработка команд =================
void parseCommand(String cmd) {
  Serial.print("Received: "); Serial.println(cmd);

  int gIndex = cmd.indexOf("G:");
  int rIndex = cmd.indexOf("R:");

  if (gIndex == -1 || rIndex == -1) return;

  int gVal = cmd.substring(gIndex + 2, cmd.indexOf(';')).toInt();
  int rVal = cmd.substring(rIndex + 2).toInt();

  Serial.print("G: "); Serial.print(gVal);
  Serial.print(" R: "); Serial.println(rVal);

  drive(gVal, rVal);
}

// ================= Логика движения =================
void drive(int G, int R) {
  float kLeft  = 1.00;
  float kRight = 1.00;  // замедляем правый борт

  int left  = constrain(-(G + R) * kLeft, -255, 255);
  int right = constrain(-(G - R) * kRight, -255, 255);

  // Левый борт
  setMotor(1, left, true);
  setMotor(2, left, true);

  // Правый борт — физическая инверсия
  setMotor(3, right, false);
  setMotor(4, right, false);
}

// ================= Управление отдельным мотором =================
// motor_side: true = левый, false = правый
void setMotor(int motor, int speed, bool motor_side) {
  bool forward = speed >= 0;
  int pwm = abs(speed);
  pwm = constrain(pwm, 0, 255);

  // для правого борта зеркалим направление
  //if(!motor_side) forward = !forward;

  switch (motor) {
    case 1: setDirection(M1_A, M1_B, forward); analogWrite(M1_PWM, pwm); break;
    case 2: setDirection(M2_A, M2_B, forward); analogWrite(M2_PWM, pwm); break;
    case 3: setDirection(M3_A, M3_B, forward); analogWrite(M3_PWM, pwm); break;
    case 4: setDirection(M4_A, M4_B, forward); analogWrite(M4_PWM, pwm); break;
  }
}

// ================= Управление направлением через 74HC595 =================
void setDirection(int a, int b, bool forward) {
  if (forward) {
    bitSet(latch_state, a);
    bitClear(latch_state, b);
  } else {
    bitSet(latch_state, b);
    bitClear(latch_state, a);
  }
  updateLatch();
}

void updateLatch() {
  digitalWrite(MOTORLATCH, LOW);
  shiftOut(MOTORDATA, MOTORCLK, MSBFIRST, latch_state);
  digitalWrite(MOTORLATCH, HIGH);
}

// ================= Стоп все моторы =================
void stopAll() {
  analogWrite(M1_PWM, 0);
  analogWrite(M2_PWM, 0);
  analogWrite(M3_PWM, 0);
  analogWrite(M4_PWM, 0);

  latch_state = 0;
  updateLatch();
}