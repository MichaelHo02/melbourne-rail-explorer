import * as T from 'three/webgpu';
import {stationTileTexture} from './materials';

type Finish='floor'|'wall'|'column'|'perforated';
const cache=new Map<string,T.MeshStandardMaterial>();

/** Original, photo-informed patterns; no reference photograph is a texture.
 * PAR: Wong F151_3609; FGS: Wong F157_1397 (wall finishes only, during works);
 * MCE: Wpcpey, Melbourne Central Station Platform 2017. Pattern sizes are
 * authored visual approximations, not measured station dimensions. */
export function stationFinish(code:string,finish:Finish):T.MeshStandardMaterial{
  const key=`${code}:${finish}`,existing=cache.get(key);if(existing)return existing;
  if(finish==='floor'&&code==='FGS'){
    const material=new T.MeshStandardMaterial({map:stationTileTexture(code),color:'#dddcd4',roughness:.76});
    cache.set(key,material);return material;
  }
  const size=512,metres=2.4;
  const canvas=document.createElement('canvas');canvas.width=canvas.height=size;
  const relief=document.createElement('canvas');relief.width=relief.height=size;
  const ctx=canvas.getContext('2d')!,bump=relief.getContext('2d')!;
  let roughness=.6,metalness=0,bumpScale=.004;
  ctx.fillStyle='#c2c0b4';ctx.fillRect(0,0,size,size);bump.fillStyle='#b8b8b8';bump.fillRect(0,0,size,size);
  const tiles=(columns:number,rows:number,palette:string[],joint:string,stagger=false)=>{
    const w=size/columns,h=size/rows;
    ctx.fillStyle=joint;ctx.fillRect(0,0,size,size);bump.fillStyle='#686868';bump.fillRect(0,0,size,size);
    for(let row=0;row<rows;row++)for(let column=-1;column<=columns;column++){
      const x=(column+(stagger&&row%2?.5:0))*w,y=row*h;
      // Overflow tiles wrap to the same logical column and colour. Hashing
      // -1/columns directly creates a colour seam halfway through edge tiles.
      const wrappedColumn=((column%columns)+columns)%columns;
      const pick=(wrappedColumn*19+row*11)%palette.length;
      ctx.fillStyle=palette[pick];ctx.fillRect(x+1,y+1,w-2,h-2);
      bump.fillStyle='#b8b8b8';bump.fillRect(x+1,y+1,w-2,h-2);
    }
  };
  if(finish==='floor'&&code==='MCE'){
    // Rectangular terracotta courses replace the former square checkerboard.
    tiles(4,8,['#a77c52','#9c7454','#ae8155','#927354','#ab805a','#92765a'],'#7f7b6a',true);
    roughness=.46;bumpScale=.003;
  }else if(finish==='floor'&&code==='PAR'){
    // A seamless diagonal stone-panel grid: deliberately quiet variation.
    ctx.fillStyle='#c7c4b5';ctx.fillRect(0,0,size,size);
    for(const target of [ctx,bump]){
      target.strokeStyle=target===ctx?'#999b91':'#656565';target.lineWidth=1.4;
      for(let offset=-size;offset<=size*2;offset+=size/2){
        target.beginPath();target.moveTo(offset,0);target.lineTo(offset-size,size);target.stroke();
        target.beginPath();target.moveTo(offset,0);target.lineTo(offset+size,size);target.stroke();
      }
    }
    roughness=.42;bumpScale=.002;
  }else if(finish==='wall'&&code==='PAR'){
    // Tall enamel panels, with thin dark joints and restrained cobalt variation.
    tiles(4,1,['#123676','#173b80','#173a7a','#153774'],'#22303c');
    roughness=.21;metalness=.12;bumpScale=.003;
  }else if(finish==='wall'&&code==='FGS'){
    tiles(8,16,['#d5d5ca','#d1d2c7','#d8d8cd','#d2d3c8'],'#979f98');
    roughness=.43;bumpScale=.002;
  }else if(finish==='column'){
    tiles(16,8,['#d2d0be','#d7d3c2','#cecdbb','#d5d1bf'],'#888e81');
    roughness=.38;bumpScale=.003;
  }else if(finish==='perforated'){
    ctx.fillStyle=code==='MCE'?'#90958b':'#898f8b';ctx.fillRect(0,0,size,size);
    bump.fillStyle='#b8b8b8';bump.fillRect(0,0,size,size);
    // Small perforations stay in a texture; thousands of holes add no geometry.
    for(let row=0;row<64;row++)for(let column=0;column<64;column++){
      const x=column*8+(row%2?4:0),y=row*8;
      for(const target of [ctx,bump]){
        target.fillStyle=target===ctx?'#414b48':'#444444';target.beginPath();target.arc(x,y,1.5,0,Math.PI*2);target.fill();
      }
    }
    roughness=.56;metalness=.45;bumpScale=.004;
  }
  // Subtle deterministic surface grain, not baked light or photographic dirt.
  let seed=5831;
  for(let i=0;i<16000;i++){
    seed=(seed*1664525+1013904223)>>>0;const x=Math.floor(seed/0x100000000*size);
    seed=(seed*1664525+1013904223)>>>0;const y=Math.floor(seed/0x100000000*size);
    ctx.fillStyle=i%2?'#ffffff05':'#00000005';ctx.fillRect(x,y,1,1);
  }
  const map=new T.CanvasTexture(canvas),bumpMap=new T.CanvasTexture(relief);
  map.colorSpace=T.SRGBColorSpace;
  for(const texture of [map,bumpMap]){texture.wrapS=texture.wrapT=T.RepeatWrapping;texture.anisotropy=8;}
  const material=new T.MeshStandardMaterial({map,bumpMap,bumpScale,roughness,metalness});
  material.userData.textureMetres=metres;cache.set(key,material);return material;
}
