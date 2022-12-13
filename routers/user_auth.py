from datetime import datetime, timedelta
import re

from bson import ObjectId
import bson
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from urllib.parse import quote_plus
import jwt
import bcrypt
from application_properties import ApplicationProperties
from models import user_auth_models
from urllib.parse import unquote

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
tester_account_applications_collection = application_settings.getCollection('tester_account_applications')

# Get admin application collection
admin_account_applications_collection = application_settings.getCollection('admin_account_applications')

# Get created users collection, these are the users that were approved
users_collection = application_settings.getCollection('users')



@router.post('/token')
async def login_for_token(form_data:OAuth2PasswordRequestForm = Depends()):
    # Search the database for a user with the given username (usernames are unique identifieres within the database)
    user = users_collection.find_one({'username':form_data.username})
    if not user:
        return HTTPException(status_code=404, detail='No such user.')
    else:
        # Compare the saved hash and the recieved password
        if not bcrypt.checkpw(form_data.password.encode(),user['password_hash'].encode()):
            raise HTTPException(status_code=400, detail='Password is incorrect.')
        else:
            # If the data checks out generate an Access Token
            data = {}
            data['sub'] = str(str(user['_id']))
            data['exp'] = datetime.utcnow() + timedelta(hours=2)
            data['priv_level'] = user['account_type']['priv_level']
            encoded_jwt = jwt.encode(data, application_settings.JWT_ENCRYPTION_KEY, algorithm=application_settings.JWT_ALGORITHM)
            return {'access_token': encoded_jwt,'token_type': 'bearer'}



# Aquire user by decoding a token
@router.get('/get_user_via_token')
async def get_user_from_token(token:str = Depends(oauth_scheme)):
    
    # Attempt to decode a token by using the JWT key
    try:
        payload = jwt.decode(token, application_settings.JWT_ENCRYPTION_KEY, algorithms=[application_settings.JWT_ALGORITHM])
        # Attempt to generate ObjectId
        try:
            oid: ObjectId = ObjectId(payload.get('sub'))
        except bson.errors.InvalidId:
            raise HTTPException(status_code=400, detail='Invalid user ID.')
    
    # React if the decoding failed
    except jwt.DecodeError:
        raise HTTPException(status_code=400, detail='Token is invalid.')
    
    # React if the token has expired
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail='Token has expired.')
    
    # Get user document from DB
    user = users_collection.find_one({'_id':oid})
    # react if user does not exist
    if user is None:
        raise HTTPException(status_code=404, detail='No such user account.')
    return {
        'username':user['username'],
        'priv_level' : user['account_type']['priv_level']
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
            return {'result' : False}
    return {'result' : True}



# Check if username is available
@router.get('/check_username_availability/{username}')
async def check_username_availability(username:str):
    res = {
        'result': True,
        'detail': []
    }
    if username == '': raise HTTPException(status_code=400, detail='Username missing.')
    username = unquote(username)
    collection_availability = [
        (tester_account_applications_collection.find_one({'username': username}) == None),
        (admin_account_applications_collection.find_one({'username': username}) == None),
        (users_collection.find_one({'username': username}) == None)
    ]
    for a in collection_availability:
        if a == False:
            res['detail'].append('Benutzername schon vergeben.')
            res['result'] = False
    if len(username) < 8 : 
        res['detail'].append('Der Benutzername ist zu kurz. (min. 8)')
        res['result'] = False
    if len(username) > 20 : 
        res['detail'].append('Der Benutzername ist zu lang. (max. 20)')
        res['result'] = False
    pattern = re.compile('[^a-zA-Z0-9\._-]')
    if pattern.search(username): 
        res['detail'].append('Der Benutzername darf nur a-z, A-Z, 0-9, \".\", \"_\" und \"-\" beinhalten.')
        res['result'] = False
    return res



# Check if password is valid
@router.get('/confirm_password_validity/{password}')
async def check_password_availability(password:str):
    pattern = re.compile('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})')
    if pattern.match(password) != None : return {'result' : True}
    return {'result' : False}



# Save an account application in the database
# this application will be approved or denied causing the entire document to be copied over to the users collection
@router.post('/account_application_tester')
async def apply_as_tester(user_data:user_auth_models.TesterAdminApplication):
    
    # Complete all checks to create account; Meant to prevent API abuse
    # check email availability
    collection_availability = [
        (tester_account_applications_collection.find_one({'email': user_data.email}) == None),
        (admin_account_applications_collection.find_one({'email': user_data.email}) == None),
        (users_collection.find_one({'email': user_data.email}) == None)
    ]
    for a in collection_availability:
        if a == False:
            raise HTTPException(status_code=400,detail='E-Mail already in use!')

    # check username availability
    collection_availability = [
        (tester_account_applications_collection.find_one({'username': user_data.username}) == None),
        (admin_account_applications_collection.find_one({'username': user_data.username}) == None),
        (users_collection.find_one({'username': user_data.username}) == None)
    ]
    for a in collection_availability:
        if a == False:
            raise HTTPException(status_code=400,detail='Username already in use!')

    # check password validity
    pattern = re.compile('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})')
    if pattern.match(user_data.password) == None: 
        raise HTTPException(status_code=400,detail='Password is invalid!')

    # Hash password and create account dict
    hashedPWD = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt(rounds=14))
    userProfile = {
        'username':user_data.username,
        'email':user_data.email,
        'password_hash':hashedPWD.decode(),
        'application_content':user_data.application_content,
        'account_type':{
            'priv_level' : 5,
            'account_type' : 'tester'
        }
    }
    # insert into database
    tester_account_applications_collection.insert_one(userProfile)
    return {'result' : True}



# Save an account application in the database
# this application will be approved or denied causing the entire document to be copied over to the users collection
@router.post('/account_application_admin')
async def apply_as_admin(user_data:user_auth_models.TesterAdminApplication):
    
    # Complete all checks to create account; Meant to prevent API abuse
    # check email availability
    collection_availability = [
        (tester_account_applications_collection.find_one({'email': user_data.email}) == None),
        (admin_account_applications_collection.find_one({'email': user_data.email}) == None),
        (users_collection.find_one({'email': user_data.email}) == None)
    ]
    for a in collection_availability:
        if a == False:
            raise HTTPException(status_code=400,detail='E-Mail already in use!')

    # check username availability
    collection_availability = [
        (tester_account_applications_collection.find_one({'username': user_data.username}) == None),
        (admin_account_applications_collection.find_one({'username': user_data.username}) == None),
        (users_collection.find_one({'username': user_data.username}) == None)
    ]
    for a in collection_availability:
        if a == False:
            raise HTTPException(status_code=400,detail='Username already in use!')

    # check password validity
    pattern = re.compile('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})')
    if pattern.match(user_data.password) == None: 
        raise HTTPException(status_code=400,detail='Password is invalid!')

    # Hash password and create account dict
    hashedPWD = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt(rounds=14))
    userProfile = {
        'username':user_data.username,
        'email':user_data.email,
        'password_hash':hashedPWD.decode(),
        'application_content':user_data.application_content,
        'account_type':{
            'priv_level' : 6,
            'account_type' : 'admin'
        }
    }
    # insert into database
    admin_account_applications_collection.insert_one(userProfile)
    return {'result' : True}



@router.patch('/update_account_status')
async def update_account_status(account:user_auth_models.AccountApprovalForm, user:dict = Depends(get_user_from_token)):
    
    if user['priv_level'] <= 5: 
        raise HTTPException(status_code=403,detail='You have to authorize as an admin.')
    # Attempt to create an instance of ObjectID
    try:
        oid = ObjectId(account.id)
    # react if ID is not validly formatted
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail='User ID is incorrect.')
    
    # Attempt to get user from all user collections
    user_doc = admin_account_applications_collection.find_one({'_id':oid})
    if user_doc == None:
        user_doc = tester_account_applications_collection.find_one({'_id':oid})
    if user_doc ==  None:
        # React if user not forund in any user collection
        raise HTTPException(status_code=404, detail='No such user found in any of the application databases.')
    # Act on denial
    if account.approved == False:
        # TODO: Make sure to send an email to the user, informing them about the account denial.
        possible_application_collections = [
            admin_account_applications_collection,
            tester_account_applications_collection
        ]
        # loop through all collections and delete doc when found
        for col in possible_application_collections:
            if col.find_one({'_id':user_doc['_id']}) != None:
                col.delete_one({'_id':user_doc['_id']})
        return {'result':True}
    
    # Act on approvement
    # TODO: Make sure to send an email to the user, informing them about the account approval.
    possible_application_collections = [
        admin_account_applications_collection,
        tester_account_applications_collection
    ]
    # loop through all collections and delete doc when found
    for col in possible_application_collections:
        if col.find_one({'_id':user_doc['_id']}) != None:
            col.delete_one({'_id':user_doc['_id']})
    users_collection.insert_one({
        'username':user_doc['username'],
        'email':user_doc['email'],
        'password_hash':user_doc['password_hash'],
        'account_type':user_doc['account_type'],
    })
    return {'result':True}