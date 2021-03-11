#!/usr/bin/python3

'''
  Copyright 2021 Guilhem Tiennot
  
  Python script working with Gqrx for receiving Manchester-coded messages
  sent by 433Manchester.ino.
  
  Dependencies: datetime, socket, struct, schmitt_trigger
  
  This file is part of manchester_reader.py.
  
  manchester_reader.py is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  manchester_reader.py is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with manchester_reader.py.  If not, see <https://www.gnu.org/licenses/>.
'''  

import socket
import struct
from schmitt_trigger import SchmittTrigger
from datetime import datetime

SAMPLE_RATE=48000 # in Hz

# Gqrx conf for receiving data
UDP_IP="127.0.0.1"
UDP_PORT=7355
UDP_CHUNK=SAMPLE_RATE

# Schmitt trigger thresholds
THRES1=0
THRES2=6000

# Message prefix and suffix
PREFIX="1010101001010101" # stands for 0xAA55
SUFFIX="11111111"         # stands for 0xFF

T=400    # Manchester code period
T_XL=4*T # Sync period

# end of config

message_started=False
previous_data=None
previous_decoded_data=None
last_msg=None


# Convert data into str
def format_data(data_string):
	r = datetime.now().isoformat()
	s = []
	
	for data_str in data_string.split(PREFIX):
		if data_str[-8:] == SUFFIX:
			
			str_data = ""
			checksum = 0
			
			for i in range(0, len(data_str)-23, 8):
				temp_data = int(data_str[i:i + 8],2)
				checksum ^= temp_data
				str_data = str_data + chr(temp_data)
			
			# Only add the message to the array if checksum is correct
			if checksum == int(data_str[-16:-8],2):
				s.append(str_data)
	if len(s)>0:
		return s[0]
		# Since the message is received many times, only return one
	else:
		return None	
	

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
	
	# algo :
	# chercher un 1 long de minimum 4T
	# puis comparer j et j+1 : front descendant -> 1, front montant -> 0
	# enfin, j += 1 si durée de j+1 == T, j+=2 si durée de j+1 == T/2
	j=0
	decoded_data=""
	while j < len(data)-1:
		if message_started:
			if not data[j][0] and data[j][1] > 2*T:
				message_started = False
				formated_data = format_data(decoded_data)
				if formated_data:
					print(formated_data)
				decoded_data = ""
			elif data[j][0] and not data[j+1][0]:
				decoded_data = decoded_data + "1"
			elif not data[j][0] and data[j+1][0]:
				decoded_data = decoded_data + "0"
			else:
				raise ValueError("Unknown symbol!")
			if data[j+1][1] > T/1.5:
				j+=1
			else:
				j+=2
			
		else:
			if data[j][0] and data[j][1] > T_XL:
				message_started = True
			else:
				j+=1
	
	if message_started:
		previous_data = data[-1]
		previous_decoded_data = decoded_data
	formated_data = format_data(decoded_data)
	if formated_data:
		print(formated_data)
