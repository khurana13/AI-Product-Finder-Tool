document.addEventListener('DOMContentLoaded', function() {
  const chatBtn = document.getElementById('chatBtn');
  const chatQuery = document.getElementById('chatQuery');
  const chatResult = document.getElementById('chatResult');

  const searchBtn = document.getElementById('searchBtn');
  const category = document.getElementById('category');
  const minPrice = document.getElementById('minPrice');
  const maxPrice = document.getElementById('maxPrice');
  const searchResult = document.getElementById('searchResult');
  const fieldsInput = document.getElementById('fields');

  // admin
  const adminTokenInput = document.getElementById('adminToken');
  const rebuildBtn = document.getElementById('rebuildBtn');
  const rotateBtn = document.getElementById('rotateBtn');
  const adminResult = document.getElementById('adminResult');

  // pagination state
  let currentPage = 1;
  let lastQueryParams = null;

  // Helper to show loading spinner
  function showLoading(element, message = 'Loading...') {
    element.innerHTML = `<div style="display:flex;align-items:center;gap:8px;color:#888"><span class="loading"></span>${message}</div>`;
  }

  chatBtn.addEventListener('click', async () => {
    const q = chatQuery.value.trim();
    if (!q) return;
    showLoading(chatResult, 'Searching...');
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: q, top_k: 5})
      });
      const j = await res.json();
      if (j.error) {
        chatResult.innerHTML = `<div style="color:#ff6b6b">❌ Error: ${j.error}</div>`;
        return;
      }
      chatResult.innerHTML = '';
      if (!j.hits || j.hits.length === 0) {
        chatResult.innerHTML = '<div style="color:#888">No matches found. Try different keywords.</div>';
        return;
      }
      j.hits.forEach((h, idx) => {
        const el = document.createElement('div');
        el.className = 'hit';
        el.style.animationDelay = `${idx * 0.1}s`;
        const title = document.createElement('div');
        title.className = 'hit-title';
        title.innerText = `${h.meta.category.toUpperCase()} — Relevance: ${(h.score * 100).toFixed(1)}%`;
        el.appendChild(title);
        const pre = document.createElement('pre');
        pre.innerText = JSON.stringify(h.row, null, 2);
        el.appendChild(pre);
        chatResult.appendChild(el);
      });
    } catch (e) {
      chatResult.innerHTML = `<div style="color:#ff6b6b">❌ Fetch error: ${e}</div>`;
    }
  });

  searchBtn.addEventListener('click', async () => {
    currentPage = 1;
    await doSearch();
  });

  async function doSearch(page = 1) {
    const cat = category.value;
    const min_p = parseFloat(minPrice.value) || 0;
    const max_p = parseFloat(maxPrice.value) || 1e18;
    const fields = fieldsInput.value.trim();
    lastQueryParams = {category: cat, filters: {}, min_price: min_p, max_price: max_p, page: page, page_size: 10, fields: fields};
    showLoading(searchResult, 'Searching products...');
    try {
      const res = await fetch('/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(lastQueryParams)
      });
      const j = await res.json();
      if (j.error) {
        searchResult.innerHTML = `<div style="color:#ff6b6b">❌ Error: ${j.error}</div>`;
        return;
      }
      searchResult.innerHTML = '';
      if (!j.results || j.results.length === 0) {
        searchResult.innerHTML = '<div style="color:#888">No products found. Try adjusting filters.</div>';
        renderPagination(j.count, j.page || 1, j.page_size || 10);
        return;
      }
      j.results.forEach((r, idx) => {
        const el = document.createElement('div');
        el.className = 'hit';
        el.style.animationDelay = `${idx * 0.08}s`;
        const title = document.createElement('div');
        title.className = 'hit-title';
        title.innerText = `🏷️ ${r.name || r.model || r.title || r.brand || 'Product'}`;
        el.appendChild(title);
        const pre = document.createElement('pre');
        pre.innerText = JSON.stringify(r, null, 2);
        el.appendChild(pre);
        searchResult.appendChild(el);
      });
      renderPagination(j.count, j.page || 1, j.page_size || 10);
    } catch (e) {
      searchResult.innerHTML = `<div style="color:#ff6b6b">❌ Fetch error: ${e}</div>`;
    }
  }

  function renderPagination(total, page, page_size) {
    const pages = Math.ceil(total / page_size);
    const pager = document.createElement('div');
    pager.style.marginTop = '16px';
    pager.style.padding = '12px';
    pager.style.background = 'rgba(255,255,255,0.05)';
    pager.style.borderRadius = '8px';
    pager.style.display = 'flex';
    pager.style.alignItems = 'center';
    pager.style.justifyContent = 'space-between';
    pager.innerHTML = `<span style="color:#a78bfa">Page ${page} of ${pages} • Total: ${total} products</span>`;
    const btnGroup = document.createElement('div');
    btnGroup.style.display = 'flex';
    btnGroup.style.gap = '8px';
    const prev = document.createElement('button'); prev.innerText = '← Prev';
    const next = document.createElement('button'); next.innerText = 'Next →';
    prev.disabled = page <= 1; next.disabled = page >= pages;
    prev.onclick = async () => { if (page>1) { currentPage = page-1; await doSearch(currentPage); }};
    next.onclick = async () => { if (page<pages) { currentPage = page+1; await doSearch(currentPage); }};
    btnGroup.appendChild(prev); btnGroup.appendChild(next);
    pager.appendChild(btnGroup);
    searchResult.appendChild(pager);
  }

  // admin handlers
  rebuildBtn.addEventListener('click', async () => {
    showLoading(adminResult, 'Rebuilding index...');
    try {
      const token = adminTokenInput.value.trim();
      const headers = {'Content-Type': 'application/json'};
      if (token) headers['X-Admin-Token'] = token;
      const res = await fetch('/admin/rebuild', {method: 'POST', headers});
      const j = await res.json();
      if (j.error) adminResult.innerHTML = `<div style="color:#ff6b6b">❌ ${j.error}</div>`;
      else adminResult.innerHTML = `<div style="color:#51cf66">✅ ${JSON.stringify(j, null, 2)}</div>`;
    } catch (e) { adminResult.innerHTML = `<div style="color:#ff6b6b">❌ Fetch error: ${e}</div>`; }
  });

  rotateBtn.addEventListener('click', async () => {
    showLoading(adminResult, 'Rotating token...');
    try {
      const token = adminTokenInput.value.trim();
      const headers = {'Content-Type': 'application/json'};
      if (token) headers['X-Admin-Token'] = token;
      const res = await fetch('/admin/rotate', {method: 'POST', headers});
      const j = await res.json();
      if (j.error) adminResult.innerHTML = `<div style="color:#ff6b6b">❌ ${j.error}</div>`;
      else adminResult.innerHTML = `<div style="color:#51cf66">✅ New token: <code style="background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:4px">${j.token}</code><br><small>${j.note || ''}</small></div>`;
    } catch (e) { adminResult.innerHTML = `<div style="color:#ff6b6b">❌ Fetch error: ${e}</div>`; }
  });

  // reset password handler
  const resetBtn = document.getElementById('resetBtn');
  const newUsernameInput = document.getElementById('newUsername');
  const newPasswordInput = document.getElementById('newPassword');
  const resetResult = document.getElementById('resetResult');

  resetBtn.addEventListener('click', async () => {
    showLoading(resetResult, 'Resetting password...');
    try {
      const token = adminTokenInput.value.trim();
      const headers = {'Content-Type': 'application/json'};
      if (token) headers['X-Admin-Token'] = token;
      const body = {username: newUsernameInput.value.trim(), password: newPasswordInput.value};
      const res = await fetch('/admin/reset_password', {method: 'POST', headers, body: JSON.stringify(body)});
      const j = await res.json();
      if (j.error) resetResult.innerHTML = `<div style="color:#ff6b6b">❌ ${j.error}</div>`;
      else resetResult.innerHTML = `<div style="color:#51cf66">✅ ${JSON.stringify(j, null, 2)}</div>`;
    } catch (e) { resetResult.innerHTML = `<div style="color:#ff6b6b">❌ Fetch error: ${e}</div>`; }
  });
});
