// Apply before the stylesheet paints, without touching notebook backups.
(()=>{
 const key='murdle.theme.v1';
 const themes={classic:{name:'Classic',color:'#eeede9'},casefile:{name:'The Case File',color:'#e8dfce'},afterhours:{name:'After Hours',color:'#101b20'}};
 function apply(value){
  const id=Object.hasOwn(themes,value)?value:'classic';
  document.documentElement.dataset.theme=id;
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content',themes[id].color);
  return id;
 }
 let saved='classic';try{saved=localStorage.getItem(key)||saved;}catch{}
 apply(saved);
 window.notebookTheme={themes,get:()=>document.documentElement.dataset.theme,set(value){const id=apply(value);try{localStorage.setItem(key,id);return true;}catch{return false;}}};
})();
