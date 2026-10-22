import * as THREE from 'three/webgpu';

function canvasTexture(size:number,draw:(ctx:CanvasRenderingContext2D)=>void){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=size;
  draw(canvas.getContext('2d')!);
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.anisotropy=8;return texture;
}
let seed=712;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
export function surfaceTexture(kind:'concrete'|'brick'){
  return canvasTexture(256,ctx=>{
    ctx.fillStyle=kind==='brick'?'#857766':'#98988e';ctx.fillRect(0,0,256,256);
    for(let i=0;i<18000;i++){
      const v=Math.floor(45+random()*110);ctx.fillStyle=`rgba(${v},${v},${v},0.15)`;
      ctx.fillRect(random()*256,random()*256,1,1);
    }
    if(kind==='brick'){
      ctx.strokeStyle='#635f56';ctx.lineWidth=2;
      for(let y=0;y<256;y+=32){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(256,y);ctx.stroke();
        for(let x=(y%64?32:0);x<256;x+=64){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+32);ctx.stroke();}}
    }
  });
}
export function labelTexture(text:string,bg='#16303b',fg='#ffffff',width=1024,height=128){
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const ctx=canvas.getContext('2d')!;ctx.fillStyle=bg;ctx.fillRect(0,0,width,height);
  ctx.fillStyle=fg;ctx.font=`600 ${Math.floor(height*.48)}px Arial`;ctx.textBaseline='middle';ctx.textAlign='center';ctx.fillText(text,width/2,height/2,width-32);
  const t=new THREE.CanvasTexture(canvas);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}

export function stationTileTexture(code:string){
  return canvasTexture(512,ctx=>{
    ctx.fillStyle=code==='MCE'?'#706f60':'#898c82';ctx.fillRect(0,0,512,512);
    const palette=code==='MCE'?['#977853','#a08460','#8c8267','#766d51','#a48a67']:['#b6b7ab','#a7ab9e','#bec0b5','#afb2a5'];
    const count=code==='MCE'?8:4,size=512/count;
    for(let y=0;y<count;y++)for(let x=0;x<count;x++){
      ctx.fillStyle=palette[(x*13+y*7)%palette.length];ctx.fillRect(x*size+1,y*size+1,size-2,size-2);
      for(let i=0;i<110;i++){ctx.fillStyle=i%2?'#ffffff09':'#00000009';ctx.fillRect(x*size+2+random()*(size-4),y*size+2+random()*(size-4),1+random()*3,1);}
    }
  });
}
