import json
import tkinter as tk
from tkinter import ttk
from tkinter import font
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import ui.settings
from missions.state import mining_mission_listeners, MiningMission
from ui.settings import Configuration, configuration, settings_ui
from helpers.logger_factory import logger
from helpers.ui import get_expiry_text
from theme import theme
#from helpers.overlay import overlay

class MiningMissionData:

    @dataclass
    class CommodityState:
        mission_count: int = 0
        required_count: int = 0
        delivered_count: int = 0
        reward: int = 0
        shareable_reward: int = 0
        min_expiry: datetime = None
        max_expiry: datetime = None

    def __init__(self, mining_mission_store: dict[int, MiningMission]):
        self.warnings: list[str] = []
        # if Log Level is set to DEBUG, this will output the current Mining Mission State to the Log File.
        # for easy searching, you can Ctrl+F for "MINING_MISSION_DATA_INPUT" and get the line below that.
        logger.debug("MiningMissionData input below: MINING_MISSION_DATA_INPUT")
        try:
            debug_message_state: dict[int, dict] = {}
            for k in mining_mission_store.keys():
                v = mining_mission_store[k]
                debug_message_state[k] = v.as_dict()
            logger.debug(json.dumps(debug_message_state))
        except Exception:
            logger.error("Failed to Log debug_message_state")
            pass

        self.commodities: dict[str, MiningMissionData.CommodityState] = {}

        self.mission_count: int = 0
        self.required_count: int = 0
        self.delivered_count: int = 0
        self.reward: int = 0
        self.shareable_reward: int = 0
        self.min_expiry: datetime = None
        self.max_expiry: datetime = None
        
        for mission in mining_mission_store.values():
            commodity_required = mission.commodity
            if commodity_required not in self.commodities.keys():
                self.commodities[commodity_required] = MiningMissionData.CommodityState()
            commodity_state = self.commodities[commodity_required]
            
            commodity_state.mission_count += 1
            commodity_state.required_count += mission.required_count
            commodity_state.delivered_count += mission.delivered_count
            commodity_state.reward += mission.reward

            if mission.is_wing:
                commodity_state.shareable_reward += mission.reward

            expiry = datetime.strptime(mission.expiry,"%Y-%m-%dT%H:%M:%SZ")                
            if commodity_state.min_expiry is None or expiry < commodity_state.min_expiry:
                commodity_state.min_expiry = expiry                
            if commodity_state.max_expiry is None or expiry > commodity_state.max_expiry:
                commodity_state.max_expiry = expiry                
                
        # After all Missions have been handled, iterate through the faction_to_count_lookup to calculate the Total Rewards   
        for commodity_state in self.commodities.values():
            self.mission_count += commodity_state.mission_count
            self.required_count += commodity_state.required_count
            self.delivered_count += commodity_state.delivered_count
            self.reward += commodity_state.reward
            self.shareable_reward += commodity_state.shareable_reward
            if self.min_expiry is None or commodity_state.min_expiry < self.min_expiry:
                self.min_expiry = commodity_state.min_expiry
            if self.max_expiry is None or commodity_state.max_expiry < self.max_expiry:
                self.max_expiry = commodity_state.max_expiry

        # Check for Warnings
        if len(self.commodities.keys()) > 1:
            self.warnings.append(f"Multiple Commodities: {', '.join(self.commodities.keys())}!")

class GridUiSettings:
    """
    Subset of the entire Configuration that focuses on which information is displayed
    """
    def __init__(self, config: Configuration):
        self.column_count = 4
        self.display_row_total = config.display_row_total
        self.display_row_stats = config.display_row_stats
        self.debug_mode_enabled = config.debug_mode_enabled
        
class MiningUI:
    def __init__(self):
        self.tabstrip: Optional[ttk.Notebook] = None
        self.frame: Optional[tk.Frame] = None
        self.data: Optional[MiningMissionData] = None        
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

    def notify_mission_state_changed(self, data: Optional[MiningMissionData]):
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
      
        if self.data is not None and self.data.mission_count > 0:
            self.display_data()

        theme.update(self.frame)
    
    def display_data(self) -> int:            
        self.tabstrip.tab(self.frame, text=f"Mining [{self.data.mission_count}]")    
        self.display_header()
        for commodity in sorted(self.data.commodities.keys()):
            self.display_row_data(commodity)

        if self.settings.display_row_total:
            self.display_row_total()

        if self.settings.display_row_stats:
            self.display_row_stats()

        for warning in self.data.warnings:
            self.display_row_warning(warning)        
    
    def display_header(self):

        default_font = font.Font(font=tk.Label()['font']).actual()
    
        commodity_label = tk.Label(self.frame, text="Commodity", font=(default_font['family'], default_font['size'], 'bold'))
        required_label = tk.Label(self.frame, text="Count", font=(default_font['family'], default_font['size'], 'bold'))
        mission_label = tk.Label(self.frame, text="Mis", font=(default_font['family'], default_font['size'], 'bold'))
        delivered_label = tk.Label(self.frame, text="Del", font=(default_font['family'], default_font['size'], 'bold'))
        remaining_label = tk.Label(self.frame, text="Rem", font=(default_font['family'], default_font['size'], 'bold'))
        value_label = tk.Label(self.frame, text="Value (Shared)", font=(default_font['family'], default_font['size'], 'bold'))
    
        ui_elements = [commodity_label, required_label, mission_label, delivered_label, remaining_label, value_label]
        for i, element in enumerate(ui_elements):
            element.grid(row=self.row_count, column=i, sticky=tk.W)
        self.row_count += 1
        
        self.settings.column_count = len(ui_elements)

    def display_row_data(self, commodity: str):

        commodity_data = self.data.commodities[commodity]

        reward_str = "{:.1f}".format(float(commodity_data.reward) / 1_000_000)
        shareable_reward_str = "{:.1f}".format(float(commodity_data.shareable_reward) / 1_000_000)

        commodity_label = tk.Label(self.frame, text=commodity)
        required_label = tk.Label(self.frame, text=commodity_data.required_count)
        mission_label = tk.Label(self.frame, text=commodity_data.mission_count)
        delivered_label = tk.Label(self.frame, text=commodity_data.delivered_count)
        remaining_label = tk.Label(self.frame, text=f"{commodity_data.required_count - commodity_data.delivered_count}")
        value_label = tk.Label(self.frame, text=f"{reward_str} ({shareable_reward_str})")
    
        ui_elements = [commodity_label, required_label, mission_label, delivered_label, remaining_label, value_label]
        for i, element in enumerate(ui_elements):
            element.grid(row=self.row_count, column=i, sticky=tk.W)
            if (commodity_data.required_count - commodity_data.delivered_count == 0):
                element.config(foreground="gray")
        self.row_count += 1
        
        # lines = [f"commodity:{commodity},count:{self.data.delivered_count}/{self.data.required_count}"]
        # overlay.send_lines("mining", lines)

    def display_row_total(self):
        label = tk.Label(self.frame, text="Total")
        required_total = tk.Label(self.frame, text=self.data.required_count)
        mission_total = tk.Label(self.frame, text=self.data.mission_count)
        delivered_total = tk.Label(self.frame, text=self.data.delivered_count)
        remaining_total = tk.Label(self.frame, text=f"{self.data.required_count - self.data.delivered_count}")
        reward_normal_total = "{:.1f}".format(float(self.data.reward) / 1_000_000)
        reward_shareable_total = "{:.1f}".format(float(self.data.shareable_reward) / 1_000_000)
        reward_total = tk.Label(self.frame, text=f"{reward_normal_total} ({reward_shareable_total})")

        ui_elements =[label, required_total, mission_total, delivered_total, remaining_total, reward_total]
        for i, element in enumerate(ui_elements):
            element.config(foreground="green")
            element.grid(row=self.row_count, column=i, sticky=tk.W)
        self.row_count += 1
        
        pb = ttk.Progressbar(self.frame, orient="horizontal", mode="determinate", length=300)
        pb.grid(column=0, row=self.row_count, columnspan=self.settings.column_count, padx=3, pady=1, ipady=1)
        pb["value"] = (float(self.data.delivered_count)/float(self.data.required_count))*100
        self.row_count += 1

    def display_row_stats(self):
        min_expiry_text = get_expiry_text(self.data.min_expiry)
        max_expiry_text = get_expiry_text(self.data.max_expiry)
        if min_expiry_text == max_expiry_text:
            expiry_text = f"Expiry: {max_expiry_text}"
        else:
            expiry_text = f"Expiry: {max_expiry_text} <-> {min_expiry_text}"        
        expiry_label = tk.Label(self.frame, text=expiry_text, foreground="green")
        expiry_label.grid(row=self.row_count, column=0, columnspan=self.settings.column_count, sticky=tk.W)
        self.row_count += 1
        
        reward_rate_text = f"{float(self.data.reward)/1000000/self.data.required_count:.2f}"
        wing_reward_rate_text = f"{float(self.data.shareable_reward)/1000000/self.data.required_count:.2f}"
        reward_text = f"Reward Rate: {reward_rate_text} ({wing_reward_rate_text}) M CR/Ton."
        reward_label = tk.Label(self.frame, text=reward_text, foreground="green")
        reward_label.grid(row=self.row_count, column=0, columnspan=self.settings.column_count, sticky=tk.W)
        self.row_count += 1
        
    def display_row_warning(self, warning: str):
        label = tk.Label(self.frame, text=warning)
        label.config(foreground="orange")
        label.grid(column=0, columnspan=self.settings.column_count, row=self.row_count, sticky=tk.W)
        self.row_count += 1
        
mining_ui = MiningUI()

def handle_mission_state_changed(data: dict[int, MiningMission]):
    data_view = MiningMissionData(data)
    mining_ui.notify_mission_state_changed(data_view)

mining_mission_listeners.append(handle_mission_state_changed)
