import { defineConfig } from 'vite';
export default defineConfig({
  build:{rollupOptions:{output:{manualChunks:{three:['three','three/addons/objects/Sky.js','three/addons/utils/BufferGeometryUtils.js']}}}},
});
