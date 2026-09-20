/** Offline replay of the runtime clipper for a saved cab camera. No browser state.
 * Photomesh-only rays ignore authored occluders; correlate with the saved image.
 * node scripts/inspect-photomesh.mjs capture.json ndcX ndcY [ndcX ndcY ...]
 */
import {readFileSync} from 'node:fs';
import {build} from 'esbuild';
import * as T from 'three';
await build({stdin:{contents:"export {clipPhotomesh} from './src/render/photomesh-clip'; export {createPhotomeshClearance} from './src/render/photomesh-clearance';",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',outfile:'/tmp/train-photomesh-analysis.mjs'});
const {clipPhotomesh,createPhotomeshClearance}=await import('/tmp/train-photomesh-analysis.mjs');
const clearance=createPhotomeshClearance();
const capture=JSON.parse(readFileSync(process.argv[2],'utf8'));
const camera=new T.PerspectiveCamera(capture.camera.fov,1280/720,.1,10000);
camera.position.fromArray(capture.camera.position);camera.quaternion.fromArray(capture.camera.quaternion);camera.updateMatrixWorld();
const manifest=JSON.parse(readFileSync('src/data/photomesh-source.json','utf8'));
const meshes=[];
for(const asset of manifest.assets){
 const buffer=readFileSync('public'+asset.path);let json,bin;
 for(let cursor=12;cursor<buffer.length;){const length=buffer.readUInt32LE(cursor),type=buffer.readUInt32LE(cursor+4),chunk=buffer.subarray(cursor+8,cursor+8+length);if(type===0x4e4f534a)json=JSON.parse(chunk.toString());else if(type===0x004e4942)bin=chunk;cursor+=8+length;}
 const attribute=id=>{
  const a=json.accessors[id],view=json.bufferViews[a.bufferView],width={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type];
  const bytes=a.componentType===5123?2:4,stride=view.byteStride??width*bytes,offset=(view.byteOffset??0)+(a.byteOffset??0);
  const out=a.componentType===5126?new Float32Array(a.count*width):new Uint32Array(a.count*width);
  for(let i=0;i<a.count;i++)for(let j=0;j<width;j++){const at=offset+i*stride+j*bytes;out[i*width+j]=a.componentType===5126?bin.readFloatLE(at):bytes===2?bin.readUInt16LE(at):bin.readUInt32LE(at);}
  return out;
 };
 for(const node of json.nodes){
  if(node.mesh===undefined)continue;
  if(node.rotation||node.scale||node.matrix)throw Error('Expected translation-only converted I3S tile');
  for(const primitive of json.meshes[node.mesh].primitives){
   const position=attribute(primitive.attributes.POSITION),normal=attribute(primitive.attributes.NORMAL),uv=attribute(primitive.attributes.TEXCOORD_0);
   const index=primitive.indices===undefined?Uint32Array.from({length:position.length/3},(_,i)=>i):attribute(primitive.indices);
   const result=clipPhotomesh({position,normal,uv,index,offset:node.translation??[0,0,0]},clearance);
   const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.BufferAttribute(result.position,3));geometry.setIndex(new T.BufferAttribute(result.index,1));
   const mesh=new T.Mesh(geometry,new T.MeshBasicMaterial());mesh.position.fromArray(result.offset);mesh.updateMatrixWorld();mesh.name=asset.name+'/'+(node.name??json.meshes[node.mesh].name??node.mesh);mesh.userData.result=result;meshes.push(mesh);
  }
 }
}
function component(mesh,face){
 const {position:p,index,offset}=mesh.userData.result,n=index.length/3,parent=Int32Array.from({length:n},(_,i)=>i),weld=new Map();
 const root=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;};
 for(let f=0;f<n;f++)for(let k=0;k<3;k++){
  const at=index[f*3+k]*3,key=[0,1,2].map(a=>Math.round(p[at+a]*100)).join(',');
  const previous=weld.get(key);if(previous!==undefined)parent[root(f)]=root(previous);else weld.set(key,f);
 }
 const selected=root(face),bounds=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity];let triangles=0;
 for(let f=0;f<n;f++)if(root(f)===selected){triangles++;for(let k=0;k<3;k++)for(let a=0;a<3;a++){const v=p[index[f*3+k]*3+a]+offset[a];bounds[a]=Math.min(bounds[a],v);bounds[a+3]=Math.max(bounds[a+3],v);}}
 return {triangles,bounds};
}
const ray=new T.Raycaster();
for(let i=3;i<process.argv.length;i+=2){const x=Number(process.argv[i]),y=Number(process.argv[i+1]);ray.setFromCamera(new T.Vector2(x,y),camera);
 const hits=ray.intersectObjects(meshes,false).slice(0,3).map(h=>({tile:h.object.name,point:h.point.toArray(),face:h.faceIndex,distance:h.distance,component:component(h.object,h.faceIndex)}));
 console.log(JSON.stringify({x,y,hits}));
}
