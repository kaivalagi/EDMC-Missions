from typing import Callable
from helpers.logger_factory import logger
from dataclasses import dataclass
from datetime import datetime
import missions.repository
from pathlib import Path
from config import config

file_location: str

if hasattr(config, 'get_str'):
    file_location = config.get_str("journaldir")
else:
    file_location = config.get("journaldir") #type: ignore
if file_location is None or file_location == "":
    file_location = config.default_journal_dir
    
@dataclass
class MassacreMission:
    id: int
    target_system: str
    target_station: str    
    source_faction: str
    reward: int
    expiry: datetime
    is_wing: bool
    target_type: str
    target_faction: str 
    kill_count: int
    victim_count: int

    def as_dict(self):
        as_dict = {
            "mission_id": self.id,
            "target_system": self.target_system,
            "target_station": self.target_station,
            "source_faction": self.source_faction,
            "reward": self.reward,
            "expiry": self.expiry,
            "is_wing": self.is_wing,
            "target_type": self.target_type,
            "target_faction": self.target_faction,
            "kill_count": self.kill_count,
            "victim_count": self.victim_count
        }
        return as_dict

@dataclass
class MiningMission:
    id: int
    target_system: str
    target_station: str        
    source_faction: str
    reward: int
    expiry: datetime
    is_wing: bool
    commodity: str
    required_count: int
    delivered_count: int

    def as_dict(self):
        as_dict = {
            "mission_id": self.id,
            "target_system": self.target_system,
            "target_station": self.target_station,
            "source_faction": self.source_faction,
            "reward": self.reward,
            "expiry": self.expiry,
            "is_wing": self.is_wing,
            "commodity": self.commodity,
            "required_count": self.required_count,
            "delivered_count": self.delivered_count
        }
        return as_dict


@dataclass
class CollectMission:
    id: int
    target_system: str
    target_station: str    
    source_faction: str
    reward: int
    expiry: datetime
    is_wing: bool
    commodity: str
    required_count: int
    delivered_count: int

    def as_dict(self):
        as_dict = {
            "mission_id": self.id,
            "target_system": self.target_system,
            "target_station": self.target_station,
            "source_faction": self.source_faction,
            "reward": self.reward,
            "expiry": self.expiry,
            "is_wing": self.is_wing,
            "commodity": self.commodity,
            "required_count": self.required_count,
            "delivered_count": self.delivered_count
        }
        return as_dict
    
@dataclass
class CourierMission:
    id: int
    target_system: str
    target_station: str
    source_faction: str
    reward: int
    expiry: datetime
    is_wing: bool
    target_faction: str 
    
    def as_dict(self):
        as_dict = {
            "mission_id": self.id,
            "target_system": self.target_system,
            "target_station": self.target_station,
            "source_faction": self.source_faction,
            "reward": self.reward,
            "expiry": self.expiry,
            "is_wing": self.is_wing,
            "target_faction": self.target_faction
        }
        return as_dict
    
def get_massacre_from_event(event: dict) -> MassacreMission:
    mission_id: int = event["MissionID"]
    target_system: str = event["DestinationSystem"]
    target_station: str = event["DestinationStation"]
    source_faction: str = event["Faction"]
    reward: int = event["Reward"]
    expiry: datetime = event["Expiry"]
    wing: bool = event["Wing"]
    target_type: str = event["TargetType"]
    target_faction: str = event["TargetFaction"]
    kill_count: int = event["KillCount"]
    victim_count: int = event.get("VictimCount",0)
    return MassacreMission(
            mission_id,
            target_system, 
            target_station, 
            source_faction, 
            reward, 
            expiry,
            wing, 
            target_type, 
            target_faction,
            kill_count,
            victim_count
        )

def get_mining_from_event(event: dict) -> MiningMission:
    mission_id: int = event["MissionID"]
    target_system: str = event["DestinationSystem"]
    target_station: str = event["DestinationStation"]
    source_faction: str = event["Faction"]
    reward: int = event["Reward"]
    expiry: datetime = event["Expiry"]
    wing: bool = event["Wing"]
    commodity: str = event["Commodity_Localised"]
    required_count: int = event["Count"]
    delivered_count: int = event.get("DeliveredCount",0)
    return MiningMission(
            mission_id,
            target_system, 
            target_station, 
            source_faction, 
            reward, 
            expiry,
            wing,
            commodity,
            required_count, 
            delivered_count
        )

def get_collect_from_event(event: dict) -> CollectMission:
    mission_id: int = event["MissionID"]
    target_system: str = event["DestinationSystem"]
    target_station: str = event["DestinationStation"]
    source_faction: str = event["Faction"]
    reward: int = event["Reward"]
    expiry: datetime = event["Expiry"]
    wing: bool = event["Wing"]
    commodity: str = event["Commodity_Localised"]
    required_count: int = event["Count"]
    delivered_count: int = event.get("DeliveredCount",0)
    return MiningMission(
            mission_id,
            target_system, 
            target_station, 
            source_faction, 
            reward, 
            expiry,
            wing,
            commodity,
            required_count, 
            delivered_count
        )

def get_courier_from_event(event: dict) -> CourierMission:
    mission_id: int = event["MissionID"]
    target_system: str = event["DestinationSystem"]
    target_station: str = event["DestinationStation"]
    source_faction: str = event["Faction"]
    reward: int = event["Reward"]
    expiry: datetime = event["Expiry"]
    wing: bool = event["Wing"]
    target_faction: str = event["TargetFaction"]
    return CourierMission(
            mission_id,
            target_system, 
            target_station, 
            source_faction, 
            reward, 
            expiry,
            wing, 
            target_faction
        )

massacre_mission_listeners: list[Callable[[dict[int, MassacreMission]], None]] = []
_massacre_mission_store: dict[int, MassacreMission] = {}

mining_mission_listeners: list[Callable[[dict[int, MiningMission]], None]] = []
_mining_mission_store: dict[int, MiningMission] = {}

collect_mission_listeners: list[Callable[[dict[int, CollectMission]], None]] = []
_collect_mission_store: dict[int, CollectMission] = {}

courier_mission_listeners: list[Callable[[dict[int, CourierMission]], None]] = []
_courier_mission_store: dict[int, CourierMission] = {}

def get_mission_type(mission: dict) -> bool:
    name = mission["Name"]
    target_type = mission.get('TargetType', None)
    if name.startswith("Mission_Massacre") and "OnFoot" not in name and target_type:
        return "massacre"
    elif name.startswith("Mission_Mining") and "OnFoot" not in name:
        return "mining"
    elif name.startswith("Mission_Collect") and "OnFoot" not in name:
        return "collect"    
    elif name.startswith("Mission_Courier") and "OnFoot" not in name:
        return "courier"        
    else:
        return "unknown"

def save_unknown_mission_type_json(mission: dict):    
    file_path = Path(file_location, "unknown_mission_types.json")
    with open(file_path, "a") as file:
        file.write(f"{mission}\n")
        
def __handle_new_missions_state(data: dict[int, dict]):

    logger.info(f"Received {len(data)} new missions.")
    
    _massacre_mission_store.clear()
    _mining_mission_store.clear()
    _collect_mission_store.clear()
    _courier_mission_store.clear()
    
    for mission in data.values():
        
        mission_id = mission["MissionID"]
        mission_type = get_mission_type(mission)
        
        if mission_type == "massacre":
            _massacre_mission_store[mission_id] = get_massacre_from_event(mission)
        elif mission_type == "mining":
            _mining_mission_store[mission_id] = get_mining_from_event(mission)
        elif mission_type == "collect":
            _collect_mission_store[mission_id] = get_collect_from_event(mission)
        elif mission_type == "courier":
            _courier_mission_store[mission_id] = get_courier_from_event(mission)            
        else:
            save_unknown_mission_type_json(mission)

    if len(_massacre_mission_store) > 0:
        for listener in massacre_mission_listeners:
            listener(_massacre_mission_store)

    if len(_mining_mission_store) > 0:
        for listener in mining_mission_listeners:
            listener(_mining_mission_store)

    if len(_collect_mission_store) > 0:
        for listener in collect_mission_listeners:
            listener(_collect_mission_store)

    if len(_courier_mission_store) > 0:
        for listener in courier_mission_listeners:
            listener(_courier_mission_store)
        
missions.repository.active_missions_changed_event_listeners.append(__handle_new_missions_state)
