import { Shape, ShapeGeometry, Color } from 'three';

interface Building {id:string;ring:[number,number][];base:number;height:number;kind?:string}
// UV atlas contract in building-materials.ts: 4×2 cells, 8px gutters in 512px.
const atlasUV=(family:number,u:number,v:number)=>[(family%4*512+8+u*496)/2048,1-(Math.floor(family/4)*512+8+(1-v)*496)/1024];
const roofUV=atlasUV(0,.5,.5);
function hash(value:string){let h=2166136261;for(const c of value)h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0;}
// Split at physical atlas boundaries so windows never stretch across a tower
// or leak into the adjacent facade family. Absolute height aligns storeys
// across stacked survey sections without changing measured elevations.
function intervals(start:number,end:number,size:number){
  const result:{a:number;b:number;u:number;v:number}[]=[];
  let a=start;
  while(a<end-1e-6){const cell=Math.floor((a+1e-6)/size),b=Math.min(end,(cell+1)*size);result.push({a,b,u:(a-cell*size)/size,v:(b-cell*size)/size});a=b;}
  return result;
}
self.onmessage=(event:MessageEvent<{buildings:Building[]}>)=>{
  const groups=new Map<string,Building[]>();
  for(const b of event.data.buildings){
    const p=b.ring[0];const key=`${Math.floor(p[0]/250)},${Math.floor(p[1]/250)}`;
    if(!groups.has(key))groups.set(key,[]);groups.get(key)!.push(b);
  }
  for(const [key,buildings] of groups){
    const positions:number[]=[],normals:number[]=[],uvs:number[]=[],colors:number[]=[];
    const vertex=(x:number,y:number,z:number,nx:number,ny:number,nz:number,uv:number[],color:Color)=>{
      positions.push(x,y,z);normals.push(nx,ny,nz);uvs.push(...uv);colors.push(color.r,color.g,color.b);
    };
    for(const b of buildings){
      const ring=b.ring.filter((p,i)=>i===0||Math.hypot(p[0]-b.ring[i-1][0],p[1]-b.ring[i-1][1])>.01);
      if(ring.length>2&&Math.hypot(ring[0][0]-ring.at(-1)![0],ring[0][1]-ring.at(-1)![1])<.01)ring.pop();
      if(ring.length<3)continue;
      let signedArea=0;for(let i=0;i<ring.length;i++){const a=ring[i],c=ring[(i+1)%ring.length];signedArea+=a[0]*c[1]-c[0]*a[1];}
      const area=Math.abs(signedArea)/2,top=b.base+b.height,seed=hash(String(b.id));
      const suspended=b.kind==='Bridge'||b.kind==='Jetty';
      const infrastructure=suspended||b.kind==='Train Platform'||b.kind==='Tram Stop';
      // Source footprints give upper elevation, not a structural cross-section.
      // Keep the surveyed top and footprint; authored thin decks leave water
      // and track space below bridges/jettys open instead of solid extrusion.
      const base=suspended?top-Math.min(.6,b.height):b.base;
      const family=infrastructure?0:top>=65?1+seed%2:top>=32?3:area>1100&&top<16?7:4+seed%3;
      const tint=new Color().setScalar(.9+(seed%11)/100),roof=new Color('#e6e7e1');
      const shape=new Shape();ring.forEach(([x,z],i)=>i?shape.lineTo(x,-z):shape.moveTo(x,-z));shape.closePath();
      // Preserve surveyed polygon roof exactly; no repeated windows on caps.
      const cap=new ShapeGeometry(shape),p=cap.attributes.position,index=cap.index;
      for(let i=0;i<(index?.count??p.count);i+=3){
        const ids=[0,1,2].map(k=>index?index.getX(i+k):i+k);
        const area2=(p.getX(ids[1])-p.getX(ids[0]))*(p.getY(ids[2])-p.getY(ids[0]))-(p.getY(ids[1])-p.getY(ids[0]))*(p.getX(ids[2])-p.getX(ids[0]));
        // Rounded survey rings contain collinear points; discard only numerical
        // slivers below 0.0025m² before Float32 precision can invert them.
        if(Math.abs(area2)<.005)continue;
        if(area2<0)ids.reverse();
        for(const j of ids)vertex(p.getX(j),top,-p.getY(j),0,1,0,roofUV,roof);
        if(base>.1)for(const j of ids.slice().reverse())vertex(p.getX(j),base,-p.getY(j),0,-1,0,roofUV,roof);
      }
      cap.dispose();
      const vertical=intervals(base,top,32),winding=Math.sign(signedArea)||1;
      for(let edge=0;edge<ring.length;edge++){
        const a=ring[edge],c=ring[(edge+1)%ring.length],length=Math.hypot(c[0]-a[0],c[1]-a[1]);
        if(length<.01)continue;
        const dx=(c[0]-a[0])/length,dz=(c[1]-a[1])/length,nx=dz*winding,nz=-dx*winding;
        const origin=a[0]*dx+a[1]*dz;
        for(const h of intervals(origin,origin+length,24))for(const v of vertical){
          const x0=a[0]+dx*(h.a-origin),z0=a[1]+dz*(h.a-origin),x1=a[0]+dx*(h.b-origin),z1=a[1]+dz*(h.b-origin);
          const points=[[x0,v.a,z0],[x1,v.a,z1],[x1,v.b,z1],[x0,v.b,z0]];
          const coords=[atlasUV(family,h.u,v.u),atlasUV(family,h.v,v.u),atlasUV(family,h.v,v.v),atlasUV(family,h.u,v.v)];
          for(const i of winding>0?[0,2,1,0,3,2]:[0,1,2,0,2,3])vertex(points[i][0],points[i][1],points[i][2],nx,0,nz,coords[i],tint);
        }
      }
    }
    const position=new Float32Array(positions),normal=new Float32Array(normals),uv=new Float32Array(uvs),color=new Float32Array(colors);
    self.postMessage({key,position,normal,uv,color}, {transfer:[position.buffer,normal.buffer,uv.buffer,color.buffer]});
  }
  self.postMessage({done:true,count:event.data.buildings.length});
};
