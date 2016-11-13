from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['scale-db']

for i in range(15):
	db.scalers.insert_one({})

