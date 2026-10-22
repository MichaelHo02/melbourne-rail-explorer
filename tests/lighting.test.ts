import {describe,expect,it} from 'vitest';
import {Color,HemisphereLight} from 'three/webgpu';
import {positionAt,STATIONS,tangentAt} from '../src/data/route';
import {StationLighting,stationLightingWeight} from '../src/render/lighting';

const underground=STATIONS.filter(station=>station.underground);
const viewAt=(distance:number,across=0,height=2.7)=>{
  const p=positionAt(distance),t=tangentAt(distance),n=Math.hypot(t.x,t.z);
  return {x:p.x+t.z/n*across,y:p.y+height,z:p.z-t.x/n*across};
};

describe('station diffuse lighting',()=>{
  it('covers curved passenger platforms and train cabs at every underground station',()=>{
    for(const station of underground)for(const along of [-145,-65,15])for(const across of [0,3.5,7.5]){
      expect(stationLightingWeight(viewAt(station.distance+along,across))).toBeCloseTo(1,6);
    }
  });

  it('does not bring station fill to surface stations, the street above, or running tunnels',()=>{
    for(const station of STATIONS.filter(s=>!s.underground))expect(stationLightingWeight(viewAt(station.distance))).toBe(0);
    for(const station of underground){
      expect(stationLightingWeight(viewAt(station.distance-65,5,27))).toBe(0);
      expect(stationLightingWeight(viewAt(station.distance+100))).toBe(0);
      expect(stationLightingWeight(viewAt(station.distance-230))).toBe(0);
    }
    const station=underground[0];
    const exitWeights=[35,40,45,50,55,60,65].map(along=>stationLightingWeight(viewAt(station.distance+along)));
    expect(exitWeights[0]).toBe(1);expect(exitWeights.at(-1)).toBe(0);
    for(let i=1;i<exitWeights.length;i++)expect(exitWeights[i]).toBeLessThanOrEqual(exitWeights[i-1]);
  });

  it('restores usable reflected irradiance without changing daylight or exposure',()=>{
    const ambient=new HemisphereLight('#c4ddeb','#787766',1.1),lighting=new StationLighting(ambient);
    const p=viewAt(underground[0].distance-65,5);
    lighting.update(p,1);
    // HemisphereLightNode interpolates these linear colors 50:50 for a vertical
    // normal. A dark coat/face previously received under .25 linear irradiance.
    const vertical=ambient.color.clone().add(ambient.groundColor).multiplyScalar(ambient.intensity/2);
    expect(Math.min(vertical.r,vertical.g,vertical.b)).toBeGreaterThan(.8);
    expect(Math.max(vertical.r,vertical.g,vertical.b)).toBeLessThan(1.1);
    expect(ambient.groundColor.r).toBeLessThan(ambient.color.r);
    lighting.update(p,0);
    expect(ambient.color).toEqual(new Color('#c4ddeb'));expect(ambient.groundColor).toEqual(new Color('#787766'));expect(ambient.intensity).toBe(1.1);
    lighting.update(viewAt(underground[0].distance+100),1);
    expect(ambient.color).toEqual(new Color('#c4ddeb'));expect(ambient.groundColor).toEqual(new Color('#787766'));expect(ambient.intensity).toBe(.55);
  });
});
