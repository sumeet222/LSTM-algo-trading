 // Saved-price components are later-known diagnostic quantities, never model inputs.
 const cp=v.components||{},present=cp.decomposition_supported;
 if(present){
  const keys=['origin_to_close','close_to_next_open','next_open_to_exit'];
  plot('components',keys.map(key=>({type:'histogram',name:key,x:ix.flatMap(i=>D.symbols.map((_,j)=>present[i*20+j][0]?cp[key][i*20+j][0]:null)).filter(x=>x!==null),opacity:.5})),{title:'Realized log-return components: supported overnight rows only',barmode:'overlay',xaxis:{title:'Price-only log return, not executable P&L'}});
  const slots=[...new Set(ix.map(i=>v.wall[i].slice(11,16)))].sort();
  plot('componentCoverage',[{type:'bar',x:slots,y:slots.map(s=>{let q=ix.filter(i=>v.wall[i].slice(11,16)===s&&v.category[i]==='OVERNIGHT');return q.length?q.reduce((a,i)=>a+present.slice(i*20,i*20+20).filter(x=>x[0]).length,0)/(q.length*20):null;})}],{title:'Observed decomposition fraction: missing close/open is not zero gap',yaxis:{range:[0,1]}});
 }else{empty('components','Source-component table unavailable in this rehearsal snapshot');empty('componentCoverage','No fabricated close/open decomposition');}
 const slots=[...new Set(ix.map(i=>v.wall[i].slice(11,16)))].sort();
 plot('slotHeat',[{type:'heatmap',x:slots,y:D.symbols,z:D.symbols.map((_,j)=>slots.map(s=>{let a=ix.filter(i=>v.wall[i].slice(11,16)===s);return a.reduce((z,i)=>z+Math.abs(v.pred[i][j]-v.truth[i][j]),0)/a.length;})),colorscale:'Blues'}],{title:'Stock × slot absolute display-rank error; selected date/category'});
 const months=[...new Set(ix.map(i=>v.days[i].slice(0,7)))].sort(),cats=['INTRADAY','OVERNIGHT'];
 plot('categoryHeat',[{type:'heatmap',x:months,y:cats,z:cats.map(c=>months.map(m=>{let ids=ix.filter(i=>v.category[i]===c&&v.days[i].startsWith(m));let ds={};for(let i of ids){let x=v.origins_metrics[i].ic;if(x!==null)(ds[v.days[i]]??=[]).push(x);}let vals=Object.values(ds).map(a=>a.reduce((s,x)=>s+x,0)/a.length);return vals.length?vals.reduce((s,x)=>s+x,0)/vals.length:null;})),zmid:0,colorscale:'RdBu'}],{title:'Month × category: equal-session Rank IC'});
 plot('offLoss',[{x:cal.map(r=>r.epoch),y:cal.map(r=>r.inner_train_off?.actual_objective),name:'Complete inner train OFF',mode:'lines+markers'},{x:cal.map(r=>r.epoch),y:cal.map(r=>r.inner_validation_off?.actual_objective),name:'Complete validation OFF',mode:'lines+markers'},{x:ref.map(r=>r.epoch),y:ref.map(r=>r.refit_off?.actual_objective),name:'Complete refit OFF',mode:'lines+markers'}],{title:arm+' deterministic full-population objective (separate from online ON)'});
 const gr=ep.filter(r=>r.gradient);
 plot('gradient',['preclip_max','postclip_max','clipped_fraction','update_mean'].map(key=>({x:gr.map(r=>r.phase+':'+r.epoch),y:gr.map(r=>r.gradient[key]),name:key,mode:'lines+markers'})),{title:'Gradient, clipping and update trace; numerical units labeled by series'});

 const years=['2021','2022','2023','2024'],arms=['NR','T2R'];
 plot('healthMatrix',[{type:'heatmap',x:years,y:arms,z:arms.map(a=>years.map(y=>{let v=D.data[y+'|'+a];if(!v)return null;let e=D.epochs.filter(r=>r.run_id===v.run&&r.phase==='refit');return e.length?Math.max(...e.map(r=>r.epoch)):null;})),colorscale:'Blues'}],{title:'All eight lifecycles: fresh-refit epoch count (untrained rehearsal =1)'});
 plot('roleMatrix',['inner_train','inner_validation','refit','oos'].map(role=>({type:'scatter',mode:'markers',name:role,x:D.metrics.filter(r=>['NR','T2R'].includes(r.model)&&r.role===role).map(r=>r.year+' '+r.model),y:D.metrics.filter(r=>['NR','T2R'].includes(r.model)&&r.role===role).map(r=>r.daily_ic)})),{title:'All eight models × four roles: daily Rank IC; OOS never selects epochs',xaxis:{type:'category'}});
