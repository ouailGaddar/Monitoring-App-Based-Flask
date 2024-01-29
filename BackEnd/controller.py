import base64
from io import BytesIO
import io
from flask import Flask, jsonify, make_response, render_template, request, redirect, send_file, session, url_for
import jwt
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import numpy as np
from io import StringIO
import pymongo
from models import Device
from dal import DeviceDAO, UserAccountDAO
from threading import Thread
import random
import time
from services import getSystemInfo, UserService , DeviceServices
from iot import send_temperature,send_temperature_thread
import random
import time
import json
import threading
from meteo import fetch_weather_data_between_dates, predict_precipitation_sum_between_dates
from datetime import datetime
from functools import wraps
import pandas as pd



from datetime import datetime, timedelta
from services import IotServices ,VilleServices
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] ='\xbcKc}2\xae\x847\x1b\x0b}\x11\xcaB\x8c\x00\xb3\xd8b{\x83F\xffP'
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_name):
    return UserService.get_user_by_username(user_name)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('authentification.html')
@app.route('/')
def show_authentification():
    if not session.get('logged_in'):
        return render_template('authentification.html')
    else :
        return redirect(url_for('dashboard'))

@app.route('/authenticate', methods=['POST'])
def authenticate():
    

    username = request.form.get('username')
    password = request.form.get('password')
    action = request.form.get('action')
    
    if action == 'login':
        result = UserService.verify_user_credentials(username, password)
        if result:
            user = UserService.get_user_by_username(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            
            return render_template('authentification.html', error='Invalid username or password')

    elif action == 'signup':
       
        return redirect(url_for('signup'))

   

    return render_template('authentification.html')


@app.route('/add_iot')
@login_required
def add_iot() :
    return render_template('add-client.html')
@app.route('/add-iot', methods=['POST'])
@login_required
def addIot():
    
    name = request.form.get('name')
    mac = request.form.get('mac')
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))

    
    result = IotServices.add_iot_data(name=name, mac=mac, latitude=latitude, longitude=longitude)

    if result :
        iot_data = IotServices.get_all_iots()
        return render_template('iot-informations.html', iot_data = iot_data)
    else :
        return render_template('add-client.html',error_message = "Failed to add")

@app.route('/update_iot')
@login_required
def updateIot() :
    iot_mac = request.args.get('mac')
    iot_data = IotServices.get_iot_by_mac(iot_mac)
    return render_template('update-iot.html',iot=iot_data)
@app.route('/update_iot/<string:mac>', methods=['POST'])
@login_required
def update_iot(mac):
    
    updated_data = {
        'name': request.form.get('name'),
        'latitude': float(request.form.get('latitude')),
        'longitude': float(request.form.get('longitude')),
     
    }

  
    result = IotServices.update_iot_data(mac, updated_data)

    if result:
        iot_data=IotServices.get_all_iots()
        return render_template('iot-informations.html',iot_data=iot_data) 
    else:
        
        return render_template('update-iot.html',error_message='Failed to update')
@app.route('/dashboard')
@login_required
def dashboard():
    
    return render_template("gestionDevices.html")
    
@app.route('/signUp')

def signUp():
    return render_template('signUp.html')


@app.route('/signup', methods=['POST'])

def signup():
        
        username = request.form.get('username')
        password = request.form.get('password')

        if UserService.get_user_by_username(username):
            return render_template('signUp.html', error='Username already exists. Choose a different one.')
        user=UserService.create_user(username, password)

        if user :
            return render_template('authentification.html')
        else :
            return render_template('signUp.html')


@app.route('/snmp-info', methods=['GET'])
@login_required
def snmp_info():
    system_info = getSystemInfo('192.168.1.162')
    
    memory_size = system_info[0]
    memory_used = system_info[1]
    cpu_load = system_info[2]


    return render_template('snmp-dashboard.html', snmp_info={'memory_used': memory_used, 'memory_size': memory_size, 'cpu_load': cpu_load})
@app.route('/dashboardIOT')
@login_required
def dashboardIot() :
    iot_data = IotServices.get_all_iots()
    return render_template('iot-informations.html',iot_data=iot_data)
@app.route('/iot-dashboard')
@login_required
def iot_dashboard():
    iot_mac = request.args.get('mac')
    print(iot_mac)
    iot_data = IotServices.get_iot_by_mac(iot_mac)
    if iot_data is None:
        return "IoT data not found."
    plt.figure(figsize=(8, 6))
    if 'temperature_history' in iot_data:
        temperatures = [entry['temperature'] for entry in iot_data['temperature_history']]
        measurement_indices = list(range(1, len(temperatures) + 1))
        plt.plot(measurement_indices, temperatures, marker='o')
        plt.title(f'Temperature History for {iot_data["name"]}')
        plt.xlabel('Measurement Index')
        plt.ylabel('Temperature (°C)')
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close()  
        img_buf.seek(0)
        graph_img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        response = make_response(base64.b64decode(graph_img_base64))
        response.headers['Content-Type'] = 'image/png'
        return response
    else:
        return "Temperature history not available for the specified IoT."



@app.route('/start-simulation')
@login_required
def start_simulation():
    
        iot_mac = request.args.get('mac')
        print('iot      :')
        print(iot_mac)
        if IotServices.start_simulation(iot_mac):
            return f"Simulation started successfully for IoT with MAC: {iot_mac}."
        else:
            return "IoT data not found or simulation already running."

    
    

@app.route('/stop-simulation')
@login_required
def stop_simulation():
  
        iot_mac = request.args.get('mac')

        if IotServices.stop_simulation(iot_mac):
            return f"Simulation stopped successfully for IoT with MAC: {iot_mac}."
        else:
            return "Simulation not found or not running."

   

@app.route('/delete_iot', methods=['GET'])
@login_required
def delete_iot():
    iot_mac = request.args.get('mac')
    result=IotServices.delete_iot_data(iot_mac)
    if result :
        iot_data = IotServices.get_all_iots()
        return render_template('iot-informations.html',iot_data = iot_data)
   
@app.route('/dashboardEndDiveces')
@login_required
def dashboardEndDiveces() :
    devices=DeviceServices.get_all_devices()
    return render_template('endDiveces-information.html',devices=devices)
@app.route('/dashboardOfDevice')
@login_required
def dashboardOfDevice() :
    ip = request.args.get('ip')

    system_info = getSystemInfo(ip)
    
    memory_size = system_info[0]
    memory_used = system_info[1]
    cpu_load = system_info[2]

    return render_template('snmp-dashboard.html', snmp_info={'memory_used': memory_used, 'memory_size': memory_size, 'cpu_load': cpu_load})
@app.route('/Ville')
@login_required
def ville() :
    ville_data = VilleServices.get_all_villes()
    return render_template('ville-informations.html',ville_data = ville_data)
@app.route('/add_ville')
@login_required
def add_ville() :
    
    return render_template('add-ville.html')
@app.route('/ajouter_ville', methods=['POST'])
@login_required
def ajouter_ville():
    if request.method == 'POST':
        name = request.form['name']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])

        result = VilleServices.add_ville(name, latitude, longitude)

        if result:
            ville_data = VilleServices.get_all_villes()
            return render_template('ville-informations.html', ville_data = ville_data)
        else:
            
            return render_template('add-ville.html',error_message='Failed to add')
@app.route('/update_ville')
@login_required
def update_ville() :
    ville_name = request.args.get('name')
    ville = VilleServices.get_ville_by_name(ville_name)
    return render_template('update-ville.html',ville=ville)


@app.route('/update_ville_form/<string:name>', methods=['POST'])
@login_required
def update_ville_form(name):
    if request.method == 'POST':
      
        ville_name = request.form.get('name')
        updated_data = {
            'latitude': float(request.form.get('latitude')),
            'longitude': float(request.form.get('longitude')),
           
        }

        result = VilleServices.update_ville_by_name(ville_name, updated_data)

        if result:
            ville_data = VilleServices.get_all_villes()
            return render_template('ville-informations.html',ville_data=ville_data)
        else:
            return render_template('update-ville.html',error_message="Failed to update Ville")
            
    else:
        
        return "Method not allowed for the requested URL"

@app.route('/dashboardOfVille') 
@login_required
def dashboardOfVille() :
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    session['latitude'] = latitude
    session['longitude'] = longitude
    return render_template('date-settings.html')
@app.route('/date-settings', methods=['POST'])
@login_required
def graph():
    start_date0 = request.form.get('startDate')
    end_date0 = request.form.get('endDate')
    start_date1 = datetime.strptime(start_date0, "%Y-%m-%d")
    end_date1 = datetime.strptime(end_date0, "%Y-%m-%d")
    
    latitude = session.get('latitude')
    longitude = session.get('longitude')
    
    start_date = "2020-07-01"
    end_date = "2024-01-20"

    weather_data = fetch_weather_data_between_dates(latitude, longitude, start_date, end_date)
    
    predictions_dict = predict_precipitation_sum_between_dates(weather_data, start_date1, end_date1)
    
    predictions_df = pd.DataFrame(list(predictions_dict.items()), columns=['date', 'precipitation_sum'])
    predictions_df['date'] = pd.to_datetime(predictions_df['date'], format='%Y-%m-%d')
    import matplotlib
    matplotlib.use('Agg')
    plt.figure(figsize=(10, 6))
    plt.plot(predictions_df['date'], predictions_df['precipitation_sum'], marker='o', linestyle='-', color='b')
    plt.title('Prédictions de precipitation_sum entre {} et {}'.format(start_date1.strftime('%d-%m-%Y'), end_date1.strftime('%d-%m-%Y')), fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Précipitation Sum', fontsize=14)
    plt.grid(True)
    plt.xticks(rotation=45)  
    plt.tight_layout()  
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    plt.close()
    img_str = "data:image/png;base64," + base64.b64encode(img_stream.read()).decode('utf-8')
    html = f"<div style='text-align: center;'><img src='{img_str}'/></div>"

    return html
@app.route('/add_device')
@login_required
def add_device() :
    return render_template('add-device.html')
@app.route('/addDevice', methods=['POST'])
@login_required
def addDevice():
   
        name = request.form.get('name') 
        ip = request.form.get('ip')
        new_device = Device(name=name, ip=ip )
        success = DeviceServices.add_device(new_device)

        if success:
            devices = DeviceServices.get_all_devices()
            return render_template('endDiveces-information.html',devices=devices)  # Redirect to a success page or another endpoint
        else:
            error_message = "Failed to add the device. Please try again."
            return render_template('add-device.html', error_message=error_message)
@app.route('/delete_ville')
@login_required
def delete_ville():

        ville_name = request.args.get('name')
        deletion_result = VilleServices.get_ville_by_name(ville_name)
        print(deletion_result)
        if deletion_result:
            VilleServices.delete_ville(ville_name)
            ville_data = VilleServices.get_all_villes()
            return render_template('ville-informations.html',ville_data=ville_data)  
   
        
        
@app.route('/delete_device')
@login_required
def delete_device():
    ip = request.args.get('ip')
    result = DeviceServices.delete_device(ip)
    
    if result:
        devices = DeviceServices.get_all_devices()
        return render_template('endDiveces-information.html',devices=devices)
@app.route('/update_device')
@login_required
def update_device() :
    device_ip = request.args.get('ip')
    device = DeviceServices.get_device_by_ip(device_ip)

    return render_template('update-device.html',device=device)
@app.route('/update_device_form<string:ip>', methods=['POST'])
@login_required
def update_device_form(ip):
    if request.method == 'POST':
        device_ip= ip
        new_name = request.form.get('name')
        print(device_ip)
        print(new_name)
        result = DeviceServices.update_device(device_ip,new_name)

        if result:
            devices = DeviceServices.get_all_devices()
            return render_template('endDiveces-information.html',devices = devices)
        else:
            return render_template('update-device.html',error_message="Failed to update Device")
            
    else:
        return "Method not allowed for the requested URL"
if __name__ == '__main__':
    app.run(debug=False)