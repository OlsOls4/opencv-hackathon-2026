const view=document.getElementById('view'),video=document.getElementById('video'),canvas=document.getElementById('canvas');
const stateEl=document.getElementById('state'),countsEl=document.getElementById('counts'),latEl=document.getElementById('latency'),errEl=document.getElementById('err');
const banner=document.getElementById('alertBanner'),alertText=document.getElementById('alertText');
let stream=null,timer=null;
function showAlert(a){if(a){banner.style.display='block';alertText.textContent='In-dashboard alert only (no SMS, email, or push sent): shelf state '+a.state+' sustained since '+a.triggered_at+'. Restock and re-baseline to clear.';}else{banner.style.display='none';alertText.textContent='';}}
document.getElementById('dismissBtn').onclick=async()=>{await fetch('/api/alerts/dismiss',{method:'POST'});showAlert(null);};
function show(r){if(r.error){errEl.textContent=r.error;return;}errEl.textContent='';
  showAlert(r.active_alert||null);
  if(r.annotated_image_base64) view.src='data:image/jpeg;base64,'+r.annotated_image_base64;
  stateEl.textContent='State: '+(r.state||'—')+(r.changed_ratio!=null?' (changed '+(r.changed_ratio*100).toFixed(1)+'%)':'');
  countsEl.textContent='Counts: '+JSON.stringify(r.counts)+' · Total: '+r.total;
  latEl.textContent='Latency: '+r.latency_ms+' ms · Model: '+r.model+' · Threshold: '+r.threshold;}
async function post(file,url){const fd=new FormData();fd.append('file',file);const conf=document.getElementById('conf').value;
  const res=await fetch(url+(url.includes('?')?'&':'?')+'conf='+conf,{method:'POST',body:fd});return res.json();}
document.getElementById('demoBtn').onclick=async()=>{const r=await fetch('/api/demo').then(x=>x.json());show(r);};
document.getElementById('resetBtn').onclick=async()=>{await fetch('/api/session/reset',{method:'POST'});countsEl.textContent='—';showAlert(null);};
document.getElementById('csvBtn').onclick=()=>{window.location='/api/export.csv';};
document.getElementById('conf').oninput=e=>{document.getElementById('confVal').textContent=e.target.value;};
document.getElementById('upload').onchange=async e=>{if(e.target.files[0]) show(await post(e.target.files[0],'/api/upload'));};
document.getElementById('snapBtn').onclick=async()=>{const blob=await captureBlob();if(!blob){errEl.textContent='Start the webcam first for a snapshot.';return;}
  const r=await post(blob,'/api/snapshot');if(r.annotated_image_base64) view.src='data:image/jpeg;base64,'+r.annotated_image_base64;
  errEl.textContent=r.label||r.error||'';};
document.getElementById('baseBtn').onclick=async()=>{const blob=await captureBlob();if(!blob){errEl.textContent='Start the webcam first to capture a baseline. Uploading a photo does not set the baseline in this version.';return;}
  const fd=new FormData();fd.append('file',blob);const r=await fetch('/api/baseline',{method:'POST',body:fd}).then(x=>x.json());errEl.textContent=r.status||r.error||'';if(!r.error) showAlert(null);};
async function captureBlob(){if(!stream) return null;canvas.width=video.videoWidth||640;canvas.height=video.videoHeight||480;
  canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);return new Promise(res=>canvas.toBlob(res,'image/jpeg',0.85));}
document.getElementById('camBtn').onclick=async()=>{
  if(stream){clearInterval(timer);stream.getTracks().forEach(t=>t.stop());stream=null;document.getElementById('camBtn').textContent='Start webcam';return;}
  try{stream=await navigator.mediaDevices.getUserMedia({video:true});video.srcObject=stream;video.style.display='block';
    document.getElementById('camBtn').textContent='Stop webcam';
    timer=setInterval(async()=>{const blob=await captureBlob();if(blob) show(await post(blob,'/api/frame'));},300);
  }catch(e){errEl.textContent='Camera denied — try Demo shelf or Upload.';}};
