from pymongo import MongoClient

# Replace with your actual MongoDB Atlas connection string
CONNECTION_STRING = "mongodb+srv://keerthanakeeru092005_db_user:chB675lqiqwQGVZo@miniprojectcluster.sxe15ez.mongodb.net/?appName=MiniProjectCluster"

client = MongoClient(CONNECTION_STRING)
db = client['search_engine_db']
collection = db['documents']

# Clear previous records to prevent duplicates
collection.delete_many({})

sample_docs = [
    {
        "title": "Introduction to NoSQL Databases",
        "content": "NoSQL databases provide flexible schemas for unstructured and semi-structured documents like JSON and BSON.",
        "category": "Databases"
    },
    {
        "title": "TF-IDF Vector Space Model",
        "content": "Term Frequency-Inverse Document Frequency is an information retrieval algorithm used to weigh and score word importance across document collections.",
        "category": "Information Retrieval"
    },
    {
        "title": "Modern Artificial Intelligence",
        "content": "Machine learning algorithms and deep neural networks process large datasets to discover complex patterns.",
        "category": "Artificial Intelligence"
    },
    {
        "title": "Cloud Computing Infrastructure",
        "content": "Distributed cloud architectures provide scalable compute resources, automated container orchestration, and storage.",
        "category": "Cloud Computing"
    },
    {
        "title": "Healthy Habits and Hydration",
        "content": "Drinking clean water, eating balanced food, and getting regular sleep are essential habits for physical and mental wellness.",
        "category": "Health & Lifestyle"
    },
    {
        "title": "Relational versus NoSQL Storage",
        "content": "While relational databases rely on tabular relations and strict foreign keys, NoSQL scales horizontally across document nodes.",
        "category": "Databases"
    }
]

collection.insert_many(sample_docs)
print("Database successfully seeded with documents!")