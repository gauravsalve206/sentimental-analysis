const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const colors = {Positive:'#1aa981',Negative:'#dc6680',Neutral:'#d99a45'};
const charts = {};

function toast(message) {
  const el = $('#toast'); el.textContent = message; el.classList.add('show');
  clearTimeout(el.timer); el.timer = setTimeout(() => el.classList.remove('show'), 2600);
}

function navigate(page) {
  $$('.page').forEach(el => el.classList.remove('active'));
  $('#' + page)?.classList.add('active');
  $$('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.page === page));
  const titles = {home:'Good morning',analyzer:'Review analyzer',bulk:'Bulk analysis',analytics:'Product analytics',comparison:'Product comparison',model:'Model performance'};
  $('#pageTitle').textContent = titles[page] || 'Reviewly';
  $('.sidebar')?.classList.remove('open');
  if (page === 'analytics') loadAnalytics();
  if (page === 'model') loadModel();
  if (page === 'comparison') loadProducts();
}

$$('[data-page]').forEach(el => el.addEventListener('click', e => { e.preventDefault(); navigate(el.dataset.page); }));
$$('[data-go]').forEach(el => el.addEventListener('click', () => navigate(el.dataset.go)));
$('#menuButton').addEventListener('click', () => $('.sidebar').classList.toggle('open'));

function chart(canvas, config) {
  if (charts[canvas.id]) charts[canvas.id].destroy();
  charts[canvas.id] = new Chart(canvas, config);
}

async function loadHome() {
  try {
    const data = await fetch('/api/analytics').then(r => r.json());
    if (!data.error) {
      $('#totalReviews').textContent = data.total.toLocaleString();
      const positive = data.sentiment.Positive || 0;
      $('#positiveRate').textContent = data.total ? ((positive / data.total) * 100).toFixed(1) + '%' : '—';
      $('#averageRating').textContent = data.averageRating ? data.averageRating.toFixed(2) : '—';
      chart($('#homeChart'), doughnutConfig(data.sentiment));
    }
  } catch (_) { toast('Could not load analytics'); }
  const model = await fetch('/api/model').then(r => r.ok ? r.json() : {results:[]});
  const best = model.results?.sort((a,b) => b.f1_macro-a.f1_macro)[0];
  if (best) $('#homeAccuracy').textContent = (best.accuracy * 100).toFixed(1) + '%';
}

function doughnutConfig(counts) {
  const labels = ['Positive','Neutral','Negative'];
  return {type:'doughnut',data:{labels,datasets:[{data:labels.map(x=>counts[x]||0),backgroundColor:labels.map(x=>colors[x]),borderWidth:0,hoverOffset:6}]},options:{responsive:true,maintainAspectRatio:false,cutout:'70%',plugins:{legend:{position:'bottom',labels:{boxWidth:8,usePointStyle:true,padding:18}}}}};
}

let selectedRating = null;
$$('#ratingPicker button').forEach(button => button.addEventListener('click', () => {
  $$('#ratingPicker button').forEach(b => b.classList.remove('active')); button.classList.add('active'); selectedRating = Number(button.dataset.rating);
}));

async function runAnalysis(text, target = '#analysisResults') {
  if (!text.trim()) { toast('Enter a review first'); return; }
  const button = $('#analyzeButton'); if (button) { button.disabled=true; button.textContent='Analyzing...'; }
  try {
    const response = await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,rating:selectedRating})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    renderAnalysis(data,target);
  } catch(error) { toast(error.message); }
  finally { if (button) { button.disabled=false; button.innerHTML='Analyze sentiment <span>→</span>'; } }
}

function renderAnalysis(data,target) {
  const confidence = data.confidence == null ? 0 : Math.round(data.confidence*100);
  const aspects = Object.entries(data.aspects || {});
  const aspectHtml = aspects.length ? aspects.map(([name,value]) => `<div class="aspect-row"><div class="aspect-row-top"><strong>${escapeHtml(name)}</strong><span class="sentiment-badge ${value.sentiment}">${value.sentiment}</span></div><small>${escapeHtml(value.excerpt)}</small></div>`).join('') : '<div class="empty-state" style="min-height:100px"><p>No configured aspects detected.</p></div>';
  const matchHtml = data.rating_sentiment ? `<div class="metric-box"><span>Rating match</span><strong>${data.rating_match?'Matched':'Mismatch detected'}</strong></div>` : '';
  $(target).innerHTML = `<div class="result-header"><div><p class="eyebrow">PREDICTED RESULT</p><span class="sentiment-badge ${data.sentiment}">${data.sentiment}</span></div><div class="confidence-ring" style="--percent:${confidence}%"><strong>${confidence}%</strong></div></div><div class="result-metrics"><div class="metric-box"><span>Detected emotion</span><strong>${escapeHtml(data.emotion)}</strong></div>${matchHtml}</div><p class="eyebrow" style="margin-top:20px">ASPECT INSIGHTS</p><div class="aspect-list">${aspectHtml}</div>`;
}

function escapeHtml(value) { const div=document.createElement('div'); div.textContent=value ?? ''; return div.innerHTML; }
$('#analyzeButton').addEventListener('click', () => runAnalysis($('#reviewText').value));
$('#quickAnalyze').addEventListener('click', () => { navigate('analyzer'); $('#reviewText').value=$('#quickReview').value; runAnalysis($('#quickReview').value); });

async function uploadBulk(file) {
  if (!file) return;
  const form = new FormData(); form.append('file', file);
  $('#bulkResults').innerHTML='<div class="empty-state"><p>Analyzing reviews...</p></div>';
  try {
    const response=await fetch('/api/bulk',{method:'POST',body:form}); const data=await response.json();
    if(!response.ok) throw new Error(data.error);
    const labels=Object.keys(data.summary); const counts=Object.values(data.summary);
    $('#bulkResults').innerHTML=`<div style="text-align:left;width:100%"><div class="result-header"><div><p class="eyebrow">ANALYSIS COMPLETE</p><h3>${data.total.toLocaleString()} reviews</h3></div><button class="secondary-button" id="bulkDone">New upload</button></div><div class="chart-wrap" style="height:180px"><canvas id="bulkChart"></canvas></div><div class="table-scroll"><table><thead><tr><th>Review</th><th>Sentiment</th><th>Confidence</th><th>Emotion</th></tr></thead><tbody>${data.preview.map(row=>`<tr><td>${escapeHtml(String(row.text||row.review_text||'').slice(0,90))}</td><td>${escapeHtml(row.Predicted_Sentiment)}</td><td>${row.Confidence==null?'—':Math.round(row.Confidence*100)+'%'}</td><td>${escapeHtml(row.Detected_Emotion)}</td></tr>`).join('')}</tbody></table></div></div>`;
    chart($('#bulkChart'),{type:'bar',data:{labels,datasets:[{data:counts,backgroundColor:labels.map(x=>colors[x]),borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'#f0f1f5'}},x:{grid:{display:false}}}}});
  } catch(error) { $('#bulkResults').innerHTML=`<div class="empty-state"><p>${escapeHtml(error.message)}</p></div>`; }
}
$('#bulkFile').addEventListener('change',e=>uploadBulk(e.target.files[0]));
const drop=$('#dropZone'); ['dragenter','dragover'].forEach(name=>drop.addEventListener(name,e=>{e.preventDefault();drop.style.borderColor='#6855d9'}));
drop.addEventListener('drop',e=>{e.preventDefault();drop.style.borderColor='#d7d8e4';uploadBulk(e.dataTransfer.files[0])});

async function loadAnalytics(){
  try{const data=await fetch('/api/analytics').then(r=>r.json());if(data.error){toast(data.error);return}$('#analyticsTotal').textContent=data.total.toLocaleString();$('#analyticsPositive').textContent=(data.sentiment.Positive||0).toLocaleString();$('#analyticsNegative').textContent=(data.sentiment.Negative||0).toLocaleString();chart($('#analyticsChart'),doughnutConfig(data.sentiment));$('#healthDetails').innerHTML=`<div class="detail-item"><span>Average rating</span><strong>${data.averageRating??'—'} / 5</strong></div><div class="detail-item"><span>Dataset source</span><strong>Amazon All Beauty</strong></div><div class="detail-item"><span>Label type</span><strong>Rating-derived</strong></div>`;}catch(error){toast('Analytics unavailable')}
}

async function loadProducts(){
  try{const data=await fetch('/api/analytics').then(r=>r.json());const select=$('#productSelect');select.innerHTML=data.products.map(p=>`<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('');if(data.products.length){[0,1].forEach(i=>{if(select.options[i])select.options[i].selected=true})}}catch(error){toast('Could not load products')}
}
$('#runComparison').addEventListener('click',async()=>{const selected=$$('#productSelect option').filter(o=>o.selected).map(o=>o.value);if(!selected.length){toast('Select at least one product');return}const data=await fetch('/api/comparison',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({products:selected})}).then(r=>r.json());if(data.error){toast(data.error);return}$('#comparisonTable').innerHTML=`<table><thead><tr><th>Product</th><th>Reviews</th><th>Rating</th></tr></thead><tbody>${data.products.map(row=>`<tr><td>${escapeHtml(row.parent_asin||row.asin)}</td><td>${row.Reviews}</td><td>${row.Average_Rating}</td></tr>`).join('')}</tbody></table>`;chart($('#comparisonChart'),{type:'bar',data:{labels:data.products.map(r=>r.parent_asin||r.asin),datasets:[{data:data.products.map(r=>r.Average_Rating),backgroundColor:'#6855d9',borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,max:5},x:{grid:{display:false}}},plugins:{legend:{display:false}}}})});

async function loadModel(){try{const data=await fetch('/api/model').then(r=>r.json());if(data.error){toast(data.error);return}const rows=data.results.sort((a,b)=>b.f1_macro-a.f1_macro);$('#modelTable tbody').innerHTML=rows.map(row=>`<tr><td><strong>${escapeHtml(row.model)}</strong></td><td>${(row.accuracy*100).toFixed(1)}%</td><td>${(row.f1_macro*100).toFixed(1)}%</td><td>${(row.precision_macro*100).toFixed(1)}%</td><td>${(row.recall_macro*100).toFixed(1)}%</td></tr>`).join('');chart($('#modelChart'),{type:'bar',data:{labels:rows.map(r=>r.model),datasets:[{label:'Macro F1',data:rows.map(r=>r.f1_macro),backgroundColor:['#6855d9','#9285df','#bbb4ea','#ddd9f4'],borderRadius:7}]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,max:1,grid:{color:'#f0f1f5'}},x:{grid:{display:false}}},plugins:{legend:{display:false}}}})}catch(error){toast('Model results unavailable')}}

loadHome();
