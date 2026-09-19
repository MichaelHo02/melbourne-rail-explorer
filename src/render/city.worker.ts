import { Shape, ExtrudeGeometry, Color, Float32BufferAttribute } from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

interface Building {id:string;ring:[number,number][];base:number;height:number}
self.onmessage=(event:MessageEvent<{buildings:Building[]}>)=>{
  const groups=new Map<string,Building[]>();
  for(const b of event.data.buildings){
    const p=b.ring[0];const key=`${Math.floor(p[0]/250)},${Math.floor(p[1]/250)}`;
    if(!groups.has(key))groups.set(key,[]);groups.get(key)!.push(b);
  }
  for(const [key,buildings] of groups){
    const parts=[];
    for(const b of buildings){
      const shape=new Shape();b.ring.forEach(([x,z],i)=>i?shape.lineTo(x,-z):shape.moveTo(x,-z));
      const g=new ExtrudeGeometry(shape,{depth:b.height,bevelEnabled:false,steps:1,curveSegments:1});
      g.rotateX(-Math.PI/2);g.translate(0,b.base,0);
      const p=g.attributes.position,n=g.attributes.normal,uv=g.attributes.uv;
      // Per-building colours stay in a single batch, while roofs use the matte
      // texture border instead of repeating window imagery across the roof.
      const palette=['#c8cfcd','#c0cdd2','#d3c7b5','#b0b9bc','#d4d4c9'];
      const tint=new Color(palette[Number(b.id)%palette.length]),roof=new Color('#b4b6ae');
      const colors=new Float32Array(p.count*3);
      for(let i=0;i<p.count;i++){
        const isRoof=Math.abs(n.getY(i))>.5,c=isRoof?roof:tint;
        if(isRoof)uv.setXY(i,.002,.002);
        else uv.setXY(i,Math.abs(n.getX(i))>.5?p.getZ(i)/22:p.getX(i)/22,p.getY(i)/22);
        colors[i*3]=c.r;colors[i*3+1]=c.g;colors[i*3+2]=c.b;
      }
      g.setAttribute('color',new Float32BufferAttribute(colors,3));
      parts.push(g);
    }
    const merged=mergeGeometries(parts,false)!;
    const position=merged.attributes.position.array as Float32Array;
    const normal=merged.attributes.normal.array as Float32Array;
    const uv=merged.attributes.uv.array as Float32Array;
    const color=merged.attributes.color.array as Float32Array;
    self.postMessage({key,position,normal,uv,color}, {transfer:[position.buffer,normal.buffer,uv.buffer,color.buffer]});
    parts.forEach(p=>p.dispose());merged.dispose();
  }
  self.postMessage({done:true,count:event.data.buildings.length});
};
