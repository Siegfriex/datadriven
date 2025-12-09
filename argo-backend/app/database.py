from neo4j import GraphDatabase
from app.config import get_settings
import logging
import os

logger = logging.getLogger(__name__)
settings = get_settings()

# Windows SSL 인증서 문제 해결: certifi 인증서 경로 설정
try:
    import certifi
    # certifi 인증서를 사용하도록 환경 변수 설정
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except ImportError:
    logger.warning("certifi 패키지가 설치되지 않았습니다. SSL 인증서 검증에 문제가 있을 수 있습니다.")

class Neo4jDriver:
    """
    Neo4j AuraDB Professional 연결 드라이버
    
    인스턴스 정보:
    - ID: be57a318
    - Type: AuraDB Professional
    - Version: 2025.10
    - Region: Google Cloud / Iowa, USA (us-central1)
    - Memory: 1GB, CPU: 1, Storage: 2GB
    - Graph Analytics: Serverless
    """
    
    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            try:
                # AuraDB Professional 최적화 설정
                # 1GB 메모리, 1 CPU 제약 고려
                # neo4j+s:// URI는 이미 암호화되어 있으므로 encrypted/trust/ssl_context 파라미터 불필요
                driver_config = {
                    "auth": (settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                    # 연결 풀 설정 (메모리 제약 고려)
                    "max_connection_lifetime": 30 * 60,  # 30분
                    "max_connection_pool_size": 10,  # 메모리 제약 고려 (기본 50 → 10)
                    "connection_acquisition_timeout": 2 * 60,  # 2분
                    "connection_timeout": 30,  # 30초
                }
                
                # neo4j+s:// 또는 bolt+s:// URI는 이미 암호화되어 있음
                # neo4j:// 또는 bolt:// URI만 encrypted/trust 파라미터 필요
                uri = settings.NEO4J_URI.lower()
                if not ("+s" in uri or "+ssc" in uri):
                    # 암호화되지 않은 URI에만 암호화 설정 추가
                    driver_config["encrypted"] = True
                    driver_config["trust"] = "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
                
                self._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    **driver_config
                )
                # 연결 즉시 검증
                self._driver.verify_connectivity()
                logger.info("✅ Neo4j AuraDB Professional 드라이버 초기화 성공")
                logger.info(f"   인스턴스: be57a318 (us-central1)")
                logger.info(f"   버전: 2025.10, 메모리: 1GB, CPU: 1")
            except Exception as e:
                logger.error(f"❌ Neo4j 드라이버 초기화 실패: {e}")
                raise
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def get_session(self):
        return self.driver.session()

# Global driver instance
db = Neo4jDriver()

def get_db():
    return db
