import os
from os.path import basename, dirname
from pathlib import Path
from helpers.logger_factory import logger
from typing import Callable, Optional
from config import config
import tkinter as tk
from tkinter import ttk
from ttkHyperlinkLabel import HyperlinkLabel
import myNotebook as nb

plugin_name = basename(Path(dirname(__file__)).parent)

class Configuration:

    def __init__(self, plugin_name: str):
       self.plugin_name = plugin_name

    @property
    def display_missions_collect(self):
        return config.get_bool(f"{self.plugin_name}.display_missions_collect", default=True)
    @display_missions_collect.setter
    def display_missions_collect(self, value: bool):
        config.set(f"{self.plugin_name}.display_missions_collect", value)
        
    @property
    def display_missions_courier(self):
        return config.get_bool(f"{self.plugin_name}.display_missions_courier", default=True)
    @display_missions_courier.setter
    def display_missions_courier(self, value: bool):
        config.set(f"{self.plugin_name}.display_missions_courier", value)
        
    @property
    def display_missions_massacre(self):
        return config.get_bool(f"{self.plugin_name}.display_missions_massacre", default=True)
    @display_missions_massacre.setter
    def display_missions_massacre(self, value: bool):
        config.set(f"{self.plugin_name}.display_missions_massacre", value)
        
    @property
    def display_missions_mining(self):
        return config.get_bool(f"{self.plugin_name}.display_missions_mining", default=True)
    @display_missions_mining.setter
    def display_missions_mining(self, value: bool):
        config.set(f"{self.plugin_name}.display_missions_mining", value)
        
    @property
    def display_row_total(self):
        return config.get_bool(f"{self.plugin_name}.display_row_total", default=True)
    @display_row_total.setter
    def display_row_total(self, value: bool):
        config.set(f"{self.plugin_name}.display_row_total", value)

    @property
    def display_row_stats(self):
        return config.get_bool(f"{self.plugin_name}.display_row_stats", default=True)
    @display_row_stats.setter
    def display_row_stats(self, value: bool):
        config.set(f"{self.plugin_name}.display_row_stats", value)

    @property
    def version_check_enabled(self):
        return config.get_bool(f"{self.plugin_name}.version_check_enabled", default=True)
    @version_check_enabled.setter
    def version_check_enabled(self, value: bool):
        config.set(f"{self.plugin_name}.version_check_enabled", value)

    @property
    def debug_mode_enabled(self):
        return config.get_bool(f"{self.plugin_name}.debug_mode_enabled", default=False)
    @debug_mode_enabled.setter
    def debug_mode_enabled(self, value: bool):
        config.set(f"{self.plugin_name}.debug_mode_enabled", value)
        
    @property
    def overlay_enabled(self):
        return config.get_bool(f"{self.plugin_name}.overlay_enabled", default=False)
    @overlay_enabled.setter
    def overlay_enabled(self, value: bool):
        config.set(f"{self.plugin_name}.overlay_enabled", value)
        
    @property
    def overlay_ttl(self):
        return config.get_int(f"{self.plugin_name}.overlay_ttl", default=5)
    @overlay_ttl.setter
    def overlay_ttl(self, value: int):
        config.set(f"{self.plugin_name}.process_journal_weeks", value)
        
    @property
    def process_journal_weeks(self):
        return config.get_int(f"{self.plugin_name}.process_journal_weeks", default=2)
    @process_journal_weeks.setter
    def process_journal_weeks(self, value: int):
        config.set(f"{self.plugin_name}.process_journal_weeks", value)
        
class SettingsUI:

    def __init__(self, plugin_name: str):
       self.plugin_name = plugin_name
       self.configuration_listeners: list[Callable[[Configuration], None]] = []
       self.setting_changes: dict[str, tk.Variable] = {}

    def notify_changed(self):
        keys = self.setting_changes.keys()

        if "display_missions_collect" in keys:
            configuration.display_missions_collect = self.setting_changes["display_missions_collect"].get()
        if "display_missions_courier" in keys:
            configuration.display_missions_courier = self.setting_changes["display_missions_courier"].get()
        if "display_missions_massacre" in keys:
            configuration.display_missions_massacre = self.setting_changes["display_missions_massacre"].get()
        if "display_missions_mining" in keys:
            configuration.display_missions_mining = self.setting_changes["display_missions_mining"].get()            
        if "display_row_total" in keys:
            configuration.display_row_total = self.setting_changes["display_row_total"].get()
        if "display_row_stats" in keys:
            configuration.display_row_stats = self.setting_changes["display_row_stats"].get()
        if "version_check_enabled" in keys:
            configuration.version_check_enabled = self.setting_changes["version_check_enabled"].get()
        if "debug_mode_enabled" in keys:
            configuration.debug_mode_enabled = self.setting_changes["debug_mode_enabled"].get()            
        if "overlay_enabled" in keys:
            configuration.overlay_enabled = self.setting_changes["overlay_enabled"].get()
        if "overlay_ttl" in keys:
            configuration.overlay_ttl = self.setting_changes['overlay_ttl'].get()
        if "process_journal_weeks" in keys:
            configuration.process_journal_weeks = self.setting_changes["process_journal_weeks"].get()
            
        for listener in self.configuration_listeners:
            listener(configuration)

    def display_settings(self, root: nb.Notebook) -> tk.Frame:
        checkbox_offset = 20
        title_offset = 10

        frame = nb.Frame(root) #type: ignore
        frame.columnconfigure(1, weight=1)
        self.setting_changes.clear()
        self.setting_changes["display_missions_collect"] = tk.IntVar(value=configuration.display_missions_collect)
        self.setting_changes["display_missions_courier"] = tk.IntVar(value=configuration.display_missions_courier)
        self.setting_changes["display_missions_massacre"] = tk.IntVar(value=configuration.display_missions_massacre)
        self.setting_changes["display_missions_mining"] = tk.IntVar(value=configuration.display_missions_mining)
        self.setting_changes["display_row_total"] = tk.IntVar(value=configuration.display_row_total)
        self.setting_changes["display_row_stats"] = tk.IntVar(value=configuration.display_row_stats) 
        self.setting_changes["version_check_enabled"] = tk.IntVar(value=configuration.version_check_enabled)
        self.setting_changes["debug_mode_enabled"] = tk.IntVar(value=configuration.debug_mode_enabled)
        self.setting_changes["overlay_enabled"] = tk.IntVar(value=configuration.overlay_enabled)    
        self.setting_changes["overlay_ttl"] = tk.IntVar(value=configuration.overlay_ttl)
        self.setting_changes["process_journal_weeks"] = tk.IntVar(value=configuration.process_journal_weeks)

        row_count = 0
        nb.Label(frame, text="Display Mission Tabs (Requires Restart)", pady=10).grid(row=row_count, sticky=tk.W, padx=title_offset)
        row_count += 1
        mission_tabs_checkboxes = [
            nb.Checkbutton(frame, text="Collect", variable=self.setting_changes["display_missions_collect"]),
            nb.Checkbutton(frame, text="Courier", variable=self.setting_changes["display_missions_courier"]),
            nb.Checkbutton(frame, text="Massacre", variable=self.setting_changes["display_missions_massacre"]),
            nb.Checkbutton(frame, text="Mining", variable=self.setting_changes["display_missions_mining"])
        ]
        for entry in mission_tabs_checkboxes:
            entry.grid(row=row_count, columnspan=2, padx=checkbox_offset, sticky=tk.W)
            row_count += 1
            
        nb.Label(frame, text="Display Mission Rows", pady=10).grid(row=row_count, sticky=tk.W, padx=title_offset)
        row_count += 1
        mission_rows_checkboxes = [
            nb.Checkbutton(frame, text="Total", variable=self.setting_changes["display_row_total"]),
            nb.Checkbutton(frame, text="Stats", variable=self.setting_changes["display_row_stats"])
        ]
        for entry in mission_rows_checkboxes:
            entry.grid(row=row_count, columnspan=2, padx=checkbox_offset, sticky=tk.W)
            row_count += 1
         
        nb.Label(frame, text="Misc Settings (Requires Restart)", pady=10).grid(row=row_count, sticky=tk.W, padx=title_offset)
        row_count += 1
    
        nb.Checkbutton(frame, text="Version Check (At Startup)", variable=self.setting_changes["version_check_enabled"])\
            .grid(row=row_count, columnspan=2, sticky=tk.W, padx=checkbox_offset)
        row_count += 1

        nb.Checkbutton(frame, text="Debug Mode Enabled", variable=self.setting_changes["debug_mode_enabled"])\
            .grid(row=row_count, columnspan=2, sticky=tk.W, padx=checkbox_offset)    
        row_count += 1

        nb.Checkbutton(frame, text="Overlay Enabled", variable=self.setting_changes["overlay_enabled"])\
            .grid(row=row_count, columnspan=2, sticky=tk.W, padx=checkbox_offset)
        row_count += 1
   
        nb.Label(frame, text="Overlay TTL")\
            .grid(row=row_count, column=0, padx=checkbox_offset, sticky=tk.W)
        nb.Entry(frame, textvariable=self.setting_changes["overlay_ttl"])\
            .grid(row=row_count, column=1, sticky=tk.W)        
        row_count += 1
    
        nb.Label(frame, text="Process Journal Weeks")\
            .grid(row=row_count, column=0, padx=checkbox_offset, sticky=tk.W)
        nb.Entry(frame, textvariable=self.setting_changes["process_journal_weeks"])\
            .grid(row=row_count, column=1, sticky=tk.W)        
        row_count += 1
        
        nb.Label(frame, text="", pady=10).grid(row=row_count)     

        return frame

settings_ui = SettingsUI(plugin_name)
configuration = Configuration(plugin_name)