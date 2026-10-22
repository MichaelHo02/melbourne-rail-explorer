import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  resolve:{alias:[
    {find:/^three\/webgpu$/,replacement:fileURLToPath(new URL('./src/render/three-native.ts',import.meta.url))},
    {find:/^three\/tsl$/,replacement:'three/src/nodes/TSL.js'},
    {find:/^three$/,replacement:'three/src/Three.Core.js'},
  ]},
  plugins:[{
    name:'require-native-webgpu',
    generateBundle(_options,bundle){
      for(const output of Object.values(bundle))if(output.type==='chunk'){
        for(const [id,module] of Object.entries(output.modules)){
          if(module.renderedLength>0&&id.includes('/webgl-fallback/'))this.error(`WebGL backend must not ship: ${id}`);
        }
      }
    },
  }],
  build:{rollupOptions:{output:{manualChunks:{three:['three/webgpu','three/tsl']}}}},
});
