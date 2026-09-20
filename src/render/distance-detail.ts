/** Separate entry/exit distances prevent detail thrashing at a tier boundary. */
export function distanceDetailVisible(distance:number,wasVisible:boolean,enter:number,exit:number){
  return Number.isFinite(distance)&&distance<(wasVisible?exit:enter);
}
