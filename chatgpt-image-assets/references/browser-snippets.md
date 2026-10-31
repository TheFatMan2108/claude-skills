# Browser snippets (javascript_tool, chatgpt.com tab)

Each `javascript_exec` call is cut off at 45 s, so every loop stops at about 38 s. Swap the stop-button label for the UI language: `Ngừng` (vi) or `Stop` (en).

## Wait for the current generation

Run twice in a row after sending; returns `busy:false` once the reply is done.

```js
const busy=()=>!!document.querySelector('button[aria-label="Ngừng"]');
const t0=Date.now();
while(Date.now()-t0<38000 && busy()) await new Promise(r=>setTimeout(r,2000));
({busy: busy(), tail: document.querySelector('main').innerText.slice(-250)})
```

## Check the newest image: size and real transparency

```js
const imgs=[...document.querySelectorAll('main img')].filter(i=>i.naturalWidth>400);
const im=imgs[imgs.length-1]; im.scrollIntoView({block:'center'});
const bm=await createImageBitmap(await (await fetch(im.src)).blob());
const c=new OffscreenCanvas(bm.width,bm.height), x=c.getContext('2d'); x.drawImage(bm,0,0);
const d=x.getImageData(0,0,bm.width,bm.height).data; let t=0,n=0;
for(let k=3;k<d.length;k+=4*37){n++; if(d[k]<10)t++;}
({w:bm.width, h:bm.height, transparentPct:Math.round(t/n*100)})
```

## Count items per row of a transparent sheet

Splits the sheet into rows at fully transparent horizontal bands, then counts separate opaque segments per row. An icon made of separate strokes (such as vibrate waves) counts as more than one item, so confirm odd counts with a screenshot.

```js
const imgs=[...document.querySelectorAll('main img')].filter(i=>i.naturalWidth>400);
const bm=await createImageBitmap(await (await fetch(imgs[imgs.length-1].src)).blob());
const c=new OffscreenCanvas(bm.width,bm.height), x=c.getContext('2d'); x.drawImage(bm,0,0);
const W=bm.width,H=bm.height;
const opaqueRow=y=>{const d=x.getImageData(0,y,W,1).data; for(let i=3;i<d.length;i+=4) if(d[i]>40) return true; return false;};
const rows=[]; let s=-1;
for(let y=0;y<=H;y++){const o=y<H&&opaqueRow(y); if(o&&s<0)s=y; if(!o&&s>=0){ if(y-s>8) rows.push([s,y]); s=-1; }}
rows.map(([a,b])=>{const d=x.getImageData(0,a,W,b-a).data, col=new Array(W).fill(0);
  for(let yy=0;yy<b-a;yy++) for(let xx=0;xx<W;xx++) if(d[(yy*W+xx)*4+3]>40) col[xx]=1;
  let cnt=0,p=0; for(const v of col){ if(v&&!p)cnt++; p=v; } return {y:[a,b], items:cnt};})
```

## Download every tagged image

Set `want` to the tags to save. Keep `window.__got` between calls so a second call only fetches what is still missing. To save the final sprite sheet under a variant tag (such as `00c`), list that tag, not `00`.

```js
window.__tagOf = im => { const w=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);
  w.currentNode=im; let n; while((n=w.previousNode())){ const t=n.textContent.trim();
    const m=t.match(/^Tag (\d+[a-z]?) -/); if(m) return m[1];
    if(t.startsWith('You are the UI artist')) return '00'; } return null; };
let sc=document.querySelector('main img');
while(sc && !(sc.scrollHeight>sc.clientHeight+50 && /auto|scroll/.test(getComputedStyle(sc).overflowY))) sc=sc.parentElement;
window.__got = window.__got || {};
const want=['00c','01','02','03','04','05','06','07','08','09','10','11','12'];
if(!window.__started){ sc.scrollTop=0; window.__started=1; await new Promise(r=>setTimeout(r,1500)); }
const t0=Date.now();
while(Date.now()-t0<36000){
  for(const im of [...document.querySelectorAll('main img')].filter(i=>i.naturalWidth>400)){
    const tag=__tagOf(im); if(!tag||!want.includes(tag)||__got[tag]) continue;
    const b=await (await fetch(im.src)).blob(); const a=document.createElement('a');
    a.href=URL.createObjectURL(b); a.download='chatgpt-tag-'+tag+'.png';
    document.body.appendChild(a); a.click(); a.remove(); __got[tag]=b.size;
    await new Promise(r=>setTimeout(r,800)); }
  if(want.every(t=>__got[t]) || sc.scrollTop+sc.clientHeight>=sc.scrollHeight-5) break;
  sc.scrollTop+=sc.clientHeight*0.6; await new Promise(r=>setTimeout(r,900)); }
({got: __got, missing: want.filter(t=>!__got[t])})
```
