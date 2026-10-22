import { Color, HemisphereLight, MathUtils } from 'three/webgpu';
import { positionAt, STATIONS, type Vec3 } from '../data/route';

// These are the authored station chambers, not surveyed lighting measurements.
// Short segments follow their curvature; a single station bounding sphere would
// also brighten the running tunnel and the street above the station.
const stationSegments=STATIONS.filter(station=>station.underground).flatMap(station=>{
  const points=Array.from({length:21},(_,i)=>positionAt(station.distance-165+i*10));
  return points.slice(1).map((b,i)=>({a:points[i],b}));
});

/** Camera-volume weight for the enclosed platform's diffuse bounce approximation. */
export function stationLightingWeight(view:Vec3){
  let weight=0;
  for(const {a,b} of stationSegments){
    const dx=b.x-a.x,dz=b.z-a.z;
    const t=MathUtils.clamp(((view.x-a.x)*dx+(view.z-a.z)*dz)/(dx*dx+dz*dz),0,1);
    const across=Math.hypot(view.x-a.x-dx*t,view.z-a.z-dz*t);
    const height=view.y-(a.y+(b.y-a.y)*t);
    // Platform, train and cab share the same fill. Above-ground inspection and
    // approaches beyond the chamber smoothly retain their existing lighting.
    const horizontal=1-MathUtils.smoothstep(across,11,28);
    const vertical=1-MathUtils.smoothstep(Math.abs(height-3),3.5,7);
    weight=Math.max(weight,horizontal*vertical);
  }
  return weight;
}

/** Reuses the existing indirect light; no new lights, shadows or material hacks.
 * Three r180's HemisphereLightNode adds normal-weighted irradiance, whereas the
 * point lamps contribute inverse-square direct light only. Emissive diffuser
 * meshes do not supply GI. The indoor lower hemisphere represents reflected
 * light from pale tiles/walls so vertical and downward-facing normals stay lit.
 */
export class StationLighting {
  private daylightCeiling=new Color('#c4ddeb');
  private daylightGround=new Color('#787766');
  private indoorCeiling=new Color('#eef2ee');
  private indoorGround=new Color('#c5bfac');

  constructor(private ambient:HemisphereLight){}

  update(view:Vec3,darkness:number){
    const weight=stationLightingWeight(view)*MathUtils.clamp(darkness,0,1);
    this.ambient.color.copy(this.daylightCeiling).lerp(this.indoorCeiling,weight);
    this.ambient.groundColor.copy(this.daylightGround).lerp(this.indoorGround,weight);
    this.ambient.intensity=MathUtils.lerp(1.1-.55*darkness,1.4,weight);
  }
}
