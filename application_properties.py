from pymongo import MongoClient, errors
from urllib.parse import quote_plus 
import yaml

class ApplicationProperties:

    """
    A class that describes all important settings and variables for the API deployment.
    Any global variables should be changed here and will automatically be reflected within all included routers.
    """

    # Global application settings
    testingBuild = False

    # Database connection settings
    database = None

    # authentication secrets
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 120
    JWT_ENCRYPTION_KEY = ""

    with open("secrets.yaml", mode="r") as file:
        secrets = yaml.safe_load(file)
        JWT_ENCRYPTION_KEY = secrets['jwt_encryption_key']



    def connectToDB(self):
        """Use this function to attempt to connect to a mongoDB instance.
        To test if the connection was established succesfully, use testDBConnection() 

        Returns:
            MongoClient(): A MongoDB Client connected to a database if the database connection is successfull.
        """

        with open("secrets.yaml", mode="r") as file:
            secrets = yaml.safe_load(file)

        databaseUser = secrets['database_username']
        databasePassword = secrets['database_password']
        databaseIp = secrets['database_ip']
        databasePort = secrets['database_port']

        uri = ""
        # Check if the current environment is testing or production, use the according parameters to establish the connection
        if(self.testingBuild):
            uri = f"mongodb://{databaseIp}:{databasePort}"
        else:
            uri = "mongodb://%s:%s@%s" % (
                quote_plus(databaseUser), 
                quote_plus(databasePassword), 
                f"{databaseIp}:{databasePort}"
            )
        self.database = MongoClient(uri,serverSelectionTimeoutMS=2)
        return self.database
 


    def testDBConnection(self, database):
        try:
            database.server_info()
            return True
        except errors.ServerSelectionTimeoutError as err:
            return False



    def getCollection(self, collection_name):
        """After the database connection is established (with connectToDB) a collection will be slected and returned.

        Args:
            collection_name (string): The name of the collection that the client should connect to.
        """
        # Connect to a DB, the DB does not need to be valid, if it isn't testDBConnection will return false and getCollection will return None
        database = self.connectToDB()
        if(self.testDBConnection(database)):
            # Connect to the DB and enter the selected collection
            usersCollection = database["soulforger_testing" if self.testingBuild else "soulforger"][collection_name]
            return usersCollection
        return None