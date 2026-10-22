const SOURCE='https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/on-street-parking-bay-sensors/exports/json';
let cached,expires=0,inflight;
async function parking(){
  if(cached&&Date.now()<expires)return cached;
  if(inflight)return inflight;
  inflight=(async()=>{
    const response=await fetch(SOURCE,{signal:AbortSignal.timeout(20000)});
    if(!response.ok)throw new Error('Parking source unavailable');
    const raw=await response.json();if(!Array.isArray(raw))throw new Error('Invalid parking response');
    const results=raw.filter(b=>b.location&&b.location.lon>=144.949&&b.location.lon<=144.981&&b.location.lat>=-37.825&&b.location.lat<=-37.805).map(b=>({kerbsideid:b.kerbsideid,location:b.location,status_description:b.status_description,lastupdated:b.lastupdated,status_timestamp:b.status_timestamp}));
    cached={mode:'observed',source:SOURCE,fetchedAt:new Date().toISOString(),results};expires=Date.now()+60000;return cached;
  })().finally(()=>{inflight=undefined;});
  return inflight;
}
export async function feedMiddleware(req,res,next){
  if(req.url?.split('?')[0]!=='/api/parking'){next();return;}
  res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');
  try{res.end(JSON.stringify(await parking()));}
  catch{res.statusCode=503;res.end(JSON.stringify({error:'Parking source unavailable; no current readings claimed'}));}
}
