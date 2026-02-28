import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import './Home.css';

export default function Home() {
  const [airlines, setAirlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [crawling, setCrawling] = useState(false);

  useEffect(() => {
    api.airlines.list()
      .then(setAirlines)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleTriggerCrawl = () => {
    setCrawling(true);
    api.admin.triggerCrawl()
      .then(() => alert('크롤링 1회 실행했습니다. 백엔드 터미널 로그에서 항공사별 크롤러·결과를 확인하세요.'))
      .catch((e) => alert(e.message))
      .finally(() => setCrawling(false));
  };

  if (loading) return <div className="page loading">항공사 목록 불러오는 중...</div>;
  if (error) return <div className="page error">오류: {error}</div>;

  return (
    <div className="page home">
      <header className="header">
        <h1>AeroFinder 관리자</h1>
        <div className="header-actions">
          <button type="button" className="btn" onClick={handleTriggerCrawl} disabled={crawling}>
            {crawling ? '실행 중...' : '지금 크롤링'}
          </button>
          <Link to="/push" className="btn info" style={{ backgroundColor: '#17a2b8', color: '#fff' }}>알림 발송</Link>
          <Link to="/notices" className="btn warning" style={{ backgroundColor: '#ff9800', color: '#fff' }}>특가 관리</Link>
          <Link to="/add" className="btn primary">+ 항공사 추가</Link>
        </div>
      </header>
      <main className="airline-grid">
        {airlines.length === 0 ? (
          <p className="empty">등록된 항공사가 없습니다. 항공사 추가 버튼으로 등록하세요.</p>
        ) : (
          airlines.map((a) => (
            <Link key={a.id} to={`/airline/${a.id}`} className="airline-card">
              <div className="airline-logo">
                {a.logo_url ? (
                  <>
                    <img src={a.logo_url} alt="" onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling?.classList.add('show'); }} />
                    <span className="logo-fallback">{(a.name || '?')[0]}</span>
                  </>
                ) : (
                  <span className="logo-fallback show">{(a.name || '?')[0]}</span>
                )}
              </div>
              <span className="airline-name">{a.name}</span>
            </Link>
          ))
        )}
      </main>
    </div>
  );
}
