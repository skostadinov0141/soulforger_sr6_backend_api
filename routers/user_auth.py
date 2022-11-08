from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
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

# Get collection using properties class function
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
            encoded_jwt = jwt.encode(data, application_settings.getJwtEncryptionKey(), algorithm=application_settings.JWT_ALGORITHM)
            return {'access_token': encoded_jwt,'token_type': 'bearer'}





# Aquire user by decoding a token
@router.get('/get_user_via_token')
async def get_user_from_token(token:str = Depends(oauth_scheme)):
    # Attempt to decode a token by using the JWT key
    try:
        payload = jwt.decode(token, application_settings.getJwtEncryptionKey(), algorithms=[application_settings.JWT_ALGORITHM])
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





# Create an account in the database so that the user can authorize themselves
@router.post('/sign_up')
async def sign_up(user_data:user_auth_models.Sign_Up):
    existingUser = users_collection.find_one({'username':user_data.username})
    if existingUser != None:
        return {'error':'A user with that username already exists.'}
    else:
        hashedPWD = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt(rounds=14))
        userProfile = {
            'username':user_data.username,
            'password_hash':hashedPWD.decode(),
            'display_name':user_data.display_name,
            'priviledge_level':0
        }
        admin_key = application_settings.getAdminKey()
        if(bcrypt.checkpw(user_data.admin_key.encode(), admin_key.encode())):
            userProfile['priviledge_level'] = 5
        users_collection.insert_one(userProfile)
        return users_collection.find_one({'username':user_data.username},{'_id':False})