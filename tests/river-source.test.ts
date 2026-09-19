import { describe, expect, it } from 'vitest';
import river from '../src/data/river-source.json';

const ring=river.geometry.coordinates[0];
function inside(lon:number,lat:number){
  let result=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];
    if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])result=!result;
  }
  return result;
}
describe('Yarra source geography',()=>{
  it('retains a closed bank polygon within the documented geographic crop',()=>{
    expect(ring[0]).toEqual(ring.at(-1));
    for(const [lon,lat] of ring){
      expect(lon).toBeGreaterThanOrEqual(river.clipBounds[0]);expect(lon).toBeLessThanOrEqual(river.clipBounds[2]);
      expect(lat).toBeGreaterThanOrEqual(river.clipBounds[1]);expect(lat).toBeLessThanOrEqual(river.clipBounds[3]);
    }
  });
  it('covers the actual river and excludes the former Southbank-building alignment',()=>{
    expect(inside(144.965,-37.81965)).toBe(true);
    expect(inside(144.965,-37.8209)).toBe(false);
  });
});
