import { createPhotomeshClearance } from './photomesh-clearance';
import { clipPhotomesh, facadeSamples, type PhotomeshGeometry } from './photomesh-clip';

const clearance=createPhotomeshClearance();
self.onmessage=(event:MessageEvent<{id:number;geometry:PhotomeshGeometry}>)=>{
  const {id,geometry}=event.data;
  try{
    const result=clipPhotomesh(geometry,clearance),facades=facadeSamples(result);
    self.postMessage({id,geometry:{...result,facades}},{transfer:[result.position.buffer,result.normal.buffer,result.uv.buffer,result.index.buffer,result.affectedBounds.buffer,facades.buffer]});
  }catch(error){self.postMessage({id,error:error instanceof Error?error.message:String(error)});}
};
