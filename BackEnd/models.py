from dataclasses import dataclass

@dataclass
class Iot:
    mac:str
    temp:float
    datetime:str
    latitude:float
    longitude:float
@dataclass
class UserAccount:
    username: str
    password: str
@dataclass
class Device:
    name: str
    memory_load: float
    cpu_load: float
    disk_usage: float