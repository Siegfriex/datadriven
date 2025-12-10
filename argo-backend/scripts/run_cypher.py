"""
Cypher 파일 실행 스크립트
- Cypher 파일을 로드하여 Neo4j에 실행
- 쿼리 블록 분리 및 개별 실행
- 결과 출력 및 로깅

Usage:
    python scripts/run_cypher.py neo4j/queries/validation_phase1.cypher
    python scripts/run_cypher.py neo4j/queries/01_relationship_creation.cypher --dry-run
"""

import sys
import os
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_cypher_file(filepath: str) -> str:
    """Cypher 파일 로드"""
    path = Path(filepath)
    if not path.is_absolute():
        path = Path(__file__).parent.parent / filepath

    if not path.exists():
        raise FileNotFoundError(f"Cypher 파일을 찾을 수 없습니다: {path}")

    return path.read_text(encoding='utf-8')


def parse_cypher_blocks(content: str) -> List[Tuple[str, str]]:
    """
    Cypher 파일에서 쿼리 블록 파싱

    Returns:
        List of (block_name, query) tuples
    """
    blocks = []
    current_name = "Unnamed Block"
    current_query_lines = []

    lines = content.split('\n')

    for line in lines:
        # 블록 헤더 감지 (// === 로 시작)
        if line.strip().startswith('// ===') and '===' in line[7:]:
            # 이전 블록 저장
            if current_query_lines:
                query = '\n'.join(current_query_lines).strip()
                if query and not query.startswith('//'):
                    blocks.append((current_name, query))

            # 새 블록 시작
            match = re.search(r'// === (.+?) ===', line)
            if match:
                current_name = match.group(1).strip()
            current_query_lines = []

        # 주석 라인 건너뛰기 (단, 파라미터 주석은 제외)
        elif line.strip().startswith('//'):
            continue

        # 빈 줄이 아닌 경우 쿼리에 추가
        elif line.strip():
            current_query_lines.append(line)

    # 마지막 블록 저장
    if current_query_lines:
        query = '\n'.join(current_query_lines).strip()
        if query:
            blocks.append((current_name, query))

    return blocks


def split_by_semicolon(query: str) -> List[str]:
    """
    세미콜론으로 쿼리 분리 (문자열 리터럴 내부 제외)
    """
    queries = []
    current = []
    in_string = False
    string_char = None

    for char in query:
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            in_string = False
            string_char = None

        if char == ';' and not in_string:
            q = ''.join(current).strip()
            if q:
                queries.append(q)
            current = []
        else:
            current.append(char)

    # 마지막 쿼리
    q = ''.join(current).strip()
    if q:
        queries.append(q)

    return queries


def execute_query(query: str, dry_run: bool = False) -> List[Dict[str, Any]]:
    """쿼리 실행"""
    if dry_run:
        logger.info(f"[DRY RUN] 쿼리: {query[:100]}...")
        return []

    return neo4j_service.execute_query(query)


def format_result(result: List[Dict[str, Any]]) -> str:
    """결과 포맷팅"""
    if not result:
        return "  (결과 없음)"

    output = []
    for row in result[:20]:  # 최대 20행만 표시
        row_str = "  " + " | ".join(
            f"{k}: {v}" for k, v in row.items()
        )
        output.append(row_str)

    if len(result) > 20:
        output.append(f"  ... 외 {len(result) - 20}개 행")

    return '\n'.join(output)


def run_cypher_file(filepath: str, dry_run: bool = False, verbose: bool = True):
    """
    Cypher 파일 실행

    Args:
        filepath: Cypher 파일 경로
        dry_run: True면 실제 실행하지 않고 쿼리만 출력
        verbose: 상세 출력 여부
    """
    print("=" * 70)
    print(f"ARGO Cypher 실행기")
    print(f"파일: {filepath}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"모드: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("=" * 70)

    try:
        # 파일 로드
        content = load_cypher_file(filepath)
        logger.info(f"파일 로드 완료: {len(content)} bytes")

        # 블록 파싱
        blocks = parse_cypher_blocks(content)
        logger.info(f"쿼리 블록 {len(blocks)}개 발견")

        if not blocks:
            # 블록 구분 없이 전체 파일을 세미콜론으로 분리
            queries = split_by_semicolon(content)
            blocks = [(f"Query {i+1}", q) for i, q in enumerate(queries)]
            logger.info(f"세미콜론으로 분리된 쿼리 {len(blocks)}개")

        # 실행 결과
        results = []
        success_count = 0
        fail_count = 0

        for name, query in blocks:
            print(f"\n{'─' * 50}")
            print(f"▶ {name}")
            print(f"{'─' * 50}")

            if verbose:
                # 쿼리 미리보기 (최대 200자)
                preview = query[:200] + "..." if len(query) > 200 else query
                print(f"쿼리:\n{preview}\n")

            try:
                result = execute_query(query, dry_run)
                success_count += 1

                if result:
                    print("결과:")
                    print(format_result(result))
                    results.append({
                        'name': name,
                        'status': 'success',
                        'result': result
                    })
                else:
                    print("  ✓ 실행 완료 (반환값 없음)")
                    results.append({
                        'name': name,
                        'status': 'success',
                        'result': None
                    })

            except Exception as e:
                fail_count += 1
                logger.error(f"쿼리 실행 실패: {e}")
                print(f"  ✗ 오류: {e}")
                results.append({
                    'name': name,
                    'status': 'error',
                    'error': str(e)
                })

        # 요약
        print(f"\n{'=' * 70}")
        print("실행 요약")
        print(f"{'=' * 70}")
        print(f"총 쿼리: {len(blocks)}개")
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")
        print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        return results

    except FileNotFoundError as e:
        logger.error(f"파일 오류: {e}")
        print(f"✗ 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"실행 오류: {e}")
        print(f"✗ 오류: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='ARGO Cypher 파일 실행기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python scripts/run_cypher.py neo4j/queries/validation_phase1.cypher
  python scripts/run_cypher.py neo4j/queries/01_relationship_creation.cypher --dry-run
  python scripts/run_cypher.py neo4j/queries/validation_final.cypher -v
        """
    )

    parser.add_argument(
        'filepath',
        help='실행할 Cypher 파일 경로'
    )

    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='실제 실행 없이 쿼리만 출력'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
        help='상세 출력 (기본값: True)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='최소 출력'
    )

    args = parser.parse_args()

    verbose = not args.quiet if args.quiet else args.verbose

    run_cypher_file(
        filepath=args.filepath,
        dry_run=args.dry_run,
        verbose=verbose
    )


if __name__ == "__main__":
    main()
