import rs485eth
import socket
import serial
import pyowm
import os
import binascii
import time
import sys
import json
import random
import paho.mqtt.client as mqtt

do_raw_log = os.getenv("LOGGING", "false").lower() == 'true'

pool_frequency = int(os.getenv("POOL_FREQUENCY", "60"))

server = os.getenv("RS485_ADDRESS", "localhost")
port = int(os.getenv("RS485_PORT", "8899"))

mqttclientid = f'python-mqtt-{random.randint(0, 1000)}'
mqttBroker = os.getenv("MQTT_ADDRESS", "localhost")
mqttPort = int(os.getenv("MQTT_PORT", "1883"))
mqttTopic = os.getenv("MQTT_TOPIC", "reading/solar")

if do_raw_log:
    print("running with debug")
    print(server)
    print(port)
    print(mqttBroker)
    print(mqttPort)
    print(mqttTopic)

def getData(client, mqttTopic):
    instrument = rs485eth.Instrument(server, port, 1, debug=False) # port name, slave address
    
    values = dict()
    print( "01a" ) 
    values['Generated (All time)'] = instrument.read_long(3008, functioncode=4, signed=False) # Read All Time Energy (KWH Total) as Unsigned 32-Bit   
    print( "01b" ) 
    values['Generated (Today)'] = instrument.read_register(3014, numberOfDecimals=1, functioncode=4, signed=False)/10 # Read Today Energy (KWH Total) as 16-Bit
    print( "01c" ) 
    values['Generated (Yesterday)'] = instrument.read_register(3015, numberOfDecimals=1, functioncode=4, signed=False)/10 # Read Today Energy (KWH Total) as 16-Bit
    print( "01d" ) 
    
    print( "02" ) 
    values['AC Watts (W)'] = instrument.read_long(3004, functioncode=4, signed=False) #Read AC Watts as Unsigned 32-Bit
    values['DC Voltage 1 (V)'] = instrument.read_register(3021, functioncode=4, signed=False) / 10 #Read DC Volts as Unsigned 16-Bit
    values['DC Current 1 (A)'] = instrument.read_register(3022, functioncode=4, signed=False) / 10 #Read DC Current as Unsigned 16-Bit
    values['DC Voltage 2 (V)'] = instrument.read_register(3023, functioncode=4, signed=False) / 10 #Read DC Volts as Unsigned 16-Bit
    values['DC Current 2 (A)'] = instrument.read_register(3024, functioncode=4, signed=False) / 10 #Read DC Current as Unsigned 16-Bit
    values['AC voltage 1 (V)'] = instrument.read_register(3033, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
    values['AC voltage 2 (V)'] = instrument.read_register(3034, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
    values['AC voltage 3 (V)'] = instrument.read_register(3035, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
    
    print( "03" ) 
    values['AC Current 1 (A)'] = instrument.read_register(3036, functioncode=4, signed=False) / 10 #Read AC Frequency as Unsigned 16-Bit
    values['AC Current 2 (A)'] = instrument.read_register(3037, functioncode=4, signed=False) / 10 #Read AC Frequency as Unsigned 16-Bit
    values['AC Current 3 (A)'] = instrument.read_register(3038, functioncode=4, signed=False) / 10#Read AC Frequency as Unsigned 16-Bit

    print( "04" ) 
    values['AC Frequency (Hz)'] = instrument.read_register(3042, functioncode=4, signed=False) / 100 #Read AC Frequency as Unsigned 16-Bit
    values['Inverter Temperature (c)'] = instrument.read_register(3041, functioncode=4, signed=True) / 10 #Read Inverter Temperature as Signed 16-B$

    print( "05" ) 
    Realtime_DATA_yy = instrument.read_register(3072, functioncode=4, signed=False) #Read Year
    Realtime_DATA_mm = instrument.read_register(3073, functioncode=4, signed=False) #Read Month
    Realtime_DATA_dd = instrument.read_register(3074, functioncode=4, signed=False) #Read Day
    Realtime_DATA_hh = instrument.read_register(3075, functioncode=4, signed=False) #Read Hour
    Realtime_DATA_mi = instrument.read_register(3076, functioncode=4, signed=False) #Read Minute
    Realtime_DATA_ss = instrument.read_register(3077, functioncode=4, signed=False) #Read Second
    print( "06" ) 

    values['ac power (A)'] = instrument.read_register(3005, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['pv power (V)'] = instrument.read_register(3007, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Total energy (W)'] = instrument.read_register(3009, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Month energy (W)'] = instrument.read_register(3011, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Last month energy (W)'] = instrument.read_register(3013, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Year energy'] = instrument.read_register(3017, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    values['Last year energy'] = instrument.read_register(3019, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit

    print( "07" ) 
    values['error'] = instrument.read_register(3043, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
    
    print( "08" ) 
#    for x in range(3008, 3099):
#        values["_" + str(x) + "_" ] = instrument.read_register(x, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
#
    if do_raw_log:
      print("Date : {:02d}-{:02d}-20{:02d} {:02d}:{:02d}:{:02d}".format(Realtime_DATA_dd, Realtime_DATA_mm, Realtime_DATA_yy, Realtime_DATA_hh, Realtime_DATA_mi, Realtime_DATA_ss) )
      print( values) 

    json_body = { k.replace("(", "").replace(")", "") : v for k, v in values.items() }
                     
    if do_raw_log:
        print(f"Send topic `{mqttTopic}`")
        print(f"Send topic `{json_body}`")

    result = client.publish(mqttTopic, json.dumps(json_body))
    # result: [0, 1]
    status = result[0]

    if status == 0:
        if do_raw_log:
            print(f"Send topic `{mqttTopic}`")
    else:
        print(f"Failed to send message to topic {mqttTopic} ")
        
        
def connect_mqtt(mqttclientid, mqttBroker, mqttPort ):
    if do_raw_log:
        print(f"mqttclientid: {mqttclientid}")
        print(f"mqttBroker: {mqttBroker}")
        print(f"mqttPort: {mqttPort}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)            
    # Set Connecting Client ID
    client = mqtt.Client(mqttclientid)
#    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(mqttBroker, mqttPort)
    return client

client=connect_mqtt(mqttclientid, mqttBroker, mqttPort )
client.loop_start()

try:
    while True:
        getData(client, mqttTopic)
        time.sleep(pool_frequency)
except Exception as e:
    print(e) 
    pass
