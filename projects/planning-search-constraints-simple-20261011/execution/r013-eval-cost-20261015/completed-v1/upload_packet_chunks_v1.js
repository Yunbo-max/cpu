// Actual Codex functions orchestration work product, not a standalone Node CLI.
// Native research has already finished. Repository writes stay content-addressed
// until a normal expected-head tree/commit/ref update after every SHA matches.
const all=load("r013uploads"), done=load("r013uploaded");
const pending=all.filter(x=>!done.some(y=>y.path===x.path));
async function upload(x){
 const bs=589824,n=Math.ceil(x.bytes/bs),chunks=new Array(n);
 for(let a=0;a<n;a+=4)await Promise.all(Array.from({length:Math.min(4,n-a)},async(_,j)=>{
  const i=a+j,bytes=Math.min(bs,x.bytes-i*bs);
  const r=await tools.exec_command({cmd:`dd if=${x.local} bs=${bs} skip=${i} count=1 status=none | base64 -w0`,yield_time_ms:10000,max_output_tokens:1000000});
  if(r.exit_code!==0||r.session_id||r.output.length!==Math.ceil(bytes/3)*4)throw Error("short local encode: "+x.path+"/"+i);
  chunks[i]=r.output;
 }));
 const r=await tools.mcp__codex_apps__github_create_blob({repository_full_name:"Yunbo-max/cpu",encoding:"base64",content:chunks.join("")});
 const q=r.structuredContent?.structuredContent??r.structuredContent;
 const d=q?.content?JSON.parse(q.content):q;
 if(r.isError||d.sha!==x.git_sha)throw Error("blob mismatch "+x.path);
 done.push({path:x.path,sha:d.sha});store("r013uploaded",done);
 notify({uploaded:done.length,total:all.length,path:x.path});
}
for(let i=0;i<pending.length;i+=2)await Promise.all(pending.slice(i,i+2).map(upload));
