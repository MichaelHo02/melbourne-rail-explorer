/** Horizontal source geometry. Vertical bridge profiles are authored presentation. */
export type PlanPoint={x:number;z:number};
export type StreetLine={points:PlanPoint[];walking:boolean;bridge:boolean;deck?:number};
export function insideRing(p:PlanPoint,ring:PlanPoint[]){
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];
    if((a.z>p.z)!==(b.z>p.z)&&p.x<(b.x-a.x)*(p.z-a.z)/(b.z-a.z)+a.x)inside=!inside;
  }
  return inside;
}
export function riverCrossings(points:PlanPoint[],ring:PlanPoint[]):{a:PlanPoint;b:PlanPoint}[]{
  const result:{a:PlanPoint;b:PlanPoint}[]=[];
  for(let k=1;k<points.length;k++){
    const a=points[k-1],b=points[k],dx=b.x-a.x,dz=b.z-a.z,ts=[0,1];
    if(Math.hypot(dx,dz)<.001)continue;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const c=ring[j],d=ring[i],ex=d.x-c.x,ez=d.z-c.z,den=dx*ez-dz*ex;
      if(Math.abs(den)<1e-9)continue;
      const cx=c.x-a.x,cz=c.z-a.z,t=(cx*ez-cz*ex)/den,u=(cx*dz-cz*dx)/den;
      if(t>0&&t<1&&u>=0&&u<=1)ts.push(t);
    }
    ts.sort((a,b)=>a-b);
    const at=(t:number)=>({x:a.x+dx*t,z:a.z+dz*t});
    for(let i=1;i<ts.length;i++)if(ts[i]-ts[i-1]>1e-8&&insideRing(at((ts[i]+ts[i-1])/2),ring))result.push({a:at(ts[i-1]),b:at(ts[i])});
  }
  return result;
}
/** Propagate a 60m smooth approach along connected source road geometry.
 * Spatially crossing underpasses stay separate. Adjacent bridge features share
 * one deck height. Heights and approach lengths remain authored. */
export function streetElevations(lines:StreetLine[]):number[][]{
  type Node={p:PlanPoint;edges:Map<number,{length:number;bridge:boolean}>;deck?:number;y:number};
  const nodes:Node[]=[],lookup=new Map<string,number>();
  const indices=lines.map(line=>line.points.map(p=>{
    // Network endpoints are snapped to 10cm solely for graph connectivity.
    // Rendered coordinates remain the original source coordinates.
    const key=`${line.walking?'walk':'road'}:${Math.round(p.x*10)},${Math.round(p.z*10)}`;
    let i=lookup.get(key);if(i===undefined){i=nodes.length;lookup.set(key,i);nodes.push({p,edges:new Map(),y:-.82});}
    if(line.deck!==undefined)nodes[i].deck=Math.max(nodes[i].deck??-Infinity,line.deck);
    return i;
  }));
  for(const [k,line] of lines.entries())for(let i=1;i<indices[k].length;i++){
    const a=indices[k][i-1],b=indices[k][i],length=Math.hypot(nodes[a].p.x-nodes[b].p.x,nodes[a].p.z-nodes[b].p.z);
    if(a===b)continue;
    const bridge=line.bridge||nodes[a].edges.get(b)?.bridge||false;
    nodes[a].edges.set(b,{length,bridge});nodes[b].edges.set(a,{length,bridge});
  }
  const visited=new Set<number>();
  for(let start=0;start<nodes.length;start++){
    if(visited.has(start)||![...nodes[start].edges.values()].some(e=>e.bridge))continue;
    const component=[start];visited.add(start);
    for(let j=0;j<component.length;j++)for(const [other,edge] of nodes[component[j]].edges){
      if(edge.bridge&&!visited.has(other)){visited.add(other);component.push(other);}
    }
    const measured=component.flatMap(i=>nodes[i].deck===undefined?[]:[nodes[i].deck!]);if(!measured.length)continue;
    const deck=Math.max(...measured),distances=new Map(component.map(i=>[i,0]));
    const queue=component.map(i=>({i,distance:0}));
    while(queue.length){
      queue.sort((a,b)=>b.distance-a.distance);const {i,distance}=queue.pop()!;
      if(distance!==distances.get(i))continue;
      const t=Math.min(1,distance/60),blend=1-t*t*(3-2*t);
      nodes[i].y=Math.max(nodes[i].y,-.82+(deck+.82)*blend);
      for(const [other,edge] of nodes[i].edges){
        const next=distance+edge.length;
        if(next>60||next>=(distances.get(other)??Infinity))continue;
        distances.set(other,next);queue.push({i:other,distance:next});
      }
    }
  }
  return indices.map(line=>line.map(i=>nodes[i].y));
}
