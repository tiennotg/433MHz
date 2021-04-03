#!/usr/bin/python

'''
  Copyright 2021 Guilhem Tiennot
  
  Python script working with Gqrx for receiving ASK-coded messages
  sent by a 433MHz remote
  
  Dependencies: socket, struct, serial, schmitt_trigger, datetime
  
  This file is part of arduino433.py.
  
  arduino433.py is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  arduino433.py is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with arduino433.py.  If not, see <https://www.gnu.org/licenses/>.
'''

import socket
import struct
import serial
from schmitt_trigger import SchmittTrigger
from datetime import datetime

SAMPLE_RATE=48000 # in Hz

# Network conf
UDP_IP="127.0.0.1"
UDP_PORT=7355
UDP_CHUNK=int(SAMPLE_RATE/2)

# Serial conf (link with the Arduino board)
SERIAL_FILE="/dev/ttyACM0"
BAUD_RATE=115200

# Thresholds for the Schmitt Trigger
THRES1=200
THRES2=600

# Expected code sent by the remote control
EXPECTED_CODE="10657150BBCE7FBD"

# Symbol duration
T=350

message_started=False
cmd_status=False

ser = serial.Serial(SERIAL_FILE, BAUD_RATE)

def format_data(data_str):
	hex_format = ""
	hex_digit = 0
	for i in range(len(data_str)):
		if data_str[i] == '1':
			hex_digit = hex_digit + pow(2, (3-i)%4)
		if (i+1) % 4 == 0:
			hex_format = "%s%01X" % (hex_format,hex_digit)
			hex_digit = 0
	return hex_format
	
	

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
trigger = SchmittTrigger(THRES1, THRES2)

while True:
	# Get audio data from GQRX
	audio_unpacked = ()
	while len(audio_unpacked) < UDP_CHUNK:
		audio, addr = sock.recvfrom(UDP_CHUNK)
		format_str = "<%dh" % (len(audio)/2)
		audio_unpacked = audio_unpacked + struct.unpack(format_str, audio)
	
	# First, find where signal is active (True), and the duration
	# of each "peak"
	data = []
	last_state = None
	
	# data format: [[value, duration],[value, duration],...]
	# value is bool, duration is float in µs
	# example: [[false, 10000],[true,651],[false,7865],[true,67]]
	for i in range(len(audio_unpacked)):
		state = trigger.compare(audio_unpacked[i])
		if state == last_state:
			data[-1][1] = data[-1][1] + 1000000/SAMPLE_RATE
		else:
			data.append([state,1000000/SAMPLE_RATE])
			last_state = state
	
	j=0
	decoded_data=""
	while j < len(data)-1:
		if message_started:
			if data[j][0] and data[j][1] > T and data[j][1] < 2*T and not data[j+1][0] and data[j+1][1] > 2*T and data[j+1][1] < 3*T:
				decoded_data = decoded_data + "0"
			elif data[j][0] and data[j][1] > 2*T and data[j][1] < 3*T and not data[j+1][0] and data[j+1][1] > T and data[j+1][1] < 2*T:
				decoded_data = decoded_data + "1"
			else:
				message_started = False
				
				if format_data(decoded_data) == EXPECTED_CODE:
					cmd_status = not cmd_status
					if cmd_status:
						print("Allumage !")
						ser.write(b"A")
					else:
						print("Extinction !")
						ser.write(b"E")
			j = j+2
		else:
			if data[j][0] and data[j][1] > T:
				message_started = True
				# Skipping header
				while message_started and j < len(data)-1 and not(data[j][0] == False and data[j][1] > 8*T and data[j][1] < 13*T):
					if data[j][1] < T or data[j][1] > 2*T:
						message_started = False
					j+=1
			j = j+1
