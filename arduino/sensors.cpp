#include "sensors.h"
#include <ArduinoJson.h>


// ---------- init ----------
void ultrasonic_init() {
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);
}

// ---------- polling echo ----------
void ultrasonic_poll() {
    bool state = digitalRead(ECHO_PIN);
    unsigned long now = micros();

    if (state && !last_echo_state) {
        echo_start = now;
    }

    if (!state && last_echo_state) {
        echo_end = now;
        new_data = true;
    }

    last_echo_state = state;
}

// ---------- FSM ----------
void ultrasonic_update() {
    unsigned long now = micros();

    ultrasonic_poll(); // всегда вызываем!

    switch (us_state) {

        case US_IDLE:
            if (millis() - last_measure >= 60) {
                digitalWrite(TRIG_PIN, LOW);
                trig_time = now;
                us_state = US_TRIG;
            }
            break;

        case US_TRIG:
            if (now - trig_time >= 2) {
                digitalWrite(TRIG_PIN, HIGH);
            }
            if (now - trig_time >= 12) {
                digitalWrite(TRIG_PIN, LOW);
                trig_time = now;
                us_state = US_WAIT;
            }
            break;

        case US_WAIT:
            if (new_data) {
                unsigned long duration = echo_end - echo_start;
                distance = duration * 0.0343 / 2;

                new_data = false;
                last_measure = millis();
                us_state = US_IDLE;
            }

            // таймаут
            if (now - trig_time > 50000) {
                distance = 400;
                last_measure = millis();
                us_state = US_IDLE;
            }
            break;
    }

    sensors.distance = distance;
}

// ================== ИК ДАТЧИКИ ==================
void ir_init() {
    pinMode(IR1_PIN, INPUT);
    pinMode(IR2_PIN, INPUT);
    pinMode(IR3_PIN, INPUT);
    pinMode(IR4_PIN, INPUT);
}

void ir_read_all() {
    sensors.ir1 = !digitalRead(IR1_PIN);
    sensors.ir2 = !digitalRead(IR2_PIN);
    sensors.ir3 = !digitalRead(IR3_PIN);
    sensors.ir4 = !digitalRead(IR4_PIN);
}

// ================== ОБЩЕЕ ==================
void sensors_init() {
    ultrasonic_init();
    ir_init();
}

void sensors_update() {
    sensors.timestamp = millis();

    ultrasonic_update();
    ir_read_all();
}

// ================== ЛОГИКА ==================
bool obstacle_ahead() {
    return sensors.distance < OBSTACLE_DISTANCE;
}

bool obstacle_ir(int num) {
    switch(num) {
        case 0: return sensors.ir1;
        case 1: return sensors.ir2;
        case 2: return sensors.ir3;
        case 3: return sensors.ir4;
        default: return false;
    }
}

void sensors_to_json() {

    StaticJsonDocument<128> doc;
    JsonObject Telemetry = doc.createNestedObject("telemetry");
    JsonObject IRSensor = Telemetry.createNestedObject("IRSensor");

    IRSensor["ir1"] = sensors.ir1;
    IRSensor["ir2"] = sensors.ir2;
    IRSensor["ir3"] = sensors.ir3;
    IRSensor["ir4"] = sensors.ir4;
    
    JsonObject UltrasonicSensor = Telemetry.createNestedObject("ultrasonicSensor");
    UltrasonicSensor["distance"] = sensors.distance;
    
    serializeJson(doc, Serial);
    Serial.println();
    Serial.print("\n"); // для python конец json
}
