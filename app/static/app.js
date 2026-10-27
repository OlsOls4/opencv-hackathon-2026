/* ShelfScan dashboard — same API routes as before, plain-language UI only.
   Endpoints: /api/demo, /api/frame, /api/upload, /api/baseline,
   /api/snapshot, /api/session/reset, /api/export.csv, /api/alerts/dismiss */
const view = document.getElementById('view');
const viewEmpty = document.getElementById('viewEmpty');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const stateBadge = document.getElementById('stateBadge');
const stateIcon = document.getElementById('stateIcon');
const stateText = document.getElementById('stateText');
const stateAction = document.getElementById('stateAction');
const changeBar = document.getElementById('changeBar');
const changeText = document.getElementById('changeText');
const countEstimate = document.getElementById('countEstimate');
const lastUpdated = document.getElementById('lastUpdated');
const errEl = document.getElementById('err');
const banner = document.getElementById('alertBanner');
const alertTitle = document.getElementById('alertTitle');
const alertText = document.getElementById('alertText');
const camBtn = document.getElementById('camBtn');
const baseBtn = document.getElementById('baseBtn');

let stream = null;
let timer = null;

const STATES = {
  'Full': { cls: 'state-full', icon: '✓', action: 'Shelf looks full. No action needed.' },
  'Low': { cls: 'state-low', icon: '!', action: 'Some items are missing. Check this shelf soon.' },
  'Gap': { cls: 'state-gap', icon: '!', action: 'A clear empty area was found. Restock this shelf now.' },
  'Check shelf': { cls: 'state-check', icon: '?', action: 'Lighting or camera moved, so this reading may not be trusted. Fix the camera or lighting, then re-capture if the shelf is full.' },
  'No baseline': { cls: 'state-none', icon: '○', action: 'Capture a full shelf first, then ShelfScan can watch it for you.' },
};

function showAlert(a) {
  if (!a) { banner.hidden = true; alertText.textContent = ''; return; }
  banner.hidden = false;
  alertTitle.textContent = a.state === 'Gap' ? 'Restock needed' : 'Check this shelf soon';
  alertText.textContent = 'Shelf state ' + a.state + ' has held since ' + a.triggered_at + '. Restock and re-capture the full shelf to clear it. No message is sent anywhere else.';
}

function show(r) {
  if (!r) return;
  if (r.error) { errEl.textContent = r.error; return; }
  errEl.textContent = '';
  showAlert(r.active_alert || null);
  if (r.annotated_image_base64) {
    view.src = 'data:image/jpeg;base64,' + r.annotated_image_base64;
    view.hidden = false;
    viewEmpty.hidden = true;
  }
  const info = STATES[r.state] || STATES['No baseline'];
  stateBadge.className = 'state-badge ' + info.cls;
  stateIcon.textContent = info.icon;
  stateText.textContent = r.state || 'No shelf checked yet';
  stateAction.textContent = info.action;
  if (r.changed_ratio != null) {
    const pct = r.changed_ratio * 100;
    changeText.textContent = pct.toFixed(1) + '% changed';
    changeBar.style.width = Math.min(100, pct) + '%';
    changeBar.className = 'meter-fill' + (pct >= 30 ? ' danger' : pct >= 10 ? ' warn' : '');
  }
  if (r.total != null) {
    countEstimate.textContent = 'About ' + r.total + (r.total === 1 ? ' product' : ' products');
  }
  lastUpdated.textContent = 'Updated ' + new Date().toLocaleTimeString();
}

async function post(file, url) {
  const fd = new FormData();
  fd.append('file', file);
  const conf = document.getElementById('conf').value;
  const res = await fetch(url + (url.includes('?') ? '&' : '?') + 'conf=' + conf, { method: 'POST', body: fd });
  return res.json();
}

function busy(btn, on) { btn.disabled = on; }

document.getElementById('dismissBtn').onclick = async () => {
  await fetch('/api/alerts/dismiss', { method: 'POST' });
  showAlert(null);
};

document.getElementById('demoBtn').onclick = async (e) => {
  busy(e.currentTarget, true);
  try { show(await fetch('/api/demo').then((x) => x.json())); }
  catch { errEl.textContent = 'Demo shelf is not available right now. Try again.'; }
  busy(e.currentTarget, false);
};

document.getElementById('resetBtn').onclick = async () => {
  await fetch('/api/session/reset', { method: 'POST' });
  showAlert(null);
  stateBadge.className = 'state-badge state-none';
  stateText.textContent = 'No shelf checked yet';
  stateAction.textContent = STATES['No baseline'].action;
  countEstimate.textContent = '—';
  changeText.textContent = '—';
  changeBar.style.width = '0%';
  lastUpdated.textContent = 'Session reset';
};

document.getElementById('csvBtn').onclick = () => { window.location = '/api/export.csv'; };

document.getElementById('conf').oninput = (e) => {
  document.getElementById('confVal').textContent = e.target.value;
};

document.getElementById('upload').onchange = async (e) => {
  if (e.target.files[0]) show(await post(e.target.files[0], '/api/upload'));
  e.target.value = '';
};

document.getElementById('snapBtn').onclick = async () => {
  const blob = await captureBlob();
  if (!blob) { errEl.textContent = 'Start the camera first, then try outlining an item.'; return; }
  const r = await post(blob, '/api/snapshot');
  if (r.annotated_image_base64) {
    view.src = 'data:image/jpeg;base64,' + r.annotated_image_base64;
    view.hidden = false;
    viewEmpty.hidden = true;
  }
  errEl.textContent = r.error || '';
};

baseBtn.onclick = async () => {
  const blob = await captureBlob();
  if (!blob) {
    errEl.textContent = 'Start the camera first to capture a full shelf. A photo upload does not set the full shelf.';
    return;
  }
  busy(baseBtn, true);
  const fd = new FormData();
  fd.append('file', blob);
  const r = await fetch('/api/baseline', { method: 'POST', body: fd }).then((x) => x.json());
  busy(baseBtn, false);
  if (r.error) { errEl.textContent = r.error; return; }
  errEl.textContent = '';
  showAlert(null);
  stateBadge.className = 'state-badge state-full';
  stateIcon.textContent = '✓';
  stateText.textContent = 'Full';
  stateAction.textContent = 'Full shelf captured. ShelfScan is now watching this shelf.';
  changeText.textContent = '0% changed';
  changeBar.style.width = '0%';
  changeBar.className = 'meter-fill';
};

async function captureBlob() {
  if (!stream) return null;
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  return new Promise((res) => canvas.toBlob(res, 'image/jpeg', 0.85));
}

camBtn.onclick = async () => {
  if (stream) {
    clearInterval(timer);
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
    video.hidden = true;
    camBtn.textContent = 'Stop camera';
    return;
  }
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.hidden = false;
    viewEmpty.hidden = true;
    camBtn.textContent = 'Stop camera';
    timer = setInterval(async () => {
      const blob = await captureBlob();
      if (blob) show(await post(blob, '/api/frame'));
    }, 300);
  } catch {
    errEl.textContent = 'Camera was not allowed — try the demo shelf or upload a photo instead.';
  }
};
