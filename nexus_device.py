#!/usr/bin/python3

'''
  Copyright 2021 Guilhem Tiennot
  
  Small python script to receive Nexus temperature device data.
  Works with Gqrx UDP output, don't forget to activate it!
  
  Nexus devices are also supported by rtl_433:
  https://github.com/merbanan/rtl_433/blob/master/src/devices/nexus.c
  
  See the link above for full description of the radio protocol.
  
  Dependencies: datetime, socket, struct, schmitt_trigger
  
  This file is part of nexus_device.py.
  
  nexus_device.py is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  nexus_device.py is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with nexus_device.py.  If not, see <https://www.gnu.org/licenses/>.
'''  

import socket
import struct
from schmitt_trigger import SchmittTrigger
from datetime import datetime

SAMPLE_RATE=48000 # in Hz

# Parameters to receive Gqrx data
UDP_IP="127.0.0.1"
UDP_PORT=7355
UDP_CHUNK=SAMPLE_RATE

# Thresholds of the Schmitt trigger
THRES1=200
THRES2=600

# Various duration patterns :
#   - HIGH_T + LOW_T_XL : sync, beginning of a message group
#   - HIGH_T + LOW_T_L  : true bit
#   - HIGH_T + LOW_T    : false bit
HIGH_T=400
LOW_T_XL=3600
LOW_T_L=1900
LOW_T=900

message_started=False

def binary_to_float(binary):
	if len(binary) == 0:
		return None
	
	r = 0
	
	# Negative number
	if binary[0] == '1':
		r = int(binary,2) - 1
		inv_binary = ''
		b_dict = {'1':'0','0':'1'}
		for i in "{0:b}".format(r):
			inv_binary += b_dict[i]
		r = -binary_to_float(inv_binary)
	else:
		r = int(binary,2)
	
	if len(binary) == 12 and binary[0] == '0':
		# Temperature, in °C*10
		return r/10
	else:
		# Humidity, in %
		return r

def format_data(data_str):
	if len(data_str) < 36:
		return None
	
	r = datetime.now().isoformat()+"\n"
	
	hex_format = "  "
	hex_digit = 0
	for i in range(len(data_str)):
		if data_str[i] == '1':
			hex_digit = hex_digit + pow(2, 3-(i%4))
		r = r + data_str[i]
		if (i+1) % 4 == 0:
			r = r + " "
			hex_format = "%s%01X    " % (hex_format,hex_digit)
			hex_digit = 0
	
	r = r + "\n" + hex_format + "\n"
		
	t_ext = binary_to_float(data_str[12:24])
	hum = binary_to_float(data_str[28:36])

	if t_ext != None and hum != None:
		r = r + "\nTempérature : %.1f°C\nHumidité : %.1f%%\n" % (t_ext, hum)
	return r
	
	

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
	
	# Then looks for patterns described above.
	j=0
	decoded_data=""
	while j < len(data)-1:
		if message_started:
			# false bit
			if data[j][0] and data[j][1] > HIGH_T and not data[j+1][0] and data[j+1][1] > LOW_T and data[j+1][1] < LOW_T_L:
				decoded_data = decoded_data + "0"
			# true bit
			elif data[j][0] and data[j][1] > HIGH_T and not data[j+1][0] and data[j+1][1] > LOW_T_L and data[j+1][1] < LOW_T_XL:
				decoded_data = decoded_data + "1"
			else:
				# We've reached end of the message
				message_started = False
				
				# Expected: 36 bits. Otherwise, there is a problem...
				if len(decoded_data) == 36:
					print(format_data(decoded_data))
				decoded_data = ""
			j = j+2
		else:
			if data[j][0] and data[j][1] > HIGH_T and not data[j+1][0] and data[j+1][1] > LOW_T_XL:
				message_started = True
				j = j+2
			else:
				j = j+1
