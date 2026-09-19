import * as T from 'three/webgpu';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import source from '../data/corridor-source.json';
import riverSource from '../data/river-source.json';
import bridgeDecks from '../data/bridge-decks.json';
import { project,positionAt,tangentAt } from '../data/route';
import type { SurfaceLibrary } from './surface-library';
import { insideRing,riverCrossings,streetElevations } from './corridor-geography';

type LineFeature={geometry:{type:string;coordinates:number[][]|number[][][]};properties:Record<string,string|number|null>};
type TreeFeature={geometry:{coordinates:number[]};properties:{com_id:string;species:number;diameter_breast_height?:number}};
type AreaFeature={geometry:{type:string;coordinates:number[][][]|number[][][][]};properties:Record<string,string|number|null>};
const data=source as unknown as {layers:{roads:{features:LineFeature[]};rails:{features:LineFeature[]};trees:{features:TreeFeature[]};openSpaces?:{features:AreaFeature[]}};treeSpecies:{common_name:string;scientific_name:string}[]};
const vec=(p:{x:number;y:number;z:number})=>new T.Vector3(p.x,p.y,p.z);
const up=new T.Vector3(0,1,0);
const river=riverSource.geometry.coordinates[0].map(([lon,lat])=>project(lon,lat));

function waterAt(p:T.Vector3){
  return insideRing(p,river);
}
function lines(feature:LineFeature):T.Vector3[][]{
  const coordinates=feature.geometry.type==='MultiLineString'?feature.geometry.coordinates:[feature.geometry.coordinates];
  return (coordinates as number[][][]).map(line=>line.map(([lon,lat])=>vec(project(lon,lat,-.82))));
}
function ribbon(points:T.Vector3[],width:number,metres=3,dy=0){
  const positions:number[]=[],uv:number[]=[];
  const sides=points.map((p,i)=>{
    const t=points[Math.min(points.length-1,i+1)].clone().sub(points[Math.max(0,i-1)]);t.y=0;
    return new T.Vector3(-t.z,0,t.x).normalize().multiplyScalar(width/2);
  });
  for(let i=1;i<points.length;i++){
    const a=points[i-1],b=points[i],sa=sides[i-1],sb=sides[i];
    for(const p of [a.clone().add(sa),b.clone().add(sb),a.clone().sub(sa),a.clone().sub(sa),b.clone().add(sb),b.clone().sub(sb)]){
      positions.push(p.x,p.y+dy,p.z);uv.push(p.x/metres,p.z/metres);
    }
  }
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.computeVertexNormals();return g;
}
function merge(parent:T.Object3D,geometries:T.BufferGeometry[],material:T.Material,shadow=false){
  if(!geometries.length)return;
  const g=mergeGeometries(geometries,false);if(!g)return;
  const mesh=new T.Mesh(g,material);mesh.receiveShadow=true;mesh.castShadow=shadow;parent.add(mesh);
  geometries.forEach(g=>g.dispose());
}
function beam(a:T.Vector3,b:T.Vector3,width:number,height=width){
  const g=new T.BoxGeometry(width,height,a.distanceTo(b));
  g.applyQuaternion(new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,1),b.clone().sub(a).normalize()));
  const m=a.clone().add(b).multiplyScalar(.5);g.translate(m.x,m.y,m.z);return g;
}
function streetWidth(feature:LineFeature){
  const p=feature.properties,kind=String(p.feature_type_code);
  if(kind==='trail'||kind==='foot_bridge'||Number(p.class_code)===9)return 3;
  const width=({2:16,3:13,4:10,5:7,6:4} as Record<number,number>)[Number(p.class_code)]??7;
  return p.div_rd==='DD'?width*.55:width;
}

/** Official horizontal geography with explicitly authored widths and elevations. */
export class CorridorScenery {
  readonly group=new T.Group();readonly ready:Promise<void>;
  private treeChunks:{group:T.Group;center:T.Vector3}[]=[];
  constructor(private surfaces:SurfaceLibrary){
    this.buildStreets();this.buildBanks();this.buildTrees();this.buildRailDetails();
    this.ready=this.loadViaduct();
  }
  private buildStreets(){
    const asphalt:T.BufferGeometry[]=[],paving:T.BufferGeometry[]=[],paint:T.BufferGeometry[]=[],structure:T.BufferGeometry[]=[],rails:T.BufferGeometry[]=[];
    const metal=new T.MeshStandardMaterial({color:'#41494b',roughness:.67,metalness:.45});
    const decks=bridgeDecks.map(b=>({ring:b.ring.map(([x,z])=>({x,z})),top:b.top}));
    const streets=data.layers.roads.features.flatMap(feature=>{
      const p=feature.properties,kind=String(p.feature_type_code);if(kind==='tunnel')return [];
      const walking=kind==='trail'||kind==='foot_bridge'||Number(p.class_code)===9;
      const bridge=kind==='bridge'||kind==='foot_bridge';
      return lines(feature).filter(line=>line.length>1).map(original=>{
        const points=[original[0]];
        for(let i=1;i<original.length;i++){
          const a=original[i-1],b=original[i],steps=Math.ceil(a.distanceTo(b)/5);
          for(let k=1;k<=steps;k++)points.push(a.clone().lerp(b,k/steps));
        }
        const crossings=bridge?riverCrossings(original,river):[];
        const measured=crossings.flatMap(({a,b})=>{
          const mid={x:(a.x+b.x)/2,z:(a.z+b.z)/2};return decks.filter(d=>insideRing(mid,d.ring)).map(d=>d.top);
        });
        const deck=crossings.length?(measured.length?Math.max(...measured)+.03:3.3):undefined;
        return {feature,points,walking,bridge,deck};
      });
    });
    const elevations=streetElevations(streets);
    streets.forEach((street,i)=>street.points.forEach((p,j)=>p.y=elevations[i][j]));
    for(const {feature,points,walking,deck} of streets){
      const width=streetWidth(feature),p=feature.properties,crossing=deck!==undefined;
        if(crossing){
          for(let i=1;i<points.length;i++){
            const a=points[i-1],b=points[i],side=new T.Vector3(-(b.z-a.z),0,b.x-a.x).normalize();
            structure.push(beam(a.clone().addScaledVector(up,-.22),b.clone().addScaledVector(up,-.22),width+.5,.45));
            for(const sign of [-1,1]){
              const x=a.clone().addScaledVector(side,sign*(width/2+.15)),y=b.clone().addScaledVector(side,sign*(width/2+.15));
              rails.push(beam(x.clone().add(new T.Vector3(0,1.05,0)),y.clone().add(new T.Vector3(0,1.05,0)),.08));
              const count=Math.ceil(x.distanceTo(y)/3);
              for(let k=0;k<=count;k++){const at=x.clone().lerp(y,k/count);rails.push(beam(at,at.clone().add(new T.Vector3(0,1.08,0)),.065));}
            }
          }
        }
        paving.push(ribbon(points,width+(walking?0:3.5),3.1,-.055));
        if(!walking){
          asphalt.push(ribbon(points,width,3));
          if(Number(p.class_code)<=4){
            let distance=0;
            for(let i=1;i<points.length;i++){
              const a=points[i-1],b=points[i],length=a.distanceTo(b);let cursor=0;
              while(cursor<length-.0001){
                const phase=(distance+cursor)%10,dash=phase<3;
                const end=Math.min(length,cursor+(dash?3-phase:10-phase));
                if(dash)paint.push(ribbon([a.clone().lerp(b,cursor/length),a.clone().lerp(b,end/length)],.12,1,.025));
                cursor=end;
              }
              distance+=length;
            }
          }
        }
    }
    merge(this.group,paving,this.surfaces.paving);merge(this.group,asphalt,this.surfaces.asphalt);
    merge(this.group,paint,new T.MeshStandardMaterial({color:'#d6d5c9',roughness:1}));
    merge(this.group,structure,new T.MeshStandardMaterial({color:'#67685f',roughness:.92}));merge(this.group,rails,metal);
    const tramRails:T.BufferGeometry[]=[];
    const roadSegments=streets.filter(s=>!s.walking).flatMap(s=>s.points.slice(1).map((b,i)=>({a:s.points[i],b,width:streetWidth(s.feature)})));
    const roadSurfaceAt=(p:T.Vector3,heading:T.Vector3)=>{
      let height=-.82,best=Infinity;
      for(const {a,b,width} of roadSegments){
        const dx=b.x-a.x,dz=b.z-a.z,length2=dx*dx+dz*dz;if(length2<.001)continue;
        if(Math.abs((dx*heading.x+dz*heading.z)/Math.sqrt(length2))/Math.hypot(heading.x,heading.z)<.85)continue;
        const t=T.MathUtils.clamp(((p.x-a.x)*dx+(p.z-a.z)*dz)/length2,0,1),distance=Math.hypot(p.x-a.x-dx*t,p.z-a.z-dz*t);
        if(distance<width/2+1&&distance<best){best=distance;height=T.MathUtils.lerp(a.y,b.y,t);}
      }
      return height;
    };
    for(const feature of data.layers.rails.features){
      if(feature.properties.feature_type_code!=='tramway')continue;
      for(const line of lines(feature))for(let i=1;i<line.length;i++){
        const a=line[i-1],b=line[i],side=new T.Vector3(-(b.z-a.z),0,b.x-a.x).normalize();
        for(const offset of [-.72,.72]){
          const x=a.clone().addScaledVector(side,offset),y=b.clone().addScaledVector(side,offset);
          const heading=b.clone().sub(a);x.y=roadSurfaceAt(x,heading)+.035;y.y=roadSurfaceAt(y,heading)+.035;tramRails.push(beam(x,y,.045,.025));
        }
      }
    }
    merge(this.group,tramRails,new T.MeshStandardMaterial({color:'#aaa99c',metalness:.8,roughness:.38}));
    const green:T.BufferGeometry[]=[];
    for(const feature of data.layers.openSpaces?.features??[]){
      const name=String(feature.properties.name??'');
      // Open-space datasets also include paved promenades. Only these park areas get grass.
      if(!/Batman|Enterprise|Alexandra|Gardens/i.test(name))continue;
      const polygons=feature.geometry.type==='MultiPolygon'?feature.geometry.coordinates:[feature.geometry.coordinates];
      for(const rings of polygons as number[][][][]){
        const paths=rings.map(r=>r.map(([lon,lat])=>{const p=project(lon,lat);return new T.Vector2(p.x,-p.z);}));
        const shape=new T.Shape(paths[0]);shape.holes.push(...paths.slice(1).map(p=>new T.Path(p)));
        const g=new T.ShapeGeometry(shape);g.rotateX(-Math.PI/2);g.translate(0,-.91,0);green.push(g);
      }
    }
    merge(this.group,green,new T.MeshStandardMaterial({color:'#697b43',roughness:1}));
  }
  private buildBanks(){
    const stone:T.BufferGeometry[]=[],caps:T.BufferGeometry[]=[],walk:T.BufferGeometry[]=[];
    for(let i=1;i<riverSource.geometry.coordinates[0].length;i++){
      const [lon,lat]=riverSource.geometry.coordinates[0][i];
      if(lon<144.953||lon>144.974||lat< -37.824)continue;
      const a=vec(river[i-1]),b=vec(river[i]);if(a.distanceTo(b)>90)continue;
      const t=b.clone().sub(a),side=new T.Vector3(-t.z,0,t.x).normalize();
      const mid=a.clone().add(b).multiplyScalar(.5);
      if(waterAt(mid.clone().addScaledVector(side,1)))side.negate();
      a.y=b.y=-.45;stone.push(beam(a,b,.45,1.2));
      caps.push(beam(a.clone().add(new T.Vector3(0,.68,0)),b.clone().add(new T.Vector3(0,.68,0)),.65,.22));
      const p=a.clone().addScaledVector(side,2),q=b.clone().addScaledVector(side,2);p.y=q.y=-.78;
      walk.push(ribbon([p,q],3.4,3.1));
    }
    merge(this.group,stone,new T.MeshStandardMaterial({color:'#4b504e',roughness:.93}));
    merge(this.group,caps,new T.MeshStandardMaterial({color:'#969b93',roughness:.85}));merge(this.group,walk,this.surfaces.paving);
  }
  private buildTrees(){
    const trackSamples=Array.from({length:84},(_,i)=>positionAt(162+i*12));
    const groups=new Map<string,TreeFeature[]>();
    for(const feature of data.layers.trees.features){
      const [lon,lat]=feature.geometry.coordinates,p=project(lon,lat),key=`${Math.floor(p.x/200)},${Math.floor(p.z/200)}`;
      const list=groups.get(key)??[];list.push(feature);groups.set(key,list);
    }
    const bark=new T.MeshStandardMaterial({color:'#706856',roughness:1});
    const foliage=new T.MeshStandardMaterial({map:leafTexture(),alphaTest:.45,alphaToCoverage:true,side:T.DoubleSide,roughness:1});
    const trunkGeometry=new T.CylinderGeometry(.7,1,1,7),leafGeometry=new T.PlaneGeometry(1,1);
    const matrix=new T.Matrix4(),q=new T.Quaternion(),scale=new T.Vector3(),euler=new T.Euler();
    for(const [key,features] of groups){
      const group=new T.Group(),trunks=new T.InstancedMesh(trunkGeometry,bark,features.length),leaves=new T.InstancedMesh(leafGeometry,foliage,features.length*18);
      let leafCount=0;
      for(const [index,feature] of features.entries()){
        const [lon,lat]=feature.geometry.coordinates,p=project(lon,lat),id=Number(feature.properties.com_id)||index;
        const diameter=T.MathUtils.clamp((Number(feature.properties.diameter_breast_height)||35)/100,.12,1.3);
        let height=T.MathUtils.clamp(5+diameter*11,6,19),crown=T.MathUtils.clamp(2+diameter*5,2.2,7);
        // Positions are mapped; sizes are authored. Keep inferred crowns below
        // the viaduct where coarse route geometry overlays a mapped tree.
        const nearest=trackSamples.reduce((a,b)=>Math.hypot(a.x-p.x,a.z-p.z)<Math.hypot(b.x-p.x,b.z-p.z)?a:b);
        if(Math.hypot(nearest.x-p.x,nearest.z-p.z)<17){height=Math.min(height,Math.max(2,nearest.y-1.5));crown=Math.min(crown,height*.32);}
        const palm=/palm/i.test(data.treeSpecies[feature.properties.species]?.common_name??'');
        const trunkHeight=palm?height:height*.62;
        q.identity();matrix.compose(new T.Vector3(p.x,trunkHeight/2-.9,p.z),q,scale.set(diameter/2,trunkHeight,diameter/2));trunks.setMatrixAt(index,matrix);
        for(let j=0;j<18;j++){
          const angle=j*2.39996+(id%29),r=crown*.48*Math.sqrt((j+.5)/18);
          const y=palm?height-.8+Math.sin(j)*.4:height*.57+Math.sin((j+.5)/18*Math.PI)*crown*.55;
          const position=new T.Vector3(p.x+Math.cos(angle)*r,y,p.z+Math.sin(angle)*r);
          euler.set(palm?-1.15:((j%3)-1)*.5,angle,(j%5-.2)*.17);q.setFromEuler(euler);
          const size=palm?crown*.8:crown*.95;
          matrix.compose(position,q,scale.set(size,palm?size*.35:size,1));leaves.setMatrixAt(leafCount,matrix);
          leaves.setColorAt(leafCount++,new T.Color().setHSL(.2+(id%13)/220,.12+(id%7)/100,.68+(id%9)/130));
        }
      }
      trunks.castShadow=true;trunks.receiveShadow=true;leaves.castShadow=true;leaves.receiveShadow=true;
      group.add(trunks,leaves);this.group.add(group);
      const [x,z]=key.split(',').map(Number);this.treeChunks.push({group,center:new T.Vector3(x*200+100,0,z*200+100)});
    }
  }
  private buildRailDetails(){
    const fasteners:T.BufferGeometry[]=[],rails:T.BufferGeometry[]=[],gantries:T.BufferGeometry[]=[],wires:number[]=[];
    const end=1154;
    // Six-track context along the training alignment; offsets are authored.
    for(const offset of [-8.4,-4.2,4.2,8.4,12.6]){
      const path:T.Vector3[]=[];
      for(let s=162;s<=end;s+=4){const p=positionAt(s),t=tangentAt(s),n=Math.hypot(t.x,t.z);path.push(new T.Vector3(p.x-t.z/n*offset,p.y,p.z+t.x/n*offset));}
      this.group.add(new T.Mesh(ribbon(path,3.8,2),this.surfaces.ballast));
      for(let i=1;i<path.length;i++){
        const a=path[i-1],b=path[i],t=b.clone().sub(a).normalize(),side=new T.Vector3(-t.z,0,t.x);
        for(const d of [-.8,.8])rails.push(beam(a.clone().addScaledVector(side,d).add(new T.Vector3(0,.22,0)),b.clone().addScaledVector(side,d).add(new T.Vector3(0,.22,0)),.07,.14));
      }
    }
    for(let s=145;s<end;s+=34){
      const p=vec(positionAt(s)),t=vec(tangentAt(s));t.y=0;t.normalize();const side=new T.Vector3(-t.z,0,t.x);
      const a=p.clone().addScaledVector(side,-11),b=p.clone().addScaledVector(side,15.2),height=6.8;
      gantries.push(beam(a,a.clone().addScaledVector(up,height),.22));gantries.push(beam(b,b.clone().addScaledVector(up,height),.22));
      gantries.push(beam(a.clone().addScaledVector(up,height),b.clone().addScaledVector(up,height),.18,.35));
      for(let d=-9;d<15;d+=2){gantries.push(beam(p.clone().addScaledVector(side,d).addScaledVector(up,height-.9),p.clone().addScaledVector(side,d+1.6).addScaledVector(up,height),.065));}
      for(const d of [-8.4,-4.2,0,4.2,8.4,12.6]){
        const hook=p.clone().addScaledVector(side,d).addScaledVector(up,5.65);
        gantries.push(beam(hook,hook.clone().addScaledVector(up,1.15),.045));
        const np=vec(positionAt(Math.min(s+34,end))),nt=vec(tangentAt(Math.min(s+34,end))),ns=new T.Vector3(-nt.z,0,nt.x).normalize();
        const next=np.addScaledVector(ns,d).addScaledVector(up,5.65);
        wires.push(...hook.toArray(),...next.toArray());
      }
    }
    for(let s=162;s<end;s+=.7){
      const p=vec(positionAt(s)),t=vec(tangentAt(s)),side=new T.Vector3(-t.z,0,t.x).normalize();
      for(const offset of [-8.4,-4.2,4.2,8.4,12.6]){
        const at=p.clone().addScaledVector(side,offset).addScaledVector(up,.08);fasteners.push(beam(at.clone().addScaledVector(side,-1.3),at.clone().addScaledVector(side,1.3),.23,.13));
      }
    }
    merge(this.group,fasteners,new T.MeshStandardMaterial({color:'#8e8b80',roughness:1}));
    merge(this.group,rails,new T.MeshStandardMaterial({color:'#767773',roughness:.31,metalness:.8}));
    merge(this.group,gantries,new T.MeshStandardMaterial({color:'#615f57',roughness:.78,metalness:.48}),true);
    const wg=new T.BufferGeometry();wg.setAttribute('position',new T.Float32BufferAttribute(wires,3));this.group.add(new T.LineSegments(wg,new T.LineBasicMaterial({color:'#333935'})));
  }
  private async loadViaduct(){
    const gltf=await new GLTFLoader().loadAsync('/models/environment/railway-viaduct.glb');
    // Instance the authored pieces in 96m cells. Close cells use the ornamental
    // fascia; distant cells retain the structure's silhouette with a light mesh.
    const detailed=gltf.scene.getObjectByName('riveted_girder_span');
    const coarse=gltf.scene.getObjectByName('low_detail');
    const masonry=gltf.scene.getObjectByName('masonry_arch_bay');
    const pier=gltf.scene.getObjectByName('bluestone_pier');
    if(!detailed||!coarse||!masonry||!pier)throw new Error('Viaduct asset is incomplete.');
    gltf.scene.traverse(child=>{
      if(!(child instanceof T.Mesh))return;
      for(const material of Array.isArray(child.material)?child.material:[child.material]){
        if(!(material instanceof T.MeshStandardMaterial))continue;
        for(const texture of [material.map,material.normalMap,material.roughnessMap])if(texture)texture.anisotropy=8;
      }
    });
    gltf.scene.updateMatrixWorld(true);
    type Placement={s:number;offset:number;outer:number};
    const addInstances=(parent:T.Group,template:T.Object3D,placements:Placement[],origin:T.Vector3,shadows:boolean)=>{
      template.traverse(child=>{
        if(!(child instanceof T.Mesh))return;
        let edge=0;
        for(let node:T.Object3D|null=child;node&&node!==template;node=node.parent){
          if(/railing|fascia/.test(node.name)){
            edge=Math.sign(new T.Box3().setFromObject(node).getCenter(new T.Vector3()).x);break;
          }
        }
        const selected=placements.filter(p=>!edge||p.outer===edge);if(!selected.length)return;
        const mesh=new T.InstancedMesh(child.geometry,child.material,selected.length);
        for(const [i,{s,offset}] of selected.entries()){
          const p=vec(positionAt(s)),t=vec(tangentAt(s)),side=new T.Vector3(-t.z,0,t.x).normalize();p.addScaledVector(side,offset).sub(origin);
          const matrix=new T.Matrix4().compose(p,new T.Quaternion().setFromUnitVectors(new T.Vector3(0,0,1),t),new T.Vector3(1.05,1,1));
          if(template===pier||template===masonry){
            const top=template===pier?-1.67:-.22,bottom=-6.8,ground=-1.05;
            const scale=(positionAt(s).y+top-ground)/(top-bottom);
            const stretch=new T.Matrix4().makeTranslation(0,top,0).multiply(new T.Matrix4().makeScale(1,scale,1)).multiply(new T.Matrix4().makeTranslation(0,-top,0));
            matrix.multiply(stretch);
          }
          matrix.multiply(child.matrixWorld);mesh.setMatrixAt(i,matrix);
        }
        mesh.castShadow=shadows;mesh.receiveShadow=true;parent.add(mesh);
      });
    };
    for(let start=162;start<1154;start+=96){
      const center=vec(positionAt(start+48)),lod=new T.LOD(),near=new T.Group(),far=new T.Group();lod.position.copy(center);
      const steel:Placement[]=[],brick:Placement[]=[],piers:Placement[]=[];
      for(let s=start+8;s<Math.min(start+96,1154);s+=16){
        for(const [offset,outer] of [[-6.3,1],[2.1,0],[10.5,-1]]){
          const placement={s,offset,outer};(s<354?brick:steel).push(placement);
          // 16m spans meet on a pier. The source establishes horizontal corridor,
          // while span spacing and this ground-relative datum remain authored.
          if(s>=354)piers.push({s:s-8,offset,outer});
        }
      }
      addInstances(near,detailed,steel,center,true);addInstances(far,coarse,steel,center,false);
      // Masonry bay is 12m long: use a denser sequence along the eastern vaults.
      if(brick.length){
        const bays:Placement[]=[];
        for(let s=start+6;s<Math.min(start+96,354);s+=12)for(const offset of [-6.3,2.1,10.5])bays.push({s,offset,outer:0});
        addInstances(near,masonry,bays,center,true);addInstances(far,masonry,bays,center,false);
      }
      addInstances(near,pier,piers,center,true);addInstances(far,pier,piers,center,false);
      lod.addLevel(near,0);lod.addLevel(far,190,0.12);lod.addLevel(new T.Group(),1500,0.1);this.group.add(lod);
    }
  }

  update(camera:T.Camera){
    for(const chunk of this.treeChunks)chunk.group.visible=chunk.center.distanceTo(camera.position)<1000;
  }
}

function leafTexture(){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=256;const ctx=canvas.getContext('2d')!;
  let seed=492;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<300;i++){
    const angle=random()*Math.PI*2,r=Math.sqrt(random())*115,x=128+Math.cos(angle)*r,y=128+Math.sin(angle)*r;
    const shade=70+random()*85;ctx.fillStyle=`rgb(${shade*.85},${shade},${shade*.64})`;
    ctx.beginPath();ctx.ellipse(x,y,4+random()*8,2+random()*5,angle,0,Math.PI*2);ctx.fill();
  }
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;return texture;
}
