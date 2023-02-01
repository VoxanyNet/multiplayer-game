from pygame.math import Vector2

class Vector(Vector2):
    def slow(self, delta_x = 0, delta_y = 0): 
        
        # subtracts if positive, adds if negative
        if self.x < 0:
            if self.x + delta_x > 0:
                self.x = 0
            else:
                self.x += delta_x
        elif self.x > 0:
            if self.x - delta_x < 0:
                self.x = 0
            else:
                self.x -= delta_x

        if self.y < 0:
            if self.y + delta_y > 0:
                self.y = 0
            else:
                self.y += delta_y
        elif self.y > 0:
            if self.y - delta_y < 0:
                self.y = 0
            else:
                self.y -= delta_y