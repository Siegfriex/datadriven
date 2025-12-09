import * as functions from 'firebase-functions/v2';
import * as admin from 'firebase-admin';

admin.initializeApp();

// 리전 설정: asia-northeast3 (서울)
const region = 'asia-northeast3';

// 예시: API 프록시 함수 (필요 시 사용)
export const apiProxy = functions.https.onRequest(
  {
    region: region,
    cors: true,
  },
  async (req, res) => {
    // CORS는 Gen 2에서 자동 처리됨 (cors: true 설정 시)
    
    // Cloud Run API로 프록시 (필요 시)
    // const apiUrl = process.env.API_URL || 'https://artdrive1208-api-xxx.run.app';
    
    // 프록시 로직은 필요 시 구현
    res.status(200).json({ message: 'API Proxy function is ready' });
  }
);

// 예시: 갤럭시 스냅샷 생성 (스케줄 함수)
export const generateGalaxySnapshot = functions.scheduler.onSchedule(
  {
    schedule: 'every 24 hours',
    timeZone: 'Asia/Seoul',
    region: region,
  },
  async (event) => {
    // 갤럭시 스냅샷 생성 로직 (향후 구현)
    console.log('Galaxy snapshot generation scheduled');
  }
);

