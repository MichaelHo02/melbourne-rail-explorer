import * as T from 'three/webgpu';

/** Meter-scaled PBR maps; assets are bundled and all loads gate scene readiness. */
export class SurfaceLibrary {
  readonly ballast=new T.MeshStandardMaterial({color:'#b1ada4',roughness:1,normalScale:new T.Vector2(.8,.8)});
  readonly asphalt=new T.MeshStandardMaterial({color:'#999c9c',roughness:1,normalScale:new T.Vector2(.35,.35)});
  readonly paving=new T.MeshStandardMaterial({color:'#b7b2a5',roughness:1,normalScale:new T.Vector2(.45,.45)});
  readonly ready:Promise<void>;
  constructor(){
    // Physical source dimensions are available before asynchronous image loads.
    this.ballast.userData.textureMetres=2;
    this.asphalt.userData.textureMetres=3;
    this.paving.userData.textureMetres=3.1;
    const loader=new T.TextureLoader();
    this.ready=Promise.all((['ballast','asphalt','paving'] as const).flatMap(name=>
      (['diff','nor_gl','rough'] as const).map(async channel=>{
        const texture=await loader.loadAsync(`/textures/surfaces/${name}-${channel}.jpg`);
        texture.colorSpace=channel==='diff'?T.SRGBColorSpace:T.NoColorSpace;
        texture.wrapS=texture.wrapT=T.RepeatWrapping;texture.anisotropy=8;
        const material=this[name];
        if(channel==='diff')material.map=texture;
        else if(channel==='nor_gl')material.normalMap=texture;
        else material.roughnessMap=texture;
        material.needsUpdate=true;
      })
    )).then(()=>{});
  }
}
