import os
import signal
import time
import paho.mqtt.client as mqtt
import subprocess

# MQTT Set
broker_address = "ec2-13-211-45-203.ap-southeast-2.compute.amazonaws.com"
topic_control = "control"

mqtt_publish_process = None

# run mqtt_publish.py
def start_mqtt_publish():
    global mqtt_publish_process
    if mqtt_publish_process is None:
        print("Starting mqtt_publish.py...")
        mqtt_publish_process = subprocess.Popen(["python3", "mqtt_publish.py"])
        print("mqtt_publish.py started.")

# stop mqtt_publish.py
def stop_mqtt_publish():
    global mqtt_publish_process
    if mqtt_publish_process is not None:
        print("Stopping mqtt_publish.py...")
        mqtt_publish_process.terminate()
        mqtt_publish_process.wait()
        mqtt_publish_process = None
        print("mqtt_publish.py stopped.")

# recive on/off and control
def on_message(client, userdata, message):
    command = message.payload.decode("utf-8").strip()
    print(f"Received command: {command}")
    
    if command == "off":
        print("Turning off USB ports and stopping mqtt_publish.py...")
        os.system("sudo uhubctl -l 1-1 -p 1 -a off")
        os.system("sudo uhubctl -l 1-1 -p 2 -a off")
        os.system("sudo uhubctl -l 1-1 -p 3 -a off")
        os.system("sudo uhubctl -l 1-1 -p 4 -a off")
        stop_mqtt_publish()
    
    elif command == "on":
        print("Turning on USB ports and starting mqtt_publish.py...")
        os.system("sudo uhubctl -l 1-1 -p 1 -a on")
        os.system("sudo uhubctl -l 1-1 -p 2 -a on")
        os.system("sudo uhubctl -l 1-1 -p 3 -a on")
        os.system("sudo uhubctl -l 1-1 -p 4 -a on")
        start_mqtt_publish()

# MQTT Client set
client = mqtt.Client()
client.on_message = on_message
client.connect(broker_address)
client.subscribe(topic_control)

# Start Monitoring
client.loop_start()

# Main Loop
try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    client.loop_stop()
    stop_mqtt_publish()
    print("Program exited.")
