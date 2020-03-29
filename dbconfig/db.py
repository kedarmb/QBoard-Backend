import pymongo
import urllib

def getConnection():
    username = urllib.parse.quote_plus('asaha@eainfobiz.com')
    password = urllib.parse.quote_plus('MongoDB@2020')
    conn = pymongo.MongoClient('mongodb://%s:%s@mongodb-6953-0.cloudclusters.net:10001/Quark?authSource=admin' % (username,password))
    # username = urllib.parse.quote_plus('vbansal@thinkperfect.io')
    # password = urllib.parse.quote_plus('Perfect@1#')
    # conn = pymongo.MongoClient("mongodb://smartbid:SmartBid1!@cluster0-ofksl.mongodb.net/test?retryWrites=true&w=majority")
    # conn = pymongo.MongoClient("mongodb://smartbid:SmartBid1!@cluster0-ofksl.mongodb.net/test?retryWrites=true&w=majority")
    # db = conn.test
    # print(db)
    return conn.get_database()




# from django.conf import settings
# def getConnection():
#     conn= pymongo.MongoClient(settings.MONGO_HOST)
#     return conn[settings.DB_NAME]
