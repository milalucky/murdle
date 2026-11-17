import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(new URL('../theme.js',import.meta.url),'utf8');
function boot(saved,blocked=false){
 const values=new Map([['murdle.theme.v1',saved],['murdle.notebook.v1','existing progress']]);
 const root={dataset:{}},meta={setAttribute(k,v){this[k]=v;}};
 const context={document:{documentElement:root,querySelector:()=>meta},window:{},localStorage:{getItem:k=>{if(blocked)throw Error('blocked');return values.get(k);},setItem:(k,v)=>{if(blocked)throw Error('blocked');values.set(k,v);}}};
 vm.runInNewContext(source,context);return{api:context.window.notebookTheme,values,root,meta};
}
test('themes restore before paint and never modify saved cases',()=>{
 for(const id of ['classic','casefile','afterhours']){const x=boot(id);assert.equal(x.root.dataset.theme,id);assert.equal(x.meta.content,x.api.themes[id].color);assert.equal(x.api.set('afterhours'),true);assert.equal(x.values.get('murdle.theme.v1'),'afterhours');assert.equal(x.values.get('murdle.notebook.v1'),'existing progress');}
});
test('invalid and blocked preferences fall back safely while allowing a session theme',()=>{
 assert.equal(boot('unknown').api.get(),'classic');assert.equal(boot('__proto__').api.get(),'classic');
 const x=boot(null,true);assert.equal(x.api.get(),'classic');assert.equal(x.api.set('afterhours'),false);assert.equal(x.api.get(),'afterhours');
});
