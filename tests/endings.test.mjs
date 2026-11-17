import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name+'.json',import.meta.url),'utf8'));
test('every official case has a sourced English ending without solution table contamination',()=>{
 for(const book of ['volume1','skulls']){
  const endings=read(book+'-endings'),cases=read(book).cases;
  assert.equal(Object.keys(endings).length,cases.length);
  for(const c of cases){
   const e=endings[c.displayId||String(c.id)];assert.ok(e,c.id);
   assert.equal(e.language,'en');assert.ok(e.text.length>100);
   assert.ok(e.sourcePages.length&&e.sourcePages.every(n=>Number.isInteger(n)&&n>0));
   assert.ok(!/KARBER|MURDLE:|\bADVENTURE\b| [|] /.test(e.text),`${book}:${c.id}`);
   assert.ok(!/^(?:\d|the corn maze|crew cabin|Land!)/.test(e.text),`${book}:${c.id}`);
  }
 }
});
test('cross-page endings include their final narrative and omit following answer tables',()=>{
 const v=read('volume1-endings'),s=read('skulls-endings');
 assert.match(v['100'].text,/at least until Volume 2/);
 assert.match(v['68'].text,/Perhaps even the one behind it all!/);
 assert.doesNotMatch(v['68'].text,/lunar rover|Raspberry/);
 assert.match(s['8.8'].text,/Hopefully, everyone else would enjoy solving them/);
 assert.match(s['3.5'].text,/small boat back to their big boat/);
 assert.match(s['7.3'].text,/Haha, you think you’ve stopped us/);
 assert.match(s['1.5'].transcriptionNote,/covered by a finger/);
});
