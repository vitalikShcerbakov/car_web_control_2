#include "ina226_driver.h"
#include <Wire.h>
#include <ArduinoJson.h>
#include <INA226_WE.h>

INA226_WE ina226 = INA226_WE(I2C_ADDRESS);
INA226_WE ina226_rasp = INA226_WE(I2C_ADDRESS_Rasp);



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
    Serial.print("\n"); // для python конец json
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
