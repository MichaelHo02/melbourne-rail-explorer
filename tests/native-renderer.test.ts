import { afterEach, describe, expect, it, vi } from 'vitest';
import { createNativeRenderer } from '../src/render/native-renderer';

afterEach(()=>vi.unstubAllGlobals());

describe('WebGPU requirement',()=>{
  it('reports an unavailable WebGPU API before creating a rendering surface',()=>{
    vi.stubGlobal('navigator',{});
    expect(()=>createNativeRenderer()).toThrow('WebGPU is unavailable');
  });

  it.each(['adapter unavailable','device rejected'])('fails without requesting another graphics context when %s',async failure=>{
    const getContext=vi.fn();
    vi.stubGlobal('document',{createElementNS:()=>({width:300,height:150,style:{},getContext})});
    const requestDevice=vi.fn().mockRejectedValue(new Error('GPU device denied'));
    const requestAdapter=vi.fn().mockResolvedValue(failure==='adapter unavailable'?null:{features:new Set(),requestDevice});
    vi.stubGlobal('navigator',{gpu:{requestAdapter}});
    const renderer=createNativeRenderer(),backend=renderer.backend;
    await expect(renderer.init()).rejects.toThrow(failure==='adapter unavailable'?'Unable to create WebGPU adapter':'GPU device denied');
    expect(renderer.backend).toBe(backend);
    expect(getContext).not.toHaveBeenCalled();
  });
});
