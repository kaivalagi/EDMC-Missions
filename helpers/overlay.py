import json
import edmcoverlay
from helpers.logger_factory import logger
import ui.settings
from ui.settings import Configuration, configuration, settings_ui
import asyncio

class Overlay:
    
    def __init__(self):
        self.config = configuration
        self.overlay = edmcoverlay.Overlay()
        
    def send_lines(self, id: str, lines: list[str], color = "green", ):
        if self.config.overlay_enabled:
            line_index = 0
            
            try:
                for line in lines:
                    
                    task = asyncio.create_task(
                        self.overlay.send_message(f'{id}-{line_index}',line,color,0,line_index, ttl=self.config.overlay_ttl))
                    background_tasks.add(task)
                    task.add_done_callback(background_tasks.discard)
                    
                    line_index += 1
            except Exception as ex:
                logger.error("Issues with overlay", exc_info=ex)
    
overlay = Overlay()
background_tasks = set()
