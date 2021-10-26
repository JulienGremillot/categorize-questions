from .views import app
import enum

class Gender(enum.Enum):
    female = 0
    male = 1
    other = 2
    undefined = 3
