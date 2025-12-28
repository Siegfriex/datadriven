// ========================================
// File: backup_snapshot.cypher
// Purpose: 현재 데이터 상태 백업용 스냅샷 쿼리 (APOC 활용)
// ========================================

// JSON으로 전체 그래프 내보내기
CALL apoc.export.json.all("backup_snapshot_" + toString(datetime()) + ".json", {useTypes:true});

// 또는 GraphML로 내보내기 (구조 포함)
// CALL apoc.export.graphml.all("backup_snapshot_" + toString(datetime()) + ".graphml", {});



