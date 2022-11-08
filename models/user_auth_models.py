# Import reqired modules to create a module
from pydantic import BaseModel

class Sign_Up(BaseModel):
    # The username of the user, this needs to be unique so that the user can be identified within the database 
    username:str
    # The user's password, this should NEVER be saved as plain-text string 
    password:str
    # The display name connected to that user profile
    display_name:str
    # A key used to make an admin account
    admin_key:str