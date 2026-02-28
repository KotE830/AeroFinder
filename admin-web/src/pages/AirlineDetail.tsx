import { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import './AirlineDetail.css';

export default function AirlineDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [airline, setAirline] = useState(null);
  const [urls, setUrls] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newUrl, setNewUrl] = useState('');
  const [newLinkSelector, setNewLinkSelector] = useState('');
  const [newTitleSelector, setNewTitleSelector] = useState('');
  const [newPeriodSelector, setNewPeriodSelector] = useState('');
  const [newNextSelector, setNewNextSelector] = useState('');
  const [editingListSelector, setEditingListSelector] = useState({});
  const [editingTitleSelector, setEditingTitleSelector] = useState({});
  const [editingPeriodSelector, setEditingPeriodSelector] = useState({});
  const [editingNextSelector, setEditingNextSelector] = useState({});
  const [newKeyword, setNewKeyword] = useState('');
  const [editingName, setEditingName] = useState('');
  const [editingBaseUrl, setEditingBaseUrl] = useState('');
  const [editingLogoUrl, setEditingLogoUrl] = useState('');
  const [savingBasic, setSavingBasic] = useState(false);

  const load = () => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      api.airlines.get(id),
      api.airlines.listUrls(id),
      api.keywords.list(id),
    ])
      .then(([a, u, k]) => {
        setAirline(a);
        setUrls(u);
        setKeywords(k);
        setEditingName(a.name ?? '');
        setEditingBaseUrl(a.base_url ?? '');
        setEditingLogoUrl(a.logo_url ?? '');
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleAddUrl = (e) => {
    e.preventDefault();
    if (!newUrl.trim() || !newLinkSelector.trim() || !newTitleSelector.trim()) {
      alert('URL, 이벤트 페이지 컴포넌트, 제목 컴포넌트를 모두 입력해야 합니다.');
      return;
    }
    api.airlines.addUrl(
      id,
      newUrl.trim(),
      newLinkSelector.trim(),
      newTitleSelector.trim(),
      newPeriodSelector.trim() || undefined,
      newNextSelector.trim() || undefined
    )
      .then(() => {
        load();
        setNewUrl('');
        setNewLinkSelector('');
        setNewTitleSelector('');
        setNewPeriodSelector('');
        setNewNextSelector('');
      })
      .catch((e) => alert(e.message));
  };

  const handleUpdateUrlSelectors = (urlId, listLinkSelector, detailTitleSelector, listPeriodSelector, listNextSelector) => {
    if (!listLinkSelector?.trim() || !detailTitleSelector?.trim()) {
      alert('이벤트 페이지 컴포넌트와 제목 컴포넌트를 모두 입력해야 합니다.');
      return;
    }
    api.airlines
      .updateUrl(id, urlId, {
        list_link_selector: listLinkSelector.trim(),
        detail_title_selector: detailTitleSelector.trim(),
        list_period_selector: listPeriodSelector ? listPeriodSelector.trim() : null,
        list_next_selector: listNextSelector ? listNextSelector.trim() : null,
      })
      .then(() => {
        load();
        setEditingListSelector((s) => ({ ...s, [urlId]: undefined }));
        setEditingTitleSelector((s) => ({ ...s, [urlId]: undefined }));
        setEditingPeriodSelector((s) => ({ ...s, [urlId]: undefined }));
        setEditingNextSelector((s) => ({ ...s, [urlId]: undefined }));
      })
      .catch((e) => alert(e.message));
  };

  const handleDeleteUrl = (urlId) => {
    if (!confirm('이 URL을 삭제할까요?')) return;
    api.airlines.deleteUrl(id, urlId)
      .then(load)
      .catch((e) => alert(e.message));
  };

  const handleAddKeyword = (e) => {
    e.preventDefault();
    if (!newKeyword.trim()) return;
    api.keywords.create(newKeyword.trim(), id)
      .then(() => { load(); setNewKeyword(''); })
      .catch((e) => alert(e.message));
  };

  const handleDeleteKeyword = (keywordId) => {
    if (!confirm('이 키워드를 삭제할까요?')) return;
    api.keywords.delete(keywordId)
      .then(load)
      .catch((e) => alert(e.message));
  };

  const handleDeleteAirline = () => {
    if (!window.confirm('정말 이 항공사를 삭제하시겠습니까?\n관련된 모든 URL, 이벤트, 키워드가 함께 삭제됩니다.')) return;
    api.airlines.delete(id)
      .then(() => {
        alert('삭제되었습니다.');
        navigate('/');
      })
      .catch((e) => alert(e.message));
  };

  const handleDeleteData = () => {
    if (!window.confirm('정말 이 항공사의 모든 크롤링 데이터를 삭제하시겠습니까?\nURL과 키워드는 유지되지만, 수집된 이벤트와 특가 정보는 모두 지워집니다.')) return;
    api.airlines.deleteData(id)
      .then(() => {
        alert('크롤링 데이터가 초기화되었습니다. 다시 크롤링을 실행해 보세요.');
      })
      .catch((e) => alert(e.message));
  };



  const handleSaveBasicInfo = (e) => {
    e.preventDefault();
    if (!editingName.trim()) {
      alert('항공사 이름을 입력하세요.');
      return;
    }
    setSavingBasic(true);
    api.airlines.update(id, {
      name: editingName.trim(),
      base_url: editingBaseUrl.trim() || undefined,
      logo_url: editingLogoUrl.trim() || undefined,
    })
      .then(() => load())
      .catch((e) => alert(e.message))
      .finally(() => setSavingBasic(false));
  };

  if (loading && !airline) return <div className="page loading">불러오는 중...</div>;
  if (error || !airline) return <div className="page error">오류: {error || '항공사를 찾을 수 없습니다.'}</div>;
  return (
    <div className="page detail">
      <header className="header">
        <Link to="/" className="back">← 목록</Link>
        <h1>{airline.name}</h1>
      </header>

      <section className="section">
        <h2>기본 정보</h2>
        <form onSubmit={handleSaveBasicInfo} className="basic-info-form">
          <label>
            <span className="input-label">항공사 이름</span>
            <input
              type="text"
              value={editingName}
              onChange={(e) => setEditingName(e.target.value)}
              placeholder="예: 대한항공"
              className="input"
            />
          </label>
          <label>
            <span className="input-label">기본 URL</span>
            <input
              type="url"
              value={editingBaseUrl}
              onChange={(e) => setEditingBaseUrl(e.target.value)}
              placeholder="https://..."
              className="input"
            />
          </label>
          <label>
            <span className="input-label">로고 URL (선택)</span>
            <input
              type="url"
              value={editingLogoUrl}
              onChange={(e) => setEditingLogoUrl(e.target.value)}
              placeholder="https://..."
              className="input"
            />
          </label>

          <button type="submit" className="btn primary" disabled={savingBasic}>
            {savingBasic ? '저장 중...' : '기본 정보 저장'}
          </button>
        </form>
      </section>

      <section className="section">
        <h2>이벤트 목록 페이지 URL · 컴포넌트</h2>
        <p className="hint">
          <strong>이벤트 목록 페이지 URL</strong>과 <strong>이벤트/제목 컴포넌트 경로</strong>는 모두 필수 입력값입니다.
        </p>
        <div style={{ backgroundColor: '#f0f8ff', padding: '12px', borderRadius: '6px', border: '1px solid #cce5ff', color: '#004085', marginBottom: '16px', fontSize: '14px', lineHeight: '1.5' }}>
          💡 <strong>팁: "AeroFinder Scraper" 크롬 확장 프로그램</strong>을 설치하고 이벤트 웹페이지에서 요소를 직접 클릭하면 정확한 컴포넌트 <strong>경로를 자동 복사</strong>하여 아래 입력란에 빠르고 정확하게 붙여넣을 수 있습니다!
        </div>
        <ul className="list urls">
          {urls.map((u) => (
            <li key={u.id} className="url-row">
              <div className="url-main">
                <a href={u.url} target="_blank" rel="noopener noreferrer" className="url-link">{u.url}</a>
                <button type="button" className="btn danger small" onClick={() => handleDeleteUrl(u.id)}>삭제</button>
              </div>
              <div className="url-selectors">
                <label className="selector-row">
                  <span className="selector-label">이벤트 페이지 컴포넌트 <span className="required">*</span></span>
                  <input
                    type="text"
                    placeholder="예: div.item (확장프로그램 활용 권장)"
                    value={editingListSelector[u.id] !== undefined ? editingListSelector[u.id] : (u.list_link_selector || '')}
                    onChange={(e) => setEditingListSelector((s) => ({ ...s, [u.id]: e.target.value }))}
                    className="input small"
                    style={{ fontFamily: "monospace" }}
                    required
                  />
                </label>
                <label className="selector-row">
                  <span className="selector-label">제목 컴포넌트 <span className="required">*</span></span>
                  <input
                    type="text"
                    placeholder="예: h1.title (확장프로그램 활용 권장)"
                    value={editingTitleSelector[u.id] !== undefined ? editingTitleSelector[u.id] : (u.detail_title_selector || '')}
                    onChange={(e) => setEditingTitleSelector((s) => ({ ...s, [u.id]: e.target.value }))}
                    className="input small"
                    style={{ fontFamily: "monospace" }}
                    required
                  />
                </label>
                <label className="selector-row">
                  <span className="selector-label">기간 컴포넌트 (선택)</span>
                  <input
                    type="text"
                    placeholder="예: span.date"
                    value={editingPeriodSelector[u.id] !== undefined ? editingPeriodSelector[u.id] : (u.list_period_selector || '')}
                    onChange={(e) => setEditingPeriodSelector((s) => ({ ...s, [u.id]: e.target.value }))}
                    className="input small"
                    style={{ fontFamily: "monospace" }}
                  />
                </label>
                <label className="selector-row">
                  <span className="selector-label">다음 페이지 버튼 (선택)</span>
                  <input
                    type="text"
                    placeholder="예: ul.paging > li.next > a"
                    value={editingNextSelector[u.id] !== undefined ? editingNextSelector[u.id] : (u.list_next_selector || '')}
                    onChange={(e) => setEditingNextSelector((s) => ({ ...s, [u.id]: e.target.value }))}
                    className="input small"
                    style={{ fontFamily: "monospace" }}
                  />
                </label>
                <button
                  type="button"
                  className="btn primary small"
                  onClick={() => handleUpdateUrlSelectors(
                    u.id,
                    editingListSelector[u.id] !== undefined ? editingListSelector[u.id] : (u.list_link_selector || ''),
                    editingTitleSelector[u.id] !== undefined ? editingTitleSelector[u.id] : (u.detail_title_selector || ''),
                    editingPeriodSelector[u.id] !== undefined ? editingPeriodSelector[u.id] : (u.list_period_selector || ''),
                    editingNextSelector[u.id] !== undefined ? editingNextSelector[u.id] : (u.list_next_selector || '')
                  )}
                >
                  적용
                </button>
              </div>
            </li>
          ))}
        </ul>
        <form onSubmit={handleAddUrl} className="add-form add-url-form">
          <label>
            <span className="input-label">이벤트 목록 페이지 URL <span className="required">*</span></span>
            <input
              type="url"
              placeholder="https://..."
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
              className="input"
              required
            />
          </label>
          <label>
            <span className="input-label">이벤트 페이지 컴포넌트 <span className="required">*</span></span>
            <input
              type="text"
              placeholder="예: div.item (확장프로그램 활용 권장)"
              value={newLinkSelector}
              onChange={(e) => setNewLinkSelector(e.target.value)}
              className="input"
              style={{ fontFamily: "monospace" }}
              required
            />
          </label>
          <label>
            <span className="input-label">제목 컴포넌트 <span className="required">*</span></span>
            <input
              type="text"
              placeholder="예: h1.title (확장프로그램 활용 권장)"
              value={newTitleSelector}
              onChange={(e) => setNewTitleSelector(e.target.value)}
              className="input"
              style={{ fontFamily: "monospace" }}
              required
            />
          </label>
          <label>
            <span className="input-label">기간 컴포넌트 (선택)</span>
            <input
              type="text"
              placeholder="예: span.date"
              value={newPeriodSelector}
              onChange={(e) => setNewPeriodSelector(e.target.value)}
              className="input"
              style={{ fontFamily: "monospace" }}
            />
          </label>
          <label>
            <span className="input-label">다음 페이지 버튼 (선택)</span>
            <input
              type="text"
              placeholder="예: ul.paging > li.next > a"
              value={newNextSelector}
              onChange={(e) => setNewNextSelector(e.target.value)}
              className="input"
              style={{ fontFamily: "monospace" }}
            />
          </label>
          <button type="submit" className="btn primary">URL 추가</button>
        </form>
      </section>

      <section className="section">
        <h2>키워드 (특가 판별용)</h2>
        <p className="hint">이 항공사 + 공통 키워드가 표시됩니다.</p>
        <ul className="list keywords">
          {keywords.map((k) => (
            <li key={k.id}>
              <span className="keyword-text">{k.keyword}</span>
              {k.airline_id ? (
                <button type="button" className="btn danger small" onClick={() => handleDeleteKeyword(k.id)}>삭제</button>
              ) : (
                <span className="badge">공통</span>
              )}
            </li>
          ))}
        </ul>
        <form onSubmit={handleAddKeyword} className="add-form">
          <input
            type="text"
            placeholder="예: 특가, 프로모션"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            className="input"
          />
          <button type="submit" className="btn primary">키워드 추가</button>
        </form>
      </section>

      <section className="section danger-zone" style={{ marginTop: '2rem', border: '1px solid #ff4d4f', padding: '1.5rem', borderRadius: '8px' }}>
        <h2 style={{ color: '#ff4d4f', marginTop: 0 }}>위험 구역 (Danger Zone)</h2>
        
        <div style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px dotted #ff4d4f' }}>
          <p className="hint">
            <strong>크롤링 데이터 초기화:</strong> 이 항공사에서 수집된 모든 이벤트(Notice)와 특가(Deal) 정보를 삭제하고 크롤링 상태를 초기화합니다. (URL과 키워드는 유지됩니다)
          </p>
          <button type="button" className="btn danger" onClick={handleDeleteData}>
            크롤링 데이터 초기화
          </button>
        </div>

        <div>
          <p className="hint">
            <strong>항공사 삭제:</strong> 항공사를 삭제하면 등록된 URL, 수집된 이벤트/특가 정보, 키워드 등이 <strong>모두 영구적으로 삭제</strong>됩니다.
          </p>
          <button type="button" className="btn danger" onClick={handleDeleteAirline}>
            이 항공사 삭제
          </button>
        </div>
      </section>
    </div>
  );
}
