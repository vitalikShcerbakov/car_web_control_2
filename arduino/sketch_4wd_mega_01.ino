#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <ArduinoJson.h> 
#include <INA226_WE.h>   
#include "Encoders.h"
#include "sensors.h" 

#define I2C_ADDRESS 0x44  // Drive
#define I2C_ADDRESS_Rasp 0x40  // Raspberyy
 
INA226_WE ina226 = INA226_WE(I2C_ADDRESS);
INA226_WE ina226_rasp = INA226_WE(I2C_ADDRESS_Rasp);

Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x60);

Adafruit_DCMotor* motors[4];

// инверсия направления (из-за зеркальной установки)
int motorDir[4] = {
    1,   // M1 (левый передний)
   -1,   // M2 (левый задний)
   -1,   // M3 (правый передний)
    1    // M4 (правый задний)
};




const unsigned long TelemetryInterval = 1000;    // Отправляем телеметрию раз в 100 мс
const unsigned long BatteryInterval = 1000;    // Отправляем инфу по батареям
#define DRIVE_CALIBRATION 0.949      // Батарея моторов 12.6V -> 13.28V показание
#define RASPBERRY_CALIBRATION 0.986  // Raspberry 5.12V -> 5.19V показание

int targetM1 = 0;
int targetM2 = 0;
int targetM3 = 0;
int targetM4 = 0;

int driveBatPin = 53;
int telemetryBatPin = 51;

int commandDriveBat = 0;
int commandTelemetryBat = 1;

#define BUFFER_SIZE 64  // 128
char inputBuffer[BUFFER_SIZE];
uint8_t bufIndex = 0;

struct INAData {
  float busVoltage_V;
  float current_mA;
  float power_mW;
  // float shuntVoltage_mV;
  // float loadVoltage_V;
  bool overflow;
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting setup....");
  pinMode(22, INPUT_PULLUP);
  pinMode(23, INPUT_PULLUP);
  pinMode(24, INPUT_PULLUP);
  pinMode(25, INPUT_PULLUP);

  pinMode(driveBatPin, OUTPUT);
  pinMode(telemetryBatPin, OUTPUT);

  motors_init();

  sensors_init();
  Wire.begin();
  if (!AFMS.begin()) {
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1); // Бесконечный цикл - индикация фатальной ошибки
  }
  Serial.println("Motor Shield found.");
  // AFMS.begin(); // запуск PCA9685
  Serial.println("end setup....");
 
}

void loop() {
while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            inputBuffer[bufIndex] = '\0';      // завершаем строку
            parseCommand(inputBuffer);         // передаем целиком
            bufIndex = 0;                      // обнуляем индекс для следующей команды
        } else {
            if (bufIndex < BUFFER_SIZE - 1) {  // защита от переполнения
                inputBuffer[bufIndex++] = c;   // накопление байт
            }
        }
    }

    static unsigned long lastBatteryRead = 0;
    if (millis() - lastBatteryRead >= BatteryInterval) {
        lastBatteryRead = millis();
        
        INAData batDrive = readVoltage(ina226, DRIVE_CALIBRATION);
        INAData batRaspberry = readVoltage(ina226_rasp, RASPBERRY_CALIBRATION); 
        // Проверяем переполнение
        if (batDrive.overflow || batRaspberry.overflow) {
            Serial.println("Warning: INA226 overflow detected!");
        }
        // Отправляем данные
        sendBatteryData(batDrive, batRaspberry);
    }

  static unsigned long t = 0;
  if (millis() - t > 200) {
    sensors_to_json();
    encoders_to_json();
    t = millis();
  }
  drive();
    // ======= Обновляем датчики =======
  sensors_update();
  updateEncoders();
  // ========== Вкючение реле ========
  controlDriverBat(commandDriveBat);
  controlTelemetryBat(commandTelemetryBat);
}

void sendBatteryData(INAData &drive, INAData &rasp) {
    StaticJsonDocument<128> doc;
    JsonObject Battery = doc.createNestedObject("battery");
    JsonObject batDrive = Battery.createNestedObject("drive");

    batDrive["bus_V"] = drive.busVoltage_V;
    batDrive["current_mA"] = drive.current_mA;
    batDrive["power_mW"] = drive.power_mW;
    
    JsonObject batRasp = Battery.createNestedObject("raspberry");
    batRasp["bus_V"] = rasp.busVoltage_V;
    batRasp["current_mA"] = rasp.current_mA;
    batRasp["power_mW"] = rasp.power_mW;
    
    doc["overflow"] = drive.overflow || rasp.overflow;
    
    serializeJson(doc, Serial);
    Serial.println();    
}

void motors_init() {
    motors[0] = AFMS.getMotor(1); // M1
    motors[1] = AFMS.getMotor(2); // M2
    motors[2] = AFMS.getMotor(3); // M3
    motors[3] = AFMS.getMotor(4); // M4
}

// ======== Парсер команды ========
void parseCommand(char* cmd) {
    int M1 = 0, M2 = 0, M3 = 0, M4 = 0;
    
    char* ptr;
    
    ptr = strstr(cmd, "M1:");
    if (ptr) M1 = atoi(ptr + 3);
    
    ptr = strstr(cmd, "M2:");
    if (ptr) M2 = atoi(ptr + 3);
    
    ptr = strstr(cmd, "M3:");
    if (ptr) M3 = atoi(ptr + 3);
    
    ptr = strstr(cmd, "M4:");
    if (ptr) M4 = atoi(ptr + 3);
    
    targetM1 = constrain(M1, -255, 255);
    targetM2 = constrain(M2, -255, 255);
    targetM3 = constrain(M3, -255, 255);
    targetM4 = constrain(M4, -255, 255);

    ptr = strstr(cmd, "driverBat:");
    if (ptr) commandDriveBat = atoi(ptr+10);

    ptr = strstr(cmd, "telemetryBat:");
    if (ptr) commandTelemetryBat = atoi(ptr+13);
}

// ================= Управление акб двигателей ================
void controlDriverBat(int state){
  digitalWrite(driveBatPin, state);
}

void controlTelemetryBat(int state){
  digitalWrite(telemetryBatPin, state);
}

INAData readVoltage(INA226_WE &ina, float calibrationFactor) {
  INAData data;
 
  ina.readAndClearFlags();
  data.busVoltage_V = ina.getBusVoltage_V() * calibrationFactor;
  data.current_mA = ina.getCurrent_mA();
  data.power_mW = ina.getBusPower();
  data.overflow = ina.overflow;
  return data;
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


