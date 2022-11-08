from fastapi import APIRouter, Depends
from pymongo import MongoClient
from application_properties import ApplicationProperties
from routers.user_auth import get_user_from_token

from models.contributions import Attribute
from models.contributions import Skill
from models.contributions import AdvantageDisadvantage

# Create a router instance
router = APIRouter(
    prefix='/contribute',
    tags=['contribute']
)

# Import properties class
application_settings = ApplicationProperties()

application_settings.connectToDB()

# Get all collections to avoid using the getCollection function every time something is needed

#############  CHARACTER PROPERTIES  ###############
attribute_collection = application_settings.getCollection('game_properties_attributes')
skills_collection = application_settings.getCollection('game_properties_skills')
advantages_collection = application_settings.getCollection('game_properties_advantages')
disadvantages_collection = application_settings.getCollection('game_properties_disadvantages')

@router.post('/modify_attribute')
async def modify_attribute_on_database(attribute: Attribute):
    attribute_dict = attribute.dict()
    attribute_dict['_id'] = attribute_dict.pop('id')
    if(attribute_collection.find_one({'_id':attribute.id}) == None):
        attribute_collection.insert_one(attribute_dict)
    else:
        attribute_collection.replace_one({'_id':attribute.id},attribute_dict)
    return attribute_collection.find_one({'_id':attribute.id})

@router.get('/get_attribute')
async def get_attribute_from_database(id: str):
    if(id == '*'):
        return list(attribute_collection.find())
    else:
        return attribute_collection.find_one({'_id':id})



@router.post('/modify_skill')
async def modify_skill_on_database(skill: Skill):
    skill_dict = skill.dict()
    skill_dict['_id'] = skill_dict.pop('id')
    skill_dict['specialties'] = skill_dict['specialties'].split(', ')
    if(skills_collection.find_one({'_id':skill.id}) == None):
        skills_collection.insert_one(skill_dict)
    else:
        skills_collection.replace_one({'_id':skill.id},skill_dict)
    return skills_collection.find_one({'_id':skill.id})

@router.get('/get_skill')
async def get_skill_from_database(id: str):
    if(id == '*'):
        return list(skills_collection.find())
    else:
        return skills_collection.find_one({'_id':id})




@router.post('/modify_advantage')
async def modify_advantage_on_database(advantage: AdvantageDisadvantage):
    advantage_dict = advantage.dict()
    advantage_dict['_id'] = advantage_dict.pop('id')
    if(advantages_collection.find_one({'_id':advantage.id}) == None):
        advantages_collection.insert_one(advantage_dict)
    else:
        advantages_collection.replace_one({'_id':advantage.id},advantage_dict)
    return advantages_collection.find_one({'_id':advantage.id})

@router.get('/get_advantage')
async def get_advantage_from_database(id: str):
    if(id == '*'):
        return list(advantages_collection.find())
    else:
        return advantages_collection.find_one({'_id':id})



@router.post('/modify_disadvantage')
async def modify_disadvantage_on_database(disadvantage: AdvantageDisadvantage):
    disadvantage_dict = disadvantage.dict()
    disadvantage_dict['_id'] = disadvantage_dict.pop('id')
    if(disadvantages_collection.find_one({'_id':disadvantage.id}) == None):
        disadvantages_collection.insert_one(disadvantage_dict)
    else:
        disadvantages_collection.replace_one({'_id':disadvantage.id},disadvantage_dict)
    return disadvantages_collection.find_one({'_id':disadvantage.id})

@router.get('/get_disadvantage')
async def get_disadvantage_from_database(id: str):
    if(id == '*'):
        return list(disadvantages_collection.find())
    else:
        return disadvantages_collection.find_one({'_id':id})



#############  AWAKENED  ###############
spells_collection = application_settings.getCollection('game_properties_spells')
rituals_collection = application_settings.getCollection('game_properties_rituals')
adept_powers_collection = application_settings.getCollection('game_properties_adept_powers')
komplex_forms_collection = application_settings.getCollection('game_properties_komplex_forms')

############# ITEMS #############
equipment_collection = application_settings.getCollection('game_properties_equipment')
weapons_collection = application_settings.getCollection('game_properties_weapons')
bodyware_collection = application_settings.getCollection('game_properties_bodyware')
vehicles_collection = application_settings.getCollection('game_properties_vehicles')