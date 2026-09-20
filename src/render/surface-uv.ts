import type { BufferGeometry, Material } from 'three/webgpu';

/** Box faces are mapped in metres before the station is bent along the route.
 * Material images load later, so UV generation must never depend on map readiness. */
export function applyBoxSurfaceUV(geometry:BufferGeometry,material:Material){
  const configured=Number(material.userData.textureMetres);
  const metres=Number.isFinite(configured)&&configured>0?configured:2;
  const p=geometry.attributes.position,n=geometry.attributes.normal,uv=geometry.attributes.uv;
  for(let i=0;i<p.count;i++){
    if(Math.abs(n.getY(i))>.5)uv.setXY(i,p.getX(i)/metres,p.getZ(i)/metres);
    else uv.setXY(i,(Math.abs(n.getX(i))>.5?p.getZ(i):p.getX(i))/metres,p.getY(i)/metres);
  }
  uv.needsUpdate=true;
}
