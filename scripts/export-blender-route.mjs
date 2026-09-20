// Rebuild the clearance ribbon input from the same route used by the game.
import {build} from 'esbuild';
import {writeFileSync} from 'node:fs';
await build({entryPoints:['src/data/route.ts'],bundle:true,platform:'node',format:'esm',outfile:'/tmp/city-loop-route.mjs'});
const {positionAt,ROUTE_LENGTH}=await import('/tmp/city-loop-route.mjs');
writeFileSync('/tmp/city-loop-clearance-route.json',JSON.stringify(Array.from({length:Math.ceil(ROUTE_LENGTH/2)},(_,i)=>({distance:i*2,...positionAt(i*2)}))));
