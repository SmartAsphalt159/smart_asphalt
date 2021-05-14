#include "GPIO.h"

GPIO<BOARD::D0> led;

void setup()
{
  led.output();
}

void loop()
{
  // Pulse width 1..10 us, not interrupted
  for (int width = 1; width < 11; width++)
    led.pulse(width);

  // Delay 10 us but observe with logic analyzer variation 10,15 us
  // as timer interrupts will occur here
  delayMicroseconds(10);
}
