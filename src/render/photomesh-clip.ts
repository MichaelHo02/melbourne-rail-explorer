/** Polygon subtraction for photographed triangle meshes. All planes point into
 * a clearance volume. Source vertex attributes remain in the tile's local space. */
export type Plane = readonly [number, number, number, number];
export interface ClearanceVolume {
  planes: Plane[];
  bounds: { minX:number; maxX:number; minZ:number; maxZ:number };
  name: string;
}
export interface PhotomeshGeometry {
  position:Float32Array; normal:Float32Array; uv:Float32Array; index:Uint32Array;
  offset:readonly number[];
}
export interface ClippedGeometry extends PhotomeshGeometry {
  sourceTriangles:number; removedTriangles:number; splitTriangles:number;
  /** World AABBs of source faces touched by a clearance, six floats each. */
  affectedBounds:Float32Array;
}
/** A compact retained-surface index. Flat road/roof triangles cannot count as
 * lower-facade evidence under an otherwise disconnected photographic roof. */
export function facadeSamples({position:p,index,offset}:PhotomeshGeometry):Float32Array {
  const samples:number[]=[];
  for(let i=0;i<index.length;i+=3){
    const a=index[i]*3,b=index[i+1]*3,c=index[i+2]*3;
    const ux=p[b]-p[a],uy=p[b+1]-p[a+1],uz=p[b+2]-p[a+2],vx=p[c]-p[a],vy=p[c+1]-p[a+1],vz=p[c+2]-p[a+2];
    const nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
    if(Math.abs(ny)>Math.hypot(nx,ny,nz)*.7)continue;
    const minY=Math.min(p[a+1],p[b+1],p[c+1])+offset[1],maxY=Math.max(p[a+1],p[b+1],p[c+1])+offset[1];if(maxY-minY<.6)continue;
    samples.push((p[a]+p[b]+p[c])/3+offset[0],(p[a+2]+p[b+2]+p[c+2])/3+offset[2],minY,maxY);
  }
  return new Float32Array(samples);
}
const EPSILON=1e-7;
type Vertex=number[];
type Polygon=Vertex[];
const distance=(p:readonly number[],plane:Plane,offset:readonly number[])=>
  plane[0]*(p[0]+offset[0])+plane[1]*(p[1]+offset[1])+plane[2]*(p[2]+offset[2])+plane[3];

/** Convex footprint extruded through a vertical interval; winding is irrelevant. */
export function prism(ring:readonly (readonly number[])[],minY:number,maxY:number,name='clearance'):ClearanceVolume {
  let area=0;
  for(let i=0;i<ring.length;i++){const a=ring[i],b=ring[(i+1)%ring.length];area+=a[0]*b[1]-b[0]*a[1];}
  const winding=Math.sign(area)||1,planes:Plane[]=[];
  for(let i=0;i<ring.length;i++){
    const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz);
    if(length<EPSILON)continue;
    const nx=-dz/length*winding,nz=dx/length*winding;
    planes.push([nx,0,nz,-nx*a[0]-nz*a[1]]);
  }
  if(Number.isFinite(minY))planes.push([0,1,0,-minY]);
  if(Number.isFinite(maxY))planes.push([0,-1,0,maxY]);
  return {planes,bounds:{minX:Math.min(...ring.map(p=>p[0])),maxX:Math.max(...ring.map(p=>p[0])),minZ:Math.min(...ring.map(p=>p[1])),maxZ:Math.max(...ring.map(p=>p[1]))},name};
}

/** No allocation for the overwhelming majority of triangles outside a mask. */
function classify(points:readonly (readonly number[])[],volume:ClearanceVolume,offset:readonly number[]){
  let contained=true;
  for(const plane of volume.planes){
    let anyInside=false,anyOutside=false;
    for(const point of points){const d=distance(point,plane,offset);if(d>=-EPSILON)anyInside=true;else anyOutside=true;}
    if(!anyInside)return -1;
    if(anyOutside)contained=false;
  }
  return contained?1:0;
}

function split(polygon:Polygon,plane:Plane,offset:readonly number[]):{inside:Polygon;outside:Polygon}{
  const inside:Polygon=[],outside:Polygon=[];
  for(let i=0;i<polygon.length;i++){
    const a=polygon[i],b=polygon[(i+1)%polygon.length],da=distance(a,plane,offset),db=distance(b,plane,offset);
    const aInside=da>=-EPSILON,bInside=db>=-EPSILON;
    (aInside?inside:outside).push(a);
    if(aInside!==bInside){
      const t=Math.max(0,Math.min(1,da/(da-db))),point=a.map((v,k)=>v+(b[k]-v)*t);
      inside.push(point);outside.push(point);
    }
  }
  return {inside,outside};
}

export function subtractVolume(polygon:Polygon,volume:ClearanceVolume,offset:readonly number[]=[0,0,0]):Polygon[]{
  const relation=classify(polygon,volume,offset);
  if(relation<0)return [polygon];
  if(relation>0)return [];
  const kept:Polygon[]=[];let remaining=polygon;
  for(const plane of volume.planes){
    const {inside,outside}=split(remaining,plane,offset);
    if(outside.length>=3)kept.push(outside);
    remaining=inside;if(remaining.length<3)break;
  }
  return kept;
}

/** Uniform broad phase: bounded by geographic mask extents, not triangle count. */
export class ClearanceIndex {
  private cells=new Map<string,number[]>();
  private visited:Int32Array;private stamp=0;
  constructor(readonly volumes:ClearanceVolume[],private cellSize=80){
    this.visited=new Int32Array(volumes.length);
    volumes.forEach((v,i)=>{const b=v.bounds;for(let x=Math.floor(b.minX/cellSize);x<=Math.floor(b.maxX/cellSize);x++)for(let z=Math.floor(b.minZ/cellSize);z<=Math.floor(b.maxZ/cellSize);z++){
      const key=`${x},${z}`,ids=this.cells.get(key);if(ids)ids.push(i);else this.cells.set(key,[i]);
    }});
  }
  query(minX:number,maxX:number,minZ:number,maxZ:number,out:number[]){
    out.length=0;const stamp=++this.stamp;
    for(let x=Math.floor(minX/this.cellSize);x<=Math.floor(maxX/this.cellSize);x++)for(let z=Math.floor(minZ/this.cellSize);z<=Math.floor(maxZ/this.cellSize);z++){
      const ids=this.cells.get(`${x},${z}`);if(!ids)continue;
      for(const id of ids){
        if(this.visited[id]===stamp)continue;this.visited[id]=stamp;
        const b=this.volumes[id].bounds;
        if(b.maxX>=minX&&b.minX<=maxX&&b.maxZ>=minZ&&b.minZ<=maxZ)out.push(id);
      }
    }
  }
}

export function clipPhotomesh(source:PhotomeshGeometry,index:ClearanceIndex):ClippedGeometry {
  const {position,normal,uv,offset}=source,kept:number[]=[],added:number[]=[],candidates:number[]=[],affected:number[]=[];
  const points=[new Array<number>(3),new Array<number>(3),new Array<number>(3)];
  let removedTriangles=0,splitTriangles=0;
  const originalVertices=position.length/3;
  for(let i=0;i<source.index.length;i+=3){
    let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
    for(let j=0;j<3;j++){
      const id=source.index[i+j],p=points[j];p[0]=position[id*3];p[1]=position[id*3+1];p[2]=position[id*3+2];
      minX=Math.min(minX,p[0]+offset[0]);maxX=Math.max(maxX,p[0]+offset[0]);minZ=Math.min(minZ,p[2]+offset[2]);maxZ=Math.max(maxZ,p[2]+offset[2]);
    }
    index.query(minX,maxX,minZ,maxZ,candidates);
    let fullyRemoved=false,crosses=false;
    for(const id of candidates){const relation=classify(points,index.volumes[id],offset);if(relation===1){fullyRemoved=true;break;}if(relation===0)crosses=true;}
    if(fullyRemoved||crosses)affected.push(minX,Math.min(points[0][1],points[1][1],points[2][1])+offset[1],minZ,maxX,Math.max(points[0][1],points[1][1],points[2][1])+offset[1],maxZ);
    if(fullyRemoved){removedTriangles++;continue;}
    if(!crosses){kept.push(source.index[i],source.index[i+1],source.index[i+2]);continue;}
    let pieces:Polygon[]=[points.map((p,j)=>{const id=source.index[i+j];return [...p,normal[id*3],normal[id*3+1],normal[id*3+2],uv[id*2],uv[id*2+1]];})];
    for(const id of candidates){
      const next:Polygon[]=[];for(const piece of pieces)next.push(...subtractVolume(piece,index.volumes[id],offset));pieces=next;
      if(!pieces.length)break;
    }
    if(!pieces.length){removedTriangles++;continue;}
    splitTriangles++;
    for(const piece of pieces){
      // Emit only real surface area; duplicate intersections on a boundary can
      // otherwise produce flickering zero-area fans on long photographic faces.
      for(let k=1;k<piece.length-1;k++){
        const a=piece[0],b=piece[k],c=piece[k+1],ux=b[0]-a[0],uy=b[1]-a[1],uz=b[2]-a[2],vx=c[0]-a[0],vy=c[1]-a[1],vz=c[2]-a[2];
        if(Math.hypot(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx)<1e-6)continue;
        for(const v of [a,b,c]){kept.push(originalVertices+added.length/8);added.push(...v);}
      }
    }
  }
  const count=originalVertices+added.length/8,p=new Float32Array(count*3),n=new Float32Array(count*3),t=new Float32Array(count*2);
  p.set(position);n.set(normal);t.set(uv);
  for(let i=0;i<added.length;i+=8){
    const out=originalVertices+i/8;p.set(added.slice(i,i+3),out*3);
    const length=Math.hypot(added[i+3],added[i+4],added[i+5])||1;n.set([added[i+3]/length,added[i+4]/length,added[i+5]/length],out*3);t.set([added[i+6],added[i+7]],out*2);
  }
  return {position:p,normal:n,uv:t,index:new Uint32Array(kept),offset,sourceTriangles:source.index.length/3,removedTriangles,splitTriangles,affectedBounds:new Float32Array(affected)};
}
