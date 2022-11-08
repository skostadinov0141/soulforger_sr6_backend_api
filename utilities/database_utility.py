from pymongo import MongoClient
from application_properties import ApplicationProperties
from utilities.console_colors import bcolors
import os

class DatabaseUtilities:
    
    application_settings = ApplicationProperties()

    def verifyDatabase(self):
        os.system('cls')

        print(f"{bcolors.WARNING}CHECKING: {bcolors.ENDC}".ljust(15), end='')
        print(f"Database connection".ljust(50,"-"), end='>')

        if(self.application_settings.testDBConnection(self.application_settings.connectToDB()) == True):
            print(f"{bcolors.OKGREEN} OKAY{bcolors.ENDC}", end='')
            print()
        else:
            print(f"{bcolors.FAIL} FAIL{bcolors.ENDC}", end='')
            print()
            print(f"""          {bcolors.HEADER}└SUGGESTION: {bcolors.ENDC}Start a dockerized MongoDB instance or make sure that the credentials and IP/Port are correct.""")

############################################################

        if(self.application_settings.testDBConnection(self.application_settings.connectToDB()) == True):
            # Connect to the database and enter the secrets collection to check if all critical values exist
            secrets_collection = self.application_settings.getCollection("secrets")

            print(f"{bcolors.WARNING}CHECKING: {bcolors.ENDC}".ljust(15), end='')
            print(f"jwt_encryption_key".ljust(50,"-"), end='>')

            if(secrets_collection.count_documents({"jwt_encryption_key" : {'$exists' : True}}) != 0):
                print(f"{bcolors.OKGREEN} OKAY{bcolors.ENDC}", end='')
                print()
            else:
                print(f"{bcolors.FAIL} FAIL{bcolors.ENDC}", end='')
                print()
                print(f"""          {bcolors.HEADER}└SUGGESTION: {bcolors.ENDC}Add the jwt_encryption_key to the secrets collection within the database.""")
                print(f"""\t\t       To do that create a complex key using https://www.lastpass.com/features/password-generator-a#generatorTool""")

############################################################

            print(f"{bcolors.WARNING}CHECKING: {bcolors.ENDC}".ljust(15), end='')
            print(f"admin_account_creation_key".ljust(50,"-"), end='>')

            if(secrets_collection.count_documents({"admin_account_creation_key" : {'$exists' : True}}) != 0):
                print(f"{bcolors.OKGREEN} OKAY{bcolors.ENDC}", end='')
                print()
            else:
                print(f"{bcolors.FAIL} FAIL{bcolors.ENDC}", end='')
                print()
                print(f"""          {bcolors.HEADER}└SUGGESTION: {bcolors.ENDC}Add the admin_account_creation_key to the secrets collection within the database.""")
                print(f"""\t\t       To do that create a secure password using https://www.lastpass.com/features/password-generator-a#generatorTool""")
                print(f"""\t\t       After that encrypt the password using https://bcrypt-generator.com""")
