PLAYER_ONE = 0
PLAYER_TWO = 1

class Player:
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id
    
    def get_color(self):
        if self.id == PLAYER_ONE:
            return (255, 0, 0)
        else:
            return (255, 255, 0)

    def get_name(self):
        if (self.id==PLAYER_ONE):
            return f"Dr House "
        else:
            return f"Dr Wilson "