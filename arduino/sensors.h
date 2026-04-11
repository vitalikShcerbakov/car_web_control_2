#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

// ================== ПИНЫ ==================
#define TRIG_PIN 9
#define ECHO_PIN 10

#define IR1_PIN 46
#define IR2_PIN 48
#define IR3_PIN 50
#define IR4_PIN 52

#define OBSTACLE_DISTANCE 30

// ================== СТРУКТУРА ==================
struct SensorData {
    float distance;
    bool ir1, ir2, ir3, ir4;
    unsigned long timestamp;
};

SensorData sensors;

// ================== УЛЬТРАЗВУК ==================
enum US_State {
    US_IDLE,
    US_TRIG,
    US_WAIT
};

US_State us_state = US_IDLE;

unsigned long trig_time = 0;
unsigned long echo_start = 0;
unsigned long echo_end = 0;

bool last_echo_state = LOW;
bool new_data = false;

float distance = 400;
unsigned long last_measure = 0;

// ---------- init ----------
void ultrasonic_init();

// ---------- polling echo ----------
void ultrasonic_poll();

// ---------- FSM ----------
void ultrasonic_update();

// ================== ИК ДАТЧИКИ ==================
void ir_init()
void ir_read_all();

// ================== ОБЩЕЕ ==================
void sensors_init();
void sensors_update();

// ================== ЛОГИКА ==================
bool obstacle_ahead();
bool obstacle_ir(int num);
void sensors_to_json();

#endif