# Import reqired modules to create a module
from pydantic import BaseModel

class Attribute(BaseModel):
    id:str
    name:str
    category:str
    description:str

class Skill(BaseModel):
    id:str
    name:str
    specialties:str
    untrained:bool
    primary_attribute:str
    secondary_attribute:dict
    description:str

class AdvantageDisadvantage(BaseModel):
    id:str
    name:str
    description:str
    karma_cost:int
    effect:str