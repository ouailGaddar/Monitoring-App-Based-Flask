from pysnmp.hlapi import *
from iot import send_temperature_thread
from dal import DeviceDAO, IotDao, UserAccountDAO, VilleDAO, WeatherDataDAO
from models import Device, Iot, UserAccount, Ville, WeatherData
from threading import Thread ,Event

community = 'public'
memory_size = '.1.3.6.1.2.1.25.2.3.1.5.1'
memory_used = '.1.3.6.1.2.1.25.2.3.1.6.1'
cpu_load_oid_base = '.1.3.6.1.2.1.25.3.3.1.2'

def get(host, oid):
    try:
        error_indication, error_status, error_index, var_bind = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid))
            )
        )
        if error_indication:
            return f'Error indication: {error_indication}'
        elif error_status:
            return f'Error status: {error_status}'
        elif error_index:
            return f'Error index: {error_index}'
        return f'{var_bind[0][1]}'
    except Exception as e:
        return f'Error: {e}'

def get_cpu_load(host):
    try:
        cpu_load_values = []

        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((host, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(cpu_load_oid_base)),
                lexicographicMode=False,
        ):
            if errorIndication:
                return f'Error indication: {errorIndication}'
            elif errorStatus:
                return f'Error status: {errorStatus} at {errorIndex}'

            for varBind in varBinds:
                oid, value = varBind
                # Convert OID to string and then split
                process_number = str(oid).split('.')[-1]
                cpu_load_values.append({'Process Number': process_number, 'CPU Load': value.prettyPrint()})

        return cpu_load_values
    except Exception as e:
        return f'Error: {e}'

def getSystemInfo(host):
    return (
        get(host, memory_size),
        get(host, memory_used),
        get_cpu_load(host)
    )
class IotServices:
    simulation_threads = {}
    running_flags = {}
    @staticmethod
    def add_iot_data(name: str, mac: str, latitude: float, longitude: float):
        # Créer une instance de la classe IotDao
        if name == "" or mac == "" or latitude == "" or longitude == "":
            return False
        else :
            if IotDao.get_iot_by_mac(mac) != None :
                return False 
            else :
                result = IotDao.add_iot_data(name, mac, latitude, longitude)

                if result:
                    
                    return True
                else:
                    return False

    @staticmethod
    def start_simulation(iot_mac: str) -> bool:
        print(iot_mac)
        print('iot_mac ****************')
        iot_data = IotDao.get_iot_by_mac(iot_mac)
        print(iot_data)
        print('iot data ****************************')
        if iot_data:
            print('***********************************')
            name = iot_data.name
            latitude = iot_data.latitude
            longitude = iot_data.longitude

            # Create a running flag for the simulation thread
            running_flag = Event()
            running_flag.set()  # Set the flag initially to True

            # Start the simulation thread with the running flag
            simulation_thread = Thread(target=send_temperature_thread, args=(name, iot_mac, latitude, longitude, running_flag))
            simulation_thread.start()

            # Save the simulation thread and its running flag
            IotServices.simulation_threads[iot_mac] = simulation_thread
            IotServices.running_flags[iot_mac] = running_flag

            print('***************************   :' )
            print(IotServices.simulation_threads[iot_mac])
            return True
        else:
            return False

    @staticmethod
    def stop_simulation(iot_mac: str) -> bool:
        # Check if the simulation thread exists for the specified IoT MAC
        print('********************************')
        print('IotServices.simulation_threads[iot_mac]')
        print(IotServices.simulation_threads[iot_mac])
        print("aaaaaaaaaaaaaaaa")
        if iot_mac in IotServices.simulation_threads:
            print('bbbbbbbbbb')
            # Terminate the simulation thread by clearing the running flag
            running_flag = IotServices.running_flags[iot_mac]
            running_flag.clear()  # Set the flag to stop the thread

            # Wait for the thread to finish
            simulation_thread = IotServices.simulation_threads[iot_mac]
            simulation_thread.join()

            # Remove the simulation thread and its running flag
            del IotServices.simulation_threads[iot_mac]
            del IotServices.running_flags[iot_mac]

            return True
        else:
            return False
    @staticmethod
    def get_iot_by_mac(mac: str):
        # Créer une instance de la classe IotDao
        iot_dao = IotDao()
        
        try:
            # Appeler la méthode get_iot_by_mac de la classe IotDao pour récupérer les données
            result = iot_dao.get_iot_by_mac(mac)
            
            if result:
                return {
                    'name': result.name,
                    'mac': result.mac,
                    'latitude': result.latitude,
                    'longitude': result.longitude,
                    'temperature_history': result.temperature_history
                }
            else:
                # Si aucune donnée n'est trouvée, retourner None
                return None
        except Exception as e:
            # En cas d'erreur, imprimer l'erreur et retourner None
            print(f"Error getting IOT data: {e}")
            return None

    @staticmethod
    def update_iot_data(mac: str, updated_data: dict):
        # Créer une instance de la classe IotDao
        iot_dao = IotDao()

        try:
            # Appeler la méthode update_iot_data de la classe IotDao pour mettre à jour les données
            result = iot_dao.update_iot_data(mac, updated_data)

            if result:
                # Si la mise à jour est réussie, retourner un message de succès
                return f"IOT Data updated for MAC: {mac}"
            else:
                # Si la mise à jour échoue, retourner un message d'échec
                return f"Failed to update IOT Data for MAC: {mac}"

        except Exception as e:
            # En cas d'erreur, imprimer l'erreur et retourner un message d'erreur
            print(f"Error updating IOT data: {e}")
            return f"Error updating IOT data: {e}"

    @staticmethod
    def delete_iot_data(mac: str):
        # Créer une instance de la classe IotDao
        iot_dao = IotDao()

        try:
            # Appeler la méthode delete_iot_by_mac de la classe IotDao pour supprimer les données
            result = iot_dao.delete_iot_by_mac(mac)

            if result:
                # Si la suppression est réussie, retourner un message de succès
                return f"IOT Data deleted for MAC: {mac}"
            else:
                # Si la suppression échoue, retourner un message d'échec
                return f"Failed to delete IOT Data for MAC: {mac}"

        except Exception as e:
            # En cas d'erreur, imprimer l'erreur et retourner un message d'erreur
            print(f"Error deleting IOT data: {e}")
            return f"Error deleting IOT data: {e}"
    @staticmethod
    def store_iot_data_periodic(iot_data):
        return IotDao.store_iot_data_periodic(iot_data)
    @staticmethod 
    def get_all_iots() :
        return IotDao.get_all_iots()
    @staticmethod
    def delete_iot_data(mac:str) :
        return IotDao.delete_iot_data(mac)
class UserService:
    @staticmethod
    def create_user(username: str, password: str) -> bool:
    
        return UserAccountDAO.create_user(username, password)
    @staticmethod
    def get_user_by_username(username: str) -> UserAccount:
       
        return UserAccountDAO.get_user_by_username(username)
    @staticmethod
    def verify_user_credentials(username: str, password: str) -> bool:
    
        return UserAccountDAO.verify_user_credentials(username, password)
class VilleServices:
    @staticmethod
    def add_ville(name: str, latitude: float, longitude: float) -> str:
        ville_data = Ville(name=name, latitude=latitude, longitude=longitude)

        result = VilleDAO.add_ville(ville_data)

        if result:
            return "Ville added successfully - ID"
        else:
            return "Failed to add ville."
    @staticmethod
    def get_ville_by_name(name: str) -> dict:
        ville_data = VilleDAO.get_ville_by_name(name)

        if ville_data:
            return {
                'name': ville_data.name,
                'latitude': ville_data.latitude,
                'longitude': ville_data.longitude
            }
        else:
            return None
    @staticmethod
    def get_ville_by_id(ville_id: str) -> dict:
        ville_data = VilleDAO.get_ville_by_id(ville_id)

        if ville_data:
            return {
                'name': ville_data.name,
                'latitude': ville_data.latitude,
                'longitude': ville_data.longitude
            }
        else:
            return None

    @staticmethod
    def get_all_villes() -> list:
        all_villes = VilleDAO.get_all_villes()

        return [{
            'name': ville.name,
            'latitude': ville.latitude,
            'longitude': ville.longitude
        } for ville in all_villes]

    @staticmethod
    def update_ville_by_name(ville_name: str, updated_data: dict) -> str:
        result_update = VilleDAO.update_ville_by_name(ville_name, updated_data)

        if result_update:
            return f"Ville updated successfully: {ville_name}"
        else:
            return f"Failed to update ville: {ville_name}"
    @staticmethod
    def delete_ville(name: str) :
          result_delete = VilleDAO.delete_ville_by_name(name)
          return result_delete

    

class WeatherDataServices :
    @staticmethod
    def add_weather_data(mac: str, weather_data: WeatherData):
        return WeatherDataDAO.add_weather_data(mac, weather_data)
class DeviceServices:
    @staticmethod
    def add_device(device: Device) -> bool:
        # Vérifier si un dispositif avec la même IP existe déjà
        existing_device = DeviceDAO.get_device_by_ip(device.ip)

        if existing_device is None:
            # Aucun dispositif avec la même IP, ajouter le nouveau dispositif
            result = DeviceDAO.add_device(device)

            if result:
                return True
            else:
                # Échec de l'ajout du nouveau dispositif
                return False
        else:
            # Un dispositif avec la même IP existe déjà
            return False

            

    @staticmethod
    def get_all_devices() -> list:
        all_devices = DeviceDAO.get_all_devices()

        return [{
            'ip': device.ip,
            'name': device.name,
         
        } for device in all_devices]

    @staticmethod
    def update_device(ip: str, new_name: dict) -> bool:
        result_update = DeviceDAO.update_device(ip, new_name)

        if result_update:
            return True
        else:
            return False

    @staticmethod
    def delete_device(ip: str) -> str:
        result_delete = DeviceDAO.delete_device(ip)

        if result_delete:
            return f"Device deleted successfully for IP: {ip}"
        else:
            return f"Failed to delete device for IP: {ip}"
    @staticmethod
    def get_device_by_ip(ip :str) :
        return DeviceDAO.get_device_by_ip(ip)
if __name__ == '__main__':
    #host_ip = '192.168.1.162'  # Replace with your desired SNMP host IP
    #print(getSystemInfo(host_ip)[2])7device_instance = Device(ip="192.168.1.1", name="SampleDevice", memory_size=8.0, cpu_load=[], memory_used=2.0)

    # Appelez la méthode add_device de DeviceServices
    device_instance = Device(ip="192.168.1.1", name="SampleDevice")
    result = DeviceServices.add_device(device_instance)

    # Vérifiez le résultat
    if result:
        print("Device ajouté avec succès.")
    else:
        print("Échec de l'ajout du device. Il existe déjà un device avec la même IP.")
