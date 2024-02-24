import json
import tkinter as tk
from tkinter import ttk
from tkinter import font
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from missions.state import massacre_mission_listeners, MassacreMission
from ui.settings import Configuration, configuration, settings_ui
from helpers.logger_factory import logger
from helpers.ui import get_expiry_text
from theme import theme
#from helpers.overlay import overlay

class MassacreMissionData:

    @dataclass
    class FactionState:
        mission_count: int = 0
        victim_count: int = 0
        kill_count: int = 0
        reward: int = 0
        shareable_reward: int = 0
        min_expiry: datetime = None
        max_expiry: datetime = None
        
    def __init__(self, massacre_mission_store: dict[int, MassacreMission]):
        self.warnings: list[str] = []
        # if Log Level is set to DEBUG, this will output the current Massacre Mission State to the Log File.
        # for easy searching, you can Ctrl+F for "MASSACRE_MISSION_DATA_INPUT" and get the line below that.
        logger.debug("MassacreMissionData input below: MASSACRE_MISSION_DATA_INPUT")
        try:
            debug_message_state: dict[int, dict] = {}
            for k in massacre_mission_store.keys():
                v = massacre_mission_store[k]
                debug_message_state[k] = v.as_dict()
            logger.debug(json.dumps(debug_message_state))
        except Exception:
            logger.error("Failed to Log debug_message_state")
            pass

        target_factions: list[str] = []
        target_types: list[str] = []
        target_systems: list[str] = []
        self.factions: dict[str, MassacreMissionData.FactionState] = {}

        self.mission_count: int = 0
        self.victim_count: int = 0
        self.kill_count: int = 0
        self.reward: int = 0
        self.shareable_reward: int = 0
        self.min_expiry: datetime = None
        self.max_expiry: datetime = None        

        for mission in massacre_mission_store.values():
            faction = mission.source_faction
            if faction not in self.factions.keys():
                self.factions[faction] = MassacreMissionData.FactionState()
            faction_state = self.factions[faction]

            faction_state.mission_count += 1            
            faction_state.victim_count += mission.victim_count
            faction_state.kill_count += mission.kill_count
            faction_state.reward += mission.reward            
            if mission.is_wing:
                faction_state.shareable_reward += mission.reward

            expiry = datetime.strptime(mission.expiry,"%Y-%m-%dT%H:%M:%SZ")                
            if faction_state.min_expiry is None or expiry < faction_state.min_expiry:
                faction_state.min_expiry = expiry                
            if faction_state.max_expiry is None or expiry > faction_state.max_expiry:
                faction_state.max_expiry = expiry         

            if mission.target_faction not in target_factions:
                target_factions.append(mission.target_faction)

            if mission.target_type not in target_types:
                target_types.append(mission.target_type)

            if mission.target_system not in target_systems:
                target_systems.append(mission.target_system)

        # After all Missions have been handled, iterate through the faction_to_count_lookup to calculate the Total Rewards   
        for faction_state in self.factions.values():
            self.mission_count += faction_state.mission_count
            self.kill_count += faction_state.kill_count
            self.victim_count += faction_state.victim_count
            self.reward += faction_state.reward
            self.shareable_reward += faction_state.shareable_reward
            if self.min_expiry is None or faction_state.min_expiry < self.min_expiry:
                self.min_expiry = faction_state.min_expiry
            if self.max_expiry is None or faction_state.max_expiry < self.max_expiry:
                self.max_expiry = faction_state.max_expiry

        # Check for Warnings
        if len(target_factions) > 1:
            self.warnings.append(f"Multiple Target Factions: {', '.join(target_factions)}!")
        if len(target_types) > 1:
            self.warnings.append(f"Multiple Target Types: {', '.join(target_types)}!")
        if len(target_systems) > 1:
            self.warnings.append(f"Multiple Target Systems: {', '.join(target_systems)}!")

class GridUiSettings:
    """
    Subset of the entire Configuration that focuses on which information is displayed
    """
    def __init__(self, config: Configuration):
        self.column_count = 4
        self.display_total = config.display_total
        self.display_stats = config.display_stats
        self.debug_mode = config.debug_mode

class MassacreUI:
    def __init__(self):
        self.tabstrip: Optional[tk.Notebook] = None
        self.frame: Optional[tk.Frame] = None
        self.data: Optional[MassacreMissionData] = None
        self.settings: GridUiSettings = GridUiSettings(configuration)
        settings_ui.configuration_listeners.append(self.rebuild_settings)

    def rebuild_settings(self, config: Configuration):
        self.settings = GridUiSettings(config)
        self.update_ui()

    def set_frame(self, parent: ttk.Notebook):
        # New EDMC Update seems to break frame.grid_size. It returned 0 for EDMC-PVPBot (where I reused the code from here)
        # So it will probably also return 0 here. Someone on the latest version should maybe check it.
        
        self.tabstrip = parent
        
        # Check if it is 0 and set it to 2. Should probably look into this further at some point.
        cspan = self.tabstrip.grid_size()[1]
        if cspan < 1:
            cspan = 2
        self.frame = tk.Frame(parent)        
        self.frame.grid(column=0, columnspan=cspan, sticky=tk.W)
        self.frame.bind("<<Refresh>>", lambda _: self.update_ui())
        self.update_ui()
        
        return self.frame

    def notify_mission_state_changed(self, data: Optional[MassacreMissionData]):
        self.data = data
        self.update_ui()

    def notify_settings_changed(self):
        self.settings: GridUiSettings = GridUiSettings(configuration)
        self.update_ui()

    def update_ui(self):
        if self.frame is None:
            logger.warning("Frame was not yet set. UI was not updated.")
            return

        logger.info("Updating UI...")
        
        for child in self.frame.winfo_children():
            child.destroy()

        self.row_count = 0
        
        if self.data is not None:
            self.display_data()

        theme.update(self.frame)

    def display_data(self) -> int:    
        self.tabstrip.tab(self.frame, text=f"Massacre [{self.data.mission_count}]")
        self.display_header()
        for faction in sorted(self.data.factions.keys()):
            self.display_row(faction)

        if self.settings.display_total:
            self.display_total()

        if self.settings.display_stats:
            self.display_stats()

        for warning in self.data.warnings:
            self.display_warning(warning)
    
    def display_header(self):

        default_font = font.Font(font=tk.Label()['font']).actual()

        faction_label = tk.Label(self.frame, text="Faction", font=(default_font['family'], default_font['size'], 'bold'))
        kills_label = tk.Label(self.frame, text="Kills", font=(default_font['family'], default_font['size'], 'bold'))
        mission_label = tk.Label(self.frame, text="Mis", font=(default_font['family'], default_font['size'], 'bold'))        
        victims_label = tk.Label(self.frame, text="Victims", font=(default_font['family'], default_font['size'], 'bold'))
        remaining_label = tk.Label(self.frame, text="Rem", font=(default_font['family'], default_font['size'], 'bold'))
        value_label = tk.Label(self.frame, text="Value (Shared)", font=(default_font['family'], default_font['size'], 'bold'))
        
        ui_elements = [faction_label, kills_label, victims_label, remaining_label, value_label]

        for i, element in enumerate(ui_elements):
            element.grid(row=self.row_count, column=i, sticky=tk.W)
        self.row_count += 1
        
        self.settings.column_count = len(ui_elements)

    def display_row(self, faction: str):      
        
        faction_data = self.data.factions[faction]
        
        reward_str = "{:.1f}".format(float(faction_data.reward) / 1_000_000)
        shareable_reward_str = "{:.1f}".format(float(faction_data.shareable_reward) / 1_000_000)
        
        faction_label = tk.Label(self.frame, text=faction)
        kills_label = tk.Label(self.frame, text=faction_data.kill_count)
        mission_label = tk.Label(self.frame, text=faction_data.mission_count)
        victims_label = tk.Label(self.frame, text=faction_data.victim_count)
        remaining_label = tk.Label(self.frame, text=f"{faction_data.kill_count - faction_data.victim_count}")
        value_label = tk.Label(self.frame, text=f"{reward_str} ({shareable_reward_str})")

        ui_elements = [faction_label, kills_label, mission_label, victims_label, remaining_label, value_label]
        for i, element in enumerate(ui_elements):
            element.grid(row=self.row_count, column=i, sticky=tk.W)
            if (faction_data.kill_count - faction_data.victim_count == 0):
                element.config(foreground="gray")            
        self.row_count += 1

        # lines = [f"commodity:{commodity},count:{self.data.delivered_count}/{self.data.required_count}"]
        # overlay.send_lines("mining", lines)
        
    def display_total(self):
        label = tk.Label(self.frame, text="Total")
        kill_total = tk.Label(self.frame, text=self.data.kill_count)
        mission_total = tk.Label(self.frame, text=self.data.mission_count)
        victim_total = tk.Label(self.frame, text=self.data.victim_count)
        remaining_total = tk.Label(self.frame, text=f"{self.data.kill_count - self.data.victim_count}")
        reward_normal_total = "{:.1f}".format(float(self.data.reward) / 1_000_000)
        reward_shareable_total = "{:.1f}".format(float(self.data.shareable_reward) / 1_000_000)
        reward_total = tk.Label(self.frame, text=f"{reward_normal_total} ({reward_shareable_total})")

        ui_elements =[label, kill_total, mission_total, victim_total, remaining_total, reward_total]
        for i, element in enumerate(ui_elements):
            element.config(foreground="green")
            element.grid(row=self.row_count, column=i, sticky=tk.W)
        self.row_count += 1
        
        pb = ttk.Progressbar(self.frame, orient="horizontal", mode="determinate", length=300)
        pb.grid(column=0, row=self.row_count, columnspan=self.settings.column_count, padx=3, pady=1, ipady=1)
        pb["value"] = (float(self.data.victim_count)/float(self.data.kill_count))*100    
        self.row_count += 1
        
    def display_stats(self):
        min_expiry_text = get_expiry_text(self.data.min_expiry)
        max_expiry_text = get_expiry_text(self.data.max_expiry)
        if min_expiry_text == max_expiry_text:
            expiry_text = f"Expiry: {max_expiry_text}"
        else:
            expiry_text = f"Expiry: {max_expiry_text} <-> {min_expiry_text}"        
        expiry_label = tk.Label(self.frame, text=expiry_text, foreground="green")
        expiry_label.grid(row=self.row_count, column=0, columnspan=self.settings.column_count, sticky=tk.W)
        self.row_count += 1
        
        reward_rate_text = f"{float(self.data.reward)/1000000/self.data.kill_count:.2f}"
        wing_reward_rate_text = f"{float(self.data.shareable_reward)/1000000/self.data.kill_count:.2f}"
        reward_text = f"Reward Rate: {reward_rate_text} ({wing_reward_rate_text}) M CR/Kill."
        reward_label = tk.Label(self.frame, text=reward_text, foreground="green")
        reward_label.grid(row=self.row_count, column=0, columnspan=self.settings.column_count, sticky=tk.W)
        self.row_count += 1        
        
    def display_warning(self, warning: str):
        label = tk.Label(self.frame, text=warning)
        label.config(foreground="orange")
        label.grid(column=0, columnspan=self.settings.column_count, row=self.row_count, sticky=tk.W)
        self.row_count += 1
        
massacre_ui = MassacreUI()

def handle_mission_state_changed(data: dict[int, MassacreMission]):
    data_view = MassacreMissionData(data)
    massacre_ui.notify_mission_state_changed(data_view)

massacre_mission_listeners.append(handle_mission_state_changed)
