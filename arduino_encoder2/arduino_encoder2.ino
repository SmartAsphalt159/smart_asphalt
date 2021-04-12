#include "GPIO.h"
#include "Button.h"
#include <SoftwareSerial.h>
#include <ArduinoJson.h>


Button<BOARD::D12> button;
#define SAMPLE_TIME_MS 400

int tally;
int now;
int then;
int dt;
StaticJsonDocument<200> data;


void setup()
{
  Serial.begin(19200);
  while (!Serial);
  tally = 0;
  now = millis();
  then = millis();
  dt = 0;
  
}

void loop()
{
  
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
  }
}
