from neo4j import GraphDatabase
from app.config import get_settings

settings = get_settings()

class Neo4jDriver:
    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()

    def get_session(self):
        return self.driver.session()

# Global driver instance
db = Neo4jDriver()

def get_db():
    return db
