#include <Wire.h>

#include "motor_driver.h"
#include "ina226_drive.h"
#include "Encoders.h"
#include "sensors.h" 


void setup() {
  Serial.begin(115200);
  Serial.println("Starting setup....");

  motors_init();
  sensors_init();

  Wire.begin();

  if (!AFMS.begin()) {
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1); // Бесконечный цикл - индикация фатальной ошибки
  }
  Serial.println("Motor Shield found.");
  AFMS.begin(); // запуск PCA9685
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
    updateEncoders();

    // sensors_read_all();
    // ultrasonic_update();
    // Serial.println(sensors_to_string());
      // вывод (не в ISR!)

  static unsigned long t = 0;
  if (millis() - t > 200) {
    sensors_to_json();
    encoders_to_json();
    t = millis();
  }
  drive();
    // ======= Обновляем датчики =======
  sensors_update();
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
}