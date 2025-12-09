from typing import Any, Dict, List, Optional
from neo4j import Session
from app.database import get_db

class Neo4jService:
    def __init__(self):
        self.driver = get_db()

    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.driver.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def find_one(self, query: str, parameters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        results = self.execute_query(query, parameters)
        return results[0] if results else None

# Singleton instance
neo4j_service = Neo4jService()
