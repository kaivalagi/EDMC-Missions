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
    def display_total(self):
        return config.get_bool(f"{self.plugin_name}.display_total", default=True)
    @display_total.setter
    def display_total(self, value: bool):
        config.set(f"{self.plugin_name}.display_total", value)

    @property
    def display_stats(self):
        return config.get_bool(f"{self.plugin_name}.display_stats", default=True)
    @display_stats.setter
    def display_stats(self, value: bool):
        config.set(f"{self.plugin_name}.display_stats", value)
        
    @property
    def journal_weeks(self):
        return config.get_int(f"{self.plugin_name}.journal_weeks", default=2)
    @journal_weeks.setter
    def journal_weeks(self, value: int):
        config.set(f"{self.plugin_name}.journal_weeks", value)

    @property
    def check_updates(self):
        return config.get_bool(f"{self.plugin_name}.check_updates", default=False)
    @check_updates.setter
    def check_updates(self, value: bool):
        config.set(f"{self.plugin_name}.check_updates", value)

    @property
    def debug_mode(self):
        return config.get_bool(f"{self.plugin_name}.debug_mode", default=False)
    @debug_mode.setter
    def debug_mode(self, value: bool):
        config.set(f"{self.plugin_name}.debug_mode", value)
        
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
        config.set(f"{self.plugin_name}.journal_weeks", value)

class SettingsUI:

    def __init__(self, plugin_name: str):
       self.plugin_name = plugin_name
       self.configuration_listeners: list[Callable[[Configuration], None]] = []
       self.setting_changes: dict[str, tk.Variable] = {}

    def notify_changed(self):
        keys = self.setting_changes.keys()

        if "display_total" in keys:
            configuration.display_total = self.setting_changes["display_total"].get()
        if "display_stats" in keys:
            configuration.display_stats = self.setting_changes["display_stats"].get()
        if "journal_weeks" in keys:
            configuration.journal_weeks = self.setting_changes["journal_weeks"].get()
        if "check_updates" in keys:
            configuration.check_updates = self.setting_changes["check_updates"].get()
        if "debug_mode" in keys:
            configuration.debug_mode = self.setting_changes["debug_mode"].get()            
        if "overlay_enabled" in keys:
            configuration.overlay_enabled = self.setting_changes["overlay_enabled"].get()
        if "overlay_ttl" in keys:
            configuration.overlay_ttl = self.setting_changes['overlay_ttl'].get()

        for listener in self.configuration_listeners:
            listener(configuration)

    def display_settings(self, root: nb.Notebook) -> tk.Frame:
        checkbox_offset = 10
        title_offset = 20

        frame = nb.Frame(root) #type: ignore
        frame.columnconfigure(1, weight=1)
        self.setting_changes.clear()
        self.setting_changes["display_total"] = tk.IntVar(value=configuration.display_total)
        self.setting_changes["display_stats"] = tk.IntVar(value=configuration.display_stats) 
        self.setting_changes["journal_weeks"] = tk.IntVar(value=configuration.journal_weeks)
        self.setting_changes["check_updates"] = tk.IntVar(value=configuration.check_updates)
        self.setting_changes["debug_mode"] = tk.IntVar(value=configuration.debug_mode)
        self.setting_changes["overlay_enabled"] = tk.IntVar(value=configuration.overlay_enabled)    
        self.setting_changes["overlay_ttl"] = tk.IntVar(value=configuration.overlay_ttl)

        row_count = 0
        nb.Label(frame, text="General UI Settings", pady=10).grid(row=row_count, sticky=tk.W, padx=title_offset)
        row_count += 1
        general_ui_settings_checkboxes = [
            nb.Checkbutton(frame, text="Display Total", variable=self.setting_changes["display_total"]),
            nb.Checkbutton(frame, text="Display Stats", variable=self.setting_changes["display_stats"])
        ]
        for entry in general_ui_settings_checkboxes:
            entry.grid(row=row_count, columnspan=2, padx=checkbox_offset, sticky=tk.W)
            row_count += 1
         
        nb.Label(frame, text="Misc Settings (Require Restart)", pady=10).grid(row=row_count, sticky=tk.W, padx=title_offset)
        row_count += 1

        nb.Label(frame, text="Journal Weeks")\
            .grid(row=row_count, column=0, padx=checkbox_offset, sticky=tk.W)
        nb.Entry(frame, textvariable=self.setting_changes["journal_weeks"])\
            .grid(row=row_count, column=1, padx=checkbox_offset, sticky=tk.W)        
        row_count += 1
    
        nb.Checkbutton(frame, text="Check for Updates on Start", variable=self.setting_changes["check_updates"])\
            .grid(row=row_count, columnspan=2, sticky=tk.W, padx=checkbox_offset)
        row_count += 1

        nb.Checkbutton(frame, text="Debug Mode", variable=self.setting_changes["debug_mode"])\
            .grid(row=row_count, columnspan=2, sticky=tk.W, padx=checkbox_offset)    
        row_count += 1

        nb.Checkbutton(frame, text="Overlay Enabled", variable=self.setting_changes["overlay_enabled"])\
            .grid(row=row_count, columnspan=2, sticky=tk.W, padx=checkbox_offset)
        row_count += 1
   
        nb.Label(frame, text="Overlay TTL")\
            .grid(row=row_count, column=0, padx=checkbox_offset, sticky=tk.W)
        nb.Entry(frame, textvariable=self.setting_changes["overlay_ttl"])\
            .grid(row=row_count, column=1, padx=checkbox_offset, sticky=tk.W)        
        row_count += 1
    
        nb.Label(frame, text="", pady=10).grid(row=row_count)     

        return frame

settings_ui = SettingsUI(plugin_name)
configuration = Configuration(plugin_name)