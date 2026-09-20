import * as T from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { labelTexture, surfaceTexture } from './materials';
import { applyBoxSurfaceUV } from './surface-uv';
import {platformInboardShift} from './platform-layout';
import { southernCrossConcourse } from './station-concourse';
import {stationFinish} from './station-materials';

type Station={name:string;code:string;underground:boolean;color:string};
// Authored architectural cues, not a survey of any operational platform.
export function stationArchitecture(group:T.Group,station:Station,index:number,ballast:T.Material){
  const structure=new T.MeshStandardMaterial({color:station.underground?'#b3b5aa':station.code==='FSS'?'#c6b987':'#647777',roughness:.78,metalness:.22});
  const parts:T.BufferGeometry[]=[];
  const box=(w:number,h:number,d:number,x:number,y:number,z:number)=>{const g=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/3)));g.translate(x,y,z);parts.push(g);};
  if(station.underground){
    const central=station.code==='MCE';
    const ceiling=new T.MeshStandardMaterial({color:central?'#c0c0b2':station.code==='FGS'?'#d4d6d0':'#c4cbce',roughness:.64,metalness:.3,side:T.DoubleSide});
    const joint=new T.MeshStandardMaterial({color:'#515956',roughness:.8});
    // Vaulted platform chambers. MCE has the broader island and faceted soffit.
    const points:number[]=[],uvs:number[]=[];
    const cross=(a:number)=>{
      if(!central)return new T.Vector3(2.5+6.5*Math.cos(a*Math.PI),3.0+3.1*Math.sin(a*Math.PI),0);
      const x=-4+19*a;
      // Broad horizontal island soffit with folded side bays, not a curved tube.
      const y=x<0?3.25+(x+4)*.725:x>11?6.15-(x-11)*.34:6.15;
      return new T.Vector3(x,y,0);
    };
    // A thick headwall follows the actual chamber profile. Its opening keeps
    // the existing running-tunnel envelope, including pantograph clearance.
    const portal=new T.Shape();portal.moveTo(-4,-.2);
    for(let k=0;k<=28;k++){const p=cross(central?k/28:1-k/28);portal.lineTo(p.x,p.y+.025);}
    if(central){
      // The far island road also continues beyond the hall; do not terminate
      // its rails against the wider headwall. The outboard part meets the
      // chamber boundary, so it is an open contour rather than an invalid hole.
      const start=Math.acos(2/3.4);portal.lineTo(15,.9+Math.sin(start)*3.9);
      for(let i=0;i<=24;i++){const a=start+i*(Math.PI+.22-start)/24;portal.lineTo(13+Math.cos(a)*3.4,.9+Math.sin(a)*3.9);}
      portal.lineTo(9.6,-.2);
    }else portal.lineTo(9,-.2);
    portal.lineTo(3.4,-.2);
    for(let i=0;i<=32;i++){const a=-.22+i*(Math.PI+.44)/32;portal.lineTo(Math.cos(a)*3.4,.9+Math.sin(a)*3.9);}
    portal.lineTo(-3.4,-.2);portal.closePath();
    const headwall=new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:station.code==='PAR'?'#8c9594':'#a3a59a',roughness:.94});
    const reveal=new T.MeshStandardMaterial({color:'#697370',roughness:.87});
    for(const side of [-1,1]){
      const wall=new T.ExtrudeGeometry(portal,{depth:.75,bevelEnabled:false,curveSegments:32});wall.translate(0,0,side*102.6-.375);
      const uv=wall.attributes.uv,pos=wall.attributes.position;for(let i=0;i<uv.count;i++)uv.setXY(i,pos.getX(i)/2,pos.getY(i)/2);
      group.add(new T.Mesh(wall,headwall));
      // Radial concrete voussoirs give the mouth thickness and shadow without
      // narrowing the route's established opening by even a centimetre.
      const collar:number[]=[];
      for(let i=0;i<24;i++){
        const a=-.22+i*(Math.PI+.44)/24,b=-.22+(i+1)*(Math.PI+.44)/24;
        const ring=(angle:number,r:number)=>[Math.cos(angle)*(3.4+r),.9+Math.sin(angle)*(3.9+r),side*102.18];
        for(const v of [ring(a,0),ring(b,0),ring(a,.2),ring(a,.2),ring(b,0),ring(b,.2)])collar.push(...v);
      }
      const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(collar,3));g.computeVertexNormals();
      const collarMat=reveal.clone();collarMat.side=T.DoubleSide;group.add(new T.Mesh(g,collarMat));
      if(central){
        const bore:number[]=[];
        for(let z=102.3;z<111.99;z+=2.425)for(let k=0;k<24;k++){
          const a=-.22+k*(Math.PI+.44)/24,b=-.22+(k+1)*(Math.PI+.44)/24;
          const at=(angle:number,z:number)=>[13+Math.cos(angle)*3.4,.9+Math.sin(angle)*3.9,side*z];
          for(const v of [at(a,z),at(b,z),at(a,z+2.425),at(a,z+2.425),at(b,z),at(b,z+2.425)])bore.push(...v);
        }
        const bg=new T.BufferGeometry();bg.setAttribute('position',new T.Float32BufferAttribute(bore,3));bg.computeVertexNormals();
        group.add(new T.Mesh(bg,new T.MeshStandardMaterial({color:'#343d3c',roughness:1,side:T.DoubleSide})));
      }
      // Complete the short floor between the platform slab and headwall.
      const edgeShift=platformInboardShift(station.code);
      box((central?9:6)+edgeShift,1.1,2.6,(central?6.75:5.25)-edgeShift/2,.5,side*101.2);
    }
    const entryAt=(z:number)=>!central&&(Math.abs(z+50)<3.2||Math.abs(z-45)<3.2);
    const slices=Array.from(new Set([...Array.from({length:69},(_,i)=>-102+i*3),-53.2,-46.8,41.8,48.2])).sort((a,b)=>a-b);
    for(let j=0;j<slices.length-1;j++)for(let k=0;k<28;k++){
      const z=slices[j],end=slices[j+1],a=cross(k/28),b=cross((k+1)/28);
      if(entryAt((z+end)/2)){
        if(a.x>7.8&&b.x>7.8)continue;
        if(a.x>7.8)a.lerp(b,(a.x-7.8)/(a.x-b.x));
        if(b.x>7.8)b.lerp(a,(b.x-7.8)/(b.x-a.x));
      }
      for(const [p,dz] of [[a,z],[b,z],[a,end],[a,end],[b,z],[b,end]] as const){points.push(p.x,p.y,dz);uvs.push(k/28,dz/3);}
    }
    const shell=new T.BufferGeometry();shell.setAttribute('position',new T.Float32BufferAttribute(points,3));shell.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));shell.computeVertexNormals();group.add(new T.Mesh(shell,ceiling));
    const seams:T.BufferGeometry[]=[];
    for(let z=-102;z<=102;z+=3){const curve=new T.CatmullRomCurve3(Array.from({length:29},(_,k)=>{const p=cross(k/28);p.z=z;p.y-=.012;return p;}).filter(p=>!entryAt(z)||p.x<=7.8));seams.push(new T.TubeGeometry(curve,28,.012,3,false));}
    // FGS tiles and PAR enamel panels carry their own fine joints. Heavy,
    // identical vertical bars hid their different photographic wall finishes.
    if(central)for(let z=-99;z<=99;z+=1.6){const g=new T.BoxGeometry(.028,2.8,.026);g.translate(-2.95,1.7,z);seams.push(g);}
    const seamsMesh=new T.Mesh(mergeGeometries(seams),joint);group.add(seamsMesh);seams.forEach(g=>g.dispose());
    // Longitudinal panel seams establish the scale of the metal soffit.
    for(const a of central?[.15,.29,.48,.68,.86]:[.13,.25,.38,.5,.62,.75,.87]){
      const p=cross(a);
      for(const [from,to] of !central&&p.x>7.8?[[-102,-53.2],[-46.8,41.8],[48.2,102]]:[[-102,102]]){
        const g=new T.BoxGeometry(.025,.018,to-from,1,1,Math.ceil((to-from)/3));g.translate(p.x,p.y-.025,(from+to)/2);group.add(new T.Mesh(g,joint));
      }
    }
    if(central)box(.15,.12,204,7.65,3.25,0);
    else for(const [a,b] of [[-102,-53.2],[-46.8,41.8],[48.2,102]])box(.15,.12,b-a,7.65,3.25,(a+b)/2);
    if(central){
      // The existing column/capital envelope is unchanged. Narrow vertical
      // cream tiles distinguish the island hall from plain structural boxes.
      const cladding=stationFinish(station.code,'column'),columns:T.BufferGeometry[]=[];
      for(let z=-88;z<=88;z+=22)for(const [w,h,d,y] of [[.9,5.1,.9,3.5],[3,.22,1.2,5.85]]){
        const g=new T.BoxGeometry(w,h,d);applyBoxSurfaceUV(g,cladding);g.translate(7.8,y,z);columns.push(g);
      }
      const tiled=new T.Mesh(mergeGeometries(columns),cladding);tiled.castShadow=true;tiled.receiveShadow=true;group.add(tiled);columns.forEach(g=>g.dispose());
      const wall=new T.Mesh(new T.BoxGeometry(.5,6,204,1,1,68),new T.MeshStandardMaterial({color:'#494b47',roughness:.6,metalness:.3}));wall.position.set(14.7,3,0);group.add(wall);
      const railMat=new T.MeshStandardMaterial({color:'#8f9894',metalness:.8,roughness:.32});
      for(const x of [12.2,13.8]){const rail=new T.Mesh(new T.BoxGeometry(.08,.15,204,1,1,68),railMat);rail.position.set(x,.22,0);group.add(rail);}
      box(.3,.08,198,11.02,1.06,0);
    }
    const recess=new T.MeshStandardMaterial({color:'#202827',roughness:.95});
    const trim=new T.MeshStandardMaterial({color:station.code==='PAR'?'#7f989e':'#9baba5',metalness:.45,roughness:.55});
    // Recessed circulation thresholds are architectural cues. The concourse
    // beyond is not modelled; keep the platform's clear walking band intact.
    for(const z of [-50,45]){
      if(!central){
        // World wall is split around this 6.4m opening. A short return lobby
        // supplies real parallax; no stairs or unverified concourse is implied.
        const back=new T.Mesh(new T.BoxGeometry(.05,2.55,6.4),recess);back.position.set(11.02,2.325,z);group.add(back);
        for(const dz of [-3.2,3.2]){const jamb=new T.Mesh(new T.BoxGeometry(3.1,2.65,.16),trim);jamb.position.set(9.48,2.375,z+dz);group.add(jamb);}
        box(3.15,.16,6.55,9.48,3.77,z);box(3.15,.13,6.4,9.48,1.005,z);
        // Close the high arch above the rectangular doorway; the vault ends
        // at this header instead of slicing down through the lobby ceiling.
        box(.28,1.35,6.55,7.94,4.36,z);
        for(const dz of [-3.2,3.2])box(3.15,1.35,.16,9.48,4.36,z+dz);
        // A concealed turn at the rear avoids a black void or fake flat door.
        box(.14,2.55,2.1,10.7,2.325,z+2.1);
      }
      if(central){box(.16,.53,3.4,7.51,3.75,z);for(const dz of [-1.25,1.25])box(.04,2.1,.04,7.51,5.04,z+dz);}
      const destination=station.code==='PAR'?'Way out →':station.code==='FGS'?'Way out →':'↑ Way out';
      const exit=new T.Mesh(new T.PlaneGeometry(3.2,.45),new T.MeshBasicMaterial({map:labelTexture(destination,'#172825')}));exit.rotation.y=-Math.PI/2;exit.position.set(7.46,3.75,z);group.add(exit);
      if(!central){
        const rail=new T.Mesh(new T.CylinderGeometry(.025,.025,16,6),trim);rail.rotation.x=Math.PI/2;rail.position.set(7.74,1.94,z+12);group.add(rail);
        for(const dz of [5,10,15,19])box(.18,.045,.045,7.82,1.94,z+dz);
      }
    }
  }else if(station.code==='SXS'){
    // Wide-span Southern Cross waveform roof and branching steel columns.
    // The hall is a sequence of broad longitudinal dunes. Open rooflight
    // bands interrupt the pale inner skin, rather than sitting invisibly
    // beneath one opaque plane. Profiles and spacings are photographic
    // interpretations for this authored route, not measured dimensions.
    // The previous profile kept its two eaves almost level with the crown.
    // It therefore read as a floating, flat field from the driver's eye. This
    // is a true transverse vault: the skin starts just above the outer roads,
    // rises over the central tracks, then undulates gently down the hall.
    // `x` is passed with the historic +20 local offset used by this station.
    const roofHeight=(x:number,z:number)=>{
      const span=T.MathUtils.clamp((x+55)/110,0,1);
      return 7.6+11.3*Math.sin(span*Math.PI)+1.65*Math.sin(z/26+span*1.3);
    };
    const roofLights=[-51,-19,13],roofLightHalfWidth=2.8;
    const nx=110,nz=113,x0=-75,z0=-113,positions:number[]=[],indices:number[]=[];
    for(let iz=0;iz<=nz;iz++)for(let ix=0;ix<=nx;ix++){
      const x=x0+ix,z=z0+iz*2;positions.push(x,roofHeight(x+20,z),z);
    }
    for(let iz=0;iz<nz;iz++)for(let ix=0;ix<nx;ix++){
      const x=x0+ix+.5;
      if(roofLights.some(light=>Math.abs(x-light)<roofLightHalfWidth))continue;
      const a=iz*(nx+1)+ix,b=a+1,c=a+nx+1,d=c+1;
      // Counter-clockwise from below gives the underside an upward normal.
      indices.push(a,c,b,b,c,d);
    }
    const roof=new T.BufferGeometry();roof.setAttribute('position',new T.Float32BufferAttribute(positions,3));roof.setIndex(indices);roof.computeVertexNormals();
    const roofMesh=new T.Mesh(roof,new T.MeshStandardMaterial({color:'#9ba09a',metalness:.18,roughness:.78,side:T.DoubleSide}));
    roofMesh.name='Southern Cross authored dune roof underside';roofMesh.receiveShadow=true;group.add(roofMesh);
    const skylight=new T.MeshStandardMaterial({color:'#a7bec0',emissive:'#506970',emissiveIntensity:.32,metalness:.08,roughness:.3,transparent:true,opacity:.72,depthWrite:false,side:T.DoubleSide});
    for(const x of roofLights){
      const g=new T.PlaneGeometry(roofLightHalfWidth*2,226,2,nz);g.rotateX(-Math.PI/2);const v=g.attributes.position;
      for(let i=0;i<v.count;i++){v.setX(i,v.getX(i)+x);v.setY(i,roofHeight(v.getX(i)+20,v.getZ(i))-.06);}g.computeVertexNormals();
      const mesh=new T.Mesh(g,skylight);mesh.name='Southern Cross rooflight band';group.add(mesh);
    }

    const steel=new T.MeshStandardMaterial({color:'#35403f',roughness:.69,metalness:.48});
    const concrete=new T.MeshStandardMaterial({color:'#b4b4aa',roughness:.92,metalness:.02});
    const frame:T.BufferGeometry[]=[];
    const member=(a:T.Vector3,b:T.Vector3,r:number,into:T.BufferGeometry[]=frame)=>into.push(new T.TubeGeometry(new T.LineCurve3(a,b),1,r,6,false));
    // Deep curved Pratt arches now run from low eaves to the crown. Their two
    // chords and alternating webs make the roof a visible load-bearing vault
    // from both the cab and the platform, rather than a ceiling with a thin
    // triangular beam laid beneath it.
    for(let z=-108;z<=108;z+=27){
      const upper:T.Vector3[]=[],lower:T.Vector3[]=[];
      for(let x=-75;x<=35;x+=2){const y=roofHeight(x+20,z)-.38;upper.push(new T.Vector3(x,y,z));lower.push(new T.Vector3(x,y-3.35,z));}
      frame.push(new T.TubeGeometry(new T.CatmullRomCurve3(upper),60,.42,8,false));
      frame.push(new T.TubeGeometry(new T.CatmullRomCurve3(lower),60,.30,8,false));
      for(let i=0;i<upper.length-1;i+=4){
        const next=Math.min(i+4,upper.length-1);
        member(upper[i],lower[i],.17);
        member(Math.floor(i/4)%2===0?lower[i]:upper[i],Math.floor(i/4)%2===0?upper[next]:lower[next],.16);
      }
      member(upper[upper.length-1],lower[lower.length-1],.17);
    }
    // Secondary cross ribs and longitudinal purlins are lighter and farther
    // apart than the primary arches, leaving the rooflight apertures legible.
    for(let z=-108;z<=108;z+=6){const points=[];for(let x=-75;x<=35;x+=2)points.push(new T.Vector3(x,roofHeight(x+20,z)-.3,z));frame.push(new T.TubeGeometry(new T.CatmullRomCurve3(points),60,.07,5,false));}
    for(let x=-73;x<=33;x+=10){const points=[];for(let z=-111;z<=111;z+=3)points.push(new T.Vector3(x,roofHeight(x+20,z)-.42,z));frame.push(new T.TubeGeometry(new T.CatmullRomCurve3(points),74,.06,4,false));}
    const frameMesh=new T.Mesh(mergeGeometries(frame),steel);frameMesh.name='Southern Cross curved triangulated roof arches';frameMesh.castShadow=true;frameMesh.receiveShadow=true;group.add(frameMesh);frame.forEach(g=>g.dispose());

    // Concrete tree columns stay beyond the outermost track and platform
    // bands. Their flared arms meet the underside chord without posts in the
    // boarding/walking space; repeated geometry shares one material batch.
    const supports:T.BufferGeometry[]=[];
    const tapered=(a:T.Vector3,b:T.Vector3,base:number,tip:number)=>{
      const delta=b.clone().sub(a),g=new T.CylinderGeometry(tip,base,delta.length(),10,1);
      g.applyQuaternion(new T.Quaternion().setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize()));
      g.translate((a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2);supports.push(g);
    };
    for(const z of [-96,-48,0,48,96])for(const x of [-67,27]){
      const top=Math.max(6.25,roofHeight(x+20,z)-3.1);
      const shaft=new T.CylinderGeometry(.72,1.18,top,10,1);shaft.translate(x,top/2,z);supports.push(shaft);
      const foot=new T.BoxGeometry(2.35,.55,2.35);foot.translate(x,.28,z);supports.push(foot);
      for(const side of [-1,1]){
        const start=new T.Vector3(x,top-.35,z),end=new T.Vector3(x+side*8.5,roofHeight(x+side*8.5+20,z)-2.7,z);
        tapered(start,end,.74,.40);
      }
    }
    const supportMesh=new T.Mesh(mergeGeometries(supports),concrete);supportMesh.name='Southern Cross outer branching concrete supports';supportMesh.castShadow=true;supportMesh.receiveShadow=true;group.add(supportMesh);supports.forEach(g=>g.dispose());
    southernCrossConcourse(group);
    // Adjacent platform roads establish the station's broad rail hall.
    const running:T.BufferGeometry[]=[],sleepers:T.BufferGeometry[]=[];
    for(const x of [-14,-28,-42,-56]){
      for(let z=-105;z<=105;z+=.72){const g=new T.BoxGeometry(2.7,.13,.23);g.translate(x,.08,z);sleepers.push(g);}
      for(const side of [-.8,.8]){const g=new T.BoxGeometry(.075,.15,212,1,1,70);g.translate(x+side,.22,0);running.push(g);}
      box(5,1.1,212,x+5.5,.5,0);
    }
    for(const [geometries,color] of [[running,'#798581'],[sleepers,'#777970']] as const){group.add(new T.Mesh(mergeGeometries(geometries),new T.MeshStandardMaterial({color,roughness:.85})));geometries.forEach(g=>g.dispose());}
  }else{
    // Flinders Street's playable canopy only. Existing pitch/extents and
    // support bays stay fixed; the finish and fitted frame layering are
    // photographic interpretations of Wong F130_8206, not measured dimensions.
    const sheet=stationFinish('FSS','canopy'),panels:T.BufferGeometry[]=[];
    for(const side of [-1,1]){
      const roof=new T.BoxGeometry(4.3,.13,200,1,1,60);applyBoxSurfaceUV(roof,sheet);
      roof.rotateZ(side*.18);roof.translate(5+side*2.1,6.1,0);panels.push(roof);
    }
    const covering=new T.Mesh(mergeGeometries(panels),sheet);covering.castShadow=true;covering.receiveShadow=true;group.add(covering);panels.forEach(g=>g.dispose());
    const underside=(x:number)=>6.1+(Math.abs(x-5)-2.1)*Math.tan(.18)-.065/Math.cos(.18);
    const member=(a:T.Vector3,b:T.Vector3,r:number)=>parts.push(new T.TubeGeometry(new T.LineCurve3(a,b),1,r,6,false));
    for(let z=-90;z<=90;z+=20){
      box(7.7,.13,.13,5,5.65,z);
      for(const side of [-1,1]){
        const brace=new T.BoxGeometry(1.7,.1,.1);brace.rotateZ(side*.65);brace.translate(6+side*.7,5.2,z);parts.push(brace);
        member(new T.Vector3(5,underside(5)-.035,z),new T.Vector3(5+side*3.85,underside(5+side*3.85)-.035,z),.027);
      }
      // Thin diagonal webs follow the underside instead of crossing its skin.
      // They share the existing structural batch, with no per-bay draw calls.
      for(let x=1.15;x<8.8;x+=1.1){
        const end=Math.min(x+1.1,8.85),middle=(x+end)/2;
        const high=new T.Vector3(middle,underside(middle)-.055,z);
        member(new T.Vector3(x,5.70,z),high,.023);member(high,new T.Vector3(end,5.70,z),.023);
      }
    }
  }
  if(station.code==='FSS'&&index===0){
    // The playable platform belongs to a broad railway precinct, not an
    // isolated viaduct. These adjacent roads are scenic, without false services.
    const batch=new Map<T.Material,T.BufferGeometry[]>();
    const concrete=new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#aaab9c',roughness:1});
    const rail=new T.MeshStandardMaterial({color:'#8d9390',metalness:.75,roughness:.4});
    const roof=new T.MeshStandardMaterial({color:'#9fa89c',metalness:.3,roughness:.75});
    const redIron=new T.MeshStandardMaterial({color:'#633d2c',roughness:.7,metalness:.4});
    const yellow=new T.MeshStandardMaterial({color:'#dbc460',roughness:.85});
    const put=(material:T.Material,w:number,h:number,d:number,x:number,y:number,z:number)=>{const geometry=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/4)));geometry.translate(x,y,z);
      applyBoxSurfaceUV(geometry,material);
      const list=batch.get(material)??[];list.push(geometry);batch.set(material,list);};
    put(concrete,112,6,395,-23,-3.35,-25);put(ballast,112,.16,395,-23,-.22,-25);
    for(const x of [12,17,-7,-12,-26,-31,-45,-50,-64,-69]){
      for(const offset of [-.8,.8])put(rail,.075,.15,390,x+offset,.22,-25);
      for(let z=-218;z<=168;z+=.75)put(concrete,2.7,.13,.23,x,.06,z);
    }
    for(const x of [24,-19,-38,-57,-76]){
      put(concrete,6.5,1.1,300,x,.5,-15);
      for(const edge of [-3.02,3.02])put(yellow,.35,.03,298,x+edge,1.07,-15);
      put(roof,7.5,.16,276,x,5.9,-15);
      for(let z=-146;z<124;z+=16){put(redIron,.16,4.8,.16,x,3.4,z);put(redIron,7,.13,.13,x,5.7,z);}
    }
    // Red/brown overhead cross-spans are prominent in the supplied reference.
    for(let z=-170;z<=160;z+=45){
      put(redIron,83,.22,.25,-37,6.8,z);
      for(const x of [3,-77]){
        // The covered platform already has its ornate support bays. A generic
        // gantry post here pierced the canopy and stood in the walking band.
        if(x===3&&Math.abs(z)<=103)continue;
        put(redIron,.25,6.8,.25,x,3.4,z);
      }
    }
    for(const [material,geometries] of batch){const mesh=new T.Mesh(mergeGeometries(geometries),material);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);geometries.forEach(g=>g.dispose());}
  }
  if(parts.length){const mesh=new T.Mesh(mergeGeometries(parts),structure);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);parts.forEach(g=>g.dispose());}
}
