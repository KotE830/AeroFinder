import { useState } from 'react';
import { api } from '../api';
import './PushNotification.css';

export default function PushNotification() {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState('');

  const handleSend = async (e) => {
    e.preventDefault();
    if (!title.trim() || !body.trim()) {
      alert('제목과 내용을 모두 입력해주세요.');
      return;
    }

    setSending(true);
    setResult('');
    
    try {
      const res = await api.admin.sendPush({ title, body, topic: 'all_users' });
      setResult(`전송 성공! (ID: ${res.message_id})`);
      setTitle('');
      setBody('');
    } catch (error) {
      setResult(`전송 실패: ${error.message}`);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="page push-notification">
      <header className="header">
        <h1>알림 발송 (전체 사용자)</h1>
        <div className="header-actions">
          <button type="button" className="btn warning" onClick={() => window.history.back()}>
            뒤로 가기
          </button>
        </div>
      </header>
      <main className="push-form-container">
        <form onSubmit={handleSend} className="push-form">
          <div className="form-group">
            <label htmlFor="title">알림 제목</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="예: 제주항공 특가 오픈!"
              maxLength={50}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="body">알림 내용</label>
            <textarea
              id="body"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="예: 지금 바로 앱에서 확인하세요!"
              rows={4}
              maxLength={200}
              required
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn primary push-btn" disabled={sending}>
              {sending ? '전송 중...' : '알림 발송하기'}
            </button>
          </div>
          {result && (
            <div className={`result-message ${result.includes('성공') ? 'success' : 'error'}`}>
              {result}
            </div>
          )}
        </form>
      </main>
    </div>
  );
}
