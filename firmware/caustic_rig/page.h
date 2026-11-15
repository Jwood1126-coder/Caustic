// Control page served by the ESP32 at http://192.168.4.1 (or http://caustic.local)
#pragma once

const char PAGE_HTML[] PROGMEM = R"rawliteral(<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Caustic Rig</title>
<style>
:root{--bg:#0d1419;--card:#16212a;--fg:#e8eef3;--mut:#90a3b4;--line:#26343f;--acc:#f2a53a;--ok:#5fd39a;--bad:#f07b6e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:560px;margin:0 auto;padding:16px;display:flex;flex-direction:column;gap:14px}
h1{font-size:24px;margin:4px 0 0}
.top{display:flex;justify-content:space-between;align-items:center}
.pill{font-size:13px;padding:4px 10px;border-radius:99px;background:var(--line);color:var(--mut)}
.pill.ok{color:var(--ok)}.pill.bad{color:var(--bad)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:12px}
.card h2{margin:0;font-size:17px}
.hint{margin:0;color:var(--mut);font-size:14px}
.row{display:flex;justify-content:space-between;align-items:baseline}
.val{font-size:22px;font-weight:600;font-variant-numeric:tabular-nums;color:var(--acc)}
input[type=range]{width:100%;height:34px;accent-color:var(--acc)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
button{font:600 15px system-ui,sans-serif;color:var(--fg);background:var(--line);border:1px solid transparent;border-radius:9px;padding:11px 14px;cursor:pointer}
button:active{transform:scale(.97)}
button.main{background:var(--acc);color:#1b1205}
button.warn{background:#5a2620;color:#ffd9d3}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
label.f{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--mut)}
input[type=number],input[type=text],input[type=password]{font:16px system-ui,sans-serif;padding:10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);width:100%}
.big{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.big button{padding:16px}
details summary{cursor:pointer;font-weight:600}
.pgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.pgrid button{padding:10px 6px;font-size:14px}
button.on{background:var(--acc);color:#1b1205}
</style></head><body><div class="wrap">

<div class="top"><h1>Caustic Rig</h1><span id="conn" class="pill">connecting…</span></div>

<div class="card">
  <div class="row"><h2>Light</h2><span class="val"><span id="ledV">–</span>%</span></div>
  <input type="range" id="led" min="0" max="100" step="1">
  <div class="chips"><button data-led="0">Off</button><button data-led="10">10%</button><button data-led="25">25%</button><button data-led="50">50%</button><button data-led="100">100%</button></div>
  <p class="hint">Keep the LED on its heatsink. Feel it after a minute at each step: warm is fine, too hot to hold is not.</p>
</div>

<div class="card">
  <div class="row"><h2>Ripple strength</h2><span class="val"><span id="ampV">–</span>%</span></div>
  <input type="range" id="amp" min="0" max="100" step="1">
  <p class="hint">How hard the speaker taps the water. Start low, around 10%.</p>
</div>

<div class="card">
  <div class="row"><h2>Ripple speed</h2><span class="val"><span id="freqV">–</span> Hz</span></div>
  <input type="range" id="freq" min="0.5" max="40" step="0.5">
  <div class="chips"><button data-freq="1">1</button><button data-freq="2">2</button><button data-freq="5">5</button><button data-freq="10">10</button><button data-freq="15">15</button><button data-freq="20">20</button><button data-freq="25">25</button></div>
  <p class="hint">Taps per second. 1–2 Hz sloshes the whole dish. 5–25 Hz makes fine ripples.</p>
</div>

<div class="card">
  <div class="row"><h2>Patterns</h2><span class="val" style="font-size:16px" id="patV">none</span></div>
  <div class="pgrid" id="pats"></div>
  <p class="hint">Each pattern plays the ripple speed in a loop. Ripple strength still sets how hard. Moving the speed slider or pressing Stop ripples ends it.</p>
</div>

<div class="card">
  <h2>Sweep</h2>
  <p class="hint">Glide the ripple speed from one value to another to find what looks best.</p>
  <div class="grid3">
    <label class="f">From Hz<input type="number" id="sFrom" value="5" min="0.5" max="40" step="0.5"></label>
    <label class="f">To Hz<input type="number" id="sTo" value="25" min="0.5" max="40" step="0.5"></label>
    <label class="f">Seconds<input type="number" id="sSec" value="20" min="1" step="1"></label>
  </div>
  <button class="main" id="sweep">Start sweep</button>
</div>

<div class="card">
  <div class="row"><h2>Flicker fix</h2><span class="val"><span id="compV">–</span>%</span></div>
  <input type="range" id="comp" min="0" max="100" step="1">
  <p class="hint">Evens out the light while the speaker runs. Set ripple speed to 2 Hz, then raise this until the light stops pulsing. Too high and it pulses the other way. Saved on the rig.</p>
</div>

<div class="big"><button id="stop">Stop ripples</button><button class="warn" id="off">Everything off</button></div>

<div class="card">
  <details><summary>Home Wi-Fi (optional)</summary>
  <p class="hint" id="wifiState"></p>
  <p class="hint">Save your home network so you can reach this page at <b>http://caustic.local</b> without switching networks. The Caustic-Rig network keeps working either way. The rig restarts after you save.</p>
  <label class="f">Network name<input type="text" id="ssid" autocomplete="off"></label>
  <label class="f">Password<input type="password" id="pass"></label>
  <div class="chips"><button class="main" id="wsave">Save and restart</button><button id="wforget">Forget home Wi-Fi</button></div>
  </details>
</div>

</div><script>
const $=id=>document.getElementById(id);
let busy=false,pending=null,dragging=null;
async function post(path,data){
  const r=await fetch(path,{method:'POST',body:new URLSearchParams(data||{})});
  if(r.headers.get('content-type')?.includes('json')) show(await r.json());
}
function send(data){ // throttle slider traffic
  pending=Object.assign(pending||{},data);
  if(busy) return;
  const d=pending; pending=null; busy=true;
  post('/api/set',d).catch(()=>{}).finally(()=>{busy=false; if(pending) send({});});
}
function show(s){
  $('conn').textContent='connected'; $('conn').className='pill ok';
  for(const k of ['led','amp','freq','comp']){
    if(dragging!==k) $(k).value=s[k];
    $(k+'V').textContent=k==='freq'?(+s[k]).toFixed(1):s[k];
  }
  $('patV').textContent=s.pattern?(pats[s.pattern-1]||('#'+s.pattern)):'none';
  document.querySelectorAll('[data-pat]').forEach(b=>b.classList.toggle('on',+b.dataset.pat===s.pattern));
  $('sweep').textContent=s.sweeping?'Sweeping…':'Start sweep';
  $('wifiState').textContent=s.home_ssid?(s.home_ip?`Connected to "${s.home_ssid}" at ${s.home_ip}.`:`Saved "${s.home_ssid}" but not connected.`):'No home network saved.';
}
for(const k of ['led','amp','freq','comp']){
  const el=$(k);
  el.addEventListener('input',()=>{dragging=k; $(k+'V').textContent=k==='freq'?(+el.value).toFixed(1):el.value; send({[k]:el.value});});
  el.addEventListener('change',()=>{dragging=null;});
}
document.querySelectorAll('[data-led]').forEach(b=>b.onclick=()=>send({led:b.dataset.led}));
document.querySelectorAll('[data-freq]').forEach(b=>b.onclick=()=>send({freq:b.dataset.freq}));
$('sweep').onclick=()=>post('/api/sweep',{from:$('sFrom').value,to:$('sTo').value,sec:$('sSec').value});
$('stop').onclick=()=>post('/api/stop');
$('off').onclick=()=>post('/api/off');
$('wsave').onclick=()=>{ if(!$('ssid').value) return; post('/api/wifi',{ssid:$('ssid').value,pass:$('pass').value}); $('wifiState').textContent='Saved. Restarting… reconnect in about 15 seconds.'; };
$('wforget').onclick=()=>{ post('/api/wifi/forget'); $('wifiState').textContent='Forgotten. Restarting…'; };
let pats=[];
fetch('/api/patterns').then(r=>r.json()).then(n=>{
  pats=n;
  $('pats').innerHTML=n.map((x,i)=>`<button data-pat="${i+1}">${i+1}. ${x}</button>`).join('');
  document.querySelectorAll('[data-pat]').forEach(b=>b.onclick=()=>post('/api/pattern',{n:b.dataset.pat}));
}).catch(()=>{});
async function poll(){
  try{ const r=await fetch('/api/status'); show(await r.json()); }
  catch(e){ $('conn').textContent='not connected'; $('conn').className='pill bad'; }
  setTimeout(poll,1000);
}
poll();
</script></body></html>)rawliteral";
