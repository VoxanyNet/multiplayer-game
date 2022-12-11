from pygame import Rect

class Test:
    def __init__(self):
        self.rect = Rect(0,0,0,0)

obama = Test()

print(obama.rect)

for attribute in obama.__dict__.values():
    if type(attribute) is Rect:
        attribute.x = 200

print(obama.rect)
