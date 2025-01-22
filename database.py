from config import SYSTEM_DIR
import os


class Database:
    def __init__(self, filename):
        self.file = os.path.join(SYSTEM_DIR, filename)
        with open(self.file) as file:
            self.money = int(file.readline())

    def save(self):
        with open(self.file, "w") as file:
            file.write(str(self.money))