from config import SYSTEM_DIR
import os


class Database:
    def __init__(self, filename):
        self.file = os.path.join(SYSTEM_DIR, filename)
        with open(self.file) as file:
            self.rating = list(map(int, file.readline().split()))
            self.money = int(file.readline())
            self.level = int(file.readline())

    def clear(self):
        self.rating, self.money, self.level = [], 0, 0

    def save(self):
        with open(self.file, "w") as file:
            file.write(" ".join(map(str, self.rating)))
            file.write(f"\n{self.money}\n{self.level}")
