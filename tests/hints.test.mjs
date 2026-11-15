import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=name=>JSON.parse(readFileSync(new URL(`../data/${name}.json`,import.meta.url)));
test('every case in both books has its own English book hint',()=>{
 for(const book of ['volume1','skulls']){
  const cases=read(book).cases,hints=read(book+'-hints');assert.equal(Object.keys(hints).length,cases.length);
  for(const c of cases){const h=hints[c.displayId||String(c.id)];assert.ok(h.text.length>30);assert.equal(h.language,'en');assert.ok(h.sourcePages.length);assert.ok(!/SOLUTIONS|ADVENTURE|KARBER/.test(h.text));}
 }
});
test('hints split across scanned pages are complete and solutions are excluded',()=>{
 const v=read('volume1-hints'),s=read('skulls-hints');
 assert.match(v['7'].text,/deacon had the shears/);assert.match(v['15'].text,/self-defense/);assert.match(v['86'].text,/General Coffee/);
 assert.match(s['4.2'].text,/cool red banner/);assert.match(s['5.3'].text,/yet another maze/);assert.match(s['6.4'].text,/volumetric flask/);
 assert.match(s['8.8'].text,/learned a lot along the way/);assert.ok(!s['8.8'].text.includes('Mayor Honey'));
});
