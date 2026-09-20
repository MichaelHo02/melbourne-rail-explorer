import {describe,expect,it} from 'vitest';
import {BoxGeometry,MeshStandardMaterial,Texture} from 'three';
import {applyBoxSurfaceUV} from '../src/render/surface-uv';

describe('station surface scale',()=>{
  it('tiles a 200 metre platform before its asynchronously loaded asphalt map exists',()=>{
    const material=new MeshStandardMaterial();material.userData.textureMetres=3;
    const platform=new BoxGeometry(6,1.1,200,1,1,50);
    expect(material.map).toBeNull();applyBoxSurfaceUV(platform,material);
    const uv=platform.attributes.uv,n=platform.attributes.normal;
    const top=Array.from({length:uv.count},(_,i)=>i).filter(i=>n.getY(i)>.5);
    const extent=(axis:'x'|'y')=>{const v=top.map(i=>axis==='x'?uv.getX(i):uv.getY(i));return Math.max(...v)-Math.min(...v);};
    expect(extent('x')).toBeCloseTo(2);expect(extent('y')).toBeCloseTo(200/3,4);
    const before=Array.from(uv.array);material.map=new Texture();applyBoxSurfaceUV(platform,material);
    expect(Array.from(uv.array)).toEqual(before);
  });
  it('keeps the existing two-metre underground tile convention',()=>{
    const material=new MeshStandardMaterial(),platform=new BoxGeometry(6,1,200);
    applyBoxSurfaceUV(platform,material);
    expect(Math.max(...Array.from(platform.attributes.uv.array))).toBe(50);
  });
});
