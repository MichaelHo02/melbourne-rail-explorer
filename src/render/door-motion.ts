/** Door leaves follow service time, so pause/save inspection cannot advance them. */
export class DoorMotion {
  private time?:number;
  private distance?:number;
  amount=0;
  sample(seconds:number,distance:number,open:boolean,complete=false){
    const target=open?1:0;
    const reset=this.time===undefined||seconds<this.time||Math.abs(distance-(this.distance??distance))>100;
    // Completion stops the simulation clock on the same tick as final closure.
    if(reset||complete)this.amount=target;
    else this.amount+=(target-this.amount)*(1-Math.exp(-5*Math.max(0,seconds-this.time!)));
    this.time=seconds;this.distance=distance;
    return this.amount;
  }
}
