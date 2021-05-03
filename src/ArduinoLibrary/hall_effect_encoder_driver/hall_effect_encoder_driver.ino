#include "GPIO.h"
#include "Button.h"
#include <SoftwareSerial.h>
#include <ArduinoJson.h>
// https://arduinojson.org/ dependency for ArduinoJson.h

/*
Button<BOARD::D12> button;
#define SAMPLE_TIME_MS 400

int tally;
int now;
int then;
int dt;
StaticJsonDocument<200> data;
*/

const byte interruptPinHallEffect = 2;
volatile byte hallEffectTickCount = 0; // Temporary

void rpm_count_isr() 
{
  hallEffectTickCount++;
}

void setup()
{
  pinMode(interruptPinHallEffect, INPUT);
  Serial.begin(9600); //19200
  attatchInterrupt(digitalPinToInterrupt(interruptPinHallEffect), rpm_count_isr, RISING);
  
  /*while (!Serial);
  tally = 0;
  now = millis();
  then = millis();
  dt = 0;*/

}

void loop()
{
  
/*
  if (button.ischanged()) {
    tally++;
  }
  now = millis();
  if(now-then > SAMPLE_TIME_MS) {
    dt = now-then;
    data["tally"] = tally;
    data["delta_time"] = dt;
    serializeJson(data, Serial);
    Serial.print("\n");
    tally = 0;
    now = millis();
    then = now;
  }*/
}
