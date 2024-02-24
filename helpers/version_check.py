import os
import subprocess
import sys
import threading
from requests import get
from helpers.logger_factory import logger
from pathlib import Path
from typing import Callable

_version_url = "https://raw.githubusercontent.com/kaivalagi/EDMC-Missions/main/version"
_download_url = "https://github.com/kaivalagi/EDMC-Missions/releases"

class VersionInfo:
    def __init__(self, current: str, latest: str, status: str):
        self.current = current
        self.latest = latest
        self.status = status
        self.download_url = _download_url
        self.latest_url = f"{_download_url}/tag/{latest}"
        
def get_version_info(callback: Callable[[VersionInfo], None]) -> None:
    try:
        version_info = VersionInfo("?", "?", "unknown")
        
        current_version = __get_current_version_string()
        
        latest_version_response = get(_version_url)
        if latest_version_response.status_code != 200:
            version_info = VersionInfo(current_version, "?", "Unknown")
            logger.warning("Failed to get Version from Remote. Ignoring...")
        else:                        
            latest_version = latest_version_response.text            

            version_info = VersionInfo(current_version, latest_version, "Latest")
            
            current_version_split = list(map(lambda x: int(x), current_version.split(".")))
            latest_version_split = list(map(lambda x: int(x), latest_version.split(".")))        

            longer_len = max([len(current_version_split), len(latest_version_split)])

            current_delta = longer_len - len(current_version_split)
            latest_delta = longer_len - len(latest_version_split)
            while current_delta > 0:
                current_version_split.append(0)
                current_delta -= 1
            while latest_delta > 0:
                latest_version_split.append(0)
                latest_delta -= 1

            for i in range(longer_len):
                if latest_version_split[i] > current_version_split[i]:
                    version_info = VersionInfo(current_version, latest_version, "Outdated")
                    break
                if latest_version_split[i] < current_version_split[i]:
                    break
            
    except IOError:
        logger.warning("Failed to get Version from Remote. Ignoring...")

    callback(version_info)

def __get_current_version_string():
    version_file = Path(__file__).parent.with_name("version")
    with version_file.open("r", encoding="utf8") as file:
        current_version = str(file.read())
        return current_version

def get_version_info_worker(cb: Callable[[VersionInfo], None]) -> threading.Thread:
    thread = threading.Thread(target=get_version_info, args=[cb])
    thread.name = "EDMC-Missions Version Check"
    thread.daemon = True

    return thread

def open_download_page(download_url: str):
    platform = sys.platform
        
    if platform == "darwin":
        subprocess.Popen(["open", download_url])
    elif platform == "win32":
        os.startfile(download_url) # type: ignore
    else:
        try:
            subprocess.Popen(["xdg-open", download_url])
        except OSError:
            logger.error("Failed to open URL")
