import { STATIONS, ROUTE_LENGTH, ROUTE_MAP, positionAt, speedLimitAt } from '../data/route';
import type { Simulation } from '../game/simulation';
import type { View } from '../render/renderer';

const icon=(name:string)=>{
  const shapes:Record<string,string>={
    train:'<rect x="6" y="3" width="12" height="15" rx="4"/><path d="M7 10h10M9 21l2-3m4 3-2-3M10 14h.01M14 14h.01"/>',
    pause:'<path d="M8 5v14M16 5v14"/>',play:'<path d="m8 5 11 7-11 7z"/>',
    camera:'<path d="M4 7h4l2-3h4l2 3h4v13H4z"/><circle cx="12" cy="13" r="4"/>',
    map:'<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2zM9 3v16M15 5v16"/>',
    sound:'<path d="m11 4-6 5H2v6h3l6 5zM15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14"/>',
    help:'<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 1 1 5 2l-2 1v2M12 17h.01"/>',
    arrow:'<path d="M4 12h15m-6-6 6 6-6 6"/>',close:'<path d="m6 6 12 12M18 6 6 18"/>',
    door:'<path d="M4 21V3h16v18M12 3v18M8 11v3M16 11v3"/>',
  };
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${shapes[name]??shapes.train}</svg>`;
};
export interface Actions{start:()=>void;resume:()=>void;restart:()=>void;pause:()=>void;view:()=>void;sound:()=>void;doors:()=>void;controller:(n:number)=>void;emergency:()=>void;quality:(high:boolean)=>void}
export class HUD {
  private root:HTMLElement;private dialog:'map'|'help'|null=null;private lastPhase='';private lastDistance:number=STATIONS[0].distance;
  private byId=(id:string)=>this.root.querySelector<HTMLElement>(`#${id}`)!;
  constructor(root:HTMLElement,private actions:Actions,hasSave:boolean){
    this.root=root;root.innerHTML=`
    <header class="topbar"><a class="brand" href="/" aria-label="Melbourne Rail Explorer home"><span class="brand-icon">${icon('train')}</span><span>Melbourne<span class="brand-sub">Rail Explorer</span></span></a>
      <div class="session-tag"><span class="live-dot"></span>City Loop <span class="separator">|</span><span id="mode-label">Driver simulator</span></div>
      <nav aria-label="Game controls"><button id="map-btn" class="icon-button" aria-label="Route map" title="Route map · M">${icon('map')}</button><button id="view-btn" class="icon-button" aria-label="Change camera" title="Change camera · C">${icon('camera')}</button><button id="sound-btn" class="icon-button muted" aria-label="Enable sound" aria-pressed="false" title="Sound">${icon('sound')}</button><button id="help-btn" class="icon-button" aria-label="Controls and information" title="Controls and information">${icon('help')}</button><button id="pause-btn" class="icon-button" aria-label="Pause" title="Pause · Esc">${icon('pause')}</button></nav>
    </header>
    <section id="welcome" class="welcome"><div class="eyebrow"><span class="mode-symbol">${icon('train')}</span>Metropolitan trains</div><h1>City Loop</h1><p class="welcome-description">All stations to Flinders Street<br><strong>via Southern Cross &amp; the City Loop</strong></p>
      <div class="service-card"><div class="service-heading"><span class="line-badge">${icon('train')}</span><div><h2>Flinders Street</h2><span>Departing 06:42 · All stations</span></div><span class="service-number">HCMT<small>7 cars</small></span></div>
      <div class="service-meta"><span>5 stations</span><i></i><span id="route-length">— km</span><i></i><span>Driver training</span></div>
      <button class="primary" id="start-btn" disabled><span id="start-label">Preparing your service</span>${icon('arrow')}</button>
      ${hasSave?'<button class="text-button" id="resume-save" disabled>Continue saved service →</button>':''}
    </div><div class="welcome-foot"><span class="key">W</span><span class="key">S</span> Power & brake <span class="control-divider"></span><span class="key">D</span> Doors <span class="control-divider"></span><span class="key">C</span> Camera</div></section>
    <div id="scene-caption" class="scene-caption"><span>Melbourne metropolitan network</span><strong>${icon('train')} Flinders Street</strong><span>City Loop training service</span></div>
    <div id="load-status" role="status" class="load-status">Preparing your service…</div>
    <main id="driving-hud" hidden>
      <div class="next-stop"><span class="eyebrow">NEXT STATION</span><h2 id="station-name">Southern Cross</h2><div><span id="station-distance">—</span><span class="next-dot">•</span><span id="station-instruction">Departure</span></div></div>
      <div class="journey-strip" id="journey-strip">${STATIONS.slice(0,-1).map((s,i)=>`<span class="journey-stop" data-index="${i}"><i></i>${s.short}</span>`).join('')}</div>
      <div id="message" class="driver-message" role="status"></div>
      <div class="dashboard"><div class="speed-display"><div><span id="speed">0</span><small>km/h</small></div><div class="speed-scale"><span id="speed-fill"></span></div></div>
        <div class="limit-block"><span class="limit" id="speed-limit">50</span><small>LIMIT</small></div>
        <div class="controller"><div class="controller-label"><span>MASTER CONTROLLER</span><strong id="controller-state">COAST</strong></div><input id="controller" type="range" min="-4" max="4" step="1" value="0" aria-label="Train controller: brake to power"/><div class="controller-ends"><span>BRAKE <kbd>S</kbd></span><span>COAST</span><span><kbd>W</kbd> POWER</span></div></div>
        <button id="doors-btn" class="door-button">${icon('door')}<span id="doors-label">Close doors</span><kbd>D</kbd></button>
        <button id="emergency-btn" class="emergency-button" aria-label="Emergency brake" title="Emergency brake · Space"><span>!</span><small>EMERGENCY</small></button>
      </div><div class="drive-footer"><span id="view-label">CAB VIEW</span><span>HCMT · 7 CARS <i></i> <span id="clock">06:42:00</span></span></div>
    </main>
    <aside id="drawer" class="drawer" hidden><div class="drawer-heading"><span id="drawer-title">The City Loop</span><button id="close-drawer" class="icon-button" aria-label="Close panel">${icon('close')}</button></div><div id="drawer-content"></div></aside>
    <section id="pause-overlay" class="modal-overlay" hidden><div class="modal"><span class="eyebrow">City Loop · Driver training</span><h2>Service paused</h2><p>Resume your service when ready.</p><button id="continue-btn" class="primary">Back to the cab ${icon('arrow')}</button><button id="restart-btn" class="secondary">Restart service</button><label class="quality-option"><input type="checkbox" id="quality-toggle" checked/> High quality lighting</label></div></section>
    <section id="complete-overlay" class="modal-overlay" hidden><div class="modal"><span class="eyebrow">BACK AT FLINDERS STREET</span><h2>Service complete</h2><p id="results-summary"></p><div id="results-list"></div><button id="again-btn" class="primary">Run another service ${icon('arrow')}</button></div></section>
    <div id="error" class="error-banner" hidden role="alert"></div>
    <footer id="credits" class="credits">Independent simulator · Development build<span>City geography © City of Melbourne · CC BY 4.0</span></footer>`;
    this.byId('route-length').textContent=`${(ROUTE_LENGTH/1000).toFixed(1)} km`;
    const bind=(id:string,fn:()=>void)=>this.root.querySelector(`#${id}`)?.addEventListener('click',fn);
    bind('start-btn',actions.start);bind('resume-save',actions.resume);bind('pause-btn',actions.pause);bind('continue-btn',actions.pause);
    bind('restart-btn',actions.restart);bind('again-btn',actions.restart);bind('view-btn',actions.view);bind('sound-btn',actions.sound);
    bind('doors-btn',actions.doors);bind('emergency-btn',actions.emergency);bind('map-btn',()=>this.togglePanel('map'));
    bind('help-btn',()=>this.togglePanel('help'));bind('close-drawer',()=>this.closePanel());
    this.byId('controller').addEventListener('input',e=>actions.controller(Number((e.target as HTMLInputElement).value)));
    this.byId('quality-toggle').addEventListener('change',e=>actions.quality((e.target as HTMLInputElement).checked));
  }
  loading(message:string){this.byId('load-status').textContent=message;}
  ready(){(this.byId('start-btn') as HTMLButtonElement).disabled=false;const resume=this.root.querySelector<HTMLButtonElement>('#resume-save');if(resume)resume.disabled=false;this.byId('start-label').textContent='Take the driver’s seat';this.byId('load-status').hidden=true;}
  error(message:string){this.byId('error').hidden=false;this.byId('error').textContent=message;}
  setSound(on:boolean){this.byId('sound-btn').classList.toggle('muted',!on);this.byId('sound-btn').setAttribute('aria-pressed',String(on));this.byId('sound-btn').setAttribute('aria-label',on?'Mute sound':'Enable sound');}
  closePanel(){this.dialog=null;this.byId('drawer').hidden=true;}
  togglePanel(panel:'map'|'help'){
    if(this.dialog===panel){this.closePanel();return;}this.dialog=panel;this.byId('drawer').hidden=false;this.byId('drawer-title').textContent=panel==='map'?'The City Loop':'In the driver’s seat';
    this.byId('drawer-content').innerHTML=panel==='map'?this.mapMarkup():`<p class="panel-intro">A good service starts with a smooth departure.</p><ol class="instructions"><li>Close the doors with <kbd>D</kbd>.</li><li>Press <kbd>W</kbd> to add power. Press <kbd>S</kbd> to move back through coast into braking.</li><li>Watch the next station distance. Begin braking early and stop within 8 metres of the marker.</li><li>Open the doors, allow 8 seconds for boarding, then close them to depart.</li></ol><div class="key-list"><span>Change camera <kbd>C</kbd></span><span>Route map <kbd>M</kbd></span><span>Horn <kbd>H</kbd></span><span>Emergency brake <kbd>SPACE</kbd></span><span>Pause <kbd>ESC</kbd></span></div><div class="about"><h3>About this driving build</h3><p>Real Melbourne building footprints and measured heights, with generated façades. Official transport route shapes are joined into a training circuit. Gradients, station interiors and train handling are approximations. This is an independent training scenario, not a current scheduled service or an operational railway model.</p><a href="https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/" target="_blank" rel="noreferrer">City of Melbourne building data · CC BY 4.0 ↗</a><br><a href="https://opendata.transport.vic.gov.au/dataset/public-transport-lines-and-stops" target="_blank" rel="noreferrer">Route data © Department of Transport and Planning · CC BY 4.0 ↗</a></div>`;
    this.updateMapDot();
  }
  private mapMarkup(){
    const pt=(p:{x:number;z:number})=>`${(p.x+1500)/8+15},${(p.z+1150)/8+12}`;
    return `<p class="panel-intro">City Loop · All stations<br>Flinders Street to Flinders Street</p><svg class="route-map" viewBox="0 0 360 270" role="img" aria-label="City Loop route with five station stops"><path d="M0 232 Q120 230 210 248 T360 218" fill="none" stroke="#8fa8ab" stroke-width="14" opacity=".35"/><polyline points="${ROUTE_MAP.map(pt).join(' ')}" fill="none" stroke="#0072ce" stroke-width="3"/>${STATIONS.slice(0,-1).map(s=>{const [x,y]=pt(positionAt(s.distance)).split(',').map(Number);return `<circle cx="${x}" cy="${y}" r="5" fill="#ffffff" stroke="#0072ce" stroke-width="2"/><text x="${x+9}" y="${y-9}" font-size="8" fill="#071c39">${s.short}</text>`;}).join('')}<circle id="train-map-dot" r="5" fill="#071c39" stroke="white" stroke-width="2"/></svg><div class="station-list">${STATIONS.map((s,i)=>`<div><span>${String(i+1).padStart(2,'0')}</span><strong>${s.name}</strong><small>${s.underground?'Underground':'Surface'}</small></div>`).join('')}</div><p class="map-note">Approximate training alignment · ${(ROUTE_LENGTH/1000).toFixed(1)} km</p>`;
  }
  update(sim:Simulation,view:View){
    const s=sim.state,station=STATIONS[s.nextStation],menu=s.phase==='ready';
    this.lastDistance=s.distance;
    if(this.lastPhase!==s.phase){
      this.byId('welcome').hidden=!menu;this.byId('scene-caption').hidden=!menu;this.byId('credits').hidden=!menu;
      this.byId('driving-hud').hidden=menu;this.byId('pause-overlay').hidden=s.phase!=='paused';this.byId('complete-overlay').hidden=s.phase!=='complete';
      this.byId('pause-btn').setAttribute('aria-label',s.phase==='paused'?'Resume':'Pause');
      this.byId('mode-label').textContent=menu?'Driver simulator':'All stations · 06:42';
      if(s.phase==='complete'){
        const served=s.results.filter(r=>r.outcome==='served').length;
        this.byId('results-summary').textContent=`${served} of ${STATIONS.length} stops served · ${Math.floor(s.time/60)}m ${Math.floor(s.time%60)}s · ${Math.round(s.overspeedSeconds)}s over the limit`;
        this.byId('results-list').innerHTML=s.results.map(r=>`<div><span>${r.station}</span><strong>${r.outcome==='missed'?'Missed':`${Math.abs(r.error).toFixed(1)} m accuracy`}</strong></div>`).join('');
      }
      this.lastPhase=s.phase;
    }
    this.byId('speed').textContent=String(Math.round(s.speed*3.6));this.byId('speed-fill').style.width=`${Math.min(100,s.speed*3.6/80*100)}%`;
    this.byId('speed').classList.toggle('overspeed',s.speed*3.6>speedLimitAt(s.distance)+2);this.byId('speed-limit').textContent=String(speedLimitAt(s.distance));
    this.byId('controller-state').textContent=s.emergency?'EMERGENCY':s.controller===0?'COAST':s.controller>0?`POWER ${s.controller}`:`BRAKE ${-s.controller}`;
    (this.byId('controller') as HTMLInputElement).value=String(s.controller);
    this.byId('doors-label').textContent=s.doors?(s.dwell>=8?'Close doors':`Boarding ${Math.ceil(8-s.dwell)}s`):'Open doors';this.byId('doors-btn').classList.toggle('open',s.doors);
    this.byId('view-label').textContent=view==='cab'?'CAB VIEW':'EXTERIOR VIEW';
    const seconds=6*3600+42*60+Math.floor(s.time);this.byId('clock').textContent=[Math.floor(seconds/3600)%24,Math.floor(seconds/60)%60,seconds%60].map(n=>String(n).padStart(2,'0')).join(':');
    this.byId('message').textContent=sim.message;
    if(station){
      const distance=station.distance-s.distance;
      this.byId('station-name').textContent=station.name;this.byId('station-distance').textContent=Math.abs(distance)<1000?`${Math.round(distance)} m`:`${(distance/1000).toFixed(2)} km`;
      this.byId('station-instruction').textContent=s.doors?'At platform':Math.abs(distance)<8&&s.speed<.05?'Open doors':distance<0?'Past stop marker':distance<250?'Approaching platform':station.underground?'Underground platform':'Surface platform';
      this.root.querySelectorAll<HTMLElement>('.journey-stop').forEach((e,i)=>{e.classList.toggle('active',i===s.nextStation%5);e.classList.toggle('visited',i<s.nextStation);});
    }
    this.updateMapDot();
  }
  private updateMapDot(){if(this.dialog!=='map')return;const p=positionAt(this.lastDistance),dot=this.root.querySelector('#train-map-dot');dot?.setAttribute('cx',String((p.x+1500)/8+15));dot?.setAttribute('cy',String((p.z+1150)/8+12));}
}
