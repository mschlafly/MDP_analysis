

class position:
    def __init__(self, x_pos, y_pos):
        self.x = x_pos
        self.y = y_pos

# Checks whether the person can take the simulated turn. Returns False if the
# person would fall off the world
def check_turn(player_loc, dir):
    if player_loc.x<3 and dir==3:
        return False
    elif player_loc.x>28 and dir==1:
        return False
    elif player_loc.y<3 and dir==2:
        return False
    elif player_loc.x>28 and dir==0:
        return False
    else:
        return True
