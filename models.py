class DrawingData:
    '''data class for drawing data'''
    def __init__(self, img, title, player_name):
        self._image = img
        self._title = title
        self._player_name = player_name

    @property
    def image(self):
        return self._image
    
    @property
    def title(self):
        return self._title
    
    @property
    def player_name(self):
        return self._player_name