const API_BASE = import.meta.env.VITE_API_URL || '';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const msg = Array.isArray(data?.detail) ? data.detail.map((d) => d.msg || JSON.stringify(d)).join(', ') : (data?.detail || res.statusText || res.status);
    throw new Error(msg);
  }
  return data;
}

export const api = {
  airlines: {
    list: () => request('/api/airlines'),
    get: (id) => request(`/api/airlines/${id}`),
    create: (body) => request('/api/airlines', { method: 'POST', body: JSON.stringify(body) }),
    update: (id, body) => request(`/api/airlines/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    delete: (id) => request(`/api/airlines/${id}`, { method: 'DELETE' }),
    deleteData: (airlineId) => request(`/api/airlines/${airlineId}/data`, { method: 'DELETE' }),
    listUrls: (airlineId) => request(`/api/airlines/${airlineId}/urls`),
    addUrl: (airlineId, url, listLinkSelector = null, detailTitleSelector = null, listPeriodSelector = null, listNextSelector = null) =>
      request(`/api/airlines/${airlineId}/urls`, {
        method: 'POST',
        body: JSON.stringify({
          url,
          list_link_selector: listLinkSelector || undefined,
          detail_title_selector: detailTitleSelector || undefined,
          list_period_selector: listPeriodSelector || undefined,
          list_next_selector: listNextSelector || undefined,
        }),
      }),
    updateUrl: (airlineId, urlId, body) =>
      request(`/api/airlines/${airlineId}/urls/${urlId}`, { method: 'PATCH', body: JSON.stringify(body) }),
    deleteUrl: (airlineId, urlId) => request(`/api/airlines/${airlineId}/urls/${urlId}`, { method: 'DELETE' }),
  },
  keywords: {
    list: (airlineId = null) => request(airlineId ? `/api/keywords?airline_id=${airlineId}` : '/api/keywords'),
    create: (keyword, airlineId = null) =>
      request('/api/keywords', { method: 'POST', body: JSON.stringify({ keyword, airline_id: airlineId }) }),
    delete: (id) => request(`/api/keywords/${id}`, { method: 'DELETE' }),
  },
  notices: {
    list: () => request('/api/notices'),
    toggleDeal: (id, isSpecialDeal) => request(`/api/notices/${id}/toggle_deal`, {
      method: 'PUT',
      body: JSON.stringify({ is_special_deal: isSpecialDeal })
    })
  },
  admin: {
    siteInfo: (url) => request(`/api/admin/site-info?url=${encodeURIComponent(url)}`),
    triggerCrawl: () => request('/api/admin/crawl', { method: 'POST' }),
    sendPush: (body) => request('/api/admin/push', { method: 'POST', body: JSON.stringify(body) }),
  },
};
