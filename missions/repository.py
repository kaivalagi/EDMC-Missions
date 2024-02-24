from enum import Flag
from typing import Callable, Optional
from helpers.logger_factory import logger
from helpers.missions import populate_missions_bounty, populate_missions_cargodepot

# The listeners are stored as a Tuple of Activator and Callback.
# Callback: (mission as dict<mission_uuid, mission>) -> void
active_missions_changed_event_listeners: list[Callable[[dict[int, dict]], None]] = []
all_missions_changed_event_listeners: list[Callable[[dict[int, dict]], None]] = []

_active_uuids_init = False
_active_uuids: list[int] = []

class MissionRepoState(Flag):
    AWAITING_INIT = 0b00
    HAS_MISSION_DATA = 0b10
    HAS_MISSIONS_EVENT = 0b01
    INITIALIZED = 0b11

class MissionRepository:

    @property
    def state(self):
        return self._state

    @property
    def active_missions(self):
        return self._active_missions

    def __init__(self, mission_store: dict[str, dict[int, dict]], cmdr: Optional[str] = None):
        self._cmdr = cmdr
        self._state = MissionRepoState.AWAITING_INIT
        self._mission_store: dict[str, dict[int, dict]] = mission_store
        self._state |= MissionRepoState.HAS_MISSION_DATA
        self._active_missions: dict[int, dict] = {}
        global _active_uuids, _active_uuids_init
        if _active_uuids_init:
            self.notify_mission_active_uuids(_active_uuids, cmdr)

    def notify_mission_active_uuids(self, uuids: list[int], cmdr: str):
        self._cmdr = cmdr
        if cmdr is None:
            logger.error("Cmdr unknown! Aborting")
            return
        
        if self._state & MissionRepoState.HAS_MISSIONS_EVENT == 0:
            self._state |= MissionRepoState.HAS_MISSIONS_EVENT
        else:
            logger.warning("Mission UUIDs were passed even though the State is already initialized")
            pass

        self._active_missions = {}

        all_known_uuids = list(self._mission_store[cmdr].keys())
        for uuid in uuids:
            if uuid in all_known_uuids:
                self._active_missions[uuid] = self._mission_store[cmdr][uuid]
            else:
                logger.warning("A Mission could not be found in the Store even though the UUID is present")
                pass

        #  Emit an Event notifying that the pool of active missions has changed
        #  The listeners should be CMDR-agnostic. They just get the active mission list.
        for listener in active_missions_changed_event_listeners:
            listener(self._active_missions)

    def notify_mission_accepted(self, mission: dict, cmdr: str):
        logger.info(f"New Mission with ID {mission['MissionID']} has been accepted")
        self._mission_store[cmdr][mission["MissionID"]] = mission
        self._active_missions[mission["MissionID"]] = mission
        self.update_all_listeners()

    def notify_mission_cargo_delivered(self, mission: dict, cmdr: str):
        changed = populate_missions_cargodepot(mission, self._active_missions)
        if changed:            
            global active_missions_changed_event_listeners
            for listener in active_missions_changed_event_listeners:
                listener(self._active_missions)
            
    def notify_bounty_awarded(self, mission: dict, cmdr: str):
        changed = populate_missions_bounty(mission, self._active_missions)
        if changed:
            global active_missions_changed_event_listeners
            for listener in active_missions_changed_event_listeners:
                listener(self._active_missions)
            
    def notify_mission_finished(self, mission_uuid: int):
        logger.info(f"Mission {mission_uuid} removed")
        del self._active_missions[mission_uuid]
        global active_missions_changed_event_listeners
        for listener in active_missions_changed_event_listeners:
            listener(self._active_missions)

    def update_all_listeners(self):
        global active_missions_changed_event_listeners, all_missions_changed_event_listeners
        for listener in active_missions_changed_event_listeners:
            listener(self._active_missions)
        for listener in all_missions_changed_event_listeners:
            listener(self._mission_store[self._cmdr])


mission_repository: Optional[MissionRepository] = None


def initialise_repository(missions: dict[str, dict[int, dict]]):
    global mission_repository
    mission_repository = MissionRepository(missions)

def set_active_uuids(uuids: list[int], cmdr: str):
    global _active_uuids, _active_uuids_init
    _active_uuids.clear()
    _active_uuids.extend(uuids)
    _active_uuids_init = True

    if mission_repository is not None:
        mission_repository.notify_mission_active_uuids(_active_uuids, cmdr)

