import paho.mqtt.client as mqtt
import random
import time
import json

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker')
    else:
        print('Failed to connect to MQTT Broker')

def send_temperature():
    MQTT_BROKER_URL = 'test.mosquitto.org'
    MQTT_BROKER_PORT = 1883
    MQTT_TOPIC = 'iot/temperature'

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)

    client.loop_start()

    try:
        while True:
            temperature = round(random.uniform(20, 30), 2)

            # Créer un dictionnaire pour représenter les données
            data = {
                'device_type': 'iot',
                'measurement': 'temperature',
                'value': temperature
            }

            # Convertir le dictionnaire en format JSON
            payload = json.dumps(data)

            # Publier les données sur le topic MQTT
            client.publish(MQTT_TOPIC, payload)

            print('Temperature (MQTT):', temperature)
            time.sleep(5)

    except KeyboardInterrupt:
        print("Script terminated by user")
        client.disconnect()

if __name__ == '__main__':
    send_temperature()
