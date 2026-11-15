import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {correctAnswer,freshCase,freshState,validateBackup,markCell,pairs} from '../core.js';
const book=JSON.parse(readFileSync(new URL('../data/skulls.json',import.meta.url)));
test('Seven Skulls has all 64 printed case numbers, assets and complete solution bijections',()=>{
 assert.equal(book.cases.length,64);
 for(const [i,c] of book.cases.entries()){
  assert.equal(c.id,i+1);assert.equal(c.displayId,`${Math.floor(i/8)+1}.${i%8+1}`);
  assert.ok([3,4].includes(c.size));assert.ok([3,4].includes(c.categories.length));
  assert.equal(c.assignments.length,c.size);assert.equal(c.assignmentsVerification,'reviewed');
  assert.equal(correctAnswer(c,c.solution),true);assert.equal(correctAnswer(c,{...c.solution,suspects:(c.solution.suspects+1)%c.size}),false);
  assert.ok(c.assignments.some(a=>Object.entries(c.solution).every(([k,v])=>a[k]===v)));
  for(const cat of c.categories){
   assert.equal(cat.items.length,c.size);assert.equal(new Set(cat.items.map(x=>x.label)).size,c.size);
   assert.deepEqual(c.assignments.map(a=>a[cat.id]).sort(),Array.from({length:c.size},(_,j)=>j));
   for(const item of cat.items){assert.ok(existsSync(new URL('../'+item.icon,import.meta.url)));const svg=readFileSync(new URL('../'+item.icon,import.meta.url),'utf8');assert.ok(svg.includes('<path'));assert.ok(!svg.includes('<image'));}
  }
  assert.ok(pairs(c.categories).length===3||pairs(c.categories).length===6);
 }
});
test('card order differences and special categories retain their grid meanings',()=>{
 const get=id=>book.cases.find(c=>c.displayId===id), labels=(id,cat)=>get(id).categories.find(c=>c.id===cat).items.map(x=>x.label);
 assert.deepEqual(labels('3.5','weapons'),['The Skull of Rewe','A Fishing Net','A Brass Telescope','A Distress Beacon']);
 assert.deepEqual(labels('3.8','weapons'),['A Coconut','A Chunk of Ice','The Skull of Rewe','A Crab']);
 assert.deepEqual(labels('7.7','motives'),['Flaxo','Smazo','Bloon','Katop']);
 assert.deepEqual(labels('8.7','motives'),['Flarnbarg','Gogobell','Meow','Please']);
 assert.equal(labels('5.8','motives')[0],'The grand opening of an amusement park');
 assert.equal(get('1.8').size,3);assert.equal(get('1.8').categories.length,4);
 assert.equal(get('8.2').size,4);assert.equal(get('8.2').categories.length,3);
 assert.equal(get('6.1').categories.find(c=>c.id==='motives').question,'And?');
 assert.equal(get('2.8').categories.find(c=>c.id==='weapons').label,'Explanations');
});
test('backup preserves and validates the archived manual template',()=>{
 const s=freshState(),r=freshCase(),old=freshCase();old.size=4;old.categoryCount=4;old.labels['weapons:0']='My first weapon';markCell(old,'weapons-suspects:0:0');old.answers.suspects=3;old.notes='Keep this';
 r.bookEdition='skulls-2026';r.legacyTemplate=old;s.profiles[0].cases['skulls:1']=r;
 assert.deepEqual(validateBackup(JSON.parse(JSON.stringify(s))),s);
 r.legacyTemplate.marks.bad=1;assert.throws(()=>validateBackup(s));delete r.legacyTemplate.marks.bad;
 r.legacyTemplate.legacyTemplate=freshCase();assert.throws(()=>validateBackup(s));
});
