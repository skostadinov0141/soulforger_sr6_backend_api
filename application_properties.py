from pymongo import MongoClient, errors
from urllib.parse import quote_plus 

class ApplicationProperties:

    """
    A class that describes all important settings and variables for the API deployment.
    Any global variables should be changed here and will automatically be reflected within all included routers.
    """

    # Global application settings
    testingBuild = True

    # Database connection settings
    database = None

    # authentication secrets
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 120





    def connectToDB(self):
        """Use this function to attempt to connect to a mongoDB instance.
        To test if the connection was established succesfully, use testDBConnection() 

        Returns:
            MongoClient(): A MongoDB Client connected to a database if the database connection is successfull.
        """
        databaseUser = "mongoadmin"
        databasePassword = r"smgfFGy2GWzU72"
        databaseIp = "127.0.0.1"
        databasePort = "27017"

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
        




    def getJwtEncryptionKey(self):
        """Get the encryption key for generating JWT Tokens which is stored in the database

        Returns:
            String: The encryption key
        """
        if(self.database == None):
            self.connectToDB()
        response = self.getCollection("secrets").find_one({"jwt_encryption_key":{"$exists":True}})
        return response["jwt_encryption_key"]
    




    def getAdminKey(self):
        """Get the key used to create admin accounts

        Returns:
            String: The admin creation key
        """
        if(self.database == None):
            self.connectToDB()
        response = self.getCollection("secrets").find_one({"admin_account_creation_key":{"$exists":True}})
        return response["admin_account_creation_key"]





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