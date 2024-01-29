import datetime
from typing import Dict, List, Union
from flask_login import UserMixin
from dataclasses import dataclass

@dataclass
class Iot:
    name:str
    mac:str
    latitude:float
    longitude:float
    temperature_history: List[Dict[str, Union[str, float]]] = None
@dataclass
class UserAccount(UserMixin):
    username: str
    password: str

    def __eq__(self, other):
        if isinstance(other, UserAccount):
            return self.username == other.username
        return False
    def get_id(self):
        # Return a unique identifier for the user (e.g., user ID as a string)
        return str(self.username)
@dataclass
class Device:
    ip:str
    name: str
 
@dataclass
class Ville :
    name:str
    latitude:float
    longitude:float
@dataclass
class WeatherData:
    date: datetime
    temperature_2m_max: float
    temperature_2m_min: float
    temperature_2m_mean: float
    precipitation_sum: float
    rain_sum: float
    snowfall_sum: float
    precipitation_hours: float
    wind_speed_10m_max: float