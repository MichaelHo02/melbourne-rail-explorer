/** Scene-only drag controls. No pointer lock, global key handlers or simulation actions. */
export class CameraDragInput {
  private enabled=false;
  private pointer:number|null=null;
  private x=0;private y=0;
  private ownerWindow:Window|null;
  get dragging(){return this.pointer!==null;}
  constructor(private canvas:HTMLCanvasElement,private onDrag:(xFraction:number,yFraction:number)=>void,private onReset:()=>void){
    this.ownerWindow=canvas.ownerDocument?.defaultView??null;this.ownerWindow?.addEventListener('blur',this.blur);
    canvas.style.touchAction='none';
    canvas.addEventListener('pointerdown',this.down);
    canvas.addEventListener('pointermove',this.move);
    canvas.addEventListener('pointerup',this.end);
    canvas.addEventListener('pointercancel',this.end);
    canvas.addEventListener('lostpointercapture',this.end);
    canvas.addEventListener('dblclick',this.reset);
  }
  setEnabled(enabled:boolean){
    this.enabled=enabled;
    if(!enabled)this.cancel();
    this.canvas.style.cursor=enabled?(this.dragging?'grabbing':'grab'):'default';
    this.canvas.dataset.cameraInput=enabled?'enabled':'disabled';
  }
  cancel(){
    const pointer=this.pointer;this.pointer=null;
    if(pointer!==null&&this.canvas.hasPointerCapture(pointer))this.canvas.releasePointerCapture(pointer);
    this.canvas.style.cursor=this.enabled?'grab':'default';
  }
  private blur=()=>this.cancel();
  private down=(event:PointerEvent)=>{
    if(!this.enabled||event.button!==0||!event.isPrimary||this.pointer!==null)return;
    event.preventDefault();this.pointer=event.pointerId;this.x=event.clientX;this.y=event.clientY;
    this.canvas.setPointerCapture(event.pointerId);this.canvas.style.cursor='grabbing';
  };
  private move=(event:PointerEvent)=>{
    if(!this.enabled||this.pointer!==event.pointerId)return;
    if(event.pointerType==='mouse'&&(event.buttons&1)===0){this.cancel();return;}
    const bounds=this.canvas.getBoundingClientRect();
    if(bounds.width>0&&bounds.height>0)this.onDrag((event.clientX-this.x)/bounds.width,(event.clientY-this.y)/bounds.height);
    this.x=event.clientX;this.y=event.clientY;event.preventDefault();
  };
  private end=(event:PointerEvent)=>{if(event.pointerId===this.pointer)this.cancel();};
  private reset=(event:MouseEvent)=>{if(!this.enabled||event.button!==0)return;event.preventDefault();this.cancel();this.onReset();};
  dispose(){
    this.cancel();this.canvas.removeEventListener('pointerdown',this.down);this.canvas.removeEventListener('pointermove',this.move);
    this.canvas.removeEventListener('pointerup',this.end);this.canvas.removeEventListener('pointercancel',this.end);
    this.canvas.removeEventListener('lostpointercapture',this.end);this.canvas.removeEventListener('dblclick',this.reset);
    this.ownerWindow?.removeEventListener('blur',this.blur);
    this.canvas.style.cursor='default';this.canvas.style.touchAction='';
  }
}
