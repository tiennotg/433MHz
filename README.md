# 433MHz
Collection of small tools for emitting/receiving in 433MHz ISM band.

# Usage
## 433Manchester.ino and manchester_reader.py
These tools provide a 433MHz unidirectionnal data link. For example, you can send text from one computer to another. To fully understand the following, you have to feel comfortable with Arduino development and Linux command line.

Required stuff:
  - An Arduino board (tested with an Arduino Uno)
  - A 433MHz remote control, whose the local oscillator can be drived by TTL levels
  - An RTL-SDR dongle
  - Two computers

First, compile `433Manchester.ino` and send it to the Arduino with the Arduino IDE. Solder a wire to the command pin of the remote oscillator, and plug it in the Arduino output pin (given in the `433Manchester.ino` file, `3` by default). Then, open a serial terminal (for example `minicom`) and change some parameters: `device: /dev/ttyACM0 ; Baud rate: 115200 ; parity: 8N1 (usually default parameter).` The transmission part is ready: every new line in the terminal is sent when pressing `Enter` down.

On the second computer, install `gqrx` or another software able to demodulate ASK and to send audio data over UDP. The manchester_reader.py program expects audio data on the 7355 UDP port - the default one used by gqrx. If you choose gqrx, before starting, don't forget to activate UDP sink (it isn't by default). Then, run `python3 mancherster_reader.py` and you should see the data sent by the other computer.
