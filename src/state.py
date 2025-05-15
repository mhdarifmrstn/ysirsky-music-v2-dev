from telegram import Audio
from dataclasses import dataclass
from typing import Dict
import io
import time


@dataclass
class UserState:
    user_id: int
    audio: Audio
    audio_path: str
    thumb_buf: io.BytesIO | None = None
    task: str | None = None
    title: str | None = None
    performer: str | None = None
    file_name: str | None = None
    msgs_to_delete: list = None


class StateManager:
    def __init__(self):
        self._states: Dict[int, UserState] = {}
        self.start_time: float = time.time()

    def get_state(self, user_id: int):
        return self._states.get(user_id, None)

    def set_state(self, user_id: int, new_state: UserState):
        self._states[user_id] = new_state

    def clear_state(self, user_id: int):
        self._states.pop(user_id, None)

    def set_task(self, user_id: int, new_task: str):
        user_state = self.get_state(user_id)

        if user_state is None:
            return
        user_state.task = new_task
        self._states[user_id] = user_state

    def set_msgs_to_delete(self, user_id: int, msgs_to_delete: list):
        user_state = self.get_state(user_id)

        if user_state is None:
            return
        user_state.msgs_to_delete = msgs_to_delete
        self._states[user_id] = user_state


state = StateManager()
