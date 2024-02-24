import tkinter as tk
from tkinter import ttk
from typing import Optional

from ui.massacre import massacre_ui
from ui.mining import mining_ui
from ui.collect import collect_ui
from ui.courier import courier_ui

from ui.settings import Configuration, configuration, settings_ui
from helpers.logger_factory import logger
from theme import theme
from helpers.version_check import open_download_page, VersionInfo

from missions.state import mining_mission_listeners, MiningMission

class GridUiSettings:
    def __init__(self, config: Configuration):
        self.display_total = config.display_total
        self.display_stats = config.display_stats
        self.debug_mode = config.debug_mode
        
class MainUI:
    def __init__(self):
        self.frame: Optional[tk.Frame] = None
        self.version_info: Optional[VersionInfo] = None
        self.no_missions_data = True
        self.settings: GridUiSettings = GridUiSettings(configuration)
        settings_ui.configuration_listeners.append(self.rebuild_settings)
        
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

        if self.no_missions_data:
            self.display_no_missions_data()
            
        if self.version_info and self.version_info.status.lower() in ["outdated","unknown"]:
            self.display_version_info()
        
        theme.update(self.frame)

    def set_tabs(self):
        tabstrip = ttk.Notebook(self.frame)    
        mining_tab = mining_ui.set_frame(tabstrip)    
        tabstrip.add(mining_tab, text="Mining [0]")
        collect_tab = collect_ui.set_frame(tabstrip)  
        tabstrip.add(collect_tab, text="Collect [0]")
        massacre_tab = massacre_ui.set_frame(tabstrip)    
        tabstrip.add(massacre_tab, text="Massacre [0]")
        courier_tab = courier_ui.set_frame(tabstrip)      
        tabstrip.add(courier_tab, text="Courier [0]")
        tabstrip.pack(expand=True, fill="both") 
        
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
        
    def notify_mission_state_changed(self, data):
        if data is not None:
            self.no_missions_data = False
            self.update_ui()
        
main_ui = MainUI()

def handle_mission_state_changed(data: any):
    main_ui.notify_mission_state_changed(data)

mining_mission_listeners.append(handle_mission_state_changed)
