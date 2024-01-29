
from datetime import datetime
from bson import ObjectId 
from pymongo import MongoClient
from models import Device, UserAccount, Ville, WeatherData
from models import Iot

class Database:
    client = None
    db = None

    @staticmethod
    def getConnection() -> MongoClient:
        try:
 
            Database.client = MongoClient('mongodb://root:1234@db:27017/')
            #Database.client = MongoClient('mongodb://localhost:27017')
            Database.db = Database.client['db_hosts']
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            Database.client = None
            Database.db = None

        return Database.client

class IotDao:
    @staticmethod
    def get_all_iots():
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return []

        try:
            collection = client.db_hosts.IOT
            result = collection.find({}, {'_id': 0})
            iots = []

            for item in result:
                iot = Iot(
                    name=item.get('name', ''),
                    mac=item.get('mac', ''),
                    latitude=item.get('latitude', 0.0),
                    longitude=item.get('longitude', 0.0),
                    temperature_history=item.get('temperature_history', [])
                )
                iots.append(iot)

            return iots
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    @staticmethod
    def get_iot_by_mac(mac: str):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return None

        try:
            collection = client.db_hosts.IOT
            result = collection.find_one({"mac": mac}, {'_id': 0})  # Exclude '_id'
            if result:
                return Iot(name=result['name'], mac=result['mac'], latitude=result['latitude'], longitude=result['longitude'], temperature_history=result['temperature_history'])
            return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    @staticmethod
    def add_iot_data(name: str, mac: str, latitude: float, longitude: float):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.IOT
            iot_data = Iot(
                name=name,
                mac=mac,
                latitude=latitude,
                longitude=longitude,
                temperature_history=[]  
            )
            result = collection.insert_one(iot_data.__dict__)
            print(f"Inserted IoT data with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

    @staticmethod
    def add_temperature_to_iot(mac: str, temperature: float):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.IOT
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_temperature_entry = {
                'datetime': current_datetime,
                'temperature': temperature
            }

            collection.update_one(
                {'mac': mac},
                {'$push': {'temperature_history': new_temperature_entry}}
            )
            print(f"Added temperature to IoT with mac: {mac}")
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

    @staticmethod
    def update_iot_data(mac: str, updated_data: dict):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.IOT
            result = collection.update_one({"mac": mac}, {"$set": updated_data})
            print(f"Updated {result.modified_count} IoT data with mac: {mac}")
            return result.modified_count > 0
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

    @staticmethod
    def store_iot_data_periodic(iot_data: Iot):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            print('Connection established ')
            collection = client.db_hosts.IOT

            for entry in iot_data.temperature_history:

                new_temperature_entry = {
                    'datetime': entry['datetime'],
                    'temperature': entry['temperature']
                }

                collection.update_one(
                    {'name': iot_data.name, 'mac': iot_data.mac,'latitude': iot_data.latitude, 'longitude' : iot_data.longitude},
                    {'$push': {'temperature_history': new_temperature_entry}},
                    upsert=True
                )

                print(f"Added temperature to IoT with mac: {iot_data.mac}")

            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False
    @staticmethod
    def delete_iot_data(mac: str):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.IOT
            result = collection.delete_one({"mac": mac})
            print(f"Deleted {result.deleted_count} IoT data with mac: {mac}")
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

   
      

class UserAccountDAO:
    @staticmethod
    def create_user(username: str, password: str):
        db = Database()
        client = db.getConnection()
        if client is None:
            with open('error_log.txt', 'a') as file:
             file.write("No valid connection.\n")
            return False

        try:
        
            collection = client.db_hosts.users  # Modify 'users' based on your collection name
            user_account = UserAccount(username=username, password=password)
            result = collection.insert_one(user_account.__dict__)
            print(f"User account created with ID: {result.inserted_id}")
            return True
        except Exception as e:
            with open('Error executing query.txt', 'a') as file:
             file.write(f"Error executing query: {e}")
            print(f"Error executing query: {e}")
            return False
      
    @staticmethod
    def get_user_by_username(username: str):
        db = Database()
        client = db.getConnection()
        if client is None:
           
           return None

        try:
            collection = client.db_hosts.users  # Modify 'users' based on your collection name
            user_data = collection.find_one({"username": username})
            if user_data:
                return UserAccount(username=user_data['username'], password=user_data['password'])
            return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if client:
                client.close()
    @staticmethod
    def verify_user_credentials(username: str, password: str) -> bool:
        user = UserAccountDAO.get_user_by_username(username)
        with open('user_info2.txt', 'a') as file:
            file.write(f'Username: {username}, User Exists: {user is not None}\n')
        if user:
            # User exists, check the password
            return user.password == password
        return False
        
class WeatherDataDAO:
    @staticmethod
    def add_weather_data(weather_data: WeatherData):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.WeatherData
            result = collection.insert_one(weather_data.__dict__)
            print(f"Inserted weather data with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

class VilleDAO:
    @staticmethod
    def add_ville(ville: Ville):
            client = Database.getConnection()
            if client is None:
                print("No valid connection.")
                return False

            try:
                collection = client.db_hosts.Ville
                result = collection.insert_one(ville.__dict__)
                print(f"Added ville data - Name: {ville.name}, Latitude: {ville.latitude}, Longitude: {ville.longitude}")
                return True
            except Exception as e:
                print(f"Error adding ville data: {e}")
                return False
    @staticmethod
    def get_ville_by_name(name: str):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return None

        try:
            collection = client.db_hosts.Ville
            result = collection.find_one({"name": name}, {"_id": 0})

            if result:
                return Ville(name=result['name'], latitude=result['latitude'], longitude=result['longitude'])
            return None
        except Exception as e:
            print(f"Error getting ville data by name: {e}")
            return None
    @staticmethod
    def get_ville_by_id(ville_id: str):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return None

        try:
            collection = client.db_hosts.Ville
            result = collection.find_one({"_id": ObjectId(ville_id)}, {"_id": 0})

            if result:
                return Ville(name=result['name'], latitude=result['latitude'], longitude=result['longitude'])
            return None
        except Exception as e:
            print(f"Error getting ville data by ID: {e}")
            return None

    @staticmethod
    def get_all_villes():
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return []

        try:
            collection = client.db_hosts.Ville
            result = collection.find({}, {"_id": 0})
            villes = []

            for item in result:
                ville = Ville(
                    name=item.get('name', ''),
                    latitude=item.get('latitude', 0.0),
                    longitude=item.get('longitude', 0.0)
                )
                villes.append(ville)

            return villes
        except Exception as e:
            print(f"Error getting all villes: {e}")
            return []

    @staticmethod
    def update_ville_by_name(ville_name: str, updated_data: dict):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.Ville
            result = collection.update_one({"name": ville_name}, {"$set": updated_data})

            print(f"Updated {result.modified_count} ville data for name: {ville_name}")
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating ville data: {e}")
            return False

    @staticmethod
    def delete_ville_by_name(name: str):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.Ville
            result = collection.delete_one({"name": name})

            print(f"Deleted {result.deleted_count} ville data with name: {name}")
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting ville data: {e}")
            return False
class DeviceDAO:
    @staticmethod
    def add_device(device: Device):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.Device
            result = collection.insert_one(device.__dict__)
            print(f"Inserted device data with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False

    @staticmethod
    def get_all_devices():
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return []

        try:
            collection = client.db_hosts.Device
            result = collection.find({}, {"_id": 0})
            devices = []

            for item in result:
                device = Device(
                    ip=item.get('ip', ''),
                    name=item.get('name', ''),
                   
                )
                devices.append(device)

            return devices
        except Exception as e:
            print(f"Error getting all devices: {e}")
            return []
    @staticmethod
    def update_device(ip: str, new_name: str) -> bool:
        client = Database.getConnection()
        
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.Device
            result = collection.update_one({"ip": ip}, {"$set": {"name": new_name}})
            
            print(f"Updated {result.modified_count} device data with IP: {ip}")
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating device data: {e}")
            return False


    @staticmethod
    def delete_device(ip: str):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            collection = client.db_hosts.Device
            result = collection.delete_one({"ip": ip})
            print(f"Deleted {result.deleted_count} device data with IP: {ip}")
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting device data: {e}")
            return False
    @staticmethod
    def get_device_by_ip(ip: str):
        client = Database.getConnection()

        if client is None:
            print("No valid connection.")
            return None

        try:
            collection = client.db_hosts.Device
            result = collection.find_one({"ip": ip}, {"_id": 0, "name": 1, "ip": 1})

            if result:
                return Device(
                    ip=result.get('ip'),
                    name=result.get('name')
                )
            return None
        except Exception as e:
            print(f"Error getting device data by IP: {e}")
            return None

if __name__ == '__main__':

    device = DeviceDAO.get_device_by_ip('192.168.1.1')
    print(device)
   
