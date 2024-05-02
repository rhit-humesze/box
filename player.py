class Player:
    def __init__(self, socket):
        self.socket = socket
        self.name = "Default Name"
        # default image path
        self.avatar = "default.png"

    def set_name(self, name):
        self.name = name

    def set_avatar_path(self, avatar):
        self.avatar = avatar

    def get_name(self):
        return self.name

    def get_avatar_path(self):
        return self.avatar
