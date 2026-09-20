import * as T from 'three/webgpu';
import { EnvironmentEffects } from './environment';
import riverSource from '../data/river-source.json';
import { stationArchitecture } from './stations';
import { stationDetails } from './station-details';
import { Passengers } from './passengers';
import { createPassengerPlacements } from './passenger-motion';
import type { TrainState } from '../game/simulation';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { SkyMesh } from 'three/addons/objects/SkyMesh.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { positionAt, tangentAt, ROUTE_LENGTH, STATIONS, project, isUnderground } from '../data/route';
import { labelTexture, surfaceTexture, stationTileTexture } from './materials';
import { createBuildingMaterial } from './building-materials';
import { SurfaceLibrary } from './surface-library';
import { CorridorScenery } from './corridor';
import { applyBoxSurfaceUV } from './surface-uv';
import { PhotographicCity } from './photographic-city';
import {platformInboardShift} from './platform-layout';

const vector=(v:{x:number;y:number;z:number})=>new T.Vector3(v.x,v.y,v.z);
export class World {
  surface=new T.Group();railway=new T.Group();stations=new T.Group();
  cityChunks:T.Mesh[]=[];cityReady=false;buildingCount=0;
  exteriorBackground?:T.Texture;
  sun:T.DirectionalLight;ambient:T.HemisphereLight;sky:SkyMesh;
  private effects:EnvironmentEffects;
  private surfaces=new SurfaceLibrary();
  private corridor:CorridorScenery;
  private passengers:Passengers;
  private photographic=new PhotographicCity();
  private concrete=new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#95978b',roughness:.96});
  private metal=new T.MeshStandardMaterial({color:'#657579',metalness:.7,roughness:.35});
  private dark=new T.MeshStandardMaterial({color:'#243139',roughness:.8});
  private worker?:Worker;
  private landmarkReady:Promise<void>=Promise.resolve();
  constructor(public scene:T.Scene){
    this.effects=new EnvironmentEffects(scene);
    scene.add(this.surface,this.railway,this.stations);
    this.sky=new SkyMesh();this.sky.scale.setScalar(45000);this.surface.add(this.sky);
    this.sky.turbidity.value=3.5;this.sky.rayleigh.value=1.4;
    const sunPosition=new T.Vector3(.7,.55,.3).normalize();this.sky.sunPosition.value.copy(sunPosition);
    this.sun=new T.DirectionalLight('#fff0ce',3.2);this.sun.position.copy(sunPosition).multiplyScalar(300);
    this.sun.castShadow=true;this.sun.shadow.mapSize.set(2048,2048);this.sun.shadow.camera.left=-170;this.sun.shadow.camera.right=170;
    this.sun.shadow.camera.top=170;this.sun.shadow.camera.bottom=-170;this.sun.shadow.camera.near=.5;this.sun.shadow.camera.far=900;
    this.sun.shadow.bias=-.0002;this.sun.shadow.normalBias=.08;scene.add(this.sun,this.sun.target);
    this.ambient=new T.HemisphereLight('#c4ddeb','#787766',1.1);scene.add(this.ambient);
    this.corridor=new CorridorScenery(this.surfaces);this.surface.add(this.corridor.group,this.photographic.group);
    this.buildGround();this.buildTrack();this.buildStations();this.buildLandmarks();
    this.passengers=new Passengers(createPassengerPlacements());this.scene.add(this.passengers.group);
  }
  private box(parent:T.Object3D,w:number,h:number,d:number,x:number,y:number,z:number,material:T.Material){
    const geometry=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/4)));
    applyBoxSurfaceUV(geometry,material);
    const m=new T.Mesh(geometry,material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
  }
  private buildGround(){
    const groundShape=new T.Shape();groundShape.moveTo(-9000,-9000);groundShape.lineTo(9000,-9000);groundShape.lineTo(9000,9000);groundShape.lineTo(-9000,9000);groundShape.closePath();
    const waterRings=riverSource.geometry.coordinates.map(ring=>ring.map(([lon,lat])=>{
      const p=project(lon,lat);return new T.Vector2(p.x,-p.z);
    }));
    groundShape.holes.push(new T.Path(waterRings[0]));
    // Cut narrow, route-following approach trenches. Without these, the flat
    // city ground clips through the windscreen before the tunnel transition.
    let approach:number[]=[];
    const finishApproach=()=>{
      if(approach.length<2){approach=[];return;}
      const edge=(s:number,side:number)=>{const p=positionAt(s),t=tangentAt(s),n=Math.hypot(t.x,t.z);return new T.Vector2(p.x+t.z/n*side,-p.z+t.x/n*side);};
      const outline=[...approach.map(s=>edge(s,5)),...approach.slice().reverse().map(s=>edge(s,-5))];
      const hole=new T.Path(outline);hole.closePath();groundShape.holes.push(hole);approach=[];
    };
    for(let s=0;s<=ROUTE_LENGTH;s+=4){const y=positionAt(s).y;if(y<2&&y>-9)approach.push(s);else finishApproach();}finishApproach();
    const groundGeometry=new T.ShapeGeometry(groundShape),uv=groundGeometry.attributes.uv;
    for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)/3.1,uv.getY(i)/3.1);
    const ground=new T.Mesh(groundGeometry,this.concrete);
    ground.rotation.x=-Math.PI/2;ground.position.y=-1;ground.receiveShadow=true;this.surface.add(ground);
    // Preserve both surveyed banks and variable width; no smoothing across city blocks.
    const waterShape=new T.Shape(waterRings[0]);
    waterShape.holes.push(...waterRings.slice(1).map(ring=>new T.Path(ring)));
    for(const ring of waterRings.slice(1)){
      const island=new T.Mesh(new T.ShapeGeometry(new T.Shape(ring)),this.concrete);
      island.rotation.x=-Math.PI/2;island.position.y=-1;island.receiveShadow=true;this.surface.add(island);
    }
    const river=new T.Mesh(new T.ShapeGeometry(waterShape),this.effects.water);
    // Authored water datum must sit below the mapped promenade/park surfaces.
    river.rotation.x=-Math.PI/2;river.position.y=-1.65;river.receiveShadow=true;this.surface.add(river);
  }
  private ribbon(curve:T.Curve<T.Vector3>,width:number,mat:T.Material,steps:number){
    const pos:number[]=[],uv:number[]=[];
    for(let i=0;i<steps;i++){
      const a=curve.getPoint(i/steps),b=curve.getPoint((i+1)/steps),t=b.clone().sub(a).normalize(),side=new T.Vector3(-t.z,0,t.x).multiplyScalar(width/2);
      const points=[a.clone().add(side),b.clone().add(side),a.clone().sub(side),a.clone().sub(side),b.clone().add(side),b.clone().sub(side)];
      points.forEach(p=>{pos.push(p.x,p.y,p.z);uv.push(p.x/2,p.z/2);});
    }
    const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.computeVertexNormals();
    const mesh=new T.Mesh(g,mat);mesh.receiveShadow=true;return mesh;
  }
  private buildTrack(){
    const decks:T.BufferGeometry[]=[];
    for(let s=0;s<ROUTE_LENGTH;s+=12){
      const p=vector(positionAt(s+6)),t=vector(tangentAt(s+6));if(p.y<1.5||(s>=162&&s<1146))continue;
      const q=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,1),t);
      const deck=new T.BoxGeometry(5.5,.6,12.4);deck.applyQuaternion(q);deck.translate(p.x,p.y-.35,p.z);decks.push(deck);
      if(Math.floor(s/12)%3===0){const support=new T.BoxGeometry(1.2,p.y,1.2);support.translate(p.x,p.y/2-.5,p.z);decks.push(support);}
    }
    // Retaining walls make the shallow cut-and-cover approaches read as a
    // railway trench while the rail level passes through the city ground.
    for(let s=0;s<ROUTE_LENGTH;s+=4){
      const p=positionAt(s+2);if(p.y>=-.5||p.y<=-6)continue;
      const t=tangentAt(s+2),length=Math.hypot(t.x,t.z)||1;
      for(const side of [-1,1]){const wall=new T.BoxGeometry(.45,-p.y+.1,4.2);wall.rotateY(Math.atan2(t.x,t.z));wall.translate(p.x+t.z/length*side*5,p.y/2-.45,p.z-t.x/length*side*5);decks.push(wall);}
    }
    const viaduct=new T.Mesh(mergeGeometries(decks),this.concrete);viaduct.receiveShadow=true;this.railway.add(viaduct);decks.forEach(g=>g.dispose());
    const points=Array.from({length:Math.ceil(ROUTE_LENGTH/4)+1},(_,i)=>vector(positionAt(Math.min(ROUTE_LENGTH,i*4))));
    const curve=new T.CatmullRomCurve3(points);
    const ballast=this.surfaces.ballast;
    this.railway.add(this.ribbon(curve,4.3,ballast,Math.ceil(ROUTE_LENGTH/4)));
    const steel=new T.MeshStandardMaterial({color:'#b4b7af',metalness:.9,roughness:.32});
    // Broad gauge: 1,600 mm between running rails. Instancing limits draw calls.
    const railParts:T.BufferGeometry[]=[];
    for(let s=0;s<ROUTE_LENGTH;s+=4){
      const p=vector(positionAt(s+2)),t=vector(tangentAt(s+2)),q=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,1),t);
      const side=new T.Vector3(-t.z,0,t.x);
      for(const offset of [-.8,.8]){
        const g=new T.BoxGeometry(.075,.15,4.15);g.applyQuaternion(q);g.translate(p.x+side.x*offset,p.y+.22,p.z+side.z*offset);railParts.push(g);
      }
    }
    const rails=new T.Mesh(mergeGeometries(railParts),steel);rails.receiveShadow=true;this.railway.add(rails);railParts.forEach(g=>g.dispose());
    const sleepers=new T.InstancedMesh(new T.BoxGeometry(2.65,.13,.25),this.concrete,Math.ceil(ROUTE_LENGTH/.7));
    const matrix=new T.Matrix4();let count=0;
    for(let s=0;s<ROUTE_LENGTH;s+=.7){const p=vector(positionAt(s));p.y+=.08;const t=vector(tangentAt(s));matrix.compose(p,new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,1),t),new T.Vector3(1,1,1));sleepers.setMatrixAt(count++,matrix);}
    sleepers.count=count;sleepers.receiveShadow=true;this.railway.add(sleepers);
    const poles:T.BufferGeometry[]=[],wires:T.Vector3[]=[];
    for(let s=10;s<ROUTE_LENGTH;s+=42){
      if(isUnderground(s)||(s>=145&&s<1160))continue;
      // Heritage cross-spans carry the wire over Flinders Street. The generic
      // near-track mast would stand inside its covered passenger platform.
      if(STATIONS.some(st=>st.code==='FSS'&&Math.abs(s-st.distance+65)<104))continue;
      const p=vector(positionAt(s)),t=vector(tangentAt(s)),side=new T.Vector3(-t.z,0,t.x);
      const post=new T.BoxGeometry(.18,6.8,.18);post.translate(p.x+side.x*3.2,p.y+3.4,p.z+side.z*3.2);poles.push(post);
      const arm=new T.BoxGeometry(4.1,.13,.13);arm.rotateY(-Math.atan2(side.z,side.x));arm.translate(p.x+side.x*1.5,p.y+6.65,p.z+side.z*1.5);poles.push(arm);
    }
    this.railway.add(new T.Mesh(mergeGeometries(poles),this.metal));poles.forEach(g=>g.dispose());
    for(let s=0;s<ROUTE_LENGTH;s+=6){if(s>=145&&s<1160)continue;const a=vector(positionAt(s)),b=vector(positionAt(Math.min(s+6,ROUTE_LENGTH)));a.y+=5.9;b.y+=5.9;wires.push(a,b);}
    this.railway.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(wires),new T.LineBasicMaterial({color:'#343e3f'})));
    // Continuous tunnel cross-section, opening into larger station chambers.
    const tunnelPos:number[]=[],tunnelUv:number[]=[];
    const tunnelBreaks=[0,ROUTE_LENGTH,...Array.from({length:Math.ceil(ROUTE_LENGTH/5)},(_,i)=>i*5),...STATIONS.filter(st=>st.underground).flatMap(st=>[st.distance-168,st.distance+38])].sort((a,b)=>a-b);
    for(let segment=0;segment<tunnelBreaks.length-1;segment++){
      const s=tunnelBreaks[segment],end=tunnelBreaks[segment+1],mid=(s+end)/2;
      if(end<=s||positionAt(mid).y>-5.6)continue;
      if(STATIONS.some(st=>st.underground&&mid>st.distance-168&&mid<st.distance+38))continue;
      const a=vector(positionAt(s)),b=vector(positionAt(end));
      const ta=vector(tangentAt(s)),tb=vector(tangentAt(end));const sa=new T.Vector3(-ta.z,0,ta.x),sb=new T.Vector3(-tb.z,0,tb.x);
      for(let k=0;k<16;k++){
        const point=(p:T.Vector3,side:T.Vector3,angle:number)=>p.clone().addScaledVector(side,Math.cos(angle)*3.4).add(new T.Vector3(0,.9+Math.sin(angle)*3.9,0));
        const theta=-.22+k*(Math.PI+.44)/16,theta2=-.22+(k+1)*(Math.PI+.44)/16;
        const p0=point(a,sa,theta),p1=point(b,sb,theta),p2=point(a,sa,theta2),p3=point(b,sb,theta2);
        [p0,p2,p1,p1,p2,p3].forEach(p=>tunnelPos.push(p.x,p.y,p.z));tunnelUv.push(k/4,s/6,(k+1)/4,s/6,k/4,(s+5)/6,k/4,(s+5)/6,(k+1)/4,s/6,(k+1)/4,(s+5)/6);
      }
    }
    const tg=new T.BufferGeometry();tg.setAttribute('position',new T.Float32BufferAttribute(tunnelPos,3));tg.setAttribute('uv',new T.Float32BufferAttribute(tunnelUv,2));tg.computeVertexNormals();
    this.railway.add(new T.Mesh(tg,new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#707a79',side:T.DoubleSide,roughness:1})));
    const lightMat=new T.MeshBasicMaterial({color:'#dde5c4'});const lights:T.BufferGeometry[]=[],frames:T.BufferGeometry[]=[];
    for(let s=0;s<ROUTE_LENGTH;s+=22){
      if(!isUnderground(s)||STATIONS.some(st=>Math.abs(s-st.distance+65)<108))continue;
      const p=vector(positionAt(s)),t=vector(tangentAt(s)),side=new T.Vector3(-t.z,0,t.x);
      const g=new T.BoxGeometry(.12,.15,1.5);g.rotateY(Math.atan2(t.x,t.z));g.translate(p.x+side.x*2.7,p.y+2.5,p.z+side.z*2.7);lights.push(g);
      if(Math.floor(s/22)%2===0){
        const ring=new T.TorusGeometry(3.4,.035,4,24,Math.PI+.4);ring.rotateZ(-.2);ring.rotateY(Math.atan2(t.x,t.z));ring.translate(p.x,p.y+1,p.z);frames.push(ring);
      }
    }
    if(lights.length)this.railway.add(new T.Mesh(mergeGeometries(lights),lightMat));
    if(frames.length)this.railway.add(new T.Mesh(mergeGeometries(frames),this.dark));
    [...lights,...frames].forEach(g=>g.dispose());
  }
  private buildStations(){
    const yellow=new T.MeshStandardMaterial({color:'#d3b349',roughness:.75});
    for(const [index,station] of STATIONS.entries()){
      const p=vector(positionAt(station.distance-65)),group=new T.Group();
      group.userData.center=p;group.userData.underground=station.underground;this.stations.add(group);
      const platformMaterial=station.code==='SXS'?this.surfaces.asphalt:station.code==='FSS'?this.surfaces.paving:new T.MeshStandardMaterial({map:stationTileTexture(station.code),color:'#dddcd4',roughness:.76});
      const edgeShift=platformInboardShift(station.code);
      this.box(group,(station.code==='MCE'?9:6)+edgeShift,1.1,200,(station.code==='MCE'?6.75:5.25)-edgeShift/2,.5,0,platformMaterial);
      this.box(group,.45,.03,198,2.48-edgeShift,1.065,0,yellow);
      this.box(group,.1,.09,198,2.21-edgeShift,.96,0,this.concrete);
      const backMaterial=new T.MeshStandardMaterial({color:station.color,roughness:station.code==='PAR'?.36:.7,metalness:station.underground?.18:0});
      if(station.underground){
        if(station.code!=='MCE'){
          // Circulation openings meet the reference-based side vestibules.
          for(const [from,to] of [[-103,-53.2],[-46.8,41.8],[48.2,103]])
            this.box(group,1,3.3,to-from,8.5,1.65,(from+to)/2,backMaterial);
        }
        this.box(group,1,3.3,206,-3.5,1.65,0,backMaterial);
      }
      stationArchitecture(group,station,index,this.surfaces.ballast);
      stationDetails(group,station.code,station.name);
      for(let z=-90;z<=90;z+=20){
        const lamp=new T.PointLight('#fff1d3',station.underground?55:8,20,2);lamp.position.set(4,4.5,z);group.add(lamp);
        if(station.underground&&station.code!=='MCE'&&(Math.abs(z+50)<3.3||Math.abs(z-45)<3.3))continue;
        const sign=new T.Mesh(new T.PlaneGeometry(station.underground?3.4:5.5,station.underground?.45:.7),new T.MeshBasicMaterial({map:labelTexture(station.name,station.underground?'#e3e4d7':'#16303b',station.underground?'#172421':'#ffffff'),side:T.DoubleSide}));
        sign.rotation.y=-Math.PI/2;sign.position.set(7.92,station.underground&&station.code!=='MCE'?2.7:3.8,z);group.add(sign);
      }
      const marker=new T.Mesh(new T.PlaneGeometry(.55,.75),new T.MeshBasicMaterial({map:labelTexture('7','#f2eee0','#1d343d',128,160),side:T.DoubleSide}));
      marker.position.set(2,2.0,65);marker.rotation.y=Math.PI;group.add(marker);
      // A paired clear signal is a training cue, not a real block/interlocking model.
      this.box(group,.09,3,.09,-2.5,1.5,92,this.metal);this.box(group,.48,1.1,.25,-2.5,3.2,92,this.dark);
      const green=new T.Mesh(new T.SphereGeometry(.13,10,8),new T.MeshBasicMaterial({color:'#70eda5'}));green.position.set(-2.5,3.4,91.85);group.add(green);
      // Bend platforms, walls, ceiling and all fittings along the exact same
      // curve used by the rails and train. A straight station box can cross
      // the running line even when its centre and bearing appear correct.
      const warp=(x:number,y:number,z:number)=>{
        const at=station.distance-65+z,clamped=T.MathUtils.clamp(at,0,ROUTE_LENGTH),point=positionAt(clamped),t=tangentAt(clamped),length=Math.hypot(t.x,t.z)||1;
        const extension=at-clamped;
        if(station.code==='FSS')x=-x;
        return new T.Vector3(point.x+t.x*extension+t.z/length*x,point.y+t.y*extension+y,point.z+t.z*extension-t.x/length*x);
      };
      for(const child of group.children){
        if(child instanceof T.Mesh){
          // Reflection relocates the platform correctly but reverses printed
          // sign faces. Reverse their U coordinates once before batching.
          if(station.code==='FSS'&&child.geometry instanceof T.PlaneGeometry){
            const uv=child.geometry.attributes.uv;
            for(let i=0;i<uv.count;i++)uv.setX(i,1-uv.getX(i));
            uv.needsUpdate=true;
          }
          child.updateMatrix();child.geometry.applyMatrix4(child.matrix);
          const attribute=child.geometry.attributes.position;
          for(let i=0;i<attribute.count;i++){const w=warp(attribute.getX(i),attribute.getY(i),attribute.getZ(i));attribute.setXYZ(i,w.x,w.y,w.z);}
          attribute.needsUpdate=true;
          if(station.code==='FSS'){
            // Mirroring the platform side changes handedness; restore outward faces.
            const indices=child.geometry.index;
            if(indices){for(let i=0;i<indices.count;i+=3){const b=indices.getX(i+1);indices.setX(i+1,indices.getX(i+2));indices.setX(i+2,b);}indices.needsUpdate=true;}
            else{for(const a of Object.values(child.geometry.attributes) as T.BufferAttribute[]){for(let i=0;i<a.count;i+=3)for(let k=0;k<a.itemSize;k++){const array=a.array,b=array[(i+1)*a.itemSize+k];array[(i+1)*a.itemSize+k]=array[(i+2)*a.itemSize+k];array[(i+2)*a.itemSize+k]=b;}a.needsUpdate=true;}}
          }
          child.geometry.computeVertexNormals();child.geometry.computeBoundingSphere();
          child.position.set(0,0,0);child.rotation.set(0,0,0);child.scale.set(1,1,1);child.updateMatrix();
        }else if(child instanceof T.PointLight){child.position.copy(warp(child.position.x,child.position.y,child.position.z));}
      }
      // Geometry is already in world space; merge repeated fittings by material.
      const batches=new Map<T.Material,T.Mesh[]>();
      for(const child of group.children){if(child instanceof T.Mesh&&!Array.isArray(child.material)){const batch=batches.get(child.material)??[];batch.push(child);batches.set(child.material,batch);}}
      for(const [material,meshes] of batches){
        if(meshes.length<2)continue;
        const merged=mergeGeometries(meshes.map(mesh=>mesh.geometry));if(!merged)continue;
        const mesh=new T.Mesh(merged,material);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);
        meshes.forEach(old=>{group.remove(old);old.geometry.dispose();});
      }
    }
  }
  private buildLandmarks(){
    // Detailed Blender-authored heritage building, referenced to the main dome.
    // The official survey's matching massing is removed by the city worker.
    this.landmarkReady=new GLTFLoader().loadAsync('/models/stations-flinders.glb').then(gltf=>{
      const p=project(144.96714,-37.81793),landmark=gltf.scene;
      landmark.position.set(p.x,0,p.z);landmark.rotation.y=.22;
      landmark.traverse(child=>{if(child instanceof T.Mesh){child.castShadow=true;child.receiveShadow=true;}});
      this.surface.add(landmark);
    });
  }
  async loadCity(onProgress:(message:string)=>void){
    onProgress('Loading Melbourne building survey…');
    await Promise.all([this.landmarkReady,this.surfaces.ready,this.corridor.ready,this.passengers.ready,this.photographic.ready]);
    const response=await fetch('/data/buildings.json');if(!response.ok)throw new Error('Building dataset could not be loaded.');
    const data=await response.json();
    const materials=[createBuildingMaterial()];
    this.worker=new Worker(new URL('./city.worker.ts',import.meta.url),{type:'module'});
    return new Promise<void>((resolve,reject)=>{
      this.worker!.onerror=()=>{this.worker?.terminate();reject(new Error('City geometry could not be prepared.'));};
      this.worker!.onmessage=(event)=>{
        if(event.data.done){this.cityReady=true;this.buildingCount=event.data.count;this.worker?.terminate();resolve();return;}
        const {key,position,normal,uv,color}=event.data;
        const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.BufferAttribute(position,3));geometry.setAttribute('normal',new T.BufferAttribute(normal,3));geometry.setAttribute('uv',new T.BufferAttribute(uv,2));if(color)geometry.setAttribute('color',new T.BufferAttribute(color,3));geometry.computeBoundingSphere();
        const [x,z]=key.split(',').map(Number);const mesh=new T.Mesh(geometry,materials[Math.abs(x+z)%materials.length]);mesh.castShadow=true;mesh.receiveShadow=true;mesh.userData.center=new T.Vector3(x*250+125,0,z*250+125);
        this.cityChunks.push(mesh);this.surface.add(mesh);onProgress(`Preparing city blocks · ${this.cityChunks.length}`);
      };
      this.worker!.postMessage({buildings:data.buildings.filter((b:{ring:[number,number][];base:number;height:number;kind?:string})=>!this.photographic.conflictsWithClearance(b)&&!this.photographic.replacesBuilding(b))});
    });
  }
  passengerMetrics(){return this.passengers.metrics();}
  update(state:TrainState,camera:T.Camera){
    const {distance,time:seconds}=state;
    const p=vector(positionAt(distance)),underground=isUnderground(distance);
    const darkness=T.MathUtils.smoothstep(-p.y,0,15);
    this.scene.environmentIntensity=.55*(1-darkness)+.025*darkness;
    this.surface.visible=!underground;this.sun.intensity=3.2*(1-darkness);this.ambient.intensity=1.1-.55*darkness;
    this.scene.background=underground?new T.Color('#141d21'):(this.exteriorBackground??null);
    this.sky.visible=!this.exteriorBackground;
    this.effects.update(darkness,seconds);this.corridor.update(camera);this.passengers.update(camera,state);this.photographic.update(camera);
    this.sun.position.copy(p).add(new T.Vector3(350,280,150));this.sun.target.position.copy(p);this.sun.target.updateMatrixWorld();
    for(const chunk of this.cityChunks)chunk.visible=chunk.userData.center.distanceTo(camera.position)<2300;
    // Only nearby platform lamps contribute to the lighting shader.
    this.stations.children.forEach(st=>{
      st.visible=st.userData.center.distanceTo(camera.position)<620;
      // Sunlit platforms retain their visible lamp fittings. The local point
      // lights illuminate enclosed stations, where they affect the scene.
      const near=st.userData.underground&&st.userData.center.distanceTo(p)<280;
      st.children.forEach(c=>{if(c instanceof T.PointLight)c.visible=near;});
    });
  }
}
