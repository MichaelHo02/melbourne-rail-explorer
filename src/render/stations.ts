import * as T from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { labelTexture, surfaceTexture } from './materials';

type Station={name:string;code:string;underground:boolean;color:string};
// Authored architectural cues, not a survey of any operational platform.
export function stationArchitecture(group:T.Group,station:Station,index=0){
  const structure=new T.MeshStandardMaterial({color:station.underground?'#b3b5aa':station.code==='FSS'?'#c6b987':'#647777',roughness:.78,metalness:.22});
  const parts:T.BufferGeometry[]=[];
  const box=(w:number,h:number,d:number,x:number,y:number,z:number)=>{const g=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/3)));g.translate(x,y,z);parts.push(g);};
  if(station.underground){
    // Chamber end walls meet the shell precisely while preserving its arch.
    const portal=new T.Shape();portal.moveTo(-4,-.2);portal.lineTo(-4,5.7);portal.lineTo(9,5.7);portal.lineTo(9,-.2);portal.lineTo(3.4,-.2);
    for(let i=0;i<=32;i++){const angle=-.22+i*(Math.PI+.44)/32;portal.lineTo(Math.cos(angle)*3.4,.9+Math.sin(angle)*3.9);}
    portal.lineTo(-3.4,-.2);portal.closePath();
    for(const z of [-103,103]){const g=new T.ShapeGeometry(portal);g.translate(0,0,z);const mesh=new T.Mesh(g,new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#8b908b',roughness:1,side:T.DoubleSide}));group.add(mesh);}
    // Ceiling ribs, wall panels, skirting, and an abstract escalator entrance.
    for(let z=-96;z<=96;z+=8){box(12,.12,.16,2.4,5.4,z);box(.12,3.9,.08,7.93,3.05,z);}
    box(.12,.25,198,7.93,1.2,0);box(.1,.28,198,-2.95,.8,0);
    for(const z of [-50,45]){
      box(.12,3.6,5,7.88,2.85,z);box(1.5,.13,5,7.2,4.65,z);
      const exit=new T.Mesh(new T.PlaneGeometry(3.5,.55),new T.MeshBasicMaterial({map:labelTexture('↑ Exit','#205d49')}));exit.rotation.y=-Math.PI/2;exit.position.set(7.79,4.15,z);group.add(exit);
    }
  }else if(station.code==='SXS'){
    // Wide-span Southern Cross waveform roof and branching steel columns.
    const roofHeight=(x:number,z:number)=>14.2+2.8*Math.sin(z/30)+1.8*Math.cos(x/13);
    const roof=new T.PlaneGeometry(98,226,54,84);roof.rotateX(-Math.PI/2);
    const p=roof.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i);p.setY(i,roofHeight(x,z));p.setX(i,x-20);}
    roof.computeVertexNormals();group.add(new T.Mesh(roof,new T.MeshStandardMaterial({color:'#acb1ac',metalness:.45,roughness:.62,side:T.DoubleSide})));
    for(let z=-108;z<=108;z+=9){const points=[];for(let x=-69;x<=29;x+=2)points.push(new T.Vector3(x,roofHeight(x+20,z)-.18,z));parts.push(new T.TubeGeometry(new T.CatmullRomCurve3(points),49,.095,5,false));}
    const skylight=new T.MeshStandardMaterial({color:'#c4d3d3',emissive:'#44545a',emissiveIntensity:.25,metalness:.22,roughness:.25,side:T.DoubleSide});
    for(const x of [-59,-31,-3,24]){
      const g=new T.PlaneGeometry(1.6,224,1,70);g.rotateX(-Math.PI/2);const v=g.attributes.position;
      for(let i=0;i<v.count;i++){v.setX(i,v.getX(i)+x);v.setY(i,roofHeight(v.getX(i)+20,v.getZ(i))+.03);}g.computeVertexNormals();group.add(new T.Mesh(g,skylight));
    }
    for(let z=-90;z<=90;z+=36)for(const x of [-57,-29,9.5]){
      box(.38,10,.38,x,5,z);
      for(const side of [-1,1]){const start=new T.Vector3(x,9,z),end=new T.Vector3(x+side*4,roofHeight(x+20+side*4,z)-.4,z);parts.push(new T.TubeGeometry(new T.LineCurve3(start,end),1,.15,6,false));}
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
    const ballast=new T.MeshStandardMaterial({map:surfaceTexture('ballast'),color:'#8b8070',roughness:1});
    const concrete=new T.MeshStandardMaterial({map:surfaceTexture('concrete'),color:'#aaab9c',roughness:1});
    const rail=new T.MeshStandardMaterial({color:'#8d9390',metalness:.75,roughness:.4});
    const roof=new T.MeshStandardMaterial({color:'#9fa89c',metalness:.3,roughness:.75});
    const redIron=new T.MeshStandardMaterial({color:'#633d2c',roughness:.7,metalness:.4});
    const yellow=new T.MeshStandardMaterial({color:'#dbc460',roughness:.85});
    const put=(material:T.Material,w:number,h:number,d:number,x:number,y:number,z:number)=>{const geometry=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/4)));geometry.translate(x,y,z);const list=batch.get(material)??[];list.push(geometry);batch.set(material,list);};
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
    for(let z=-170;z<=160;z+=45){put(redIron,83,.22,.25,-37,6.8,z);for(const x of [3,-77])put(redIron,.25,6.8,.25,x,3.4,z);}
    for(const [material,geometries] of batch){const mesh=new T.Mesh(mergeGeometries(geometries),material);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);geometries.forEach(g=>g.dispose());}
  }
  if(parts.length){const mesh=new T.Mesh(mergeGeometries(parts),structure);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);parts.forEach(g=>g.dispose());}
}

export function platformPassengers(group:T.Group,seed:number){
  const palettes=['#344a56','#71695b','#375a69','#795649','#49584f','#ac977c'];
  const batches:T.BufferGeometry[][]=palettes.map(()=>[]);
  const skin:T.BufferGeometry[]=[],hair:T.BufferGeometry[]=[];
  for(let j=0;j<18;j++){
    const x=3.35+(j%4)*.72,z=-84+(j*37+seed*11)%174,height=.92+(j%5)*.035,turn=j*.83;
    const transform=(g:T.BufferGeometry)=>{g.rotateY(turn);g.translate(x,1.05,z);return g;};
    const body=new T.CapsuleGeometry(.17,.48,3,7);body.scale(1,height,.7);body.translate(0,1.03*height,0);batches[j%6].push(transform(body));
    for(const side of [-1,1]){const leg=new T.CylinderGeometry(.065,.08,.73*height,6);leg.translate(side*.095,.37*height,side*.045);batches[(j+2)%6].push(transform(leg));const arm=new T.CapsuleGeometry(.055,.44,2,5);arm.rotateZ(side*.12);arm.translate(side*.24,.99*height,.025);batches[j%6].push(transform(arm));}
    const head=new T.SphereGeometry(.13,8,6);head.scale(.85,1.2,.95);head.translate(0,1.56*height,0);skin.push(transform(head));
    const cap=new T.SphereGeometry(.133,8,5,0,Math.PI*2,0,Math.PI*.54);cap.translate(0,1.61*height,0);hair.push(transform(cap));
    if(j%3===0){const bag=new T.BoxGeometry(.27,.36,.12);bag.translate(0,1.02*height,-.18);batches[(j+3)%6].push(transform(bag));}
  }
  [...batches,skin,hair].forEach((parts,i)=>{if(!parts.length)return;const mesh=new T.Mesh(mergeGeometries(parts),new T.MeshStandardMaterial({color:i<6?palettes[i]:i===6?'#b9957c':'#343332',roughness:1}));mesh.castShadow=true;group.add(mesh);parts.forEach(g=>g.dispose());});
}
