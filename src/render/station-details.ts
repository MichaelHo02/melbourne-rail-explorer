import * as T from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { labelTexture } from './materials';

/** Fittings referenced to photographs; dimensions are authored, not surveyed. */
export function stationDetails(group:T.Group,code:string,name:string){
  const heritage=code==='FSS',surface=heritage||code==='SXS';
  const materials={
    cream:new T.MeshStandardMaterial({color:'#d1c39b',roughness:.85}),
    iron:new T.MeshStandardMaterial({color:heritage?'#693c31':'#858e89',metalness:.45,roughness:.6}),
    steel:new T.MeshStandardMaterial({color:'#a6aba5',metalness:.7,roughness:.45}),
    dark:new T.MeshStandardMaterial({color:'#242b2c',roughness:.85}),
    seat:new T.MeshStandardMaterial({color:heritage?'#345445':'#c7cec7',roughness:.65,metalness:.25}),
    coping:new T.MeshStandardMaterial({color:'#deded2',roughness:1}),
  };
  const batches=new Map<T.Material,T.BufferGeometry[]>();
  function put(g:T.BufferGeometry,mat:T.Material){const batch=batches.get(mat)??[];batch.push(g);batches.set(mat,batch);}
  function box(w:number,h:number,d:number,x:number,y:number,z:number,mat:T.Material){const g=new T.BoxGeometry(w,h,d,1,1,Math.max(1,Math.ceil(d/3)));g.translate(x,y,z);put(g,mat);}
  function pipe(points:T.Vector3[],r:number,mat:T.Material){put(new T.TubeGeometry(new T.CatmullRomCurve3(points),12,r,5,false),mat);}
  function sign(text:string,w:number,h:number,x:number,y:number,z:number,bg='#0067ae',fg='#fff',rotation=-Math.PI/2){
    const m=new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:labelTexture(text,bg,fg,Math.round(w*160),Math.round(h*160)),side:T.DoubleSide}));
    m.position.set(x,y,z);m.rotation.y=rotation;group.add(m);
  }
  // Fixtures sit within a shallow dark channel below the actual soffit.
  // Emissive diffusers complement the existing station lights; no new shadow
  // lights or per-fixture draw calls are introduced.
  const diffuser=new T.MeshStandardMaterial({color:'#ecf2e9',emissive:'#ddebdc',emissiveIntensity:1.6,roughness:.5});
  if(!surface){
    for(const x of code==='MCE'?[3.8,9.5]:[3.8,6.5]){
      const y=code==='MCE'?6.03:3+3.1*Math.sqrt(1-((x-2.5)/6.5)**2)-.12;
      box(.31,.10,198,x,y,0,materials.dark);
      for(let z=-96;z<=96;z+=6){
        box(.20,.035,5.84,x,y-.055,z,diffuser);
        box(.32,.025,.09,x,y-.075,z+2.96,materials.steel);
      }
    }
    // A narrow stainless wall base and horizontal panel division provide
    // a consistent scale against the three stations' different wall finishes.
    for(const x of code==='MCE'?[-2.97,14.42]:[-2.97,7.96]){
      const runs=x===7.96?[[-99,-53.2],[-46.8,41.8],[48.2,99]]:[[-99,99]];
      for(const [a,b] of runs){box(.045,.16,b-a,x,1.17,(a+b)/2,materials.steel);box(.025,.04,b-a,x,3.03,(a+b)/2,materials.dark);}
    }
  }else if(heritage){
    for(const x of [3.9,7.1])for(let z=-94;z<=94;z+=8){
      box(.25,.11,2.5,x,5.77,z,materials.iron);
      box(.18,.035,2.32,x,5.70,z,diffuser);
      for(const dz of [-1,1])box(.04,.2,.04,x,5.91,z+dz,materials.steel);
    }
    // Narrow rainwater goods complete the canopy edge; downpipes follow
    // existing columns, outside the edge and passenger circulation band.
    for(const x of [.97,8.96])box(.14,.15,198,x,5.88,0,materials.iron);
    for(const z of [-90,-10,70])box(.075,4.5,.075,6.15,3.3,z,materials.iron);
  }else{
    // Southern Cross light battens are roof-mounted, following the waveform.
    for(const x of [3.7,6.1])for(let z=-96;z<=96;z+=6){
      const y=14.2+2.8*Math.sin(z/30)+1.8*Math.cos((x+20)/13)-.43;
      box(.28,.12,2.7,x,y,z,materials.dark);
      box(.18,.035,2.5,x,y-.075,z,diffuser);
    }
  }
  // White coping and a narrow shadow joint give the platform edge a scale cue.
  box(.24,.06,198,2.25,1.06,0,materials.coping);
  box(.025,.07,198,2.1,.96,0,materials.dark);
  // Recessed tactile studs are encoded in a repeatable bump map, not thousands of draw calls.
  const c=document.createElement('canvas');c.width=c.height=128;const ctx=c.getContext('2d')!;
  ctx.fillStyle='#555';ctx.fillRect(0,0,128,128);ctx.fillStyle='#ccc';
  for(let y=8;y<128;y+=16)for(let x=8;x<128;x+=16){ctx.beginPath();ctx.arc(x,y,3.4,0,Math.PI*2);ctx.fill();}
  const bump=new T.CanvasTexture(c);bump.wrapS=bump.wrapT=T.RepeatWrapping;bump.repeat.set(1,198/.4);bump.anisotropy=8;
  const tactile=new T.Mesh(new T.PlaneGeometry(.4,198,1,100),new T.MeshStandardMaterial({color:heritage?'#c8b886':'#c8a253',bumpMap:bump,bumpScale:.008,roughness:.92}));
  tactile.rotation.x=-Math.PI/2;tactile.position.set(2.56,1.085,0);group.add(tactile);
  if(heritage){
    for(let z=-90;z<=90;z+=20){
      box(.22,2.1,.22,6,2.1,z,materials.iron);box(.19,2.6,.19,6,4.4,z,materials.cream);
      box(.35,.12,.35,6,1.14,z,materials.iron);box(.3,.16,.3,6,3.12,z,materials.cream);
      for(const side of [-1,1]){
        pipe([new T.Vector3(6,4.7,z),new T.Vector3(6+side*.35,5.3,z),new T.Vector3(6+side*1.45,5.68,z)],.047,materials.cream);
        const ring=new T.TorusGeometry(.28,.034,5,16);ring.translate(6+side*.48,5.28,z);put(ring,materials.cream);
      }
      // Repeated crossed bracing under the historic platform canopies.
      for(let x=1.8;x<8.7;x+=1.15){
        pipe([new T.Vector3(x,5.76,z),new T.Vector3(x+.54,6.13,z),new T.Vector3(x+1.08,5.76,z)],.033,materials.cream);
      }
    }
    for(const x of [.85,9.05]){
      box(.12,.2,198,x,5.89,0,materials.iron);
      const verts:number[]=[];
      for(let z=-99;z<99;z+=.65){
        // The characteristic cream scalloped valance, visible from the train.
        for(let j=0;j<6;j++){
          const a=z+j*.65/6,b=z+(j+1)*.65/6;
          const ya=5.49+.09*Math.cos(j*Math.PI/3),yb=5.49+.09*Math.cos((j+1)*Math.PI/3);
          verts.push(x,5.84,a,x,ya,a,x,5.84,b,x,5.84,b,x,ya,a,x,yb,b);
        }
      }
      const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(verts,3));g.computeVertexNormals();
      const mat=materials.cream.clone();mat.side=T.DoubleSide;put(g,mat);
    }
  }
  for(const z of [-68,-10,48]){
    // Narrow slatted seats with actual legs and armrests.
    for(let j=0;j<5;j++)box(.10,.045,2.25,5.02+j*.12,1.52,z,materials.seat);
    for(let j=0;j<4;j++)box(.055,.10,2.25,5.63,1.67+j*.13,z,materials.seat);
    for(const end of [-.86,.86]){box(.08,.48,.1,5.15,1.28,z+end,materials.iron);box(.08,.48,.1,5.6,1.28,z+end,materials.iron);box(.6,.055,.055,5.32,1.85,z+end,materials.iron);}
    box(.5,.84,.48,7.2,1.5,z+4,materials.steel);box(.45,.08,.38,7.17,1.82,z+4,materials.dark);
  }
  // The three underground stations use suspended black displays, rather
  // than repeating Southern Cross's purpose-designed equipment pylon.
  for(const z of [-55,35]){
    const number=heritage?'5':code==='SXS'?'11':'2';
    if(!surface){
      const x=5.35,y=4.38;
      box(2.25,.92,.18,x,y,z,materials.dark);
      const spineY=code==='MCE'?6.01:5.52;
      for(const dx of [-.82,.82])box(.04,spineY-(y+.46),.04,x+dx,(spineY+y+.46)/2,z,materials.steel);
      for(const [dz,rotation] of [[-.10,Math.PI],[.10,0]]){
        sign('City Loop',1.96,.27,x,y+.19,z+dz,'#101819','#f2f4ec',rotation);
        sign('All stations · Training',1.96,.18,x,y-.16,z+dz,'#101819','#cbd7d5',rotation);
      }
      // A single shallow equipment spine recalls the photographs' ventilation
      // and service panels. Slots are batched geometry, not separate objects.
      box(1.18,.07,4.2,5.35,spineY,z,materials.steel);
      for(let dz=-1.8;dz<=1.8;dz+=.16)box(.76,.014,.045,5.35,spineY-.045,z+dz,materials.dark);
    }else{
      const x=6.55,y=3.7;
      box(.18,2.7,.25,x,2.4,z,materials.iron);box(.21,1.18,2.85,x,y,z,materials.dark);
      sign(number,.7,1.1,x-.12,y,z-.96,'#0067ae');
      sign(name,2.2,.35,x-.13,y+.37,z+.23,'#005c99');
      sign('CITY LOOP',1.55,.35,x-.13,y+.03,z+.23,'#0a1117','#ecf0ec');
      sign('All stations · Training',1.65,.21,x-.13,y-.32,z+.23,'#0a1117','#bbd4df');
      if(code==='SXS')for(const dz of [-.95,.95]){const g=new T.SphereGeometry(.15,12,8);g.translate(x,y+.84,z+dz);put(g,materials.dark);}
      box(.26,.5,.3,x-.04,2.15,z,materials.steel);sign('i',.22,.22,x-.2,2.2,z,'#183d65');
    }
  }
  // Platform-end barriers delineate the passenger area from the trackside
  // maintenance area. They stop short of the coping and never enter x<2.8.
  const endWidth=code==='MCE'?7.8:4.8,endCentre=2.8+endWidth/2;
  for(const side of [-1,1]){
    const z=side*98.6;
    for(const y of [1.25,2.12])box(endWidth,.045,.045,endCentre,y,z,materials.iron);
    for(let x=2.8;x<=2.8+endWidth+.01;x+=.6)box(.035,1.08,.035,x,1.61,z,materials.iron);
    box(.04,1.15,.065,endCentre,1.62,z,materials.iron);
    sign('Staff only',.66,.18,endCentre,1.86,z-side*.04,'#e7e7dc','#303a3a',side<0?0:Math.PI);
    if(!surface){
      // Framed service door and modest vent in the new solid headwall.
      box(1.12,2.25,.06,6.55,2.19,side*102.16,materials.steel);
      box(1.04,2.17,.065,6.55,2.19,side*102.12,materials.dark);
      box(.025,.24,.035,6.91,2.1,side*102.06,materials.steel);
      for(let y=3.67;y<=4.15;y+=.08)box(1.05,.035,.05,6.55,y,side*102.13,materials.dark);
    }else{
      // Short outboard maintenance steps soften the slab's abrupt end. The
      // gate remains the visible limit of the public platform.
      for(let i=0;i<5;i++)box(1.25,1.0-i*.18,.42,7.35,(1.0-i*.18)/2,side*(100.2+i*.42),materials.coping);
      for(const x of [6.68,8.02])pipe([new T.Vector3(x,2.06,side*99.8),new T.Vector3(x,2.06,side*100.2),new T.Vector3(x,1.3,side*102)],.025,materials.iron);
    }
  }
  if(surface){
    // Limited wayfinding gives the open platforms a circulation destination
    // without inventing an entire concourse or branded retail interior.
    const y=heritage?4.8:5.6,z=-35;
    box(2.65,.46,.14,5.8,y,z,materials.dark);
    for(const dx of [-1.05,1.05]){
      const x=5.8+dx,top=heritage?6.1+(x<5?-(x-2.9):x-7.1)*Math.tan(.18)-.07:14.2+2.8*Math.sin(z/30)+1.8*Math.cos((x+20)/13)-.3;
      box(.035,top-y-.23,.035,x,(top+y+.23)/2,z,materials.iron);
    }
    for(const [dz,r] of [[-.08,Math.PI],[.08,0]])sign(heritage?'Way out · Subway ↓':'Way out · Concourse ↑',2.4,.30,5.8,y,z+dz,'#142c34','#edf2e9',r);
  }else if(code!=='MCE'){
    // Recess lighting and side return rails reveal the lobby's real depth.
    for(const z of [-50,45]){
      box(2.4,.045,.22,9.3,3.65,z,diffuser);
      for(const dz of [-3.04,3.04])pipe([new T.Vector3(8.05,1.96,z+dz),new T.Vector3(9.3,1.96,z+dz),new T.Vector3(10.55,1.96,z+dz)],.025,materials.steel);
      box(.09,.72,.44,7.89,2.05,z-3.65,materials.steel);
      sign('Help',.33,.14,7.83,2.21,z-3.65,'#194b73');
      sign('i',.18,.18,7.83,1.96,z-3.65,'#194b73');
    }
  }
  for(const [mat,parts] of batches){
    const m=new T.Mesh(mergeGeometries(parts),mat);m.castShadow=true;m.receiveShadow=true;group.add(m);parts.forEach(g=>g.dispose());
  }
}
