import {describe,it,expect} from 'vitest';
import {positionAt,tangentAt} from '../src/data/route';
import {conflictsWithRunningLine} from '../src/render/photomesh-clearance';
function box(distance:number,offset=0){
 const p=positionAt(distance),t=tangentAt(distance),x=p.x+t.z*offset,z=p.z-t.x*offset;
 return {ring:[[x-1,z-1],[x+1,z-1],[x+1,z+1],[x-1,z+1]],base:0,height:30};
}
describe('train swept clearance against surveyed scenery',()=>{
 it('rejects buildings in each reported interstation surface corridor',()=>{
  for(const distance of [640,1740,5200])expect(conflictsWithRunningLine(box(distance))).toBe(true);
 });
 it('retains buildings beside the route and over deep tunnels',()=>{
  expect(conflictsWithRunningLine(box(640,30))).toBe(false);
  expect(conflictsWithRunningLine(box(3000))).toBe(false);
 });
 it('keeps thin bridge decks with enough overhead clearance and rejects low decks',()=>{
  const b=box(640),y=positionAt(640).y;
  expect(conflictsWithRunningLine({...b,kind:'Bridge',height:y+7})).toBe(false);
  expect(conflictsWithRunningLine({...b,kind:'Bridge',height:y+3})).toBe(true);
 });
});
