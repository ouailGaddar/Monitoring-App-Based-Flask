import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime, timedelta

from dal import Iot ,IotDao
import threading
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker')
    else:
        print('Failed to connect to MQTT Broker')

def send_temperature(name, mac, latitude, longitude):
   
    MQTT_BROKER_URL = 'test.mosquitto.org'
    MQTT_BROKER_PORT = 1883
    MQTT_TOPIC = 'iot/temperature'

    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT)

    client.loop_start()

    temperatures = []

    try:
        while True:
            temperature = round(random.uniform(20, 40), 2)

            data = {
                'device_type': 'iot',
                'measurement': 'temperature',
                'value': temperature,
                'timestamp': datetime.now().isoformat()
            }

            # Convertir le dictionnaire en format JSON
            payload = json.dumps(data)

            # Publier les données sur le topic MQTT
            client.publish(MQTT_TOPIC, payload)

            temperatures.append(data)
            #print('Temperature (MQTT):', temperature)

            # Ajout des données à la base de données
            iot_data = Iot(
                name=name,
                mac=mac,
                latitude=latitude,
                longitude=longitude,
                temperature_history=[{
                    'datetime': data['timestamp'],
                    'temperature': data['value']
                }]
            )

            success = IotDao.store_iot_data_periodic(iot_data)
            if not success:
                print("Failed to store IoT data in the database.")
            else:
                print("ajouter avec succes")

            time.sleep(2)

    except KeyboardInterrupt:
        print("Script terminated by user")
        client.disconnect()


    return temperatures, success
def send_temperature_thread(name, mac, latitude, longitude):
    temperatures_list, success = send_temperature( name, mac, latitude, longitude)
    if success:
        print("IoT data successfully stored in the database.")
    else:
        print("Failed to store IoT data in the database.")
