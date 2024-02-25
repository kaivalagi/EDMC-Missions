import tkinter as tk
from tkinter import ttk
from typing import Optional

from missions.state import CollectMission, CourierMission, MassacreMission, MiningMission, collect_mission_listeners, courier_mission_listeners, massacre_mission_listeners, mining_mission_listeners
from ui.massacre import massacre_ui
from ui.mining import mining_ui
from ui.collect import CollectMissionData, collect_ui
from ui.courier import courier_ui

from ui.settings import Configuration, configuration, settings_ui
from helpers.logger_factory import logger
from theme import theme
from helpers.version_check import open_download_page, VersionInfo

class GridUiSettings:
    def __init__(self, config: Configuration):
        self.display_missions_collect = config.display_missions_collect
        self.display_missions_courier = config.display_missions_courier
        self.display_missions_massacre = config.display_missions_massacre
        self.display_missions_mining = config.display_missions_mining
        self.display_row_total = config.display_row_total
        self.display_row_stats = config.display_row_stats
        self.debug_mode_enabled = config.debug_mode_enabled

class MainUI:
    def __init__(self):
        self.frame: Optional[tk.Frame] = None
        self.version_info: Optional[VersionInfo] = None
        self.no_collect_missions_data = True
        self.no_courier_missions_data = True
        self.no_massacre_missions_data = True
        self.no_mining_missions_data = True
        self.settings: GridUiSettings = GridUiSettings(configuration)
        settings_ui.configuration_listeners.append(self.rebuild_settings)
        
        self.tabstrip = Optional[ttk.Notebook]
        self.collect_tab = Optional[tk.Frame]
        self.courier_tab = Optional[tk.Frame]
        self.massacre_tab = Optional[tk.Frame]
        self.mining_tab = Optional[tk.Frame]
        
        self.display_missions_collect = False
        self.display_missions_courier = False
        self.display_missions_massacre = False
        self.display_missions_mining = False
    
    def rebuild_settings(self, config: Configuration):
        self.settings = GridUiSettings(config)
        self.update_ui()
        
    def set_frame(self, parent: ttk.Frame):
        # Check if it is 0 and set it to 2. Should probably look into this further at some point.
        cspan = parent.grid_size()[1]
        if cspan < 1:
            cspan = 2
        self.frame = tk.Frame(parent)
        self.frame.grid(column=0, columnspan=cspan, sticky=tk.W)        
        self.frame.bind("<<Refresh>>", lambda _: self.update_ui())
        self.set_tabs() # don't need to refresh this in update_ui as it's content is
        self.update_ui()
        return parent

    def update_ui(self):
        if self.frame is None:
            logger.warning("Frame was not yet set. UI was not updated.")
            return

        logger.info("Updating UI...")

        for child in self.frame.winfo_children():
            if child.widgetName != "ttk::notebook": # don't destroy the tabs
                child.destroy()

        if self.display_missions_collect:
            self.tabstrip.select(self.collect_tab)
        elif self.display_missions_courier:
            self.tabstrip.select(self.courier_tab)
        elif self.display_missions_massacre:
            self.tabstrip.select(self.massacre_tab)
        elif self.display_missions_mining:
            self.tabstrip.select(self.mining_tab)
        else:
            self.display_no_missions_data()            
            
        if self.version_info and self.version_info.status.lower() in ["outdated","unknown"]:
            self.display_version_info()
        
        theme.update(self.frame)

    def set_tabs(self):
        self.tabstrip = ttk.Notebook(self.frame)
        if self.settings.display_missions_collect:
            self.collect_tab = collect_ui.set_frame(self.tabstrip)  
            self.tabstrip.add(self.collect_tab, text="Collect [0]")
        if self.settings.display_missions_courier:
            self.courier_tab = courier_ui.set_frame(self.tabstrip)      
            self.tabstrip.add(self.courier_tab, text="Courier [0]")
        if self.settings.display_missions_massacre:
            self.massacre_tab = massacre_ui.set_frame(self.tabstrip)    
            self.tabstrip.add(self.massacre_tab, text="Massacre [0]")            
        if self.settings.display_missions_mining:
            self.mining_tab = mining_ui.set_frame(self.tabstrip)    
            self.tabstrip.add(self.mining_tab, text="Mining [0]")

        self.tabstrip.pack(expand=True, fill="both") 
        
    def display_no_missions_data(self):
        no_data_frame = tk.Frame(self.frame)     
        warning_label = tk.Label(no_data_frame, text="No active missions have been established.\nPlease re-log in the game to refresh.")
        warning_label.config(foreground="orange")
        warning_label.pack()
        no_data_frame.pack()
        theme.update(no_data_frame)
        
    def display_version_info(self) -> int:
        if self.version_info.status.lower() == "outdated":
            version_info_text = f"Version {self.version_info.current}<{self.version_info.latest} {self.version_info.status}"
            download_text = f"Download {self.version_info.latest}"
            download_url = self.version_info.latest_url
        elif self.version_info.status.lower() == "unknown":
            version_info_text=f"Version {self.version_info.current}, Latest Unknown"
            download_text = "View Releases"
            download_url = self.version_info.download_url
        else:
            version_info_text=f"Version {self.version_info.current}, Status {self.version_info.status}"
            download_text = "View Releases"
            download_url = self.version_info.download_url
        
        version_info_frame = tk.Frame(self.frame)
        update_label = tk.Label(version_info_frame, text=version_info_text)
        update_label.pack(side=tk.LEFT, fill=tk.X, padx=10)
        download_button = ttk.Button(version_info_frame, text=download_text, command=lambda: open_download_page(download_url))
        download_button.pack(side=tk.LEFT, fill=tk.X, padx=10)
        dismiss_button = ttk.Button(version_info_frame, text="Dismiss", command=self.notify_version_info_ignored)
        dismiss_button.pack(side=tk.LEFT, fill=tk.X, padx=10)
        version_info_frame.pack()
        theme.update(version_info_frame)

    def notify_version_info(self, version_info):
        self.version_info = version_info
        self.frame.event_generate("<<Refresh>>") # type: ignore

    def notify_version_info_ignored(self):
        self.version_info.status = "Ignored"
        self.update_ui()
        
    def notify_collect_mission_state_changed(self, data: dict[int, CollectMission]):
        if data is None or len(data) == 0:
            self.display_missions_collect = False
        else:
            self.display_missions_collect = True
        self.update_ui()
            
    def notify_courier_mission_state_changed(self, data: dict[int, CourierMission]):
        if data is None or len(data) == 0:
            self.display_missions_courier = False
        else:
            self.display_missions_courier = True
        self.update_ui()
            
    def notify_massacre_mission_state_changed(self, data: dict[int, MassacreMission]):
        if data is None or len(data) == 0:
            self.display_missions_massacre = False
        else:
            self.display_missions_massacre = True
        self.update_ui()
            
    def notify_mining_mission_state_changed(self, data: dict[int, MiningMission]):
        if data is None or len(data) == 0:
            self.display_missions_mining = False
        else:
            self.display_missions_mining = True
        self.update_ui()
        
main_ui = MainUI()
    
collect_mission_listeners.append(main_ui.notify_collect_mission_state_changed)
courier_mission_listeners.append(main_ui.notify_courier_mission_state_changed)
massacre_mission_listeners.append(main_ui.notify_massacre_mission_state_changed)
mining_mission_listeners.append(main_ui.notify_mining_mission_state_changed)