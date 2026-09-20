import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../artifacts/pov-survey/',import.meta.url));
export function povCapturePlugin(){return {
 name:'local-pov-survey',apply:'serve',
 configureServer(server){server.middlewares.use('/__pov_capture',async(req,res)=>{
  if(req.method!=='POST'){res.statusCode=405;res.end();return;}
  // Same-origin, loopback-only development artifact writer. No arbitrary paths.
  if(!['127.0.0.1','::1','::ffff:127.0.0.1'].includes(req.socket.remoteAddress)||req.headers.origin!==`http://${req.headers.host}`){res.statusCode=403;res.end();return;}
  try{
   let body='',bytes=0;for await(const chunk of req){bytes+=chunk.length;if(bytes>4_000_000)throw Error('Capture exceeds 4MB');body+=chunk;}
   const p=JSON.parse(body);
   if(!/^[a-z0-9-]{1,48}$/.test(p.run)||!Number.isInteger(p.distance)||p.distance<0||p.distance>6000||typeof p.png!=='string')throw Error('Invalid capture identity');
   const png=Buffer.from(p.png,'base64');if(!png.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))throw Error('Expected PNG');
   const folder=`${root}${p.run}/`,stem=String(p.distance).padStart(5,'0');await mkdir(folder,{recursive:true});
   await writeFile(`${folder}${stem}.png`,png,{flag:'wx'});
   await writeFile(`${folder}${stem}.json`,JSON.stringify({distance:p.distance,camera:p.camera,metrics:p.metrics,frameMs:p.frameMs},null,2),{flag:'wx'});
   res.setHeader('Content-Type','application/json');res.end(JSON.stringify({saved:`artifacts/pov-survey/${p.run}/${stem}.png`}));
  }catch(error){res.statusCode=400;res.end(String(error));}
 });},
};}
