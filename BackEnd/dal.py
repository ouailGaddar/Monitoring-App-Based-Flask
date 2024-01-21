
from datetime import datetime 
from pymongo import MongoClient
from models import UserAccount

class Database:
    client = None
    db = None

    @staticmethod
    def getConnection() -> MongoClient:
        try:
            # Modifier l'URI de connexion en fonction de votre configuration MongoDB
            Database.client = MongoClient('mongodb://root:1234@db:27017/')
            Database.db = Database.client['db_hosts']
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            Database.client = None
            Database.db = None

        return Database.client

class IotDao:
    @staticmethod
    def getAllTemp():
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return []

        try:
           
            collection = client.db_hosts.IOT
            result = collection.find({})
           
            return list(result)
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
        finally:
            if client:
                client.close()
    @staticmethod
    def addIotData(mac: str, temp: float, latitude: float, longitude: float):
        client = Database.getConnection()
        if client is None:
            print("No valid connection.")
            return False

        try:
            # Modifier 'collection_name' par le nom de votre collection MongoDB
            collection = client.db_hosts.IOT
            iot_data = {
                "mac": mac,
                "temp": temp,
               "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": latitude,
                "longitude": longitude
            }
            result = collection.insert_one(iot_data)
            print(f"Inserted IOT data with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False
        finally:
            if client:
                client.close()
class UserAccountDAO:
    def create_user(self, username: str, password: str):
        db = Database()
        client = db.getConnection()
        if client is None:
            with open('error_log.txt', 'a') as file:
             file.write("No valid connection.\n")
            return False

        try:
            print("***************************")
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
      

    def get_user_by_username(self, username: str):
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
    def verify_user_credentials(self, username: str, password: str) -> bool:
        user = self.get_user_by_username(username)
        with open('user_info2.txt', 'a') as file:
            file.write(f'Username: {username}, User Exists: {user is not None}\n')
        if user:
            # User exists, check the password
            return user.password == password
        return False
        

# Test UserAccountDAO methods
if __name__ == '__main__':
    user_dao = UserAccountDAO()

    

