import os
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DATABASE", "nvas_captcha")
        self.client = None
        self.db = None
        self.verification_collection = None

    def connect(self):
        try:
            # ServerSelectionTimeoutMS avoids blocking forever if DB is down
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.db = self.client[self.db_name]
            self.verification_collection = self.db["verification_sessions"]
            
            # Create indexes
            self._create_indexes()
            
            # Verify connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
            self.verification_collection = None
        except Exception as e:
            logger.error(f"MongoDB initialization error: {e}")
            self.client = None

    def _create_indexes(self):
        if self.verification_collection is not None:
            try:
                self.verification_collection.create_index([("session_id", ASCENDING)], unique=True)
                self.verification_collection.create_index([("timestamp", DESCENDING)])
                self.verification_collection.create_index([("action", ASCENDING)])
                logger.info("MongoDB indexes verified/created")
            except PyMongoError as e:
                logger.error(f"Error creating indexes: {e}")

    def is_connected(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except PyMongoError:
            return False

    def save_verification(self, document: dict):
        if self.verification_collection is not None:
            try:
                self.verification_collection.insert_one(document)
            except PyMongoError as e:
                logger.error(f"Failed to save verification document: {e}")
        else:
            logger.warning("MongoDB is not connected. Verification log skipped.")

# Singleton instance
db = DatabaseClient()
db.connect()
