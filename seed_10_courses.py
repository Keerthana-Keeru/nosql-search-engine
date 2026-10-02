from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://keerthanakeeru092005_db_user:chB675lqiqwQGVZo@miniprojectcluster.sxe15ez.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
client = MongoClient(CONNECTION_STRING)
db = client['search_engine_db']
courses_collection = db['courses']

def generate_chapters(course_topic):
    chapters = []
    for i in range(1, 11):
        quiz = []
        for q in range(1, 11):
            quiz.append({
                "question": f"Q{q}. What is a core principle or operational mechanism regarding {course_topic} - Chapter {i}?",
                "options": [
                    "A. Primary architectural configuration and schema flexibility",
                    "B. Strict static relational table normalization",
                    "C. Manual file-system byte parsing without indexes",
                    "D. Local volatile memory isolation"
                ],
                "correct_answer": "A. Primary architectural configuration and schema flexibility"
            })
        chapters.append({
            "chapter_number": i,
            "title": f"CHAPTER {i} — Advanced Concepts in {course_topic}",
            "content": f"This chapter explores deep architectural principles, operational scaling patterns, and implementation strategies for Chapter {i} of {course_topic}. Students will examine internal mechanics, performance trade-offs, and best practices.",
            "quiz": quiz
        })
    return chapters

def generate_final_exam(course_topic):
    questions = []
    for j in range(1, 21):
        questions.append({
            "question": f"Final Q{j}: Evaluate the enterprise scalability and failure recovery behavior for {course_topic}.",
            "options": [
                "A. Horizontal partitioning, replication consistency, and fault tolerance",
                "B. Single-node monolithic locking without redundancy",
                "C. Complete data purging on network disconnection",
                "D. Manual row-by-row text file parsing"
            ],
            "correct_answer": "A. Horizontal partitioning, replication consistency, and fault tolerance"
        })
    return {"questions": questions}

courses_data = [
    {
        "title": "MongoDB Essentials & Document Design",
        "description": "A complete, hands-on course covering NoSQL database concepts, document-oriented data models, BSON data structures, MongoDB CRUD operations, indexing, and aggregation pipelines.",
        "chapters": generate_chapters("MongoDB"),
        "final_assessment": generate_final_exam("MongoDB")
    },
    {
        "title": "Distributed Systems, Sharding & CAP Theorem",
        "description": "Master the theoretical and practical foundations of distributed data stores, partition tolerance, consensus protocols, and horizontal cluster scaling.",
        "chapters": generate_chapters("Distributed Systems"),
        "final_assessment": generate_final_exam("Distributed Systems")
    },
    {
        "title": "Apache Cassandra & Wide-Column Store Architecture",
        "description": "Explore decentralized masterless architecture, peer-to-peer gossip protocols, LSM-tree storage engines, and CQL query-driven data modeling.",
        "chapters": generate_chapters("Apache Cassandra"),
        "final_assessment": generate_final_exam("Apache Cassandra")
    },
    {
        "title": "Redis In-Memory Data Structures & Caching Patterns",
        "description": "Learn high-throughput in-memory data structures, persistence models, Redis Cluster hash slots, Lua scripting, and advanced caching patterns.",
        "chapters": generate_chapters("Redis"),
        "final_assessment": generate_final_exam("Redis")
    },
    {
        "title": "Neo4j Graph Databases & Relationship Modeling",
        "description": "Master property graph models, Cypher query language optimization, index-free adjacency traversals, and connected data analytics.",
        "chapters": generate_chapters("Neo4j Graphs"),
        "final_assessment": generate_final_exam("Neo4j Graphs")
    },
    {
        "title": "PostgreSQL Relational Design & Advanced SQL",
        "description": "Explore advanced relational database design, ACID compliance, complex joins, indexing strategies, window functions, and query optimization.",
        "chapters": generate_chapters("PostgreSQL"),
        "final_assessment": generate_final_exam("PostgreSQL")
    },
    {
        "title": "Database Indexing & Query Performance Tuning",
        "description": "Deep dive into B-Tree indexes, compound index design, execution plan profiling, query cost estimation, and bottleneck mitigation.",
        "chapters": generate_chapters("Indexing & Tuning"),
        "final_assessment": generate_final_exam("Indexing & Tuning")
    },
    {
        "title": "GraphQL APIs & Modern Data Fetching",
        "description": "Understand GraphQL schema definitions, query resolvers, mutations, subscriptions, and efficient client-server data exchange architectures.",
        "chapters": generate_chapters("GraphQL"),
        "final_assessment": generate_final_exam("GraphQL")
    },
    {
        "title": "Elasticsearch & Full-Text Search Engines",
        "description": "Learn inverted indices, text analysis tokenizers, distributed full-text search queries, aggregation analytics, and cluster management.",
        "chapters": generate_chapters("Elasticsearch"),
        "final_assessment": generate_final_exam("Elasticsearch")
    },
    {
        "title": "Vector Databases & AI Retrieval Architectures",
        "description": "Explore high-dimensional vector embeddings, approximate nearest neighbor (ANN) search algorithms, and RAG backend integrations.",
        "chapters": generate_chapters("Vector Databases"),
        "final_assessment": generate_final_exam("Vector Databases")
    }
]

# Clear existing courses and insert all 10 complete courses
courses_collection.delete_many({})
result = courses_collection.insert_many(courses_data)
print(f"Successfully seeded {len(result.inserted_ids)} complete courses into MongoDB Atlas database 'search_engine_db'.")