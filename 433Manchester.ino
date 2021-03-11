/*
 * Copyright 2021 Guilhem Tiennot
 * 
 * Send messages in Manchester code, for example with a 433MHz external
 * oscillator.
 * 
 * Dependencies: Arduino standard library
 * 
 * This file is part of 433Manchester.
 * 
 * 433Manchester is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * 433Manchester is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with 433Manchester.  If not, see <https://www.gnu.org/licenses/>.
 * 
 */ 

#define OUTPUT_PIN 3
#define T 400 			 // Manchester code period (in µs)
#define DELAY 10         // delay to prevent issues with Serial (in ms)
#define REPEAT_X_TIMES 6 // Number of times the message is repeated
#define SERIAL_BAUD_RATE 115200

String msg = String("");

void send_message(const char *str)
{
  int output_status = HIGH;
  char *encoded_str = NULL;
  int msg_length = strlen(str);
  int encoded_msg_length = msg_length + 4; // Add two first sync bytes, one for checksum, one for end byte.
  char checksum = '\x00';

  // Memory allocation
  if ((encoded_str = (char*) malloc(sizeof(char) * (encoded_msg_length + 1))) == NULL)
    return;

  // Checksum calculation (simple xor between bytes)
  for (int i=0; i<msg_length; i++)
    checksum ^= str[i];
  // Format encoded str with start bytes, checksum byte and end byte
  sprintf(encoded_str,"\xAA\x55%s%c\xFF", str, checksum);

  // Starting impulsion
  digitalWrite(OUTPUT_PIN, output_status);
  delayMicroseconds(5*T);

  for (int x=0; x<REPEAT_X_TIMES; x++)
    for (int i=0; i<encoded_msg_length; i++)
    {
      // Send bits
      for (int j=7; j>=0; j--)
      {
        int previous_status = output_status;
        
        if (bitRead(encoded_str[i],j))
          output_status = HIGH;
        else
          output_status = LOW;

        if (output_status != previous_status)
          digitalWrite(OUTPUT_PIN, output_status);
        
        delayMicroseconds(T/2);
        
        output_status = !output_status;
        digitalWrite(OUTPUT_PIN, output_status);
        
        delayMicroseconds(T/2);
      }
    }
  digitalWrite(OUTPUT_PIN, LOW);
  free(encoded_str);
}

void setup() {
  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN, LOW);
  Serial.begin(SERIAL_BAUD_RATE);
}

void loop() {  
  if (Serial.available()>0)
  {
    char c = Serial.read();
    Serial.print(c);
    if (c == '\r' || c == '\n')
    {
      send_message(msg.c_str());
      Serial.println("Envoyé : "+msg);
      msg = String("");
    }
    else
      msg += c;
  }
  delay(DELAY);
}
