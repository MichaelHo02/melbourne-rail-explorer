import Renderer from 'three/src/renderers/common/Renderer.js';
import WebGPUBackend from 'three/src/renderers/webgpu/WebGPUBackend.js';
import StandardNodeLibrary from 'three/src/renderers/webgpu/nodes/StandardNodeLibrary.js';

/** Native WebGPU only, retaining the standard GLB-to-node material mappings. */
export function createNativeRenderer() {
  if (!navigator.gpu) throw new Error('WebGPU is unavailable. Use a browser and GPU with WebGPU enabled.');
  const options = { antialias: true, powerPreference: 'high-performance' as const };
  const renderer = new Renderer(new WebGPUBackend(options), options);
  renderer.library = new StandardNodeLibrary();
  return renderer;
}
