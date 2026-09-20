import * as T from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { labelTexture, surfaceTexture } from './materials';
import { applyBoxSurfaceUV } from './surface-uv';

type Station={name:string;code:string;underground:boolean;color:string};
// Authored architectural cues, not a survey of any operational platform.
export function stationArchitecture(group:T.Group,station:Station,index:number,ballast:T.Material){
  const structure=new T.MeshStandardMaterial({color:station.underground?'#b3b5aa':station.code==='FSS'?'#c6b987':'#647777',roughness:.78,metalness:.22});
  const parts:T.BufferGeometry[]=[];
  const box=(w:number,h:number,d:number,x:number,y:number,z:number)=>{const g=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/3)));g.translate(x,y,z);parts.push(g);};
  if(station.underground){
    // Chamber end walls meet the shell precisely while preserving its arch.
    const portal=new T.Shape();portal.moveTo(-4,-.2);portal.lineTo(-4,5.7);portal.lineTo(9,5.7);portal.lineTo(9,-.2);portal.lineTo(3.4,-.2);
    for(let i=0;i<=32;i++){const angle=-.22+i*(Math.PI+.44)/32;portal.lineTo(Math.cos(angle)*3.4,.9+Math.sin(angle)*3.9);}
    portal.lineTo(-3.4,-.2);portal.closePath();
    for(const z of [-103,103]){const g=new T.ShapeGeometry(portal);g.translate(0,0,z);const mesh=new T.Mesh(g,new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#8b908b',roughness:1,side:T.DoubleSide}));group.add(mesh);}
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
    for(let z=-102;z<102;z+=3)for(let k=0;k<28;k++){
      const a=cross(k/28),b=cross((k+1)/28);
      for(const [p,dz] of [[a,z],[b,z],[a,z+3],[a,z+3],[b,z],[b,z+3]] as const){points.push(p.x,p.y,dz);uvs.push(k/28,dz/3);}
    }
    const shell=new T.BufferGeometry();shell.setAttribute('position',new T.Float32BufferAttribute(points,3));shell.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));shell.computeVertexNormals();group.add(new T.Mesh(shell,ceiling));
    const seams:T.BufferGeometry[]=[];
    for(let z=-102;z<=102;z+=3){const curve=new T.CatmullRomCurve3(Array.from({length:29},(_,k)=>{const p=cross(k/28);p.z=z;p.y-=.012;return p;}));seams.push(new T.TubeGeometry(curve,28,.012,3,false));}
    for(let z=-99;z<=99;z+=1.6){const g=new T.BoxGeometry(.028,2.8,.026);g.translate(7.95,1.7,z);if(!central)seams.push(g);const left=g.clone();left.translate(-10.9,0,0);seams.push(left);}
    const seamsMesh=new T.Mesh(mergeGeometries(seams),joint);group.add(seamsMesh);seams.forEach(g=>g.dispose());
    // Longitudinal panel seams establish the scale of the metal soffit.
    for(const a of central?[.15,.29,.48,.68,.86]:[.13,.25,.38,.5,.62,.75,.87]){
      const p=cross(a);const g=new T.BoxGeometry(.025,.018,204,1,1,68);g.translate(p.x,p.y-.025,0);
      const mesh=new T.Mesh(g,joint);group.add(mesh);
    }
    box(.15,.12,204,7.65,3.25,0);
    if(central){
      for(let z=-88;z<=88;z+=22){box(.9,5.1,.9,7.8,3.5,z);box(3,.22,1.2,7.8,5.85,z);}
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
        const back=new T.Mesh(new T.BoxGeometry(.04,2.7,4.5),recess);back.position.set(7.94,2.43,z);group.add(back);
        for(const dz of [-2.28,2.28]){const reveal=new T.Mesh(new T.BoxGeometry(.45,2.75,.12),trim);reveal.position.set(7.74,2.43,z+dz);group.add(reveal);}
        box(.48,.18,4.7,7.72,3.86,z);
      }
      if(central){box(.16,.53,3.4,7.51,3.75,z);for(const dz of [-1.25,1.25])box(.04,2.1,.04,7.51,5.04,z+dz);}
      const destination=station.code==='PAR'?'↑ Collins Street':station.code==='FGS'?'↑ William Street':'↑ Swanston Street';
      const exit=new T.Mesh(new T.PlaneGeometry(3.2,.45),new T.MeshBasicMaterial({map:labelTexture(destination,'#172825')}));exit.rotation.y=-Math.PI/2;exit.position.set(7.46,3.75,z);group.add(exit);
      if(!central){
        const rail=new T.Mesh(new T.CylinderGeometry(.025,.025,16,6),trim);rail.rotation.x=Math.PI/2;rail.position.set(7.74,1.94,z+12);group.add(rail);
        for(const dz of [5,10,15,19])box(.18,.045,.045,7.82,1.94,z+dz);
      }
    }
  }else if(station.code==='SXS'){
    // Wide-span Southern Cross waveform roof and branching steel columns.
    const roofHeight=(x:number,z:number)=>14.2+2.8*Math.sin(z/30)+1.8*Math.cos(x/13);
    const roof=new T.PlaneGeometry(98,226,54,84);roof.rotateX(-Math.PI/2);
    const p=roof.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i);p.setY(i,roofHeight(x,z));p.setX(i,x-20);}
    roof.computeVertexNormals();const roofMesh=new T.Mesh(roof,new T.MeshStandardMaterial({color:'#acb1ac',metalness:.45,roughness:.62,side:T.DoubleSide}));
    roofMesh.name='Southern Cross authored ceiling underside';group.add(roofMesh);
    for(let z=-108;z<=108;z+=6){const points=[];for(let x=-69;x<=29;x+=2)points.push(new T.Vector3(x,roofHeight(x+20,z)-.18,z));parts.push(new T.TubeGeometry(new T.CatmullRomCurve3(points),49,.115,6,false));}
    const skylight=new T.MeshStandardMaterial({color:'#c4d3d3',emissive:'#44545a',emissiveIntensity:.25,metalness:.22,roughness:.25,side:T.DoubleSide});
    for(const x of [-59,-31,-3,24]){
      const g=new T.PlaneGeometry(1.6,224,1,70);g.rotateX(-Math.PI/2);const v=g.attributes.position;
      for(let i=0;i<v.count;i++){v.setX(i,v.getX(i)+x);v.setY(i,roofHeight(v.getX(i)+20,v.getZ(i))-.055);}g.computeVertexNormals();group.add(new T.Mesh(g,skylight));
    }
    // Longitudinal purlins follow the dune surface. Their depth produces
    // legible underside shadows, with each curve sampled for route warping.
    for(let x=-66;x<=27;x+=3){
      const points=[];for(let z=-111;z<=111;z+=3)points.push(new T.Vector3(x,roofHeight(x+20,z)-.28,z));
      parts.push(new T.TubeGeometry(new T.CatmullRomCurve3(points),74,.052,4,false));
    }
    for(let z=-90;z<=90;z+=36)for(const x of [-57,-29,7.5]){
      box(.5,9.5,.5,x,5.8,z);box(.82,.25,.82,x,1.18,z);
      for(const side of [-1,1]){const start=new T.Vector3(x,9.6,z),end=new T.Vector3(x+side*4,roofHeight(x+20+side*4,z)-.4,z);parts.push(new T.TubeGeometry(new T.LineCurve3(start,end),1,.2,8,false));}
    }
    for(let z=-90;z<=90;z+=36)for(const x of [-57,-29,7.5])for(const side of [-1,1]){
      const start=new T.Vector3(x,9.6,z),end=new T.Vector3(x,roofHeight(x+20,z+side*5)-.35,z+side*5);
      parts.push(new T.TubeGeometry(new T.LineCurve3(start,end),4,.16,6,false));
    }
    // Adjacent platform roads establish the station's broad rail hall.
    const running:T.BufferGeometry[]=[],sleepers:T.BufferGeometry[]=[];
    for(const x of [-14,-28,-42,-56]){
      for(let z=-105;z<=105;z+=.72){const g=new T.BoxGeometry(2.7,.13,.23);g.translate(x,.08,z);sleepers.push(g);}
      for(const side of [-.8,.8]){const g=new T.BoxGeometry(.075,.15,212,1,1,70);g.translate(x+side,.22,0);running.push(g);}
      box(5,1.1,212,x+5.5,.5,0);
    }
    for(const [geometries,color] of [[running,'#798581'],[sleepers,'#777970']] as const){group.add(new T.Mesh(mergeGeometries(geometries),new T.MeshStandardMaterial({color,roughness:.85})));geometries.forEach(g=>g.dispose());}
  }else{
    // Flinders Street: a modest pitched canopy and fine repeated iron supports.
    for(const side of [-1,1]){const roof=new T.BoxGeometry(4.3,.13,200,1,1,60);roof.rotateZ(side*.18);roof.translate(5+side*2.1,6.1,0);parts.push(roof);}
    for(let z=-90;z<=90;z+=20){box(7.7,.13,.13,5,5.65,z);for(const side of [-1,1]){const brace=new T.BoxGeometry(1.7,.1,.1);brace.rotateZ(side*.65);brace.translate(6+side*.7,5.2,z);parts.push(brace);}}
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
