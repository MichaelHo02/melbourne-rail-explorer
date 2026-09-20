import * as T from 'three/webgpu';

/** Authored grass detail, not an aerial photograph or a surveyed planting map. */
export function lawnMaterial(){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=512;
  const ctx=canvas.getContext('2d')!;
  let seed=3721;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
  ctx.fillStyle='#727c5b';ctx.fillRect(0,0,512,512);
  // Fine interlocking strokes read as turf close up and average cleanly in mips.
  for(let i=0;i<85000;i++){
    const x=random()*512,y=random()*512,v=random();
    ctx.strokeStyle=`rgba(${Math.round(65+v*68)},${Math.round(79+v*67)},${Math.round(45+v*45)},.42)`;
    ctx.lineWidth=.5+random();ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+(random()-.5)*3,y-1-random()*3);ctx.stroke();
  }
  const map=new T.CanvasTexture(canvas);map.colorSpace=T.SRGBColorSpace;
  map.wrapS=map.wrapT=T.RepeatWrapping;map.anisotropy=8;
  return new T.MeshStandardMaterial({map,roughness:1,vertexColors:true});
}

/** Preserve the exact triangulated parcel/hole boundaries while adding enough
 * interior vertices for gentle, deterministic changes in turf colour. */
export function detailLawn(source:T.BufferGeometry){
  const positions:number[]=[],uvs:number[]=[],colors:number[]=[],p=source.attributes.position,indices=source.index;
  const sample=(i:number)=>new T.Vector3().fromBufferAttribute(p,i);
  const emit=(a:T.Vector3,b:T.Vector3,c:T.Vector3,depth:number)=>{
    if(depth<7&&Math.max(a.distanceToSquared(b),b.distanceToSquared(c),c.distanceToSquared(a))>24*24){
      const ab=a.clone().add(b).multiplyScalar(.5),bc=b.clone().add(c).multiplyScalar(.5),ca=c.clone().add(a).multiplyScalar(.5);
      emit(a,ab,ca,depth+1);emit(ab,b,bc,depth+1);emit(ca,bc,c,depth+1);emit(ab,bc,ca,depth+1);return;
    }
    for(const v of [a,b,c]){
      positions.push(v.x,v.y,v.z);uvs.push(v.x/5,v.z/5);
      const variation=.89+.065*Math.sin(v.x/18+Math.sin(v.z/27))+.035*Math.cos(v.z/11-v.x/31);
      colors.push(variation,variation,variation*.98);
    }
  };
  for(let i=0;i<(indices?.count??p.count);i+=3)emit(sample(indices?indices.getX(i):i),sample(indices?indices.getX(i+1):i+1),sample(indices?indices.getX(i+2):i+2),0);
  const result=new T.BufferGeometry();result.setAttribute('position',new T.Float32BufferAttribute(positions,3));
  result.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));result.setAttribute('color',new T.Float32BufferAttribute(colors,3));result.computeVertexNormals();source.dispose();return result;
}
