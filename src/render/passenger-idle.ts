/** Weights for local anatomical morphs. Time is the simulation clock, never wall time. */
export interface PassengerIdle {lookLeft:number;lookRight:number;breathe:number}
const ease=(t:number)=>t*t*(3-2*t);
const pulse=(time:number,start:number,rise:number,hold:number,fall:number)=>{
  const t=time-start;
  if(t<=0||t>=rise+hold+fall)return 0;
  if(t<rise)return ease(t/rise);
  if(t<rise+hold)return 1;
  return 1-ease((t-rise-hold)/fall);
};
export function passengerIdle(seconds:number,seed:number):PassengerIdle {
  const phase=((seed*0.61803398875)%1+1)%1;
  const t=Math.max(0,Number.isFinite(seconds)?seconds:0);
  // Long quiet intervals between a brief glance down the platform. Different
  // passengers have different periods and phase; neither their roots nor feet move.
  const glancePeriod=19+phase*11;
  const glance=(t+phase*glancePeriod)%glancePeriod;
  const amplitude=.65+phase*.35;
  const breathingPeriod=4.2+phase*1.7;
  const breath=(t+phase*breathingPeriod)%breathingPeriod;
  return {
    lookLeft:pulse(glance,2,1.2,1.1,1.8)*amplitude,
    lookRight:pulse(glance,11.5,1.4,.8,1.6)*amplitude,
    breathe:pulse(breath,0,breathingPeriod*.39,0,breathingPeriod*.61),
  };
}
