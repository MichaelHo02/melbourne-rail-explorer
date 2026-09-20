import { STATIONS, ROUTE_LENGTH, ROUTE_MAP, positionAt, speedLimitAt } from '../data/route';
import type { Simulation } from '../game/simulation';
import type { View } from '../render/renderer';
import { stoppingDistance } from '../game/motion';

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

// Printed instrument faces use game speed and controller demand, not pressure telemetry.
const dialTicks=(maximum:number)=>Array.from({length:13},(_,i)=>{
  const a=(135+i*22.5)*Math.PI/180,major=i%3===0;
  return `<line x1="${64+Math.cos(a)*(major?47:51)}" y1="${64+Math.sin(a)*(major?47:51)}" x2="${64+Math.cos(a)*56}" y2="${64+Math.sin(a)*56}"/>${major?`<text x="${64+Math.cos(a)*39}" y="${67+Math.sin(a)*39}">${i/12*maximum}</text>`:''}`;
}).join('');

export interface Actions{start:()=>void;resume:()=>void;restart:()=>void;pause:()=>void;view:()=>void;sound:()=>void;doors:()=>void;controller:(n:number)=>void;emergency:()=>void}
export class HUD {
  private root:HTMLElement;private dialog:'map'|'help'|null=null;private lastPhase='';private lastDistance:number=STATIONS[0].distance;
  private byId=(id:string)=>this.root.querySelector<HTMLElement>(`#${id}`)!;
  constructor(root:HTMLElement,private actions:Actions,hasSave:boolean){
    this.root=root;root.innerHTML=`
    <header class="topbar"><a class="brand" href="/" aria-label="Melbourne Rail Explorer home"><span class="brand-icon"><img src="/brand/melbourne-rail-explorer.png" alt="" width="62" height="62"/></span><span>Melbourne<span class="brand-sub">Rail Explorer</span></span></a>
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
      <div class="next-stop"><span class="eyebrow">NEXT STATION</span><h2 id="station-name">Southern Cross</h2><div><span id="station-distance">—</span><span class="next-dot">•</span><span id="station-instruction">Departure</span></div><div id="stop-guide" class="stop-guide" hidden><span>TRAINING ASSIST</span><strong id="stop-guidance"></strong><div id="stop-scale" class="stop-scale" aria-hidden="true"><i></i><b id="stop-prediction"></b></div><small id="stop-guide-detail"></small></div></div>
      <div class="journey-strip" id="journey-strip">${STATIONS.slice(0,-1).map((s,i)=>`<span class="journey-stop" data-index="${i}"><i></i>${s.short}</span>`).join('')}</div>
      <div id="message" class="driver-message" role="status"></div><div id="announcement" class="announcement" role="status" hidden><span>SERVICE INFORMATION</span><p id="announcement-text"></p></div>
      <section class="dashboard" aria-label="Driving desk">
        <div class="desk-fascia" aria-hidden="true"></div>
        <div class="master-controller">
          <label class="desk-label" for="controller">POWER / BRAKE</label>
          <div class="controller-plate" id="controller-plate">
            <div class="lever-scale" aria-hidden="true"><span>BRAKE <kbd>S</kbd></span><span>COAST</span><span>POWER <kbd>W</kbd></span></div>
            <div class="lever-slot" aria-hidden="true"></div><div class="controller-handle" aria-hidden="true"><i></i></div>
            <input id="controller" type="range" min="-4" max="4" step="1" value="0" aria-label="Train controller: brake to power" aria-valuetext="Coast"/>
          </div>
          <strong id="controller-state" class="controller-readout">COAST</strong>
        </div>
        <div class="instrument-cluster">
          <div class="speed-instrument">
            <svg class="speed-dial" viewBox="0 0 128 128" aria-hidden="true"><circle class="dial-face" cx="64" cy="64" r="59"/><g class="dial-marks">${dialTicks(80)}</g><text class="dial-unit" x="64" y="47">km/h</text><path id="speed-needle" d="M69 59L30 98L59 69Z"/><circle class="needle-pivot" cx="64" cy="64" r="5"/></svg>
            <span id="speed" class="speed-readout" aria-label="Speed in kilometres per hour">0</span>
          </div>
          <div class="effort-instrument">
            <svg class="effort-dial" viewBox="0 0 128 128" aria-hidden="true"><circle class="dial-face" cx="64" cy="64" r="59"/><g class="dial-marks">${dialTicks(100)}</g><path id="effort-needle" d="M68 60L31 97L60 68Z"/><circle class="needle-pivot" cx="64" cy="64" r="5"/></svg>
            <span id="effort-label" class="effort-label">EFFORT</span><span class="effort-readout"><b id="effort-value">0</b><small>% DEMAND</small></span>
          </div>
          <div class="cab-indicators"><div class="train-status" id="train-status"><i aria-hidden="true"></i><span id="traction-status">DOOR INTERLOCK</span></div><span class="cab-limit">LIMIT <strong id="speed-limit">50</strong><small>km/h</small></span></div>
        </div>
        <div class="door-control"><span class="desk-label">PASSENGER DOORS</span><button id="doors-btn" class="door-button"><span class="door-lens">${icon('door')}</span><span id="doors-label">Close doors</span><kbd>D</kbd></button></div>
        <button id="emergency-btn" class="emergency-button" aria-label="Emergency brake" title="Emergency brake · Space" aria-pressed="false"><span class="emergency-mount"><span class="emergency-cap">STOP</span></span><span class="emergency-label">EMERGENCY<br>BRAKE</span><kbd>SPACE</kbd></button>
      </section>
    </main>
    <aside id="drawer" class="drawer" hidden><div class="drawer-heading"><span id="drawer-title">The City Loop</span><button id="close-drawer" class="icon-button" aria-label="Close panel">${icon('close')}</button></div><div id="drawer-content"></div></aside>
    <section id="pause-overlay" class="modal-overlay" hidden><div class="modal"><span class="eyebrow">City Loop · Driver training</span><h2>Service paused</h2><p>Resume your service when ready.</p><button id="continue-btn" class="primary">Back to the cab ${icon('arrow')}</button><button id="restart-btn" class="secondary">Restart service</button></div></section>
    <section id="complete-overlay" class="modal-overlay" hidden><div class="modal"><span class="eyebrow">BACK AT FLINDERS STREET</span><h2>Service complete</h2><p id="results-summary"></p><div id="results-list"></div><button id="again-btn" class="primary">Run another service ${icon('arrow')}</button></div></section>
    <div id="error" class="error-banner" hidden role="alert"></div>
    <footer id="credits" class="credits">Independent simulator · Development build<span>Geography © City of Melbourne & State of Victoria · CC BY 4.0</span></footer>`;
    this.byId('route-length').textContent=`${(ROUTE_LENGTH/1000).toFixed(1)} km`;
    const bind=(id:string,fn:()=>void)=>this.root.querySelector(`#${id}`)?.addEventListener('click',fn);
    bind('start-btn',actions.start);bind('resume-save',actions.resume);bind('pause-btn',actions.pause);bind('continue-btn',actions.pause);
    bind('restart-btn',actions.restart);bind('again-btn',actions.restart);bind('view-btn',actions.view);bind('sound-btn',actions.sound);
    bind('doors-btn',actions.doors);bind('emergency-btn',actions.emergency);bind('map-btn',()=>this.togglePanel('map'));
    bind('help-btn',()=>this.togglePanel('help'));bind('close-drawer',()=>this.closePanel());
    this.byId('controller').addEventListener('input',e=>actions.controller(Number((e.target as HTMLInputElement).value)));
  }
  loading(message:string){this.byId('load-status').textContent=message;}
  ready(){(this.byId('start-btn') as HTMLButtonElement).disabled=false;const resume=this.root.querySelector<HTMLButtonElement>('#resume-save');if(resume)resume.disabled=false;this.byId('start-label').textContent='Take the driver’s seat';this.byId('load-status').hidden=true;}
  startupError(message:string){this.byId('load-status').hidden=true;this.byId('start-label').textContent='Service unavailable';this.error(message);}
  error(message:string){this.byId('error').hidden=false;this.byId('error').textContent=message;}
  setSound(on:boolean){this.byId('sound-btn').classList.toggle('muted',!on);this.byId('sound-btn').setAttribute('aria-pressed',String(on));this.byId('sound-btn').setAttribute('aria-label',on?'Mute sound':'Enable sound');}
  setAnnouncement(text:string){this.byId('announcement').hidden=!text;this.byId('announcement-text').textContent=text;}
  closePanel(){this.dialog=null;this.byId('drawer').hidden=true;}
  togglePanel(panel:'map'|'help'){
    if(this.dialog===panel){this.closePanel();return;}this.dialog=panel;this.byId('drawer').hidden=false;this.byId('drawer-title').textContent=panel==='map'?'The City Loop':'In the driver’s seat';
    this.byId('drawer-content').innerHTML=panel==='map'?this.mapMarkup():`<p class="panel-intro">A good service starts with a smooth departure.</p><ol class="instructions"><li>Close the doors with <kbd>D</kbd>.</li><li>Press <kbd>W</kbd> to add power. Press <kbd>S</kbd> to move back through coast into braking.</li><li>Watch the next station distance. Use the training assist to begin braking early; stop within 8 metres of the marker.</li><li>Open the doors, allow 8 seconds for boarding, then close them to depart.</li></ol><div class="key-list"><span>Change camera <kbd>C</kbd></span><span>Route map <kbd>M</kbd></span><span>Horn <kbd>H</kbd></span><span>Emergency brake <kbd>SPACE</kbd></span><span>Pause <kbd>ESC</kbd></span></div><div class="about"><h3>About this driving build</h3><p>Real Melbourne building footprints, street alignments, Yarra banks and mapped trees, with photographed city mesh captured in 2020 in selected surface areas. Platform fittings use photographic references; interiors and remaining façades are authored. Official transport route shapes are joined into a training circuit. Bridge approaches, tree sizes, gradients, station interiors and train handling are approximations. Nearby traffic replays the official timetable for 19 September 2026. Train types and adjacent track placement are illustrative; no live feed is connected. Cab-inspired instruments simplify the actual controls. This is an independent training scenario, not a current scheduled service or an operational railway model.</p><p>Location sound: Southern Cross field ambience by eaglechopper and Flinders/Swanston street ambience by melbourne.atmospheres (CC0). Parliament: “Xtrap depart.mp3” by Tanoseki, Freesound, <a href="https://creativecommons.org/licenses/by/3.0/" target="_blank" rel="noreferrer">CC BY 3.0</a>; filtered, normalised and faded. These are historic recordings, not dynamic announcements. Service-information captions, the two-note cue and mechanical door/controller/brake effects are authored.</p><a href="https://freesound.org/people/Tanoseki/sounds/69560/" target="_blank" rel="noreferrer">Parliament recording · Tanoseki ↗</a><br><a href="https://data.melbourne.vic.gov.au/explore/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020/information/" target="_blank" rel="noreferrer">Photographic mesh © City of Melbourne · CC BY 4.0 ↗</a><br><a href="https://opendata.transport.vic.gov.au/dataset/gtfs-schedule" target="_blank" rel="noreferrer">Timetable © Transport Victoria · CC BY 4.0 ↗</a><br><a href="https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/" target="_blank" rel="noreferrer">City of Melbourne building data · CC BY 4.0 ↗</a><br><a href="https://opendata.transport.vic.gov.au/dataset/public-transport-lines-and-stops" target="_blank" rel="noreferrer">Route data © Department of Transport and Planning · CC BY 4.0 ↗</a><br><a href="https://discover.data.vic.gov.au/dataset/vicmap-hydro-water-polygon" target="_blank" rel="noreferrer">Yarra banks © State of Victoria (DTP), Vicmap Hydro · CC BY 4.0 ↗</a><br><a href="https://discover.data.vic.gov.au/dataset/vicmap-transport" target="_blank" rel="noreferrer">Roads & rail © State of Victoria (DTP), Vicmap Transport · CC BY 4.0 ↗</a><br><a href="https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/" target="_blank" rel="noreferrer">Mapped trees © City of Melbourne · CC BY 4.0 ↗</a><br><a href="https://discover.data.vic.gov.au/dataset/veac-metropolitan-melbourne-open-space-inventory" target="_blank" rel="noreferrer">Park boundaries © State of Victoria (DEECA) · CC BY 4.0 ↗</a><br><a href="https://polyhaven.com/license" target="_blank" rel="noreferrer">Surface textures & sky · Poly Haven CC0 ↗</a></div>`;
    this.updateMapDot();
  }
  private mapMarkup(){
    const pt=(p:{x:number;z:number})=>`${(p.x+1500)/8+15},${(p.z+1150)/8+12}`;
    return `<p class="panel-intro">City Loop · All stations<br>Flinders Street to Flinders Street</p><svg class="route-map" viewBox="0 0 360 270" role="img" aria-label="City Loop route with five station stops"><path d="M0 232 Q120 230 210 248 T360 218" fill="none" stroke="#8fa8ab" stroke-width="14" opacity=".35"/><polyline points="${ROUTE_MAP.map(pt).join(' ')}" fill="none" stroke="#0072ce" stroke-width="3"/>${STATIONS.slice(0,-1).map(s=>{const [x,y]=pt(positionAt(s.distance)).split(',').map(Number);return `<circle cx="${x}" cy="${y}" r="5" fill="#ffffff" stroke="#0072ce" stroke-width="2"/><text x="${x+9}" y="${y-9}" font-size="8" fill="#071c39">${s.short}</text>`;}).join('')}<circle id="train-map-dot" r="5" fill="#071c39" stroke="white" stroke-width="2"/></svg><div class="station-list">${STATIONS.map((s,i)=>`<div><span>${String(i+1).padStart(2,'0')}</span><strong>${s.name}</strong><small>${s.underground?'Underground':'Surface'}</small></div>`).join('')}</div><p class="map-note">Approximate training alignment · ${(ROUTE_LENGTH/1000).toFixed(1)} km</p>`;
  }
  update(sim:Simulation,_view:View){
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
    this.byId('speed').textContent=String(Math.round(s.speed*3.6));
    this.byId('speed-needle').setAttribute('transform',`rotate(${Math.min(80,s.speed*3.6)*3.375} 64 64)`);
    this.byId('traction-status').textContent=s.emergency?'EMERGENCY BRAKE':s.doors?'DOOR INTERLOCK':s.controller>0?'TRACTION ENABLED':s.controller<0?'SERVICE BRAKE':'DOORS SECURED';
    this.byId('train-status').classList.toggle('warning',s.doors||s.emergency);
    // Door interlock inhibits traction, not the driver's brake demand or emergency latch.
    const demand=s.emergency?100:s.doors&&s.controller>0?0:Math.abs(s.controller)*25;
    this.byId('effort-value').textContent=String(demand);
    this.byId('effort-label').textContent=s.emergency||s.controller<0?'BRAKE':s.controller>0?'POWER':'EFFORT';
    this.byId('effort-needle').setAttribute('transform',`rotate(${demand*2.7} 64 64)`);
    this.byId('controller-plate').style.setProperty('--handle-offset',`${(s.controller+4)*10.5}px`);
    this.byId('emergency-btn').setAttribute('aria-pressed',String(s.emergency));
    this.byId('speed').classList.toggle('overspeed',s.speed*3.6>speedLimitAt(s.distance)+2);this.byId('speed-limit').textContent=String(speedLimitAt(s.distance));
    this.byId('controller-state').textContent=s.emergency?'EMERGENCY':s.controller===0?'COAST':s.controller>0?`POWER ${s.controller}`:`BRAKE ${-s.controller}`;
    const controller=this.byId('controller') as HTMLInputElement;
    controller.value=String(s.controller);controller.setAttribute('aria-valuetext',this.byId('controller-state').textContent??'Coast');
    this.byId('doors-label').textContent=s.doors?(s.dwell>=8?'Close doors':`Boarding ${Math.ceil(8-s.dwell)}s`):'Open doors';this.byId('doors-btn').classList.toggle('open',s.doors);
    this.byId('message').textContent=sim.message;
    if(station){
      const distance=station.distance-s.distance;
      this.byId('station-name').textContent=station.name;this.byId('station-distance').textContent=Math.abs(distance)<1000?`${Math.round(distance)} m`:`${(distance/1000).toFixed(2)} km`;
      this.byId('station-instruction').textContent=s.doors?'At platform':Math.abs(distance)<8&&s.speed<.05?'Open doors':distance<0?'Past stop marker':distance<250?'Approaching platform':station.underground?'Underground platform':'Surface platform';
      const guide=this.byId('stop-guide');guide.hidden=s.doors||distance>650||s.phase==='complete';
      this.root.classList.toggle('show-stop-guide',!guide.hidden&&!menu);
      if(!guide.hidden){
        const braking=s.controller<0||s.emergency,brake=braking?s.controller:-3;
        const prediction=stoppingDistance(s,brake),error=prediction-distance;
        const aligned=Math.abs(distance)<=8&&s.speed<.05;
        const warning=!aligned&&(distance< -8||!Number.isFinite(prediction)||error>8);
        guide.classList.toggle('warning',warning);guide.classList.toggle('aligned',aligned);
        let label:string,detail:string;
        if(aligned){label='On the stop marker';detail='Open the doors to board';}
        else if(distance< -8){label='Stop marker passed';detail='Continue to the next station';}
        else if(s.speed<.05){label=`Move forward ${Math.max(0,Math.round(distance))} m`;detail='Ease into power, then brake gently';}
        else if(!Number.isFinite(prediction)){label='Increase braking';detail='Current brake will not stop in time';}
        else if(braking){label=Math.abs(error)<=8?'Stopping on target':`Stopping ~${Math.round(Math.abs(error))} m ${error<0?'short':'beyond'}`;detail=s.emergency?'Emergency brake applied':`Estimate with brake ${-brake}`;}
        else{const before=distance-prediction-6;label=before>8?`Brake in ~${Math.round(before)} m`:'Brake for the platform';detail='Use brake 3, then ease off near the marker';}
        this.byId('stop-guidance').textContent=label;this.byId('stop-guide-detail').textContent=detail;
        this.byId('stop-scale').hidden=!braking||!Number.isFinite(error)||s.speed<.05;
        this.byId('stop-prediction').style.left=`${Math.max(2,Math.min(98,50+error))}%`;
      }
      this.root.querySelectorAll<HTMLElement>('.journey-stop').forEach((e,i)=>{e.classList.toggle('active',i===s.nextStation%5);e.classList.toggle('visited',i<s.nextStation);});
    }
    this.updateMapDot();
  }
  private updateMapDot(){if(this.dialog!=='map')return;const p=positionAt(this.lastDistance),dot=this.root.querySelector('#train-map-dot');dot?.setAttribute('cx',String((p.x+1500)/8+15));dot?.setAttribute('cy',String((p.z+1150)/8+12));}
}
