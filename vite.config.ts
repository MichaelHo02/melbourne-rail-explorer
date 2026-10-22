import { defineConfig } from 'vite';
// @ts-expect-error Shared Node middleware is authored as ESM JavaScript.
import { feedMiddleware } from './server/feeds.mjs';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  resolve:{alias:[
    {find:/^three\/webgpu$/,replacement:fileURLToPath(new URL('./src/render/three-native.ts',import.meta.url))},
    {find:/^three\/tsl$/,replacement:'three/src/nodes/TSL.js'},
    {find:/^three$/,replacement:'three/src/Three.Core.js'},
  ]},
  plugins:[{name:'city-observatory-feeds',configureServer(server){server.middlewares.use(feedMiddleware);}}, {
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
