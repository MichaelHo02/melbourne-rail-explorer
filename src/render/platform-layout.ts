/** Authored platform coping clearances, checked against the moving GLB hull.
 * Curved Southern Cross/Parliament platforms retain more corner-swing space. */
export function platformInboardShift(code:string){
  return code==='SXS'?.22:code==='PAR'?.17:code==='FSS'?.34:.36;
}
