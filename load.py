import tkinter as tk
from tkinter import ttk
import sys
import time
from tkinter import END
from l10n import Locale
import os
from typing import Any, Optional
from os.path import basename, dirname
from datetime import date, timedelta
from helpers.missions import get_cmdr_missions
from missions.repository import set_active_uuids, mission_repository, initialise_repository

from ui.main import main_ui
from helpers.logger_factory import logger
from ui.settings import Configuration, configuration, settings_ui
from helpers.version_check import get_version_info_worker, VersionInfo

this = sys.modules[__name__]  # For holding module globals

plugin_name = os.path.basename(os.path.dirname(__file__))
selected_cmdr: Optional[str] = None

try:
    from config import config
except ImportError:
    config = dict()
    
def plugin_app(parent: tk.Frame) -> tk.Frame:
    
    main_ui.set_frame(parent)

    if configuration.version_check_enabled:
        logger.info("Starting Version Check in new Thread...")

        def notify_main_ui_version_info(version_info: VersionInfo):
            main_ui.notify_version_info(version_info)
                
        thread = get_version_info_worker(notify_main_ui_version_info)
        thread.start()
    else:
        logger.info("Skipping Update Check. Disabled in Settings")

    return parent

def plugin_start3(_: str) -> str:
    logger.info("Starting Mission Status Plugin")
    mission_store = get_cmdr_missions(date.today() - timedelta(weeks=4))
    logger.info(f"Found Missions for {len(mission_store)} CMDRs")
    initialise_repository(mission_store)    
    logger.info("Awaiting Cmdr and active missions to start building Mission Index")
    return basename(dirname(__file__))

def journal_entry(cmdr: str, _is_beta: bool, _system: str, _station: str, entry: dict[str, Any], _state: dict[str, Any]):
    if entry["event"] == "Missions":
        active_mission_uuids = map(lambda x: int(x["MissionID"]), entry["Active"])        
        set_active_uuids(list(active_mission_uuids), cmdr)

    elif entry["event"] in ["MissionAbandoned", "MissionCompleted", "MissionRedirected"]:
        mission_uuid = entry["MissionID"]
        if mission_repository is not None:
            mission_repository.notify_mission_finished(mission_uuid)
            
    elif entry["event"] == "MissionAccepted":
        if mission_repository is not None:
            mission_repository.notify_mission_accepted(entry, cmdr)

    elif entry["event"] == "CargoDepot" and entry["UpdateType"] == "Deliver":
        if mission_repository is not None:
            mission_repository.notify_mission_cargo_delivered(entry, cmdr)

    elif entry["event"] == "Bounty":
        if mission_repository is not None:
            mission_repository.notify_bounty_awarded(entry, cmdr)                            

def plugin_prefs(parent: Any, _cmdr: str, _is_beta: bool):
    return settings_ui.display_settings(parent)

def prefs_changed(_cmdr: str, _is_beta: bool):
    settings_ui.notify_changed()
    