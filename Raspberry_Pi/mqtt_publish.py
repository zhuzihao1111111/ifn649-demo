import os
import time
import serial
import paho.mqtt.client as mqtt
import glob

# MQTT set
broker_address = "ec2-13-211-45-203.ap-southeast-2.compute.amazonaws.com"  # 替换为您的MQTT Broker地址
topic_ifn649 = "ifn649"
client = mqtt.Client()

def find_serial_device():
    ports = glob.glob('/dev/ttyACM*')
    if ports:
        return ports[0]
    return None

def setup_mqtt():
    client.connect(broker_address)
    client.loop_start()

def upload_data():
    serial_device = find_serial_device()
    if serial_device:
        try:
            print(f"Opening serial port {serial_device}...")
            ser = serial.Serial(serial_device, 9600, timeout=1)
            print(f"Serial port {serial_device} opened successfully.")
            
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Received from Teensy: {data}")
                    client.publish(topic_ifn649, data)
                    print(f"Published: {data} to topic: {topic_ifn649}")
                time.sleep(2)
        
        except Exception as e:
            print(f"Error reading from serial: {e}")
        finally:
            ser.close()

if __name__ == "__main__":
    setup_mqtt()
    upload_data()
