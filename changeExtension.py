import os
from pathlib import Path

extensions = ['PNG']

path = os.path.abspath(r"D:/Computing/Python/Chess/Images")

for f in os.listdir(path):
    p = Path(f)
    p.rename(p.with_suffix('.jpg'))

self.define_moves()
        valid = False
        for i in self.moves:
            if i[0]+self.pos[0] >= 0 and i[0]+self.pos[0] < 8 and i[1]+self.pos[1] >= 0 and i[1]+self.pos[1] < 8:
                for j in board:
                    check_pos = j.get_pos()
                    if i[0] + self.pos[0] == check_pos[0] and i[1] + self.pos[1] == check_pos[1]:
                        if j.get_color == None:
                            self.valid_moves.append([self.pos[0] + i[0], self.pos[1] + i[1]])
        for i in self.check:
            for j in board:
                check_pos = j.get_pos()
                if i[0]+self.pos[0] == check_pos[0] and i[1]+self.pos[1] == check_pos[1]:
                    self.valid_moves.append([self.pos[0] + i[0], self.pos[1] + i[1]])