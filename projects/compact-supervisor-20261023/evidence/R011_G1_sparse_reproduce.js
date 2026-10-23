#!/usr/bin/env node
// Reproducer for the exact integer-capacity one-edge-failure probe.
// External input pins: bstabler/TransportationNetworks@d1639b4ef218c17928ba573e806ddf8ba5e7ae6d
// Files: SiouxFalls_net.tntp (git blob 66d0eca4ddcfb82f861bea040060deab7a741b2f)
//        SiouxFalls_trips.tntp (git blob db70eda57738877811e9ac07c25a567973d3b6a0)
// Usage: node R011_G1_sparse_reproduce.js SiouxFalls_net.tntp SiouxFalls_trips.tntp
// This is an equivalent standalone reproduction, not the exact JS wrapper previously executed.
const fs=require('fs'),crypto=require('crypto');
function readChecked(file,sha){
 const data=fs.readFileSync(file);
 const actual=crypto.createHash('sha1').update(Buffer.from('blob '+data.length+'\0'.replace('\0','\0'))).update(data).digest('hex');
 if(actual!==sha)throw Error('Git blob mismatch '+file+' '+actual);
 return data.toString('utf8');
}
function main(netText,tripsText){
 const raw=netText.split(/\r?\n/).filter(x=>/^\s*\d+\s+\d+\s+\d/.test(x)).map(x=>x.trim().split(/\s+/));
 const d=Math.max(...raw.map(x=>(x[2].split('.')[1]||'').length)),scale=10**d;
 function capacity(t){let [a,b='']=t.split('.');let v=Number(a)*scale+Number(b.padEnd(d,'0'));if(!Number.isSafeInteger(v))throw Error('unsafe capacity');return v;}
 const edges=raw.map(x=>[+x[0],+x[1],capacity(x[2])]);
 const capsum=edges.reduce((s,e)=>s+e[2],0);if(!Number.isSafeInteger(capsum))throw Error('unsafe total');
 const chunks=tripsText.split(/Origin\s+(\d+)/),pairs=[];
 for(let i=1;i<chunks.length;i+=2){const s=+chunks[i];for(let m of chunks[i+1].matchAll(/(\d+)\s*:\s*([\d.]+)\s*;/g)){const t=+m[1],v=+m[2];if(s!==t&&v>0)pairs.push({s,t,demand:v})}}
 pairs.sort((a,b)=>b.demand-a.demand||a.s-b.s||a.t-b.t);
 let unique=[],seen=new Set();
 for(let p of pairs){let key=Math.min(p.s,p.t)+':'+Math.max(p.s,p.t);if(!seen.has(key)){seen.add(key);unique.push(p)}if(unique.length===5)break}
 function flow(src,dst,deleted){
  let g=Array.from({length:25},()=>[]);
  function add(u,v,c){g[u].push({to:v,c,rev:g[v].length});g[v].push({to:u,c:0,rev:g[u].length-1});}
  edges.forEach(([u,v,c],i)=>{if(i!==deleted)add(u,v,c)});
  let total=0;
  while(true){
   let lev=Array(25).fill(-1),queue=[src];lev[src]=0;
   for(let i=0;i<queue.length;i++)for(const e of g[queue[i]])if(e.c>0&&lev[e.to]<0){lev[e.to]=lev[queue[i]]+1;queue.push(e.to)}
   if(lev[dst]<0)break;
   let it=Array(25).fill(0);
   function dfs(u,rem){
    if(u===dst)return rem;
    for(;it[u]<g[u].length;it[u]++){let e=g[u][it[u]];if(e.c===0||lev[e.to]!==lev[u]+1)continue;
     let t=dfs(e.to,Math.min(rem,e.c));if(t>0){e.c-=t;g[e.to][e.rev].c+=t;return t}}
    return 0;
   }
   while(true){let sent=dfs(src,capsum);if(sent===0)break;total+=sent}
  }
  return total;
 }
 const rows=unique.map(p=>{const base=flow(p.s,p.t,-1);const drops=edges.map((e,i)=>base-flow(p.s,p.t,i));
 if(drops.some(x=>x<0))throw Error('flow rose upon edge deletion');
 const vital=drops.map((x,i)=>x>0?i:-1).filter(i=>i>=0);
 return {s:p.s,t:p.t,od_demand:p.demand,baseline_flow:base/scale,
 vital_count:vital.length,unchanged_edges:edges.length-vital.length,
 mean_drop_uniform:drops.reduce((a,b)=>a+b,0)/edges.length/scale,
 max_drop:Math.max(...drops)/scale,
 exact_sparse_response_bits:64+7+vital.length*(7+64),full_response_table_bits:edges.length*64,
 vital_edge_indices_0based:vital};
 });
 return {note:'UNOBSERVED failure distribution; uniform single-edge deletion is a synthetic query protocol',
 dataset_pin:'bstabler/TransportationNetworks@d1639b4ef218c17928ba573e806ddf8ba5e7ae6d',
 n_nodes:24,n_edges:edges.length,positive_od_pairs:pairs.length,
 selection:'top five OD demand-ranked unordered-distinct source/sink pairs',
 num_maxflow_calls:unique.length*(edges.length+1),scale,rows};
}
if(process.argv.length!==4)throw Error('Expected two pinned TNTP local files');
const net=readChecked(process.argv[2],'66d0eca4ddcfb82f861bea040060deab7a741b2f');
const trips=readChecked(process.argv[3],'db70eda57738877811e9ac07c25a567973d3b6a0');
console.log(JSON.stringify(main(net,trips),null,2));
