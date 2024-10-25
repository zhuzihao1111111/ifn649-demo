import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)
socketio = SocketIO(app)


MQTT_BROKER = "ec2-13-211-45-203.ap-southeast-2.compute.amazonaws.com"
MQTT_TOPIC = "ifn649"
CONTROL_TOPIC = "control"

latest_message = "No message received yet."

def on_message(client, userdata, message):
    global latest_message
    latest_message = message.payload.decode('utf-8')
    print(f"Received message: {latest_message}")
    socketio.emit('mqtt_message', {'message': latest_message})

def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_control', methods=['POST'])
def send_control():
    data = request.json
    message = data.get('message')
    if message in ['on', 'off']:
        client = mqtt.Client()
        client.connect(MQTT_BROKER)
        client.publish(CONTROL_TOPIC, message)  
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid control message'}), 400

if __name__ == '__main__':
    port = 5001
    print(f"Application running at http://localhost:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
