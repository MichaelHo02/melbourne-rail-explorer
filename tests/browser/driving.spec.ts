import { test,expect } from '@playwright/test';

test('loads Melbourne and drives with real input through braking, pause, and camera changes',async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto('/');
  const start=page.getByRole('button',{name:'Take the driver’s seat'});
  await expect(start).toBeEnabled({timeout:60000});
  await expect(page.locator('#viewport canvas')).toHaveAttribute('data-renderer-backend',/^(WebGPU|WebGL2)$/);
  await page.screenshot({path:'artifacts/01-city-menu.png'});
  await start.click();
  await expect(page.locator('#driving-hud')).toBeVisible();
  await page.keyboard.press('w');await page.waitForTimeout(500);
  expect(await page.evaluate(()=>(window as any).__RAIL_EXPLORER__.state().speed)).toBe(0);
  await page.keyboard.press('d');await page.keyboard.press('w');await page.keyboard.press('w');
  await expect.poll(()=>page.evaluate(()=>(window as any).__RAIL_EXPLORER__.state().speed)).toBeGreaterThan(.5);
  await page.screenshot({path:'artifacts/02-cab-departure.png'});
  await page.keyboard.press('c');await page.waitForTimeout(350);await page.screenshot({path:'artifacts/03-exterior.png'});
  await page.keyboard.press('Escape');const paused=await page.evaluate(()=>(window as any).__RAIL_EXPLORER__.state());
  await page.waitForTimeout(250);expect(await page.evaluate(()=>(window as any).__RAIL_EXPLORER__.state().distance)).toBe(paused.distance);
  await page.getByRole('button',{name:'Back to the cab'}).click();
  await page.keyboard.press('Space');
  await expect.poll(()=>page.evaluate(()=>(window as any).__RAIL_EXPLORER__.state().speed),{timeout:15000}).toBe(0);
  await page.keyboard.press('c');
  await page.evaluate(()=>(window as any).__RAIL_EXPLORER__.scenario('tunnel'));
  await page.waitForTimeout(1000);await page.screenshot({path:'artifacts/04-tunnel.png'});
  await page.keyboard.press('m');await expect(page.getByRole('img',{name:'City Loop route with five station stops'})).toBeVisible();
  await page.screenshot({path:'artifacts/05-map.png'});
  await page.getByRole('button',{name:'Close panel'}).click();
  await page.evaluate(()=>(window as any).__RAIL_EXPLORER__.scenario('platform'));
  await expect(page.locator('#station-instruction')).toHaveText('Open doors');
  await page.keyboard.press('d');await expect(page.locator('#doors-label')).toContainText('Boarding');
  await page.screenshot({path:'artifacts/08-underground-platform.png'});
  await expect(page.locator('#doors-label')).toHaveText('Close doors',{timeout:12000});
  await page.keyboard.press('d');await expect(page.locator('#station-name')).toHaveText('Parliament');
  await page.keyboard.press('Escape');await page.reload();
  await expect(page.getByRole('button',{name:'Continue saved service'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Take the driver’s seat'})).toBeEnabled({timeout:60000});
  await page.getByRole('button',{name:'Continue saved service'}).click();await expect(page.locator('#driving-hud')).toBeVisible();
  console.log('RENDER_METRICS',await page.evaluate(()=>(window as any).__RAIL_EXPLORER__.metrics()));
  expect(errors).toEqual([]);
});

test('WebGPU renderer can use its WebGL2 compatibility backend',async({page})=>{
  const errors:string[]=[];
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto('/?renderer=webgl&scene=platform');
  await expect(page.locator('#driving-hud')).toBeVisible({timeout:60000});
  await expect(page.locator('#viewport canvas')).toHaveAttribute('data-renderer-backend','WebGL2');
  await page.keyboard.press('d');
  await expect(page.locator('#doors-label')).toContainText('Boarding');
  await expect.poll(()=>page.evaluate(()=>(window as any).__RAIL_EXPLORER__.metrics().drawCalls)).toBeGreaterThan(0);
  await page.screenshot({path:'artifacts/webgl-compatibility.png'});
  expect(errors).toEqual([]);
});

test('narrow browser remains usable',async({page})=>{
  await page.setViewportSize({width:600,height:850});await page.goto('/');
  await expect(page.getByRole('button',{name:'Take the driver’s seat'})).toBeEnabled({timeout:60000});
  await page.screenshot({path:'artifacts/06-narrow-menu.png'});
  await page.getByRole('button',{name:'Take the driver’s seat'}).click();
  await expect(page.locator('#driving-hud')).toBeVisible();
  await expect(page.locator('#welcome')).toBeHidden();
  await page.screenshot({path:'artifacts/07-narrow-cab.png'});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBe(600);
});
