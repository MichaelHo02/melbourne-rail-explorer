import { Color, MeshPhysicalNodeMaterial, Scene } from 'three/webgpu';
import { fog, mix, positionWorld, rangeFogFactor, smoothstep, transformNormalToView, uniform, vec3 } from 'three/tsl';

/** Native WebGPU atmosphere and water; only uniforms change during play. */
export class EnvironmentEffects {
  private near = uniform(700);
  private far = uniform(4300);
  private underground = uniform(0);
  private fogColor = uniform(new Color('#c8d4d5'));
  private seconds = uniform(0);
  private daylight = new Color('#c8d4d5');
  private tunnel = new Color('#141d21');
  readonly water: MeshPhysicalNodeMaterial;

  constructor(scene: Scene) {
    // Distant low-lying city blocks collect more haze than the skyline.
    const heightFactor = mix(1, .55, smoothstep(8, 180, positionWorld.y));
    const factor = rangeFogFactor(this.near, this.far).mul(mix(heightFactor, 1, this.underground));
    Object.assign(scene, { fogNode: fog(this.fogColor, factor) });

    this.water = new MeshPhysicalNodeMaterial({
      color: '#625c43', roughness: .31, metalness: 0, ior: 1.333,
      clearcoat: .65, clearcoatRoughness: .22,
    });
    // Two gentle travelling wave directions, in metres, independent of mesh UVs.
    const a = positionWorld.x.mul(.42).add(positionWorld.z.mul(.23)).add(this.seconds.mul(.8));
    const b = positionWorld.x.mul(-.19).add(positionWorld.z.mul(.57)).sub(this.seconds.mul(.53));
    const normal = transformNormalToView(vec3(
      a.cos().mul(.055).add(b.cos().mul(-.023)),
      1,
      a.cos().mul(.03).add(b.cos().mul(.067)),
    ).normalize());
    this.water.normalNode = normal;
    this.water.clearcoatNormalNode = normal;
  }

  update(darkness: number, seconds: number) {
    this.underground.value = darkness;
    this.near.value = 700 + (45 - 700) * darkness;
    this.far.value = 4300 + (280 - 4300) * darkness;
    this.fogColor.value.copy(this.daylight).lerp(this.tunnel, darkness);
    this.seconds.value = seconds;
  }
}
