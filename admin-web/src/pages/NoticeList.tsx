import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import './Home.css';

export default function NoticeList() {
  const [notices, setNotices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortOrder, setSortOrder] = useState('created'); // 'created' or 'app'

  const [ongoingExpanded, setOngoingExpanded] = useState(true);
  const [upcomingExpanded, setUpcomingExpanded] = useState(true);
  const [expiredExpanded, setExpiredExpanded] = useState(true);

  useEffect(() => {
    fetchNotices();
  }, []);

  const fetchNotices = () => {
    setLoading(true);
    api.notices.list()
      .then((data) => {
        setNotices(data);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const sortedNotices = [...notices].sort((a, b) => {
    if (sortOrder === 'created') {
      return new Date(b.created_at) - new Date(a.created_at);
    } else {
      // App Order: event_start (desc, nulls last) -> event_end (desc, nulls last) -> airline name (asc)
      const aStart = a.event_start ? new Date(a.event_start).getTime() : 0;
      const bStart = b.event_start ? new Date(b.event_start).getTime() : 0;
      const aEnd = a.event_end ? new Date(a.event_end).getTime() : 0;
      const bEnd = b.event_end ? new Date(b.event_end).getTime() : 0;

      if (aStart !== bStart) return bStart - aStart; // desc
      if (aEnd !== bEnd) return bEnd - aEnd; // desc
      return a.airline.localeCompare(b.airline); // asc
    }
  });

  const now = new Date();
  now.setHours(0, 0, 0, 0);

  const ongoingNotices = sortedNotices.filter(d => {
    if (!d.event_start && !d.event_end) return true;
    const start = d.event_start ? new Date(d.event_start) : null;
    const end = d.event_end ? new Date(d.event_end) : null;
    if (start) start.setHours(0, 0, 0, 0);
    if (end) end.setHours(23, 59, 59, 999);

    if (start && start > now) return false; // Upcoming
    if (end && end < now) return false; // Expired
    return true;
  });

  const upcomingNotices = sortedNotices.filter(d => {
    if (!d.event_start) return false;
    const start = new Date(d.event_start);
    start.setHours(0, 0, 0, 0);
    return start > now;
  });

  const expiredNotices = sortedNotices.filter(d => {
    if (!d.event_end) return false;
    const end = new Date(d.event_end);
    end.setHours(23, 59, 59, 999);
    return end < now;
  });

  const handleToggle = async (noticeId, currentStatus) => {
    try {
      await api.notices.toggleDeal(noticeId, !currentStatus);
      setNotices(notices.map(n => n.id === noticeId ? { ...n, is_special_deal: !currentStatus } : n));
    } catch (e) {
      alert("변경 실패: " + e.message);
    }
  };

  if (loading && notices.length === 0) return <div className="page loading">이벤트 목록 로딩 중...</div>;
  if (error) return <div className="page error">오류: {error}</div>;

  const renderNoticeCard = (n) => (
    <div key={n.id} style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '1rem',
      background: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
      borderLeft: n.is_special_deal ? '4px solid var(--primary-color)' : '4px solid #eee'
    }}>
      <div style={{flex: 1, marginRight: '1rem'}}>
        <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.25rem' }}>
          <span style={{ fontWeight: 600, color: 'var(--text-color)' }}>{n.airline}</span>
          <span style={{ margin: '0 0.5rem' }}>|</span>
          {new Date(n.created_at).toLocaleString()}
          <span style={{ margin: '0 0.5rem' }}>|</span>
          {n.content_type === 'image' ? '🖼️ 이미지 공지' : '📝 텍스트 공지'}
        </div>
        <div style={{ fontWeight: 500, marginBottom: '0.5rem' }}>
          <a href={n.source_url} target="_blank" rel="noreferrer" style={{ color: 'var(--primary-color)', textDecoration: 'none' }}>
            {n.title || n.source_url}
          </a>
        </div>
        <div style={{ fontSize: '0.85rem', color: '#888' }}>
          {(!n.event_start && !n.event_end) ? '기간 미정' : 
            `${n.event_start ? n.event_start.substring(0, 10) : ''} ~ ${n.event_end ? n.event_end.substring(0, 10) : ''}`}
        </div>
      </div>
      <div>
        <button 
          className={`btn ${n.is_special_deal ? 'danger' : 'primary'}`}
          onClick={() => handleToggle(n.id, n.is_special_deal)}
        >
          {n.is_special_deal ? '특가 제외' : '특가로 설정'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="page notices-page" style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
      <header className="header" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/" className="btn">← 뒤로</Link>
          <h1 style={{ margin: 0 }}>전체 수집 이벤트 관리</h1>
        </div>
      </header>
      
      <p style={{marginBottom: "2rem", color: "#666"}}>크롤러가 긁어온 모든 공지사항을 조망하고, 잘못 누락된 특가를 강제로 추가하거나 뺄 수 있습니다.</p>

      <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <label htmlFor="sortOrder" style={{ fontWeight: 'bold' }}>정렬 기준:</label>
        <select 
          id="sortOrder"
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
        >
          <option value="created">공지 등록순 (최신순)</option>
          <option value="app">어플순 (시작일/종료일/항공사명)</option>
        </select>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        <section>
          <div 
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', borderBottom: '2px solid #eee', paddingBottom: '0.5rem', marginBottom: '1rem' }}
            onClick={() => setOngoingExpanded(!ongoingExpanded)}
          >
            <h2 style={{ margin: 0 }}>진행 중인 이벤트 ({ongoingNotices.length})</h2>
            <span style={{ fontSize: '1.2rem', color: '#666' }}>{ongoingExpanded ? '▲' : '▼'}</span>
          </div>
          {ongoingExpanded && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {ongoingNotices.map(renderNoticeCard)}
              {ongoingNotices.length === 0 && <p style={{ color: '#888' }}>해당하는 이벤트가 없습니다.</p>}
            </div>
          )}
        </section>

        <section>
          <div 
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', borderBottom: '2px solid #eee', paddingBottom: '0.5rem', marginBottom: '1rem' }}
            onClick={() => setUpcomingExpanded(!upcomingExpanded)}
          >
            <h2 style={{ margin: 0 }}>진행 예정 이벤트 ({upcomingNotices.length})</h2>
            <span style={{ fontSize: '1.2rem', color: '#666' }}>{upcomingExpanded ? '▲' : '▼'}</span>
          </div>
          {upcomingExpanded && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {upcomingNotices.map(renderNoticeCard)}
              {upcomingNotices.length === 0 && <p style={{ color: '#888' }}>해당하는 이벤트가 없습니다.</p>}
            </div>
          )}
        </section>

        <section>
          <div 
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', borderBottom: '2px solid #eee', paddingBottom: '0.5rem', marginBottom: '1rem' }}
            onClick={() => setExpiredExpanded(!expiredExpanded)}
          >
            <h2 style={{ margin: 0, color: '#999' }}>종료된 이벤트 ({expiredNotices.length})</h2>
            <span style={{ fontSize: '1.2rem', color: '#999' }}>{expiredExpanded ? '▲' : '▼'}</span>
          </div>
          {expiredExpanded && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', opacity: 0.8 }}>
              {expiredNotices.map(renderNoticeCard)}
              {expiredNotices.length === 0 && <p style={{ color: '#888' }}>해당하는 이벤트가 없습니다.</p>}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}
