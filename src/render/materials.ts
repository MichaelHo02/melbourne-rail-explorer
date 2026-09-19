import * as THREE from 'three/webgpu';

function canvasTexture(size:number,draw:(ctx:CanvasRenderingContext2D)=>void){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=size;
  draw(canvas.getContext('2d')!);
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.anisotropy=8;return texture;
}
let seed=712;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
export function surfaceTexture(kind:'ballast'|'concrete'|'brick'){
  return canvasTexture(256,ctx=>{
    ctx.fillStyle=kind==='ballast'?'#5d594f':kind==='brick'?'#857766':'#98988e';ctx.fillRect(0,0,256,256);
    for(let i=0;i<18000;i++){
      const v=Math.floor(45+random()*110);ctx.fillStyle=`rgba(${v},${v},${v},${kind==='ballast'?.6:.15})`;
      const r=kind==='ballast'?1+random()*4:1;ctx.fillRect(random()*256,random()*256,r,r);
    }
    if(kind==='brick'){
      ctx.strokeStyle='#635f56';ctx.lineWidth=2;
      for(let y=0;y<256;y+=32){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(256,y);ctx.stroke();
        for(let x=(y%64?32:0);x<256;x+=64){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+32);ctx.stroke();}}
    }
  });
}
export function facadeTexture(){return canvasTexture(512,ctx=>{
  ctx.fillStyle='#8c9798';ctx.fillRect(0,0,512,512);
  for(let x=0;x<512;x+=64)for(let y=0;y<512;y+=64){
    const light=random();ctx.fillStyle=light>.84?'#a5acac':light>.35?'#667c85':'#4d646e';ctx.fillRect(x+5,y+5,54,47);
    const g=ctx.createLinearGradient(x,y,x+54,y+47);g.addColorStop(0,'rgba(184,205,210,.22)');g.addColorStop(1,'rgba(18,30,40,.25)');ctx.fillStyle=g;ctx.fillRect(x+5,y+5,54,47);
    ctx.fillStyle='#abb3b0';ctx.fillRect(x+31,y+5,2,47);
  }
});}
export function facadeRoughnessTexture(){const texture=canvasTexture(512,ctx=>{
  ctx.fillStyle='#ebebeb';ctx.fillRect(0,0,512,512);
  for(let x=0;x<512;x+=64)for(let y=0;y<512;y+=64){ctx.fillStyle='#606060';ctx.fillRect(x+5,y+5,54,47);ctx.fillStyle='#cccccc';ctx.fillRect(x+31,y+5,2,47);}
});texture.colorSpace=THREE.NoColorSpace;return texture;}
export function labelTexture(text:string,bg='#16303b',fg='#ffffff',width=1024,height=128){
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const ctx=canvas.getContext('2d')!;ctx.fillStyle=bg;ctx.fillRect(0,0,width,height);
  ctx.fillStyle=fg;ctx.font=`600 ${Math.floor(height*.48)}px Arial`;ctx.textBaseline='middle';ctx.textAlign='center';ctx.fillText(text,width/2,height/2,width-32);
  const t=new THREE.CanvasTexture(canvas);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
