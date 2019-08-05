import pymongo
import urllib

def getConnection():
    username = urllib.parse.quote_plus('asaha@eainfobiz.com')
    password = urllib.parse.quote_plus('MongoDB@2020')
    conn = pymongo.MongoClient('mongodb://%s:%s@mongodb-1763-0.cloudclusters.net:10007/Quark?authSource=admin' % (username,password))
    return conn.get_database()

# from django.conf import settings
# def getConnection():
#     conn= pymongo.MongoClient(settings.MONGO_HOST)
#     return conn[settings.DB_NAME]
