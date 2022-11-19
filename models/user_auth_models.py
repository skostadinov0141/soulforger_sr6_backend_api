# Import reqired modules to create a module
from pydantic import BaseModel

class Tester_Application(BaseModel):
    # The username of the user, this needs to be unique so that the user can be identified within the database 
    username:str
    # The user's password, this should NEVER be saved as plain-text string 
    password:str
    # The email that is bound to the account
    email:str
    # The application that the user has sent, specifically why he/she thinks he/she should become a tester
    application_content:str