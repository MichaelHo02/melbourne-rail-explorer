import { CanvasTexture, ClampToEdgeWrapping, MeshStandardMaterial, NoColorSpace, SRGBColorSpace } from 'three/webgpu';

/** Authored facade families, not observations of individual Melbourne buildings.
 * Atlas contract with city.worker.ts: 4 columns × 2 rows, 512px cells,
 * 8px gutters. Each facade cell covers 24 × 32 metres. Cell 0 is matte roof.
 */
export function createBuildingMaterial():MeshStandardMaterial {
  const width=2048,height=1024,cell=512,pad=8,inner=cell-pad*2;
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const roughness=document.createElement('canvas');roughness.width=width;roughness.height=height;
  const c=canvas.getContext('2d')!,r=roughness.getContext('2d')!;
  const fill=(ctx:CanvasRenderingContext2D,color:string,x:number,y:number,w:number,h:number)=>{ctx.fillStyle=color;ctx.fillRect(x,y,w,h);};
  // Large glass sheets, restrained spandrels and continuous vertical rhythms.
  // Lower buildings use masonry openings rather than the same glass checker.
  for(let family=0;family<8;family++){
    const ox=family%4*cell,oy=Math.floor(family/4)*cell;
    const wall=['#9c9d94','#869b9f','#8e9e9e','#bec0b9','#c4bba8','#947b68','#c7cac6','#a4aaa6'][family];
    fill(c,wall,ox,oy,cell,cell);fill(r,family===0?'#f4f4f4':'#dedede',ox,oy,cell,cell);
    c.save();r.save();c.beginPath();c.rect(ox+pad,oy+pad,inner,inner);c.clip();r.beginPath();r.rect(ox+pad,oy+pad,inner,inner);r.clip();
    const x0=ox+pad,y0=oy+pad;
    if(family===1||family===2){
      // Eight 3m bays, eight 4m floors. Reflection gradients run continuously
      // down the glazing, avoiding randomly lit checkerboard windows.
      for(let bay=0;bay<8;bay++){
        const x=x0+bay*inner/8,w=inner/8;
        const gradient=c.createLinearGradient(x,y0,x+w,y0+inner);
        gradient.addColorStop(0,family===1?'#a8babf':'#a7b4ad');
        gradient.addColorStop(.45,family===1?'#708b95':'#7e9692');
        gradient.addColorStop(1,family===1?'#536c77':'#5e7475');
        c.fillStyle=gradient;c.fillRect(x+1,y0,w-2,inner);
        fill(r,'#777777',x+1,y0,w-2,inner);
        fill(c,'#c0c8c7',x,y0,2,inner);fill(r,'#bdbdbd',x,y0,2,inner);
        // One fine intermediate mullion per tall sheet.
        fill(c,'#7b9095',x+w/2,y0,1.4,inner);
      }
      for(let floor=0;floor<8;floor++){
        const y=y0+floor*inner/8;
        fill(c,family===1?'#687d85':'#738783',x0,y,inner,6);
        fill(r,'#b7b7b7',x0,y,inner,6);
        fill(c,'#b1bfc0',x0,y+6,inner,1.5);
      }
    }else if(family!==0){
      const bays=family===7?6:family===3?8:10,bayWidth=inner/bays;
      for(let floor=0;floor<8;floor++)for(let bay=0;bay<bays;bay++){
        const x=x0+bay*bayWidth,y=y0+floor*inner/8;
        const inset=family===3?7:family===7?3:12;
        const top=family===7?10:7.5,h=family===7?27.5:family===3?47:39.5;
        fill(c,'#6c7472',x+inset-2,y+top-2,bayWidth-inset*2+4,h+4);
        fill(c,family===5?'#526265':family===7?'#7b8b8c':'#637b84',x+inset,y+top,bayWidth-inset*2,h);
        fill(r,'#898989',x+inset,y+top,bayWidth-inset*2,h);
        fill(c,'#9daaa9',x+inset,y+top,bayWidth-inset*2,4);
        if(family===3||family===6)fill(c,wall,x+bayWidth/2,y+top,2,h);
        fill(c,family===5?'#b09d88':'#d0cec1',x+inset-3,y+top+h+1,bayWidth-inset*2+6,3);
      }
      for(let y=0;y<inner;y+=inner/8){
        fill(c,family===5?'#806e5e':'#969e9b',x0,y0+y+inner/8-3,inner,2);
        fill(r,'#e8e8e8',x0,y0+y+inner/8-3,inner,2);
      }
      if(family===5){
        // Quiet brick coursing visible only close to the viaduct.
        c.strokeStyle='#b39c8340';c.lineWidth=.6;
        for(let y=0;y<inner;y+=4){c.beginPath();c.moveTo(x0,y0+y);c.lineTo(x0+inner,y0+y);c.stroke();}
      }
      if(family===7){
        for(let x=0;x<inner;x+=12)fill(c,'#78827c25',x0+x,y0,1,inner);
      }
    }
    c.restore();r.restore();
  }
  // Keep the previous (.002,.002) roof sentinel matte as well as cell 0.
  fill(c,'#9c9d94',0,height-16,16,16);fill(r,'#f4f4f4',0,height-16,16,16);
  const map=new CanvasTexture(canvas),roughnessMap=new CanvasTexture(roughness);
  map.colorSpace=SRGBColorSpace;roughnessMap.colorSpace=NoColorSpace;
  for(const texture of [map,roughnessMap]){texture.wrapS=texture.wrapT=ClampToEdgeWrapping;texture.anisotropy=8;}
  map.name='Authored Melbourne facade families';roughnessMap.name='Facade glazing and matte roof roughness';
  return new MeshStandardMaterial({map,roughnessMap,vertexColors:true,color:'#ffffff',metalness:.08,roughness:1});
}
