import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {feedMiddleware} from './feeds.mjs';
const root=path.resolve('dist'),mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.glb':'model/gltf-binary','.png':'image/png','.jpg':'image/jpeg','.hdr':'application/octet-stream'};
const server=http.createServer((req,res)=>feedMiddleware(req,res,()=>{
  let name;try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400).end();return;}
  const file=path.resolve(root,'.'+(name==='/'?'/index.html':name));
  if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
  fs.stat(file,(error,stat)=>{if(error||!stat.isFile()){res.writeHead(404).end('Not found');return;}res.setHeader('Content-Type',mime[path.extname(file)]??'application/octet-stream');fs.createReadStream(file).pipe(res);});
}));
server.listen(Number(process.env.PORT)||5173,'127.0.0.1',()=>console.log('Melbourne City Observatory: http://127.0.0.1:'+server.address().port));
