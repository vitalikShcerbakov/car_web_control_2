#include "Encoders.h"
#include <ArduinoJson.h> 


// Инициализация объектов энкодеров
Encoder myEnc1(2, 22);
Encoder myEnc2(3, 24);
Encoder myEnc3(18, 26);
Encoder myEnc4(19, 28);  // Для 4-го энкодера


// Переменные для хранения последних позиций
long lastPosition1 = -999;
long lastPosition2 = -999;
long lastPosition3 = -999;
long lastPosition4 = -999;

// ================== СТРУКТУРА ==================
struct EncodersData {
    long enc1, enc2, enc3, enc4;
    unsigned long timestamp;
};

EncodersData encoders;

// Функция для обновления и вывода данных энкодеров
void updateEncoders() {
  encoders.enc1 = myEnc1.read();
  encoders.enc2 = myEnc2.read();
  encoders.enc3 = myEnc3.read();
  encoders.enc4 = myEnc4.read();
  
  // Проверяем, изменилось ли положение
  if (encoders.enc1 != lastPosition1 || encoders.enc2 != lastPosition2 || 
      encoders.enc3 != lastPosition3 || encoders.enc4 != lastPosition4) {
    
    lastPosition1 = encoders.enc1;
    lastPosition2 = encoders.enc2;
    lastPosition3 = encoders.enc3;
    lastPosition4 = encoders.enc4;
  }
}

void encoders_to_json() {

    StaticJsonDocument<128> doc;
    JsonObject Encoders = doc.createNestedObject("encoders");

    Encoders["enc1"] = encoders.enc1;
    Encoders["enc2"] = encoders.enc2;
    Encoders["enc3"] = encoders.enc3;
    Encoders["enc4"] = encoders.enc4;
    
    serializeJson(doc, Serial);
    Serial.println();
    Serial.print("\n"); // для python конец json
}
