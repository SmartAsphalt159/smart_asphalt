#include "GPIO.h"
#include "Button.h"

Button<BOARD::D7> button;

void setup()
{
  Serial.begin(57600);
  while (!Serial);
}

void loop()
{
  if (button.ischanged()) {
    Serial.print(button.timestamp());
    Serial.print(':');
    Serial.println(button ? F("released") : F("pushed"));
  }
}
