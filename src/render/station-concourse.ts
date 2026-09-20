import * as T from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { applyBoxSurfaceUV } from './surface-uv';
import { surfaceTexture } from './materials';

/**
 * Southern Cross's raised circulation layer, referenced to the supplied cab
 * photograph and Transport Victoria's station access description. Coordinates
 * and dimensions are authored for the playable hall, not a surveyed concourse.
 * Keep meshes directly in the station group so its route warp reaches them.
 */
export function southernCrossConcourse(group:T.Group){
  const deckY=8,platformY=1.05,bridgeZ=52,bridgeDepth=8;
  const startX=-61,endX=14,stairCentres=[6.8,-8.5,-36.5];
  const steel=new T.MeshStandardMaterial({color:'#66716f',roughness:.55,metalness:.52});
  const girder=new T.MeshStandardMaterial({color:'#434d4d',roughness:.65,metalness:.38});
  const concrete=new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#b7b9af',roughness:.9});
  const tread=new T.MeshStandardMaterial({color:'#929b96',roughness:.74,metalness:.3});
  const nosing=new T.MeshStandardMaterial({color:'#d9d5b4',roughness:.8});
  const glass=new T.MeshStandardMaterial({color:'#a4bfbc',roughness:.23,metalness:.08,transparent:true,opacity:.24,depthWrite:false,side:T.DoubleSide});
  const batches=new Map<T.Material,T.BufferGeometry[]>();
  function put(g:T.BufferGeometry,material:T.Material){const parts=batches.get(material)??[];parts.push(g);batches.set(material,parts);}
  function box(w:number,h:number,d:number,x:number,y:number,z:number,material:T.Material){
    const g=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/2)));
    g.translate(x,y,z);applyBoxSurfaceUV(g,material);put(g,material);
  }
  function bar(a:T.Vector3,b:T.Vector3,r:number,material:T.Material=steel){
    const delta=b.clone().sub(a),g=new T.CylinderGeometry(r,r,delta.length(),6,Math.max(1,Math.ceil(delta.length()/2)));
    g.applyQuaternion(new T.Quaternion().setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize()));g.translate((a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2);put(g,material);
  }
  const width=endX-startX,cx=(startX+endX)/2,front=bridgeZ-bridgeDepth/2,rear=bridgeZ+bridgeDepth/2;
  // Readable dark edge girders and lighter soffit, with all structure above
  // 6.9 m over the running roads (the authored contact wire is at 5.9 m).
  box(width,.27,bridgeDepth,cx,deckY-.135,bridgeZ,concrete);
  for(const z of [front+.12,rear-.12]){
    box(width,.88,.18,cx,deckY-.66,z,girder);
    for(const y of [deckY-.26,deckY-1.05])box(width,.10,.48,cx,y,z,girder);
    for(let x=startX+1;x<endX;x+=3.5)box(.065,.72,.25,x,deckY-.64,z,steel);
  }
  for(let x=startX+1;x<endX;x+=5)box(.14,.40,bridgeDepth-.45,x,deckY-.49,bridgeZ,steel);
  // Supports land on island platforms, never on a rail or platform edge.
  for(const x of [-50.5,-22.5,7.5])for(const z of [front+1.3,rear-1.3]){
    box(.38,deckY-.55-platformY,.38,x,(deckY-.55+platformY)/2,z,steel);
    box(.63,.16,.63,x,platformY+.08,z,concrete);
    box(1.8,.24,.46,x,deckY-.50,z,girder);
  }
  // Glazed balustrades have genuinely open stair thresholds on the rear edge.
  function guard(from:number,to:number,z:number){
    if(to-from<.05)return;
    box(to-from,.12,.13,(from+to)/2,deckY+.10,z,girder);
    box(to-from,.045,.06,(from+to)/2,deckY+1.27,z,steel);
    const count=Math.ceil((to-from)/1.7),span=(to-from)/count;
    for(let i=0;i<count;i++){
      const x=from+(i+.5)*span;
      box(span-.065,1.06,.022,x,deckY+.66,z,glass);
      box(.052,1.3,.06,from+i*span,deckY+.65,z,steel);
    }
    box(.052,1.3,.06,to,deckY+.65,z,steel);
  }
  guard(startX,5.67,front);
  guard(7.93,endX,front);
  let last=startX;
  for(const x of [...stairCentres].sort((a,b)=>a-b)){guard(last,x-1.13,rear);last=x+1.13;}
  guard(last,endX,rear);
  for(const x of [startX,endX]){
    box(.06,1.3,bridgeDepth,x,deckY+.65,bridgeZ,steel);
    box(.022,1.07,bridgeDepth-.12,x,deckY+.66,bridgeZ,glass);
  }

  // Two 20-riser flights, a proper intermediate landing and a short top
  // return. The playable stair occupies x=5.675..7.925, leaving the passenger
  // walking band and tactile strip clear; identical distant stairs give depth.
  const risers=20,rise=(deckY-platformY)/(risers*2),going=.29,flightRun=risers*going;
  const topLanding=1.8,midLanding=1.65,upperStart=rear+topLanding,upperEnd=upperStart+flightRun;
  const lowerStart=upperEnd+midLanding,lowerEnd=lowerStart+flightRun,middleY=(deckY+platformY)/2;
  const stairWidth=2.15;
  for(const x of stairCentres){
    for(const [near,far,y] of [[rear,upperStart,deckY],[upperEnd,lowerStart,middleY],[lowerEnd,lowerEnd+1.4,platformY]]){
      box(stairWidth,.15,far-near,x,y-.075,(near+far)/2,tread);
      for(const dx of [-stairWidth/2,stairWidth/2]){
        const rx=x+dx;
        bar(new T.Vector3(rx,y+1.03,near),new T.Vector3(rx,y+1.03,far),.028);
        bar(new T.Vector3(rx,y+.52,near),new T.Vector3(rx,y+.52,far),.018);
        for(const z of [near,far])bar(new T.Vector3(rx,y,z),new T.Vector3(rx,y+1.03,z),.022);
      }
    }
    for(const [start,high] of [[upperStart,deckY],[lowerStart,middleY]]){
      for(let i=0;i<risers;i++){
        const y=high-i*rise,z=start+(i+.5)*going;
        // Thin horizontal tread plus vertical riser, rather than a stack of
        // full-height boxes, leaves the underside open like the reference.
        box(stairWidth,.065,going+.008,x,y-.0325,z,tread);
        box(stairWidth,rise,.045,x,y-rise/2,start+(i+1)*going,tread);
        box(stairWidth-.05,.012,.045,x,y+.008,start+(i+1)*going-.035,nosing);
      }
      for(const dx of [-stairWidth/2,stairWidth/2]){
        const rx=x+dx,end=start+flightRun,low=high-risers*rise;
        bar(new T.Vector3(rx,high-.22,start),new T.Vector3(rx,low-.22,end),.105,girder);
        for(const h of [.52,1.03])bar(new T.Vector3(rx,high+h,start),new T.Vector3(rx,low+h,end),h===1.03?.028:.018);
        for(let i=0;i<=risers;i+=4){const z=start+i*going,y=high-i*rise;bar(new T.Vector3(rx,y-.12,z),new T.Vector3(rx,y+1.03,z),.022);}
      }
    }
    // Intermediate landing carries its own slim support frame; low fencing
    // makes the under-stair area visually distinct from the through path.
    for(const dx of [-.86,.86]){
      box(.13,middleY-platformY-.12,.13,x+dx,(middleY+platformY-.12)/2,(upperEnd+lowerStart)/2,steel);
      bar(new T.Vector3(x+dx,platformY+.2,upperEnd),new T.Vector3(x+dx,middleY-.25,lowerStart),.036);
    }
    for(const dx of [-stairWidth/2,stairWidth/2]){
      for(const y of [platformY+.04,platformY+1.01])box(.035,.035,lowerStart-rear,x+dx,y,(rear+lowerStart)/2,steel);
      // Open vertical guard pickets read as a restricted understair zone.
      for(let z=rear;z<lowerStart;z+=.30)box(.022,1.00,.022,x+dx,platformY+.50,z,steel);
    }
  }

  // One glass lift enclosure supplies a second vertical circulation cue in
  // the playable island's rear band. It is scenic; no operable lift is implied.
  const liftX=6.8,liftZ=44.25,liftWidth=2.15,liftDepth=2.8,liftTop=deckY+2.65;
  box(liftWidth,.16,liftDepth,liftX,liftTop,liftZ,steel);
  for(const dx of [-liftWidth/2,liftWidth/2])for(const dz of [-liftDepth/2,liftDepth/2])box(.085,liftTop-platformY,.085,liftX+dx,(liftTop+platformY)/2,liftZ+dz,steel);
  for(const dx of [-liftWidth/2,liftWidth/2]){
    box(.025,liftTop-platformY,liftDepth,liftX+dx,(liftTop+platformY)/2,liftZ,glass);
    for(const y of [middleY,deckY])box(.07,.065,liftDepth,liftX+dx,y,liftZ,steel);
  }
  for(const dz of [-liftDepth/2,liftDepth/2])box(liftWidth,liftTop-platformY,.025,liftX,(liftTop+platformY)/2,liftZ+dz,glass);
  // Lift faces the platform at ground level; the upper door opens directly
  // onto a small deck spur, so the shaft does not finish beside a sealed rail.
  box(liftWidth,.22,front-(liftZ+liftDepth/2),liftX,deckY-.11,(front+liftZ+liftDepth/2)/2,concrete);
  for(const dx of [-liftWidth/2,liftWidth/2])bar(new T.Vector3(liftX+dx,deckY+1.1,liftZ+liftDepth/2),new T.Vector3(liftX+dx,deckY+1.1,front),.025);
  box(.045,2.18,.90,liftX-liftWidth/2-.022,platformY+1.09,liftZ,tread);
  box(.055,2.18,.025,liftX-liftWidth/2-.03,platformY+1.09,liftZ,steel);
  box(.90,2.18,.045,liftX,deckY+1.09,liftZ+liftDepth/2+.022,tread);
  box(.025,2.18,.055,liftX,deckY+1.09,liftZ+liftDepth/2+.03,steel);
  for(const [material,parts] of batches){
    const geometry=mergeGeometries(parts);const mesh=new T.Mesh(geometry,material);
    mesh.name='Southern Cross concourse '+(material===glass?'glazing':material===girder?'girders':material===concrete?'decks':material===nosing?'stair nosings':'structure');
    mesh.castShadow=material!==glass;mesh.receiveShadow=true;group.add(mesh);parts.forEach(g=>g.dispose());
  }
}
