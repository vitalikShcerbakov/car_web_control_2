#ifndef INA226_DRIVER
#define INA226_DRIVER

#include <INA226_WE.h>

#define I2C_ADDRESS 0x44  // Drive
#define I2C_ADDRESS_Rasp 0x40  // Raspberyy

INA226_WE ina226 = INA226_WE(I2C_ADDRESS);
INA226_WE ina226_rasp = INA226_WE(I2C_ADDRESS_Rasp);

const unsigned long BatteryInterval = 1000;    // Отправляем инфу по батареям
#define DRIVE_CALIBRATION 0.949      // Батарея моторов 12.6V -> 13.28V показание
#define RASPBERRY_CALIBRATION 0.986  // Raspberry 5.12V -> 5.19V показание


struct INAData {
  float busVoltage_V;
  float current_mA;
  float power_mW;
  // float shuntVoltage_mV;
  // float loadVoltage_V;
  bool overflow;
};

void sendBatteryData(INAData &drive, INAData &rasp);
INAData readVoltage(INA226_WE &ina, float calibrationFactor);

#endif