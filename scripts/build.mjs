import {cp,mkdir,rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=new URL('../',import.meta.url),out=new URL('../dist/',import.meta.url);
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
for(const name of ['index.html','design-concepts.html','app.js','theme.js','core.js','style.css','favicon.svg','data','assets','.nojekyll'])await cp(new URL(name,root),new URL(name,out),{recursive:true});
console.log('GitHub Pages files: '+fileURLToPath(out));
