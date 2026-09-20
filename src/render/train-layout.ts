/** Metre-scale dimensions shared with the authored Blender HCMT asset. */
export const CAR_SPACING=22.85;
export const CAB_TO_CAR_CENTRE=11.2;
export const DOOR_OFFSETS=[-5.62,.57,7.07] as const;

export function trainDoorDistances(front:number){
  return Array.from({length:7},(_,car)=>DOOR_OFFSETS.map(z=>front-CAB_TO_CAR_CENTRE-car*CAR_SPACING+(car===6?z:-z))).flat();
}

/** Positive is the asset's right side; the rear driving car faces backwards. */
export function doorLeafSide(name:string,car:number){
  return (name.startsWith('door_L_')?-1:1)*(car===6?-1:1);
}
