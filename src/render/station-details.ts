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
  for(const z of [-55,35]){
    const number=heritage?'5':code==='SXS'?'11':'2';
    const x=6.55,y=surface?3.7:3.5;
    box(.18,2.7,.25,x,2.4,z,materials.iron);box(.21,1.18,2.85,x,y,z,materials.dark);
    sign(number,.7,1.1,x-.12,y,z-.96,'#0067ae');
    sign(name,2.2,.35,x-.13,y+.37,z+.23,'#005c99');
    sign('CITY LOOP',1.55,.35,x-.13,y+.03,z+.23,'#0a1117','#ecf0ec');
    sign('All stations · Training',1.65,.21,x-.13,y-.32,z+.23,'#0a1117','#bbd4df');
    // Integrated speaker / CCTV heads, as in Grimshaw's Southern Cross kit.
    for(const dz of [-.95,.95]){const g=new T.SphereGeometry(.15,12,8);g.translate(x,y+.84,z+dz);put(g,materials.dark);}
    box(.26,.5,.3,x-.04,2.15,z,materials.steel);
    sign('i',.22,.22,x-.2,2.2,z,'#183d65');
  }
  for(const [mat,parts] of batches){
    const m=new T.Mesh(mergeGeometries(parts),mat);m.castShadow=true;m.receiveShadow=true;group.add(m);parts.forEach(g=>g.dispose());
  }
}
