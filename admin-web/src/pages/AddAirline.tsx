import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api';
import './AddAirline.css';

export default function AddAirline() {
  const navigate = useNavigate();
  const [fetchUrl, setFetchUrl] = useState('');
  const [fetching, setFetching] = useState(false);
  const [name, setName] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [initialUrls, setInitialUrls] = useState('');
  const [initialLinkSelector, setInitialLinkSelector] = useState('');
  const [initialTitleSelector, setInitialTitleSelector] = useState('');
  const [initialPeriodSelector, setInitialPeriodSelector] = useState('');
  const [initialNextSelector, setInitialNextSelector] = useState('');
  const [initialKeywords, setInitialKeywords] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);



  const handleFetchSiteInfo = (e) => {
    e.preventDefault();
    if (!fetchUrl.trim()) return;
    setFetching(true);
    setError(null);
    api.admin.siteInfo(fetchUrl.trim())
      .then(({ name: n, logo_url: l }) => {
        if (n) setName(n);
        if (l) setLogoUrl(l);
        if (!baseUrl) setBaseUrl(new URL(fetchUrl.trim()).origin);
      })
      .catch((e) => setError(e.message))
      .finally(() => setFetching(false));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !baseUrl.trim()) {
      setError('항공사 이름과 기본 URL은 필수입니다.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const airline = await api.airlines.create({
        name: name.trim(),
        base_url: baseUrl.trim(),
        logo_url: logoUrl.trim() || undefined,
      });
      const urlList = initialUrls.split(/[\n,]/).map((s) => s.trim()).filter(Boolean);
      const keywordList = initialKeywords.split(/[\n,]/).map((s) => s.trim()).filter(Boolean);
      const linkSelector = initialLinkSelector.trim();
      const titleSelector = initialTitleSelector.trim();
      const periodSelector = initialPeriodSelector.trim();
      const nextSelector = initialNextSelector.trim();
      
      if (urlList.length > 0 && (!linkSelector || !titleSelector)) {
        throw new Error('이벤트 URL을 입력한 경우 이벤트 컴포넌트 경로(선택자)는 필수입니다.');
      }
      for (const url of urlList) {
        await api.airlines.addUrl(airline.id, url, linkSelector, titleSelector, periodSelector, nextSelector);
      }
      for (const kw of keywordList) {
        await api.keywords.create(kw, airline.id);
      }
      navigate(`/airline/${airline.id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page add-airline">
      <header className="header">
        <h1>항공사 추가</h1>
        <Link to="/" className="btn">← 목록</Link>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="section">
        <h2>URL에서 이름·로고 가져오기 (선택)</h2>
        <form onSubmit={handleFetchSiteInfo} className="fetch-form">
          <input
            type="url"
            placeholder="https://항공사이벤트페이지..."
            value={fetchUrl}
            onChange={(e) => setFetchUrl(e.target.value)}
            className="input"
          />
          <button type="submit" className="btn primary" disabled={fetching}>
            {fetching ? '가져오는 중...' : '가져오기'}
          </button>
        </form>
      </section>

      <form onSubmit={handleSubmit} className="form">
        <section className="section">
          <h2>기본 정보</h2>
          <label>
            항공사 이름 <span className="required">*</span>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="예: 대한항공"
              className="input"
              required
            />
          </label>
          <label>
            기본 URL (사이트 주소) <span className="required">*</span>
            <input
              type="url"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="https://..."
              className="input"
              required
            />
          </label>
          <label>
            로고 URL (선택)
            <input
              type="url"
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              placeholder="https://..."
              className="input"
            />
          </label>
        </section>

        <section className="section">
          <h2>이벤트 목록 페이지 URL · 컴포넌트</h2>
          <p className="hint">이벤트 목록 페이지 URL을 한 줄에 하나, 또는 쉼표로 구분해 입력하세요. URL 등록 시 이벤트/제목 컴포넌트는 필수값입니다.</p>
          <div style={{ backgroundColor: '#f0f8ff', padding: '12px', borderRadius: '6px', border: '1px solid #cce5ff', color: '#004085', marginBottom: '16px', fontSize: '14px', lineHeight: '1.5' }}>
            💡 <strong>팁: "AeroFinder Scraper" 크롬 확장 프로그램</strong>을 설치하고 이벤트 웹페이지에서 요소를 직접 클릭하면 정확한 컴포넌트 <strong>경로를 자동 복사</strong>하여 아래 입력란에 빠르고 정확하게 붙여넣을 수 있습니다!
          </div>
          <label>
            <span className="input-label">이벤트 목록 페이지 URL <span className="required">*</span></span>
            <textarea
              value={initialUrls}
              onChange={(e) => setInitialUrls(e.target.value)}
              placeholder="https://www.koreanair.com/event/..."
              className="textarea"
              rows={4}
              required
            />
          </label>
          <label>
            <span className="input-label">이벤트 페이지 컴포넌트 <span className="required">*</span></span>
            <input
              type="text"
              value={initialLinkSelector}
              onChange={(e) => setInitialLinkSelector(e.target.value)}
              placeholder="예: div.promo-list > div.item (확장 프로그램으로 복사 후 붙여넣기)"
              className="input"
              style={{ fontFamily: "monospace" }}
              required
            />
          </label>
          <label>
            <span className="input-label">제목 컴포넌트 <span className="required">*</span></span>
            <input
              type="text"
              value={initialTitleSelector}
              onChange={(e) => setInitialTitleSelector(e.target.value)}
              placeholder="예: h1.event-title (확장 프로그램으로 복사 후 붙여넣기)"
              className="input"
              style={{ fontFamily: "monospace" }}
              required
            />
          </label>
          <label>
            <span className="input-label">기간 컴포넌트 (선택)</span>
            <input
              type="text"
              value={initialPeriodSelector}
              onChange={(e) => setInitialPeriodSelector(e.target.value)}
              placeholder="예: span.date (이벤트 날짜를 추출할 텍스트 컴포넌트)"
              className="input"
              style={{ fontFamily: "monospace" }}
            />
          </label>
          <label>
            <span className="input-label">다음 페이지 버튼 (선택)</span>
            <input
              type="text"
              value={initialNextSelector}
              onChange={(e) => setInitialNextSelector(e.target.value)}
              placeholder="예: ul.paging > li.next > a (여러 페이지 이벤트 수집용)"
              className="input"
              style={{ fontFamily: "monospace" }}
            />
          </label>
        </section>

        <section className="section">
          <h2>키워드 (특가 판별용)</h2>
          <p className="hint">한 줄에 하나, 또는 쉼표로 구분. 예: 특가, 프로모션, 할인</p>
          <textarea
            value={initialKeywords}
            onChange={(e) => setInitialKeywords(e.target.value)}
            placeholder="특가, 프로모션, 할인"
            className="textarea"
            rows={3}
          />
        </section>

        <div className="form-actions">
          <button type="submit" className="btn primary" disabled={submitting}>
            {submitting ? '저장 중...' : '항공사 추가'}
          </button>
          <Link to="/" className="btn">취소</Link>
        </div>
      </form>
    </div>
  );
}
