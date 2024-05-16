class DrawingData:
    '''data class for drawing data'''
    def __init__(self, img, title, player_name):
        self.image = img
        self.title = title
        self.player_name = player_name

    def get_image(self):
        return self.image
    
    def get_title(self):
        return self.title
    
    def get_player_name(self):
        return self.player_name