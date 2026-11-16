import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {freshState,validateBackup} from '../core.js';
test('new notebooks require onboarding and have no personal default name',()=>{const s=freshState();assert.equal(s.onboarded,false);assert.equal(s.profiles[0].name,'Detective');assert.equal(validateBackup(s),s);});
test('all interface copy and book category labels are English',()=>{for(const name of ['app.js','core.js','index.html','README.md'])assert.ok(!/[А-Яа-яЁё]/.test(readFileSync(new URL('../'+name,import.meta.url),'utf8')),name);for(const book of ['volume1','skulls']){const d=JSON.parse(readFileSync(new URL('../data/'+book+'.json',import.meta.url)));for(const c of d.cases)for(const cat of c.categories)assert.ok(!/[А-Яа-яЁё]/.test(cat.label));}});
