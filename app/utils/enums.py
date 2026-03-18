from enum import Enum

class RoleName(str, Enum):
    coach = "coach"
    mentee = "mentee"
    dreamer = "dreamer"
    system = "system"

class WeightUnit(str, Enum):
    kg = "kg"
    lb = "lb"

class LengthUnit(str, Enum):
    cm = "cm"
    in_ = "in"

class Gender(str, Enum):
    male = "Male"
    female = "Female"
    empty = ""

class ExerciseFrequency(str, Enum):
    one = "1 day per week"
    two = "2 days per week"
    three = "3 days per week"
    four = "4 days per week"
    five = "5 days per week"
    six = "6 days per week"
    seven = "7 days per week"

class ActivityLevel(str, Enum):
    active = "Active"
    sedentary = "Sedentary"

class Suplement(str, Enum):
    protein_powder = "Protein Powder"
    creatine = "Creatine"
    bcaas = "BCAAs"
    pre_workout = "Pre-workout"
    multivitamins = "Multivitamins"
    omega3 = "Omega-3"

class ObjectiveType(str, Enum):
    bulking = "bulking"
    cutting = "cutting"
    maintenance = "maintenance"