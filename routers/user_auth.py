from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from urllib.parse import quote_plus
import jwt
import bcrypt
from application_properties import ApplicationProperties
from models import user_auth_models

# Create a router instance
router = APIRouter(
    prefix='/user_auth',
    tags=['user_auth']
)

# Import properties class
application_settings = ApplicationProperties()

# Instantiate a schema for the OAuth2
oauth_scheme = OAuth2PasswordBearer(tokenUrl='user_auth/token')

# Get tester application collection
tester_account_applications_collection = application_settings.getCollection("tester_account_applications")

# Get admin application collection
admin_account_applications_collection = application_settings.getCollection("admin_account_applications")

# Get created users collection, these are the users that were approved
users_collection = application_settings.getCollection("users")



@router.post('/token')
async def login_for_token(form_data:OAuth2PasswordRequestForm = Depends()):
    # Search the database for a user with the given username (usernames are unique identifieres within the database)
    user = users_collection.find_one({'username':form_data.username},{'_id':False})
    if not user:
        return {'error':'User not found.'}
    else:
        # Compare the saved hash and the recieved password
        if not bcrypt.checkpw(form_data.password.encode(),user['password_hash'].encode()):
            return {'error':'Incorrect password.'}
        else:
            # If the data checks out generate an Access Token
            data = {}
            data['sub'] = user['username']
            data['exp'] = datetime.utcnow() + timedelta(minutes=30)
            encoded_jwt = jwt.encode(data, application_settings.JWT_ENCRYPTION_KEY, algorithm=application_settings.JWT_ALGORITHM)
            return {'access_token': encoded_jwt,'token_type': 'bearer'}



# Aquire user by decoding a token
@router.get('/get_user_via_token')
async def get_user_from_token(token:str = Depends(oauth_scheme)):
    # Attempt to decode a token by using the JWT key
    try:
        payload = jwt.decode(token, application_settings.JWT_ENCRYPTION_KEY, algorithms=[application_settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return {'error':'The token cannot be decoded.'}
    # React if the decoding failed
    except jwt.DecodeError:
        return {'error':'Could not validate credentials.'}
    user = users_collection.find_one({'username':username},{'_id':False})
    if user is None:
        return {'error': 'No user associated with that token.'}
    return {
        'username':user['username'],
        'priviledge_level' : user['priviledge_level']
    }



# Check if email is available
@router.get('/check_email_availability/{email}')
async def check_email_availability(email:str):
    collection_availability = [
        (tester_account_applications_collection.find_one({'email': email}) == None),
        (admin_account_applications_collection.find_one({'email': email}) == None),
        (users_collection.find_one({'email': email}) == None)
    ]
    for a in collection_availability:
        if a == False:
            return {"result" : False}
    return {"result" : True}



# Check if username is available
@router.get('/check_username_availability/{username}')
async def check_username_availability(username:str):
    collection_availability = [
        (tester_account_applications_collection.find_one({'username': username}) == None),
        (admin_account_applications_collection.find_one({'username': username}) == None),
        (users_collection.find_one({'username': username}) == None)
    ]
    for a in collection_availability:
        if a == False:
            return {"result" : False}
    return {"result" : True}



# Check if password is valid
@router.get("/confirm_password_validity/{password}")
async def checkPasswordAvailability(password:str):
    pattern = re.compile("(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})")
    if pattern.match(password) != None : return {"result" : True}
    return {"result" : False}



# Save an account application in the database
# this application will be approved or denied causing the entire document to be copied over to the users collection
@router.post('/account_application_tester')
async def sign_up(user_data:user_auth_models.Tester_Application):
    
    # Complete all checks to create account; Meant to prevent API abuse
    # check email availability
    collection_availability = [
        (tester_account_applications_collection.find_one({'email': user_data.email}) == None),
        (admin_account_applications_collection.find_one({'email': user_data.email}) == None),
        (users_collection.find_one({'email': user_data.email}) == None)
    ]
    for a in collection_availability:
        if a == False:
            raise HTTPException(status_code=400,detail="E-Mail already in use!")

    # check username availability
    collection_availability = [
        (tester_account_applications_collection.find_one({'username': user_data.username}) == None),
        (admin_account_applications_collection.find_one({'username': user_data.username}) == None),
        (users_collection.find_one({'username': user_data.username}) == None)
    ]
    for a in collection_availability:
        if a == False:
            raise HTTPException(status_code=400,detail="Username already in use!")

    # check password validity
    pattern = re.compile("(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})")
    if pattern.match(user_data.password) == None: 
        raise HTTPException(status_code=400,detail="Password is invalid!")

    # Hash password and create account dict
    hashedPWD = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt(rounds=14))
    userProfile = {
        'username':user_data.username,
        'email':user_data.email,
        'password_hash':hashedPWD.decode(),
        'application_content':user_data.application_content,
        'account_type':{
            "priv_level" : 5,
            "account_type" : "tester"
        }
    }
    # insert into database
    tester_account_applications_collection.insert_one(userProfile)
    return {"result" : True}

