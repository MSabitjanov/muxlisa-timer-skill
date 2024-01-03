from mycroft import MycroftSkill, intent_file_handler


class MuxlisaTimer(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('timer.muxlisa.intent')
    def handle_timer_muxlisa(self, message):
        self.speak_dialog('timer.muxlisa')


def create_skill():
    return MuxlisaTimer()

