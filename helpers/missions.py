import json
import datetime as dt
from pathlib import Path
from config import config
from helpers.logger_factory import logger
from datetime import datetime, timedelta

file_location: str

if hasattr(config, 'get_str'):
    file_location = config.get_str("journaldir")
else:
    file_location = config.get("journaldir") #type: ignore
if file_location is None or file_location == "":
    file_location = config.default_journal_dir


def get_logs_after_timestamp(timestamp: dt.date) -> list[Path]:
    logs_after_timestamp = []

    for log_file in Path(file_location).glob("*.log"):
        if not log_file.is_file():
            continue
        if timestamp < dt.datetime.fromtimestamp(log_file.stat().st_mtime, tz=dt.timezone.utc).date():
            logs_after_timestamp.append(log_file)
    logger.debug(f"Loaded {len(logs_after_timestamp)} Logs for all CMDRs")
    return logs_after_timestamp

def get_cmdr_missions(timestamp: dt.date) -> dict[str, dict[int, dict]]:
    cmdr = ""
    cmdr_events = {}

    for file_path in get_logs_after_timestamp(timestamp):
        with open(file_path, "r", encoding="utf8") as current_log_file:
            line = current_log_file.readline()
            while line != "":
                try:
                    event = json.loads(line)
                    if event["event"] == "Commander":                        
                        cmdr = str(event["Name"])
                        if cmdr not in cmdr_events.keys():
                            cmdr_events[cmdr] = {}
                            
                    elif event["event"] == "MissionAccepted":                        
                        cmdr_events[cmdr][event["MissionID"]] = event
                        
                    elif event["event"] == "CargoDepot" and event["UpdateType"] == "Deliver":                        
                        populate_missions_cargodepot(event, cmdr_events[cmdr])
                            
                    elif event["event"] == "Bounty":                        
                        populate_missions_bounty(event, cmdr_events[cmdr])

                except Exception as ex:
                    logger.warning(f"Error Occurred: {ex}\nFailed to process journal {file_path}. Skipping...")
                finally:
                    line = current_log_file.readline()
                    
    return cmdr_events

def populate_missions_bounty(bounty: dict, missions: dict[int, dict]):
    changed = False
    associated_missions = [mission for mission in missions.values() if (mission["Name"].startswith("Mission_Massacre") and mission["TargetFaction"] == bounty["VictimFaction"])]
    if associated_missions:
        factions = []  
        for mission in associated_missions:
            if mission["Faction"] not in factions:
                    
                if "VictimCount" not in mission or mission["VictimCount"] < mission["KillCount"]:
                    if "VictimCount" not in mission:
                        mission["VictimCount"] = 0
                    mission["VictimCount"] += 1
                    logger.info(f"Mission {mission['MissionID']} kill count increased")
                    factions.append(mission["Faction"])
                    changed = True
                else:
                    next

    return changed

def populate_missions_cargodepot(cargodepot: dict, missions: dict[int, dict]):
    changed = False
    if cargodepot["MissionID"] in missions.keys():
        logger.info(f"Mission {cargodepot['MissionID']} cargo delivered")
        mission = missions[cargodepot["MissionID"]]
        if "DeliveredCount" not in mission:
            mission["DeliveredCount"] = 0
        mission["DeliveredCount"] += cargodepot["Count"]
        changes = True
        
    return changed
