import pymongo

class MongoDataBase():
    def __init__(self):
        self.connection_string = "mongodb://localhost:27017/"
        self.db_name = "REDORD"
        self.DB_Client = pymongo.MongoClient(self.connection_string)
        self.DB = self.DB_Client[self.db_name]

    def get_client(self):
        return self.DB_Client

    def get_DB(self):
        return self.DB

    def get_collection(self, collection):
        return self.DB[collection]