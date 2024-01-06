from datetime import timedelta
from pathlib import Path

from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import  match_one
from mycroft.util.time import now_local
from mycroft.util.audio_utils import play_wav
from mycroft.messagebus.message import Message

import threading
from datetime import timedelta
import time

class MuxlisaTimer(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.time_durations = {
            "soniyaga": "seconds",
            "daqiqaga": "minutes",
            "soatga": "hours",
        }
        self.event = threading.Event()
        self.sound_file_path = Path(__file__).parent.joinpath("sounds", "two-beep.wav")

    def initialize(self):
        self.register_entity_file('duration.entity')

    @intent_file_handler('timer.muxlisa.intent')
    def handle_timer_muxlisa(self, message):
        """
            time_measure: soniya, daqiqa, soat
            duration: 2, 3, ...
        """
        duration = self.extract_duration(message)
        timer = threading.Thread(target=self.start_timer, args=(duration,))
        timer.start()

    def start_timer(self, duration):
        last_timer_expire_dialog_time = now_local()
        self.expire_time = now_local() + duration
        self.speak_dialog('timer.start')
        while not self.event.is_set():  # Continue until stop is called
            if now_local() > self.expire_time:
                play_wav(self.sound_file_path)

                if now_local() - last_timer_expire_dialog_time > timedelta(seconds=5):
                    self.speak_dialog('timer.done')
                    last_timer_expire_dialog_time = now_local()

            time.sleep(1)

    def extract_duration(self, message) -> timedelta:
        """Extract duration from message"""
        time_measure = message.data.get('time_measure')
        duration = message.data.get('duration')

        measure, confidence = match_one(time_measure, self.time_durations)
        if confidence < 0.5:
            self.speak_dialog('measure.error')
            return

        converted_duration = self._convert_duration_to_int(duration)
        return timedelta(**{measure: converted_duration})

    def _convert_duration_to_int(self, duration):
        """Convert duration to int"""
        try:
            return int(duration)
        except ValueError:
            self.log.error(f"duration: {duration}")

    def stop(self):
        self.event.set()
        return True

    @intent_file_handler('timer.stop.intent')
    def handle_timer_stop(self, message):
        self.speak_dialog('timer.stop')
        self.stop()

def create_skill():
    return MuxlisaTimer()
