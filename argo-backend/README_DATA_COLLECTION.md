# ARGO 데이터 수집 가이드

## 빠른 시작

### 1. API 키 발급

**ARKO API 키 발급** (필수):

1. [공공데이터포털](https://www.data.go.kr) 접속
2. "한국문화예술위원회_미술작가목록_20200518" 검색
3. API 신청 및 인증키 발급
4. 발급받은 인증키를 `.env` 파일에 설정

### 2. 환경변수 설정

`argo-backend/.env` 파일에 다음을 추가:

```env
# ARKO API (공공데이터포털에서 발급받은 실제 키)
ARKO_API_KEY=your_actual_api_key_here
ARKO_SERVICE_KEY=your_actual_service_key_here

# Neo4j
NEO4J_URI=neo4j+s://be57a318.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Gemini API
GEMINI_API_KEY=your_gemini_key
```

### 3. API 테스트

```bash
cd argo-backend
python test_arko_api.py
```

**예상 출력**:
```
✅ API 호출 성공
   전체 작가 수: 1000명
   현재 페이지: 10명
```

### 4. 데이터 수집 실행

```bash
# 기본 실행 (50명 수집)
python data_collection_pipeline.py

# 지정된 수량 수집
python data_collection_pipeline.py --count 100

# 테스트 모드 (업로드 없이)
python data_collection_pipeline.py --count 10 --dry-run
```

## 문제 해결

### "등록되지 않은 인증키 입니다" 오류

**원인**: API 키가 유효하지 않거나 발급되지 않음

**해결**:
1. 공공데이터포털에서 API 키를 정확히 발급받았는지 확인
2. `.env` 파일의 `ARKO_SERVICE_KEY` 값이 정확한지 확인
3. API 키에 공백이나 특수문자가 포함되지 않았는지 확인

### "Connection refused" 오류 (Neo4j)

**원인**: Neo4j 연결 실패

**해결**:
1. `.env` 파일의 Neo4j 인증 정보 확인
2. Neo4j Aura 인스턴스 상태 확인
3. 방화벽 설정 확인

## 상세 문서

- `docs/ARGO_DATA_COLLECTION_METHODOLOGY.md`: 전체 방법론 문서
- `app/collectors/arko_collector.py`: ARKO API 수집기 구현
- `app/normalizers/`: 데이터 정규화 모듈
- `app/validators/`: 데이터 검증 모듈
- `app/uploaders/`: Neo4j 업로드 모듈

