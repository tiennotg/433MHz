/*
 * Copyright 2021 Guilhem Tiennot
 * 
 * Very simple program that transforms Arduino card into GPIO device.
 * It turns OUTPUT_PIN high when C_ON char is received over Serial,
 * or low when it's C_OFF.
 * 
 * Dependencies: Arduino standard library
 * 
 * This file is part of 433ArduinoIO.
 * 
 * 433ArduinoIO is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * 433ArduinoIO is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with 433ArduinoIO.  If not, see <https://www.gnu.org/licenses/>.
 * 
 */ 

#define OUTPUT_PIN 10
#define BAUD_RATE 115200
#define C_ON 'A'
#define C_OFF 'E'

void setup() {
  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN, LOW);
  Serial.begin(BAUD_RATE);
}

void loop() {
  if (Serial.available() > 0)
  {
    char c = Serial.read();
    if (c == C_ON)
      digitalWrite(OUTPUT_PIN, HIGH);
    else if (c == C_OFF)
      digitalWrite(OUTPUT_PIN, LOW);
  }
}
