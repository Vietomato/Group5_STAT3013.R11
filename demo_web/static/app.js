"use strict";
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const number = (n) => new Intl.NumberFormat("en-US").format(n);
const pct = (n, decimals = 2) => n == null ? "—" : (n * 100).toFixed(decimals) + "%";
const fixed = (n, digits = 3) => Number(n).toFixed(digits);
const scientific = (n) => n < .0001 ? Number(n).toExponential(2) : Number(n).toPrecision(3);
let meta, analysis, sample, lastResult, baselineResult, dashboardRequest = 0, modelSplit = "validation";
let predicting = false, inputRevision = 0, revealResult = null;
let mockData = null, mockBatch = null;
// Problem 2 state: loaded late order, latest estimate, estimate for the unedited order, revealed outcome.
let delaySample = null, delayResult = null, delayOriginal = null, delayReveal = null, delayRevision = 0, delayRunning = false;
const PAGES = {dashboard:"Dashboard", analysis:"Statistical insights", predict:"Problem 1 · Will it be late?", delay:"Problem 2 · How many days?", mock2026:"Mock orders 2026"};
const days = (n, digits = 1) => n == null ? "—" : Number(n).toFixed(digits);

async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Request failed.");
  return result;
}

function errorAt(selector, message = "") {
  const element = $(selector); element.textContent = message; element.hidden = !message;
}

function route() {
  const page = Object.hasOwn(PAGES, location.hash.slice(1)) ? location.hash.slice(1) : "dashboard";
  document.querySelectorAll(".page").forEach(element => element.hidden = element.id !== "page-" + page || !meta);
  document.querySelectorAll("[data-page]").forEach(element => {
    const active = element.dataset.page === page;
    element.classList.toggle("active", active);
    if (active) element.setAttribute("aria-current", "page"); else element.removeAttribute("aria-current");
  });
  $("#breadcrumb").textContent = PAGES[page];
}

const svg = (width, height, label, body) => `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>${body}</svg>`;
const text = (x, y, value, anchor = "start", color = "#7b8b89", size = 10) => `<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${color}" font-size="${size}" font-family="Segoe UI,Arial,sans-serif">${esc(value)}</text>`;

function lineChart(rows) {
  if (!rows.length) return '<div class="empty-chart">No labeled orders match these filters.</div>';
  const w = 600, h = 215, left = 42, right = 15, top = 15, bottom = 33;
  const max = Math.min(1, Math.max(.10, ...rows.map(row => row.rate)) * 1.12);
  const x = i => rows.length === 1 ? w / 2 : left + i * (w - left - right) / (rows.length - 1);
  const y = value => top + (1 - value / max) * (h - top - bottom);
  let body = "";
  for (let i = 0; i <= 3; i++) {
    const value = max * i / 3, yy = y(value);
    body += `<line x1="${left}" y1="${yy}" x2="${w-right}" y2="${yy}" stroke="#eaf0e9"/>` + text(left-8, yy+3, pct(value,0), "end", "#7b8b89",9);
  }
  const points = rows.map((row,i) => `${x(i)},${y(row.rate)}`).join(" ");
  body += `<polygon points="${x(0)},${y(0)} ${points} ${x(rows.length-1)},${y(0)}" fill="#dff2e7" opacity=".7"/><polyline points="${points}" fill="none" stroke="#43846b" stroke-width="2" stroke-linejoin="round"/>`;
  rows.forEach((row,i) => {
    body += `<circle cx="${x(i)}" cy="${y(row.rate)}" r="${row.orders < 30 ? 4 : 3}" fill="${row.orders < 30 ? '#a2aaa7' : '#43846b'}"><title>${esc(row.purchase_month)}: ${pct(row.rate)} · ${number(row.late)} Late / ${number(row.orders)} orders${row.orders < 30 ? ' · SMALL SAMPLE' : ''}</title></circle>`;
    if (rows.length <= 6 || i % Math.ceil(rows.length/5) === 0 || i === rows.length-1) body += text(x(i),h-10,row.purchase_month,"middle","#7b8b89",9);
  });
  return svg(w,h,"Late delivery rate by purchase month. Hover points for counts.",body);
}

function bars(rows, key, label) {
  if (!rows.length) return '<div class="empty-chart">No labeled orders match these filters.</div>';
  const w=470, rowHeight=29, h=rows.length*rowHeight+22, left=88, right=55, top=5;
  const max=Math.max(.10,...rows.map(row=>row.rate))*1.1;
  let body="";
  rows.forEach((row,i)=>{
    const y=top+i*rowHeight, size=Math.max(1,row.rate/max*(w-left-right));
    const color=row.orders<30?'#c5ceca':'#8abda4';
    body+=text(left-10,y+14,row[key],"end","#627874",10);
    body+=`<rect x="${left}" y="${y+2}" width="${w-left-right}" height="17" rx="3" fill="#f2f5f0"/><rect x="${left}" y="${y+2}" width="${size}" height="17" rx="3" fill="${color}"><title>${esc(row[key])}: ${pct(row.rate)} · ${number(row.late)} Late / ${number(row.orders)} orders${row.orders<30?' · SMALL SAMPLE':''}</title></rect>`;
    body+=text(w-3,y+15,pct(row.rate,1),"end","#35564b",10);
  });
  return svg(w,h,label,body);
}

// Horizontal bars of order counts (not rates); used for the delay distribution and importance shares.
function countBars(rows, key, valueKey, label, format, color = "#8abda4", right = 70) {
  if (!rows.length) return '<div class="empty-chart">No late orders match these filters.</div>';
  const w=470, rowHeight=29, h=rows.length*rowHeight+10, left=118, top=5;
  const max=Math.max(...rows.map(row=>row[valueKey]), 1e-9);
  let body="";
  rows.forEach((row,i)=>{
    const y=top+i*rowHeight, size=Math.max(1,row[valueKey]/max*(w-left-right));
    body+=text(left-10,y+14,row[key],"end","#627874",10);
    body+=`<rect x="${left}" y="${y+2}" width="${w-left-right}" height="17" rx="3" fill="#f2f5f0"/><rect x="${left}" y="${y+2}" width="${size}" height="17" rx="3" fill="${color}"><title>${esc(row[key])}: ${esc(format(row))}</title></rect>`;
    body+=text(w-3,y+15,format(row),"end","#35564b",10);
  });
  return svg(w,h,label,body);
}

async function refreshDashboard() {
  const request=++dashboardRequest;
  const state=$("#state-filter").value, month=$("#month-filter").value;
  try {
    const data=await api(`/api/dashboard?${new URLSearchParams({state,month})}`);
    if(request!==dashboardRequest)return;
    errorAt("#global-error");
    const cards=[
      ["Orders in cohort",number(data.total),"Including orders without valid labels","▦"],
      ["Valid delivery labels",number(data.valid),`${number(data.unlabeled)} unlabeled orders excluded from rates`,"✓"],
      ["Late orders",number(data.late),"Actual date after estimated date","↗"],
      ["Late delivery rate",pct(data.rate),"Denominator: valid delivery labels","%"]
    ];
    $("#dashboard-kpis").innerHTML=cards.map((c,i)=>`<article class="panel kpi ${i===3?'featured':''}"><div class="kpi-label">${c[0]}<span class="kpi-mark" aria-hidden="true">${c[3]}</span></div><div class="kpi-value">${c[1]}</div><div class="kpi-caption">${c[2]}</div></article>`).join("");
    $("#monthly-chart").innerHTML=lineChart(data.monthly);
    $("#distance-chart").innerHTML=bars(data.distance,"distance_group","Late rate by distance group in kilometers.");
    $("#state-chart").innerHTML=bars(data.states.slice(0,10),"customer_state","Late rate for the ten states with the most labeled orders.");
    const rate=data.rate||0, circumference=2*Math.PI*70;
    $("#distribution-chart").innerHTML=data.valid?`<div class="donut-wrap">${svg(180,180,"Late versus Not Late label distribution",`<circle cx="90" cy="90" r="70" fill="none" stroke="#edf2ed" stroke-width="17"/><circle cx="90" cy="90" r="70" fill="none" stroke="#78b99a" stroke-width="17" stroke-dasharray="${rate*circumference} ${circumference}" transform="rotate(-90 90 90)"/>`)}<div class="donut-center"><strong>${pct(rate)}</strong><span>late delivery</span></div></div><div class="legend"><span><i class="legend-dot" style="background:#78b99a"></i>Late · ${number(data.late)}</span><span><i class="legend-dot" style="background:#e5ece4"></i>Not Late · ${number(data.valid-data.late)}</span></div>`:'<div class="empty-chart">No valid labels in this cohort.</div>';
    const d=data.delay, lateTotal=d.late_orders||1;
    $("#delay-chart").innerHTML=countBars(d.groups.map(row=>({...row,label:row.delay_group+" days"})),"label","orders","Late orders by days after the estimated date.",row=>`${number(row.orders)} · ${pct(row.orders/lateTotal,0)}`);
    $("#delay-stats").innerHTML=[["Median",d.median],["Mean",d.mean],["90th percentile",d.p90]].map(([label,value])=>`<div><strong>${value==null?"—":days(value)} d</strong><span>${label} · ${number(d.late_orders)} late orders</span></div>`).join("");
    $("#cohort-note").textContent=[state||"All states",month||"All months"].join(" · ");
  } catch(error){if(request===dashboardRequest)errorAt("#global-error",error.message);}
}

const research = [
  {title:"Distance", heading:"Do distance distributions differ?",unit:"rank-biserial",digits:3,explanation:"Late orders tend to rank higher in distance. Mann–Whitney compares distributions; it is not automatically a test of medians.",adjusted:"At 200 versus 100 km, adjusted odds are about 19% higher. Odds changes are not probability changes."},
  {title:"Freight",heading:"Is average freight different?",unit:"BRL · Late minus Not Late",digits:2,explanation:"Mean freight is higher among Late orders in the unadjusted comparison. Welch's test allows unequal group variances.",adjusted:"At 20 versus 10 BRL, the adjusted interval includes 1. The adjusted freight association remains unclear."},
  {title:"Holiday",heading:"Does the late rate differ on holidays?",unit:"percentage points · holiday minus non-holiday",digits:2,explanation:"Holiday purchases have a lower observed late rate. This is an absolute percentage-point difference, not a relative percentage change.",adjusted:"Holiday versus non-holiday purchases have lower adjusted odds. This is not evidence of a protective causal effect."},
  {title:"Rainfall",heading:"Does pre-purchase rainfall differ?",unit:"mm · Late minus Not Late",digits:2,explanation:"Late orders have a higher mean destination rainfall index. Seven-day block bootstrap preserves some shared temporal structure.",adjusted:"The main OR is about 1.29 for 5 versus 0 mm. With calendar adjustment it falls to about 1.04 and the interval includes 1."}
];

function renderResearch(index=0){
  $("#rq-tabs").innerHTML=research.map((rq,i)=>`<button data-rq="${i}" class="${i===index?'active':''}" aria-pressed="${i===index}">${rq.title}</button>`).join("");
  const item=research[index],test=analysis.tests[index],reg=analysis.regression[index];
  const factor=index===2?100:1;
  const estimate=fixed(test.estimate*factor,item.digits),low=fixed(test.ci_lower*factor,item.digits),high=fixed(test.ci_upper*factor,item.digits);
  const min=Math.min(.4,reg.ci_lower*.8),max=Math.max(1.5,reg.ci_upper*1.1);
  const x=value=>35+(value-min)/(max-min)*430;
  const forest=svg(500,64,"Adjusted odds ratio and pointwise 95 percent confidence interval",`<line x1="${x(1)}" y1="4" x2="${x(1)}" y2="45" stroke="#abb7b1" stroke-dasharray="3 3"/><line x1="${x(reg.ci_lower)}" y1="24" x2="${x(reg.ci_upper)}" y2="24" stroke="#43846b" stroke-width="3"/><line x1="${x(reg.ci_lower)}" y1="18" x2="${x(reg.ci_lower)}" y2="30" stroke="#43846b"/><line x1="${x(reg.ci_upper)}" y1="18" x2="${x(reg.ci_upper)}" y2="30" stroke="#43846b"/><circle cx="${x(reg.adjusted_or)}" cy="24" r="5" fill="#235941"/>${text(x(1),60,"OR = 1","middle")}${text(x(reg.ci_lower),44,fixed(reg.ci_lower),"middle")}${text(x(reg.ci_upper),44,fixed(reg.ci_upper),"middle")}`);
  $("#rq-detail").innerHTML=`<div class="rq-heading">${item.heading}</div><p class="small muted">${esc(test.method)} · n = ${number(test.n)}</p><div class="effect-grid"><div class="effect-box"><span>UNADJUSTED ESTIMATE</span><strong>${estimate}</strong><span>${item.unit}</span><p class="small">95% CI [${low}, ${high}]</p></div><div class="effect-box"><span>ADJUSTED ODDS RATIO</span><strong>${fixed(reg.adjusted_or,2)}</strong><span>${esc(reg.comparison)}</span><p class="small">95% CI [${fixed(reg.ci_lower,2)}, ${fixed(reg.ci_upper,2)}]</p></div></div><p class="rq-explanation">${item.explanation}</p><p class="small muted">Holm-adjusted p = ${scientific(test.p_value_holm)}</p><div class="ci-chart">${forest}</div><p class="rq-explanation">${item.adjusted}</p><p class="ci-caption">Regression: 56,553 complete-case Train orders · seven-day clustered uncertainty.</p>`;
}

function renderModels(){
  const rows=analysis[modelSplit==="validation"?"validation":"test_models"];
  $("#model-table").innerHTML=`<div class="table-scroll"><table class="data-table"><thead><tr><th>Model</th><th>AP</th><th>ROC-AUC</th><th>Brier</th></tr></thead><tbody>${rows.map(row=>`<tr class="${row.model==='CatBoost'?'selected':''}"><td>${esc(row.model)}${row.model==='CatBoost'?'<span class="pill green">SELECTED</span>':''}</td><td>${fixed(row.AP,5)}</td><td>${fixed(row.ROC_AUC,3)}</td><td>${fixed(row.Brier,4)}</td></tr>`).join("")}</tbody></table></div>`;
}

function renderAnalysis(){
  renderResearch();renderModels();
  const names={train:"Train",validation_a:"Validation A",validation_b:"Validation B",test:"Test"};
  $("#split-list").innerHTML=analysis.splits.map(row=>`<div class="split-row"><span>${names[row.final_split]}</span><div class="split-bar"><span style="width:${row.share_percent}%"></span></div><strong>${number(row.orders)}</strong></div><div class="split-dates">${row.earliest_purchase.slice(0,10)} → ${row.latest_purchase.slice(0,10)} · ${number(row.late_orders)} Late</div>`).join("");
  const m=analysis.threshold_metrics;
  $("#confusion").innerHTML=`<div class="matrix"><span></span><span class="matrix-label">Predicted Not Late</span><span class="matrix-label">Predicted Late</span><span class="matrix-label">Actual<br>Not Late</span><div class="matrix-cell"><strong>${number(m.TN)}</strong>True negatives</div><div class="matrix-cell false-alert"><strong>${number(m.FP)}</strong>False alerts</div><span class="matrix-label">Actual<br>Late</span><div class="matrix-cell"><strong>${number(m.FN)}</strong>Missed delays</div><div class="matrix-cell true-alert"><strong>${number(m.TP)}</strong>True alerts</div></div>`;
  $("#evaluation-metrics").innerHTML=[["Recall",m.Recall],["Precision",m.Precision],["Alert rate",m.alert_rate]].map(([label,value])=>`<div><strong>${pct(value)}</strong><span>${label}</span></div>`).join("");
  const raw=analysis.calibration.find(row=>row.probability_type==="raw"),calibrated=analysis.calibration.find(row=>row.probability_type==="calibrated");
  $("#calibration-note").textContent=`Calibration worsened Test Brier: ${fixed(raw.Brier,5)} → ${fixed(calibrated.Brier,5)} (lower is better). ${number(m.alerts)} alerts out of ${number(m.n)} orders. High recall does not establish deployment readiness.`;
}

const fields={
  distance_km_mean:["Mean shipping distance","km"],customer_state:["Destination state",""],
  item_count:["Number of items","count"],seller_count:["Number of sellers","count"],
  estimated_window_days:["Estimated delivery window","days"],items_value:["Items value","BRL"],
  freight_value:["Freight value","BRL"],purchase_hour:["Purchase hour","0–23"],
  purchase_weekday:["Purchase weekday",""],total_product_weight_g:["Total product weight","g"],
  total_product_volume_cm3:["Total product volume","cm³"],product_category_count:["Product categories","count"],
  purchase_is_national_holiday:["Purchase on a national holiday","0 or 1"],days_to_next_national_holiday:["Days to next national holiday","days"],
  national_holiday_count_in_estimated_window:["Holidays in delivery window","count"],
  destination_rain_state_mean_mm:["Destination rainfall index","mm"],origin_rain_state_mean_mm:["Origin rainfall index","mm"],
  destination_humidity_state_mean_pct:["Destination humidity","%"],origin_humidity_state_mean_pct:["Origin humidity","%"],
  destination_air_temp_state_mean_c:["Destination air temperature","°C"],origin_air_temp_state_mean_c:["Origin air temperature","°C"]
};
const primary=["customer_state","distance_km_mean","items_value","freight_value","item_count","seller_count","estimated_window_days"];
const integerFields=["item_count","seller_count","purchase_hour","estimated_window_days","product_category_count","purchase_is_national_holiday","days_to_next_national_holiday","national_holiday_count_in_estimated_window"];

function buildFields(prefix="f",primaryTarget="#primary-fields",advancedTarget="#advanced-fields"){
  const field=(feature)=>{
    const [label,unit]=fields[feature];
    let input;
    if(feature==="customer_state"||feature==="purchase_weekday"){
      const options=feature==="customer_state"?meta.states:meta.weekdays;
      input=`<select id="${prefix}-${feature}" name="${feature}"><option value="">Missing · frozen imputation</option>${options.map(v=>`<option value="${v}">${v}</option>`).join("")}</select>`;
    }else{
      const min=feature.includes("temp")?"":`min="${["item_count","seller_count","product_category_count"].includes(feature)?1:0}"`;
      const max=feature.includes("humidity")?'max="100"':feature==="purchase_hour"?'max="23"':feature==="purchase_is_national_holiday"?'max="1"':"";
      input=`<input id="${prefix}-${feature}" name="${feature}" type="number" step="${integerFields.includes(feature)?'1':'any'}" ${min} ${max} placeholder="Missing · frozen imputation">`;
    }
    return `<div class="field"><label for="${prefix}-${feature}">${label}<span class="unit">${unit}</span></label>${input}</div>`;
  };
  $(primaryTarget).innerHTML=primary.map(field).join("");
  $(advancedTarget).innerHTML=meta.features.filter(row=>!primary.includes(row.feature)).map(row=>field(row.feature)).join("");
}

function readInputs(prefix="f"){
  return Object.fromEntries(meta.features.map(row=>{
    const value=$(`#${prefix}-`+row.feature).value;
    return [row.feature,value===""?null:["customer_state","purchase_weekday"].includes(row.feature)?value:Number(value)];
  }));
}

function sameInputs(a,b){return meta.features.every(row=>a[row.feature]===b[row.feature]);}
function inputsChanged(){
  inputRevision++;revealResult=null;
  if(lastResult)renderResult();
  $("#input-provenance").textContent=sample&&sameInputs(readInputs(),sample.features)?sample.kind==="mock2026"?`Synthetic order ${sample.id} · purchase ${sample.purchase_timestamp} · estimated ${sample.estimated_date} · no actual outcome.`:"Original Test sample · all 21 historical inputs loaded.":"Edited scenario · inspect all 21 inputs below. Unchanged fields retain their loaded values.";
}

function applySample(value){
  sample=value;lastResult=null;baselineResult=null;revealResult=null;inputRevision++;
  for(const [feature,value] of Object.entries(sample.features))$("#f-"+feature).value=value??"";
  errorAt("#form-error");inputsChanged();
  $("#prediction-result").innerHTML='<div class="empty-result"><div class="empty-icon">↗</div><h2>Order loaded. Ready to run.</h2><p>Review the inputs or edit a scenario, then select Run prediction.</p></div>';
}

async function loadSample(){
  const button=$("#load-sample");button.disabled=true;
  try{
    const id=$("#sample-select").value,local=tryOrder(id);
    applySample(local||await api("/api/sample?id="+encodeURIComponent(id)));
  }catch(error){errorAt("#form-error",error.message);}finally{button.disabled=false;}
}

function renderResult(){
  if(!lastResult)return;
  const r=lastResult,stale=!sameInputs(readInputs(),r.features),original=sample&&sameInputs(r.features,sample.features);
  const historical=original&&sample.kind!=="mock2026";
  const provenance=sample?.kind==="mock2026"?"Synthetic 2026 inputs. Historical model, not validated for 2026; no actual outcome is available.":historical?"Historical Test inputs. The outcome was not supplied to the model.":"Edited scenario. The original order’s outcome does not validate this scenario.";
  const comparison=baselineResult&&!original&&!stale?`<div class="comparison">Compared with the original sample: <strong>${pct(baselineResult.probability)} → ${pct(r.probability)}</strong><br>Change: ${((r.probability-baselineResult.probability)*100).toFixed(2)} percentage points. This is model sensitivity, not a causal effect.</div>`:"";
  $("#prediction-result").innerHTML=`${stale?'<div class="stale-note">Inputs changed. This result belongs to the previous inputs. Run prediction again.</div>':''}<div class="risk-value">${(r.probability*100).toFixed(2)}<small>%</small></div><div class="probability-caption">Estimated late-delivery probability · calibrated</div><span class="pill ${r.prediction?'amber':'green'}">${r.prediction?'LATE ALERT':'NO LATE ALERT'}</span><div class="risk-track"><div class="fill" style="width:${r.probability*100}%"></div><span class="threshold" style="left:${r.threshold*100}%"></span></div><div class="risk-scale"><span>0%</span><span>100%</span></div><p class="threshold-caption">Marker: frozen alert threshold ${pct(r.threshold,3)} · alert if probability ≥ threshold</p><div class="result-detail"><span>Raw model probability</span><strong>${pct(r.raw_probability)}</strong></div><div class="result-detail"><span>Model</span><strong>CatBoost baseline</strong></div><div class="result-detail"><span>Probability mapping</span><strong>Frozen sigmoid calibration</strong></div>${r.delay?`<div class="comparison">If this order is late, Problem 2 estimates <strong>${days(r.delay.days)} days</strong> late (baseline guess: ${days(r.delay.baseline_days,0)} days). On validation this estimate was not more accurate than the baseline. <a href="#delay"><strong>Open Problem 2 ↗</strong></a></div>`:""}${comparison}${r.warnings.length?`<ul class="warning-list">${r.warnings.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`:''}<p class="result-provenance">${provenance}</p><div class="result-actions"><button id="reveal-button" class="button subtle" ${!historical||stale?'disabled':''}>Reveal actual outcome</button><button id="download-result" class="button subtle" ${stale?'disabled':''}>Download result</button></div><div id="actual-outcome">${revealResult&&!stale?outcomeMarkup(revealResult):''}</div>`;
  $("#reveal-button").onclick=async()=>{
    const capturedRevision=inputRevision,capturedId=sample.id;
    try{
      const result=await api("/api/reveal?id="+encodeURIComponent(capturedId));
      if(capturedRevision!==inputRevision||sample.id!==capturedId)return;
      revealResult=result;$("#actual-outcome").innerHTML=outcomeMarkup(result);
    }catch(error){errorAt("#form-error",error.message);}
  };
  $("#download-result").onclick=()=>{
    const blob=new Blob([JSON.stringify({...r,scenario:sample?.kind==='mock2026'?'synthetic_2026':historical?'historical_sample':'edited_inputs',sample_id:sample?.id,actual:revealResult?.actual??null},null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download="olist-demo-prediction.json";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
}

function outcomeMarkup(result){
  const correct=result.actual===lastResult.prediction;
  return `<div class="note ${correct?'':'warning'}">Actual outcome: <strong>${result.actual?'Late':'Not Late'}</strong>.<br>${correct?'The frozen prediction matches this historical outcome.':lastResult.prediction?'This is a false alert: flagged Late, actually Not Late.':'This is a missed delay: not flagged, actually Late.'} One example is illustrative; use aggregate Test metrics for performance.</div>`;
}

async function predict(event){
  event.preventDefault();if(predicting)return;
  const values=readInputs(),revision=inputRevision;
  predicting=true;$("#predict-button").disabled=true;$("#predict-button").textContent="Running model…";errorAt("#form-error");
  try{
    const result=await api("/api/predict",{features:values});
    if(revision!==inputRevision){errorAt("#form-error","Inputs changed during inference. Run prediction again for the current inputs.");return;}
    lastResult=result;revealResult=null;
    if(sample&&sameInputs(values,sample.features))baselineResult=result;
    renderResult();
  }catch(error){errorAt("#form-error",error.message);}finally{
    predicting=false;$("#predict-button").disabled=!meta.model_ready;$("#predict-button").innerHTML='Run prediction <span>↗</span>';
  }
}

/* ---------- Problem 2 · delay-duration regression ---------- */
const DELAY_COLORS={MedianBaseline:"#9db4ae",CatBoostDelayRegressor:"#267657"};
const DELAY_NAMES={MedianBaseline:"Baseline · always 7 days",CatBoostDelayRegressor:"CatBoost regressor",CatBoost21:"CatBoost · 21 inputs",CatBoost15_noWeather:"CatBoost · no weather"};
const FOLD_PERIODS={fold_1:"Jul–Sep 2017",fold_2:"Oct–Dec 2017",fold_3:"Jan–Feb 2018"};
const signed=(n,digits=2)=>(n>0?"+":n<0?"−":"")+Math.abs(n).toFixed(digits);

function intervalChart(rows,label){
  // rows: {name,d,lo,hi}; negative = first model better.
  const w=480,rowH=40,h=rows.length*rowH+30,left=8,right=12,x0=Math.min(-.35,...rows.map(r=>r.lo-.05)),x1=Math.max(.7,...rows.map(r=>r.hi+.05));
  const X=v=>left+(v-x0)/(x1-x0)*(w-left-right);
  let body=`<line x1="${X(0)}" x2="${X(0)}" y1="4" y2="${h-24}" stroke="#20363b" stroke-dasharray="3 3"/>`;
  rows.forEach((r,i)=>{
    const y=i*rowH+30;
    body+=`<text x="${left}" y="${y-12}" fill="#35564b" font-size="10" font-family="Segoe UI,Arial,sans-serif" stroke="#fff" stroke-width="4" paint-order="stroke">${esc(`${r.name}  ${signed(r.d)} days [${signed(r.lo)}, ${signed(r.hi)}]`)}</text>`;
    body+=`<line x1="${X(r.lo)}" x2="${X(r.hi)}" y1="${y}" y2="${y}" stroke="#20363b" stroke-width="2"/><line x1="${X(r.lo)}" x2="${X(r.lo)}" y1="${y-5}" y2="${y+5}" stroke="#20363b" stroke-width="2"/><line x1="${X(r.hi)}" x2="${X(r.hi)}" y1="${y-5}" y2="${y+5}" stroke="#20363b" stroke-width="2"/><circle cx="${X(r.d)}" cy="${y}" r="5" fill="${r.hi<0?'#267657':'#a46616'}" stroke="#fff" stroke-width="2"/>`;
  });
  body+=text(X(0),h-8,"0 = no difference · left: model better · right: model worse","middle","#7b8b89",9);
  return svg(w,h,label,body);
}

function renderDelayEvidence(){
  const a=analysis.delay,diff=a.difference;
  $("#delay-verdict").textContent=diff.catboost_better
    ?`CatBoost beat the 7-day baseline on validation: MAE ${days(diff.catboost_mae,2)} vs ${days(diff.baseline_mae,2)} days.`
    :`The regressor did not beat a constant 7-day guess. Validation MAE ${days(diff.catboost_mae,2)} vs ${days(diff.baseline_mae,2)} days; the 95% interval of the difference includes 0, so the baseline is retained.`;
  $("#delay-verdict-figures").innerHTML=[[days(diff.baseline_mae,2),"Baseline MAE · days"],[days(diff.catboost_mae,2),"CatBoost MAE · days"],[`[${signed(diff.ci95_low)}, ${signed(diff.ci95_high)}]`,"95% interval of difference"]].map(([v,l])=>`<div><b>${v}</b><span>${l}</span></div>`).join("");
  const scopes={validation_pooled:"A + B pooled",validation_a:"Validation A",validation_b:"Validation B",train_in_sample:"Train (in-sample)"};
  $("#delay-metrics").innerHTML=`<div class="table-scroll"><table class="data-table"><thead><tr><th>Scope · model</th><th>Orders</th><th>MAE</th><th>Median abs. error</th><th>Within ±3 days</th></tr></thead><tbody>${a.metrics.filter(r=>r.scope!=="train_in_sample").map(r=>`<tr class="${r.scope==='validation_pooled'?'selected':''}"><td>${scopes[r.scope]} · ${esc(DELAY_NAMES[r.model])}</td><td>${number(r.orders)}</td><td>${days(r.MAE,2)}</td><td>${days(r.MedAE,2)}</td><td>${days(r.within_3_days_pct)}%</td></tr>`).join("")}</tbody></table></div>`;
  $("#delay-ci").innerHTML=`<div class="ci-chart">${intervalChart([{name:"Validation: CatBoost − baseline",d:diff.difference,lo:diff.ci95_low,hi:diff.ci95_high}],"MAE difference with 95 percent interval")}</div><p class="ci-caption">Only ${days(diff.share_of_replicates_below_0_pct)}% of ${number(2000)} bootstrap resamples favour CatBoost.</p>`;
  // Grouped bars: MAE per actual-delay group, both guesses side by side, values labelled.
  const groups=[...new Set(a.groups.map(r=>r.delay_group))],models=["MedianBaseline","CatBoostDelayRegressor"];
  const w=480,h=210,left=34,bottom=34,top=18,maxV=Math.max(...a.groups.map(r=>r.MAE))*1.15,slot=(w-left-10)/groups.length,bw=slot*.3;
  const Y=v=>top+(1-v/maxV)*(h-top-bottom);
  let body="";
  for(let i=0;i<=3;i++){const v=maxV*i/3;body+=`<line x1="${left}" x2="${w-10}" y1="${Y(v)}" y2="${Y(v)}" stroke="#eaf0e9"/>`+text(left-6,Y(v)+3,v.toFixed(0),"end","#7b8b89",9);}
  groups.forEach((g,i)=>{
    const n=a.groups.find(r=>r.delay_group===g).orders;
    models.forEach((m,j)=>{
      const r=a.groups.find(x=>x.delay_group===g&&x.model===m),x=left+i*slot+slot*.18+j*(bw+3);
      body+=`<rect x="${x}" y="${Y(r.MAE)}" width="${bw}" height="${Y(0)-Y(r.MAE)}" rx="3" fill="${DELAY_COLORS[m]}"><title>${esc(DELAY_NAMES[m])} · ${g} days: MAE ${days(r.MAE,2)}</title></rect>`+text(x+bw/2,Y(r.MAE)-4,days(r.MAE),"middle","#35564b",9);
    });
    body+=text(left+i*slot+slot*.5,h-18,`${g} days`,"middle","#627874",10)+text(left+i*slot+slot*.5,h-6,`n=${n}`,"middle","#7b8b89",9);
  });
  $("#delay-group-chart").innerHTML=`<div class="legend-row">${models.map(m=>`<span><i class="legend-dot" style="background:${DELAY_COLORS[m]}"></i>${DELAY_NAMES[m]}</span>`).join("")}</div>`+svg(w,h,"Mean absolute error by actual delay group for the baseline and CatBoost.",body);
  // Train-only diagnostics.
  const fm=a.folds,pick=(f,m)=>fm.find(r=>r.fold===f&&r.model===m);
  $("#delay-folds").innerHTML=`<div class="table-scroll"><table class="data-table"><thead><tr><th>Predict period</th><th>Orders</th><th>Baseline</th><th>CatBoost · 21</th><th>CatBoost · no weather</th></tr></thead><tbody>${Object.keys(FOLD_PERIODS).map(f=>`<tr><td>${FOLD_PERIODS[f]}</td><td>${number(pick(f,"MedianBaseline").score_orders)}</td><td><strong>${days(pick(f,"MedianBaseline").out_of_time_MAE,2)}</strong></td><td>${days(pick(f,"CatBoost21").out_of_time_MAE,2)}</td><td>${days(pick(f,"CatBoost15_noWeather").out_of_time_MAE,2)}</td></tr>`).join("")}</tbody></table></div><p class="small muted">Out-of-time MAE in days; the baseline is lowest in every period.</p>`;
  const short={"CatBoost21 minus MedianBaseline":"CatBoost 21 − baseline","CatBoost15_noWeather minus MedianBaseline":"No weather − baseline","CatBoost15_noWeather minus CatBoost21":"No weather − with weather"};
  $("#delay-fold-ci").innerHTML=`<div class="ci-chart">${intervalChart(a.fold_differences.map(r=>({name:short[r.comparison],d:r.difference,lo:r.ci95_low,hi:r.ci95_high})),"Pooled out-of-time MAE differences within Train")}</div>`;
  const gain=Object.fromEntries(a.pooled_folds.map(r=>[r.model,r.in_sample_gain_vs_baseline_mean])),fp=a.fingerprint[a.fingerprint.length-1];
  $("#delay-fingerprint").innerHTML=`<strong>Weather works as a date fingerprint.</strong> ${days(fp.vectors_on_one_date_pct,0)}% of state + weather vectors in Train (${number(fp.orders_with_complete_values)} orders) occur on exactly one purchase date. With weather, CatBoost fits its training period ${days(gain.CatBoost21,2)} days better than the baseline but predicts later periods worse; removing weather narrows that gap. The main cause remains weak signal: even without weather it loses to the baseline.`;
  const imp=a.importance.map(r=>({label:(fields[r.feature]||[r.feature])[0],value:r.importance,weather:/rain|humidity|temp/.test(r.feature)}));
  $("#delay-importance").innerHTML=countBars(imp,"label","value","Top eight CatBoost regressor feature importances.",row=>`${row.value.toFixed(1)}%${row.weather?" · weather":""}`,"#9fcfb6",104);
}

function applyDelaySample(value){
  delaySample=value;delayResult=null;delayOriginal=null;delayReveal=null;delayRevision++;
  for(const [feature,v] of Object.entries(value.features))$("#d-"+feature).value=v??"";
  errorAt("#delay-form-error");delayInputsChanged();
  $("#delay-result").innerHTML='<div class="empty-result"><div class="empty-icon">⧗</div><h2>Late order loaded.</h2><p>Review or edit the inputs, then select Estimate days late.</p></div>';
}

async function loadDelaySample(){
  const button=$("#delay-load-sample");button.disabled=true;
  try{const id=$("#delay-sample-select").value;applyDelaySample(tryOrder(id)||await api("/api/delay/sample?id="+encodeURIComponent(id)));}
  catch(error){errorAt("#delay-form-error",error.message);}finally{button.disabled=false;}
}

function delayInputsChanged(){
  delayRevision++;delayReveal=null;
  if(delayResult)renderDelayResult();
  const original=delaySample&&sameInputs(readInputs("d"),delaySample.features);
  const synthetic=delaySample?.kind==="mock2026";
  $("#delay-provenance").textContent=!delaySample?"The same 21 purchase-time inputs as Problem 1.":original?(synthetic?`Synthetic try-out order ${delaySample.id} · purchase ${delaySample.purchase_timestamp} · estimated ${delaySample.estimated_date} · no actual outcome.`:"Original late validation order · all 21 inputs loaded · actual delay hidden."):"Edited scenario · unchanged fields keep the loaded values.";
}

function renderDelayResult(){
  if(!delayResult)return;
  const r=delayResult,stale=!sameInputs(readInputs("d"),r.features),original=delaySample&&sameInputs(r.features,delaySample.features),synthetic=delaySample?.kind==="mock2026";
  const change=delayOriginal&&!original&&!stale?`<div class="comparison">Compared with the original order: <strong>${days(delayOriginal.days)} → ${days(r.days)} days</strong> (${signed(r.days-delayOriginal.days,1)}). Model sensitivity, not a causal effect.</div>`:"";
  const reveal=delayReveal&&!stale&&original?(()=>{
    const actual=delayReveal.actual_delay_days,eC=Math.abs(r.days-actual),eB=Math.abs(r.baseline_days-actual);
    return `<div class="note ${eC<eB?'':'warning'}">Actual delay: <strong>${actual} days</strong> (${delayReveal.split==="validation_a"?"Validation A":"Validation B"}).<br>CatBoost missed by ${days(eC)} days; the 7-day baseline missed by ${days(eB)} days. ${eC<eB?"CatBoost was closer for this order.":eC>eB?"The baseline was closer for this order.":"Both were equally close."} One order is illustrative; the aggregate MAE decides.</div>`;
  })():"";
  $("#delay-result").innerHTML=`${stale?'<div class="stale-note">Inputs changed. This estimate belongs to the previous inputs. Run it again.</div>':''}<div class="delay-value">${days(r.days)}<small>days late</small></div><div class="probability-caption">Estimated days after the promised date · if the order is late</div><div class="versus"><div class="catboost"><strong>${days(r.days)} d</strong><span>CatBoost regressor</span></div><div><strong>${days(r.baseline_days,0)} d</strong><span>Baseline · Train median</span></div></div><div class="result-detail"><span>Validation MAE · CatBoost / baseline</span><strong>${days(analysis.delay.difference.catboost_mae,2)} / ${days(analysis.delay.difference.baseline_mae,2)} days</strong></div><div class="result-detail"><span>Model</span><strong>CatBoost · MAE loss · late orders</strong></div>${r.raw_days<1?'<div class="result-detail"><span>Floor applied</span><strong>Raw estimate below 1 day</strong></div>':''}${change}${r.warnings.length?`<ul class="warning-list">${r.warnings.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`:''}<p class="result-provenance">${synthetic&&original?"Synthetic 2026 try-out order. It assumes the order is late; there is no actual delay to compare, and the model is not validated for 2026.":original?"Historical late validation order. Its actual delay was not supplied to the model.":"Edited scenario. The original order’s actual delay does not validate this scenario."}</p><div class="result-actions"><button id="delay-reveal" class="button subtle" ${!original||stale||synthetic?'disabled':''}>Reveal actual delay</button></div><div id="delay-actual">${reveal}</div>`;
  $("#delay-reveal").onclick=async()=>{
    const revision=delayRevision,id=delaySample.id;
    try{const value=await api("/api/delay/reveal?id="+encodeURIComponent(id));if(revision!==delayRevision||delaySample.id!==id)return;delayReveal=value;renderDelayResult();}
    catch(error){errorAt("#delay-form-error",error.message);}
  };
}

async function predictDelay(event){
  event.preventDefault();if(delayRunning)return;
  const values=readInputs("d"),revision=delayRevision,button=$("#delay-predict-button");
  delayRunning=true;button.disabled=true;button.textContent="Running regressor…";errorAt("#delay-form-error");
  try{
    const result=await api("/api/delay/predict",{features:values});
    if(revision!==delayRevision){errorAt("#delay-form-error","Inputs changed during inference. Run it again for the current inputs.");return;}
    delayResult=result;delayReveal=null;
    if(delaySample&&sameInputs(values,delaySample.features))delayOriginal=result;
    renderDelayResult();
  }catch(error){errorAt("#delay-form-error",error.message);}finally{
    delayRunning=false;button.disabled=!meta.delay_ready;button.innerHTML='Estimate days late <span>↗</span>';
  }
}

function renderMock(){
  const rows=(mockBatch||mockData).orders;
  $("#mock-table").innerHTML=`<table class="data-table mock-table"><thead><tr><th>Mock order</th><th>Set</th><th>Purchase date</th><th>State</th><th>Distance</th><th>Window</th><th>Probability</th><th>Alert</th><th>If late · days</th><th></th></tr></thead><tbody>${rows.map(row=>`<tr><td title="${esc(row.description)}">${esc(row.id)}</td><td>${row.set==="Order book"?"Order book":'<span class="pill green">TRY-OUT</span>'}</td><td>${row.purchase_timestamp.slice(0,10)}</td><td>${row.features.customer_state}</td><td>${number(row.features.distance_km_mean)} km</td><td>${row.features.estimated_window_days} d</td><td>${row.probability==null?'Not run':pct(row.probability)}</td><td>${row.prediction==null?'—':`<span class="pill ${row.prediction?'amber':'green'}">${row.prediction?'ALERT':'NO ALERT'}</span>`}</td><td title="Problem 2 estimate; baseline guess is 7 days">${row.delay?days(row.delay.days):'—'}</td><td><button class="button subtle" data-open-mock="${row.id}">Inspect</button></td></tr>`).join("")}</tbody></table>`;
  $("#mock-summary").innerHTML=mockBatch?`<div><strong>${mockBatch.count}</strong><span>Synthetic orders scored</span></div><div><strong>${mockBatch.alerts}</strong><span>Predicted alerts · not confirmed delays</span></div><div><strong>Unavailable</strong><span>Actual outcomes · no performance metrics</span></div>`:"";
  $("#download-mock-results").disabled=!mockBatch;
}

const tryOrders=()=>mockData?mockData.orders.filter(row=>row.id.startsWith("TRY-")):[];
const tryOrder=id=>tryOrders().find(row=>row.id===id)||null;
function addTryOptions(){
  const options=tryOrders().map(row=>`<option value="${esc(row.id)}">${esc(row.id)} · ${esc(row.features.customer_state)} · ${row.purchase_timestamp.slice(0,10)} · ${esc(row.description)}</option>`).join("");
  if(!options)return;
  for(const [selector,label] of [["#sample-select","Historical Test orders"],["#delay-sample-select","Late validation orders"]]){
    const select=$(selector),current=select.value;
    if(select.querySelector("optgroup"))continue;
    select.innerHTML=`<optgroup label="${label}">${select.innerHTML}</optgroup><optgroup label="2026 try-out · synthetic, no outcome">${options}</optgroup>`;
    select.value=current;
  }
}

async function loadMockOrders(){
  try{
    mockData=await api("/api/mock-orders");
    $("#mock-notice").textContent=mockData.notice;
    $("#run-mock").disabled=!meta.model_ready;
    $("#run-mock").innerHTML=`Predict all ${mockData.orders.length} orders <span>↗</span>`;
    addTryOptions();
    renderMock();
  }catch(error){errorAt("#mock-error",error.message);$("#run-mock").disabled=true;}
}

async function predictMock(){
  const button=$("#run-mock");button.disabled=true;button.textContent=`Scoring ${mockData.orders.length} orders…`;errorAt("#mock-error");
  try{mockBatch=await api("/api/predict-mock",{});renderMock();}
  catch(error){errorAt("#mock-error",error.message);}
  finally{button.disabled=!meta.model_ready;button.innerHTML=`Predict all ${mockData.orders.length} orders <span>↗</span>`;}
}

function downloadMockResults(){
  if(!mockBatch)return;
  const columns=["order_id","purchase_timestamp","estimated_date","data_source",...meta.features.map(row=>row.feature),"raw_probability","calibrated_probability","prediction","threshold","delay_days_if_late","delay_baseline_days"];
  const quote=value=>'"'+String(value??"").replaceAll('"','""')+'"';
  const rows=mockBatch.orders.map(row=>[row.id,row.purchase_timestamp,row.estimated_date,"synthetic_demo_2026",...meta.features.map(f=>row.features[f.feature]),row.raw_probability,row.probability,row.prediction,row.threshold,row.delay?.days,row.delay?.baseline_days]);
  const csv=[columns,...rows].map(row=>row.map(quote).join(",")).join("\r\n");
  const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
  const link=document.createElement("a");link.href=url;link.download="mock_orders_2026_predictions.csv";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

async function init(){
  route();
  try{
    [meta,analysis]=await Promise.all([api("/api/meta"),api("/api/analysis")]);
    $("#state-filter").insertAdjacentHTML("beforeend",meta.states.map(v=>`<option value="${v}">${v}</option>`).join(""));
    $("#month-filter").insertAdjacentHTML("beforeend",meta.months.map(v=>`<option value="${v}">${v}</option>`).join(""));
    $("#sample-select").innerHTML=meta.samples.map(s=>`<option value="${s.id}">${esc(s.label)}</option>`).join("");
    buildFields();buildFields("d","#delay-primary-fields","#delay-advanced-fields");renderAnalysis();renderDelayEvidence();
    $("#delay-sample-select").innerHTML=meta.delay_samples.map(s=>`<option value="${s.id}">${esc(s.label)}</option>`).join("");
    $("#delay-status").textContent=meta.delay_ready?"● Delay model ready":"Delay model unavailable";
    $("#delay-status").className="pill "+(meta.delay_ready?"green":"amber");
    $("#delay-predict-button").disabled=!meta.delay_ready;
    if(!meta.delay_ready)errorAt("#delay-error","Saved Problem 2 results are shown, but live estimates need outputs/models/delay_regression/CatBoostDelayRegressor.joblib. Run notebooks/06_delay_prediction/02_delay_regression_catboost.ipynb. "+(meta.delay_error||""));
    $("#delay-load-sample").onclick=loadDelaySample;
    $("#delay-restore").onclick=()=>{if(!delaySample)return;for(const [key,value]of Object.entries(delaySample.features))$("#d-"+key).value=value??"";delayInputsChanged();};
    $("#delay-form").oninput=delayInputsChanged;$("#delay-form").onchange=delayInputsChanged;
    $("#delay-form").onsubmit=predictDelay;
    $("#model-status").textContent=meta.model_ready?"● Frozen model ready":"Model unavailable";
    $("#model-status").className="pill "+(meta.model_ready?"green":"amber");
    $("#predict-button").disabled=!meta.model_ready;
    if(!meta.model_ready)errorAt("#model-error","The dashboard is available, but live inference needs the frozen model artifacts and matching Python environment. See demo_web/README.md. "+(meta.model_error||""));
    $("#state-filter").onchange=refreshDashboard;$("#month-filter").onchange=refreshDashboard;
    $("#reset-filters").onclick=()=>{$("#state-filter").value="";$("#month-filter").value="";refreshDashboard();};
    $("#rq-tabs").onclick=event=>{const button=event.target.closest("[data-rq]");if(button)renderResearch(Number(button.dataset.rq));};
    document.querySelectorAll("[data-model-split]").forEach(button=>button.onclick=()=>{
      modelSplit=button.dataset.modelSplit;
      document.querySelectorAll("[data-model-split]").forEach(b=>{b.classList.toggle("active",b===button);b.setAttribute("aria-pressed",String(b===button));});
      renderModels();
    });
    $("#load-sample").onclick=loadSample;
    $("#restore-sample").onclick=()=>{if(!sample)return;for(const [key,value]of Object.entries(sample.features))$("#f-"+key).value=value??"";inputsChanged();};
    $("#prediction-form").oninput=inputsChanged;$("#prediction-form").onchange=inputsChanged;
    $("#prediction-form").onsubmit=predict;
    $("#run-mock").onclick=predictMock;
    $("#download-mock-results").onclick=downloadMockResults;
    $("#mock-table").onclick=event=>{
      const button=event.target.closest("[data-open-mock]");if(!button||!mockData)return;
      const row=mockData.orders.find(order=>order.id===button.dataset.openMock);
      if(row){applySample(row);location.hash="predict";window.scrollTo({top:0});}
    };
    await Promise.all([refreshDashboard(),loadSample(),loadDelaySample(),loadMockOrders()]);
    $("#loading").hidden=true;route();
  }catch(error){$("#loading").hidden=true;errorAt("#global-error",error.message+" Start the Python demo server and check the project files.");}
}
window.addEventListener("hashchange",route);
init();
