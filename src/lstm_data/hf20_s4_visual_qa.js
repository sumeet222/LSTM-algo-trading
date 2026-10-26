if(new URLSearchParams(location.search).has('qa')){
 setTimeout(async()=>{
 const results=[];
 try {
 const keys=Object.keys(D.data).filter(k=>['NR','T2R'].includes(k.split('|')[1]));
 if(!keys.length)throw Error('NO_NEURAL_VIEW');
 for(const key of keys){
  const [year,arm]=key.split('|');$('year').value=year;$('model').value=arm;
  $('category').value='ALL';resetDates();$('full').click();
  const v=D.data[key];
  for(const category of ['ALL','OPENING','OLD_MORNING','AFTERNOON','INTRADAY','OVERNIGHT']){
   $('category').value=category;update();
   const n=v.days.filter((_,i)=>categoryMatch(v,i)).length;
   if(!window.__rankViewStatus.ready||window.__rankViewStatus.origins!==n)throw Error('CATEGORY_COUNT_'+key+'_'+category);
   if($('predHeat').data[0].z.length!==20)throw Error('HEATMAP_20_STOCKS');
   if($('trajectory').layout.yaxis.range[0]!==20.5)throw Error('RANK_DIRECTION');
   results.push({key,category,origins:n,status:'PASS'});
   await new Promise(r=>setTimeout(r,40));
  }
  for(const role of ['inner_train','inner_validation','refit','oos']){
   $('role').value=role;update();
   if(!$('roleMetrics').textContent.includes(role))throw Error('ROLE_MISSING_'+role);
  }
 }
 const [year,arm]=keys[0].split('|');$('year').value=year;$('model').value=arm;
 $('category').value='ALL';$('role').value='oos';resetDates();
 $('stocks').options[1].selected=true;update();
 if(window.__rankViewStatus.stocks.length!==2)throw Error('MULTISTOCK');
 $('stocks').options[1].selected=false;update();
 const e=document.createElement('pre');e.id='qa-result';e.textContent=JSON.stringify({status:'PASS',cases:results});document.body.appendChild(e);
 }catch(error){const e=document.createElement('pre');e.id='qa-result';e.textContent=JSON.stringify({status:'FAIL',error:String(error),cases:results});document.body.appendChild(e);}
 },200);
}
