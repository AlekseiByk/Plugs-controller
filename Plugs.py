#!/usr/bin/python
import tinytuya
import time
import threading
import json
import logging
import datetime
import sys
import requests

server_url="" #http://site:port/
secret = "" # secret phrase (to check connection to server)

d = []
DB = None
state = True
cur_state = True
devices = None

logger = logging.getLogger("Plugs")

def prepare_var():
	global devices
	dev = open('/home/pi/Desktop/Plugs/config/devices.json')
	devices = json.load(dev)         # returns JSON object as a dict
	dev.close()
	i = 0
	for device in devices:
		d.append( tinytuya.OutletDevice(device.get('id'), 
                                  		device.get('ip'), 
                                    	device.get('key')))
		d[i].set_version(float(device.get('version')))
		i += 1



def wait_until(stop_time):
    Time = datetime.time(*(map(int, stop_time.split(':'))))
    while Time > datetime.datetime.today().time(): 
        time.sleep(10)
    return

def set_logger(logger: logging.Logger, filename):
	format = "%(asctime)s >>> %(user)-9s - %(message)s"
	logging.basicConfig(level=logging.INFO, format=format)
	filehand = logging.FileHandler(f"/home/pi/Desktop/Plugs/logs/{filename}")
	filehand.setFormatter(logging.Formatter(format))
	logger.addHandler(filehand)

def run_logging(plug_number):
	global devices, logger, state
	cur_state = 0
	cur_i = 0

	while state:
		try:
			d[plug_number].updatedps([18]) 
			data = d[plug_number].status()
			d[plug_number].close()

			cur_st = data.get('dps').get('1')
			cur_i = data.get('dps').get('18')

			log_str = f"{cur_state}, I: {cur_i :06} mA"
			logger.info(log_str,
               			extra = {'user':devices[plug_number].get('name')})

			time.sleep(60)
		except:
			print(f"{devices[plug_number].get('name')} error")
			time.sleep(60)
	return


def log_program():
    
	prepare_var()
	obj = datetime.datetime.now()
	set_logger(logger, f"Plugs{obj.date()}.log")

	threads = []
	i = 0
	for device in d:
		print(i)
		threads.append( threading.Thread(target=run_logging, args=(i, )) )          
		threads[i].start()
		i += 1

	while True:
    	
		wait_until("23:59:50")
		time.sleep(12)
		
		obj = datetime.datetime.now()
		logger.removeHandler(logger.handlers[0])
		set_logger(logger, f"Plugs{obj.date()}.log")
		
def notification(number, text = ''):
	global logger

	payload = {text: number}
	logger.info(str(number) + '=' + text, 
				extra = {'user': number})

	requests.post(server_url+secret, data=payload)


def run_main(thread_number):
	global DB, devices, logger, state
	cur_state = [False, False, False, False]
	cur_i = 0
	cur_st = 0
	washing_status = False

	counter = 0
	last_i = 0
	while True:
		try:
			d[thread_number].updatedps([18]) 
			data = d[thread_number].status()
			d[thread_number].close()

			cur_st = data.get('dps').get('1')
			cur_i = data.get('dps').get('18')



			if cur_i > 0:
				counter = (counter + 1) if (last_i > 0) else 0
			if cur_i == 0:
				counter = (counter + 1) if (last_i == 0) else 0

			if (washing_status == False and cur_i > 0 and counter > 2):
       
				washing_status = True
				notification(number = int(devices[thread_number].get('name')), 
							 text = 'start_washing')

			if (washing_status == True and cur_i == 0 and counter > 2):
       
				washing_status = False
				notification(number = int(devices[thread_number].get('name')),
							 text = 'end_washing')

			last_i = cur_i

			log_str = f"{cur_st}, {cur_i :06} mA"
			logger.info(log_str, 
               			extra = {'user': devices[thread_number].get('name')})
			time.sleep(60)
		except:
			print(f"{devices[thread_number].get('name')} error")
			time.sleep(60)
	return
	
	# TODO check time for booking
	
	# TODO if cur_state = False && check_booking = False -> turn_off
		
def main():
	# TODO wait for commad -> turn on/off 
	prepare_var()
	obj = datetime.datetime.now()
	set_logger(logger, f"main.log")

	threads = []
	i = 0
	for device in d:
		print(i)
		threads.append( threading.Thread(target=run_main, args=(i, )) )          
		threads[i].start()
		i += 1
	return



if __name__ == '__main__':
	if len (sys.argv) < 2 or len (sys.argv) > 2:
		print("Unknown usage")
		sys.exit (1)

	if (sys.argv[1] == "--log" or
		sys.argv[1] == "-l"):
		log_program()
	elif (sys.argv[1] == "--main" or
		sys.argv[1] == "-m"):
		main()
	else:
		print(f"Unknown parametr:{sys.argv[1]}")
		sys.exit (1)

