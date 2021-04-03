# 433MHz
Collection of small tools for emitting/receiving in 433MHz ISM band. They are introduced in this video: https://peertube.tiennot.net/videos/watch/3698f644-0e85-4c51-aa12-6a1c73834683 (only in French for the moment).

# Usage
To fully understand the following, you have to feel comfortable with Arduino environment and Linux command line. A RTL-SDR dongle is also required (https://www.rtl-sdr.com/).

## nexus_device.py
This program receives and extracts data from Nexus weather device, as temperature or humidity. It's similar to rtl_433, but it works better in low level signals. See the protocol description here: https://github.com/merbanan/rtl_433/blob/master/src/devices/nexus.c

Steps:
  - First, install gqrx: `apt-get install gqrx-sdr` (for Debian/Ubuntu) or any other software able to demodulate ASK signals and send audio data over UDP.
  - Launch it and enable UDP audio output:
    - click down to `...` button at bottom-right corner, and in the `network` tab, set `host: 127.0.0.1 ; port: 7355 ; 'stereo' box unchecked`)
    - click down to `UDP` button, to enable UDP stream.
  - Select your frequency, and run capture with the play button at top-left.
  - Launch the nexus_device program: `python3 nexus_device.py`
  - Data should be printed on screen when a frame is received.

## 433Manchester.ino and manchester_reader.py
These tools provide a 433MHz unidirectionnal data link. For example, you can send text from one computer to another.

Required stuff:
  - An Arduino board (tested with an Arduino Uno)
  - A 433MHz remote control, whose the local oscillator can be drived by TTL levels
  - A RTL-SDR dongle
  - Two computers

First, compile `433Manchester.ino` and send it to the Arduino with the Arduino IDE. Solder a wire to the command pin of the remote oscillator, and plug it in the Arduino output pin (given in the `433Manchester.ino` file, `3` by default). Then, open a serial terminal (for example `minicom`) and change some parameters: `device: /dev/ttyACM0 ; Baud rate: 115200 ; parity: 8N1 (usually default parameter).` The transmission part is ready: every new line in the terminal is sent when pressing `Enter` down.

On the second computer, install `gqrx` or another software able to demodulate ASK and to send audio data over UDP (see previous section for more details). The manchester_reader.py program expects audio data on the 7355 UDP port - the default one used by gqrx. If you choose gqrx, before starting, don't forget to activate UDP sink (it isn't by default). Then, run `python3 mancherster_reader.py` and you should see the data sent by the other computer.

## arduino433.py and 433ArduinoIO.ino
With these tools, you can control an Arduino output with a 433MHz remote.

First, compile `433ArduinoIO.ino` and send it to the Arduino with the Arduino IDE. Connect your stuff to control to the pin number 10. On your computer, install and launch gqrx, as described in the first section. Don't forget to activate UDP audio sink. Then, install rtl_433 (Debian/Ubuntu: `apt-get install rtl-433`) and run it. Press the button of your remote, to get the code, and change the `EXPECTED_CODE` variable at the beginning of `arduino433.py` in consequence. Last, run the script with the `python3 arduino433.py` command. You should be able to control your stuff with the remote.
