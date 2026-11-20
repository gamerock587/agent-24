function renderModelActivity(value){
 const activity=value.model_activity||[];
 for(const [id,name] of [['qwen','Qwen'],['d1','Liquid']]){
  const calls=activity.filter(c=>c.model.startsWith(name)),running=calls.find(c=>c.status==='running'),recent=calls.find(c=>c.status==='completed'&&Date.now()/1000-c.finished<2);
  const row=document.getElementById(id+'-model-row'),label=document.getElementById(id+'-activity');
  row.classList.toggle('model-working',Boolean(running));row.classList.toggle('model-just-finished',!running&&Boolean(recent));
  label.textContent=running?'Working · '+running.purpose+' · '+Math.max(0,Math.floor(Date.now()/1000-running.created))+'s':recent?'Reply received · '+(recent.finished-recent.created).toFixed(1)+'s':value.models?.[id]?.ready?'Ready · waiting for a task':'Unavailable';
 }
 document.getElementById('model-status').textContent=activity.some(c=>c.status==='running')?'AI working':value.models?.qwen?.ready&&value.models?.d1?.ready?'Connected':'Check services';
}
(()=>{
 const node=id=>document.getElementById(id),panel=node('ai-chat-panel'),feed=node('ai-chat-feed');
 let filter='all',signature='',loading=false,wire=null,wireStatus='',contextId=null,pending=false,before=null,oldest=null;
 let modelFilter=localStorage.getItem('agent24-chat-model')||'all';
 if(!['all','qwen','liquid'].includes(modelFilter))modelFilter='all';
 const text=(tag,value,cls)=>{const e=document.createElement(tag);e.textContent=value;if(cls)e.className=cls;return e};
 function toggle(open){panel.hidden=!open;node('ai-chat-launcher').setAttribute('aria-expanded',String(open));if(open)refreshChat()}
 node('ai-chat-launcher').onclick=()=>toggle(panel.hidden);node('ai-chat-close').onclick=()=>toggle(false);
 document.querySelectorAll('[data-chat-filter]').forEach(b=>b.onclick=()=>{filter=b.dataset.chatFilter;document.querySelectorAll('[data-chat-filter]').forEach(x=>x.classList.toggle('active',x===b));wire=null;node('ai-chat-wire').hidden=true;feed.hidden=false;signature='';refreshChat()});
 document.querySelectorAll('[data-model-filter]').forEach(b=>{
  b.classList.toggle('active',b.dataset.modelFilter===modelFilter);b.setAttribute('aria-pressed',String(b.dataset.modelFilter===modelFilter));
  b.onclick=()=>{modelFilter=b.dataset.modelFilter;localStorage.setItem('agent24-chat-model',modelFilter);before=null;signature='';wire=null;node('ai-chat-wire').hidden=true;feed.hidden=false;
   document.querySelectorAll('[data-model-filter]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b))});refreshChat()};
 });
 function messageText(value){
  const body=text('div','','ai-readable-text');
  // Format a small safe subset of Markdown using text nodes only.
  for(const part of String(value||'').split(/(```[\s\S]*?```|\*\*[^*]+\*\*|`[^`\n]+`)/g)){
   if(part.startsWith('```'))body.append(text('pre',part.replace(/^```\w*\n?/, '').replace(/```$/, '')));
   else if(part.startsWith('**')&&part.endsWith('**'))body.append(text('strong',part.slice(2,-2)));
   else if(part.startsWith('`')&&part.endsWith('`'))body.append(text('code',part.slice(1,-1)));
   else body.append(document.createTextNode(part));
  }return body;
 }
 function readable(value){
  if(typeof value==='string'){try{return JSON.stringify(JSON.parse(value),null,2)}catch{return value}}
  return JSON.stringify(value,null,2);
 }
 async function showWire(id,direction){
  wire={id,direction};feed.hidden=true;node('ai-chat-wire').hidden=false;node('ai-chat-wire-content').textContent='Loading actual model exchange…';
  await updateWire();
 }
 async function updateWire(){
  if(!wire)return;const chosen={...wire};try{const v=await api('/model-turns/'+chosen.id);if(!wire||wire.id!==chosen.id||wire.direction!==chosen.direction)return;
   node('ai-chat-wire-title').textContent=v.model+' · '+chosen.direction;
   let value=v[chosen.direction];
   if(chosen.direction==='input'&&value){value={...value};if(typeof value.input==='string'){try{value.input=JSON.parse(value.input)}catch{}}}
   if(chosen.direction==='output'&&value?.body){try{value={...value,body:JSON.parse(value.body)}}catch{}}
   node('ai-chat-wire-content').textContent=value===null?'Waiting for the model response…':readable(value);wireStatus=v.status;
  }catch(e){node('ai-chat-wire-content').textContent=e.message}
 }
 node('ai-chat-back').onclick=()=>{wire=null;node('ai-chat-wire').hidden=true;feed.hidden=false};
 node('ai-chat-older').onclick=()=>{before=oldest;filter='models';document.querySelectorAll('[data-chat-filter]').forEach(b=>b.classList.toggle('active',b.dataset.chatFilter===filter));wire=null;node('ai-chat-wire').hidden=true;feed.hidden=false;signature='';refreshChat()};
 node('ai-chat-latest').onclick=()=>{before=null;signature='';refreshChat()};
 function render(data){
  const atBottom=feed.scrollHeight-feed.scrollTop-feed.clientHeight<55,oldScroll=feed.scrollTop;feed.replaceChildren();
  const rows=[...(filter==='models'||modelFilter==='liquid'?[]:data.messages.map(m=>({...m,type:'message'}))),...(filter==='chat'?[]:data.turns.filter(t=>filter==='models'||t.purpose!=='live-chat').map(t=>({...t,type:'turn'})))].sort((a,b)=>a.created-b.created);
  if(!rows.length)feed.append(text('p',filter==='chat'?'Ask Qwen about this assessment. Replies and model calls are saved locally.':'Waiting for a model call. Calls made before this update were not recorded.','ai-chat-empty'));
  for(const row of rows){
   const item=text('article','',row.type==='message'?'ai-chat-message '+row.role:'ai-model-call '+row.status),head=document.createElement('header');
   head.append(text('strong',row.type==='message'?(row.role==='user'?'You':row.role==='error'?'Connection error':'Qwen'):row.model),text('span',new Date(row.created*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'})));item.append(head);
   if(row.type==='message')item.append(messageText(row.content));
   else{
    item.append(text('p',row.purpose+' · '+row.status+(row.finished?' · '+(row.finished-row.created).toFixed(1)+'s':'')));
    const sent=text('section','','ai-exchange sent');sent.append(text('h4','Sent to '+row.model));
    for(const block of row.readable?.sent||[]){
     if(block.label==='Instructions'||block.collapsed){const instructions=document.createElement('details');instructions.append(text('summary',block.label==='Instructions'?'System instructions':block.label),messageText(block.text));sent.append(instructions)}
     else{sent.append(text('small',block.label),messageText(block.text))}
    }
    const received=text('section','','ai-exchange received');received.append(text('h4','Received from '+row.model),messageText(row.readable?.received||(row.status==='running'?'Waiting for the reply…':'No text response recorded.')));
    item.append(sent,received);
    const technical=document.createElement('details');technical.className='ai-technical';technical.append(text('summary','Technical details'));
    for(const direction of ['input','output']){const b=text('button',direction==='input'?'Raw request':'Raw response');b.type='button';b.onclick=()=>showWire(row.id,direction);technical.append(b)}item.append(technical);
   }feed.append(item);
  }
  if(node('ai-chat-follow').checked&&(atBottom||oldScroll===0))feed.scrollTop=feed.scrollHeight;else feed.scrollTop=oldScroll;
 }
 async function refreshChat(){
  if(loading||typeof selected==='undefined'||!selected||!token){node('ai-chat-send').disabled=true;return}
  if(panel.hidden)return;loading=true;const ident=selected;
  if(contextId!==ident){contextId=ident;before=null;wire=null;signature='';node('ai-chat-wire').hidden=true;feed.hidden=false}
  try{const params=new URLSearchParams();if(before)params.set('before',before);if(modelFilter!=='all')params.set('model',modelFilter);const requestedFilter=modelFilter;const data=await api('/runs/'+ident+'/chat?'+params);if(selected!==ident||requestedFilter!==modelFilter)return;
   oldest=data.turns[0]?.created;node('ai-chat-older').disabled=!data.has_older;node('ai-chat-latest').hidden=!before;node('ai-chat-page').textContent=before?'Earlier calls':'Latest calls';
   node('ai-chat-target').textContent=data.target;node('ai-chat-count').textContent=data.turns.length;
   const running=data.turns.some(t=>t.status==='running'),last=data.messages[data.messages.length-1];pending=last?.role==='user';
   node('ai-chat-status').textContent=running?'Model working':pending?'Reply queued':'Live';node('ai-chat-send').disabled=pending;
   if(!pending)node('ai-chat-help').textContent='Live call updates · full replies appear when each call finishes.';
   const next=JSON.stringify([data.messages,data.turns,filter,modelFilter]);if(signature!==next){signature=next;render(data)}
   if(wire&&wireStatus==='running')await updateWire();
  }catch(e){node('ai-chat-status').textContent='Reconnecting';node('ai-chat-help').textContent=e.message}
  finally{loading=false}
 }
 node('ai-chat-form').onsubmit=async e=>{e.preventDefault();const content=node('ai-chat-input').value.trim();if(!content||!selected||pending)return;
  node('ai-chat-send').disabled=true;try{await api('/runs/'+selected+'/chat',{method:'POST',body:JSON.stringify({content})});node('ai-chat-input').value='';pending=true;node('ai-chat-help').textContent='Message saved. Waiting for Qwen…';await refreshChat()}catch(error){node('ai-chat-help').textContent=error.message;node('ai-chat-send').disabled=false}
 };
 node('ai-chat-input').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();node('ai-chat-form').requestSubmit()}};
 setInterval(refreshChat,1000);refreshChat();
})();
