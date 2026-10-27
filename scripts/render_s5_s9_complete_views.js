
async function supplementary(v,rows){
 const xs=rows.map(r=>r.origin_id), mean=(a)=>a.reduce((s,x)=>s+x,0)/a.length;
 const rolling=(a)=>a.map((_,i)=>mean(a.slice(Math.max(0,i-19),i+1)));
 let scatter=[],error=[],curves=[],st='',et='',rt='';
 if(v.arm==='META-T2R'){
  scatter=[{x:rows.map(r=>r.prediction_rank),y:rows.map(r=>r.actual_rank),mode:'markers',name:'Rank 1 = best'}];
  error=[{x:rows.map(r=>r.prediction_rank),y:rows.map(r=>r.prediction_rank-r.actual_rank),mode:'markers',name:'Predicted minus realized rank'}];
  curves=[line(xs,rolling(rows.map(r=>Math.abs(r.prediction_rank-r.actual_rank))),'Absolute rank error')];
  st='Visible ticker: predicted versus later-known realized rank';et='Visible ticker: signed rank error versus predicted rank';rt='Visible ticker: trailing up-to-20-observation absolute rank error';
 }else if(v.arm==='MAG'){
  scatter=[{x:rows.map(r=>r.prediction_A),y:rows.map(r=>Math.abs(r.return_4h)),mode:'markers',name:'Forecast versus observed |R|'}];
  error=[{x:rows.map(r=>r.prediction_A),y:rows.map(r=>Math.abs(r.return_4h)-r.prediction_A),mode:'markers',name:'Observed minus forecast |R|'}];
  curves=[line(xs,rolling(rows.map(r=>r.actual_loss)),'Actual transformed MSE')];
  st='Visible ticker: forecast |R| (x) versus realized |R| (y)';et='Visible ticker: raw-magnitude residual (y) versus forecast (x)';rt='Visible ticker: trailing up-to-20-observation log1p-target MSE';
 }else if(v.arm==='EVENT'){
  scatter=[{x:rows.filter(r=>r.event_class===1).map(r=>r.p_ANY),type:'histogram',name:'Observed ordinary',opacity:.65},{x:rows.filter(r=>r.event_class!==1).map(r=>r.p_ANY),type:'histogram',name:'Observed ANY-tail',opacity:.65}];
  const b=rows.map(r=>((r.event_class===1?0:1)-r.p_ANY)**2);
  error=[{x:rows.map(r=>r.p_ANY),y:b,mode:'markers',name:'ANY Brier row error'}];curves=[line(xs,rolling(b),'ANY Brier, not optimized 3-class CE')];
  st='Visible ticker probability histogram: observation counts, not weighted prevalence';et='Visible ticker: ANY Brier error (y) versus probability (x)';rt='Visible ticker: trailing up-to-20-observation ANY Brier';
 }else{
  scatter=[{x:rows.map(r=>r.quantiles_y_95-r.quantiles_y_05),y:rows.map(r=>Math.abs(r.TG20-r.quantiles_y_50)),mode:'markers',name:'Width versus deviation, original TG20 units'}];
  error=[{x:xs,y:rows.map(r=>r.TG20<r.quantiles_y_05?1:0),mode:'markers',name:'Below 5% quantile'},{x:xs,y:rows.map(r=>r.TG20>r.quantiles_y_95?1:0),mode:'markers',name:'Above 95% quantile'}];
  for(const [q,a] of [['05',.05],['50',.5],['95',.95]]){curves.push(line(xs,rolling(rows.map(r=>r.TG20<=r['quantiles_y_'+q]?1:0)),q+'% empirical'));curves.push(line(xs,rows.map(()=>a),q+'% nominal',{line:{dash:'dot'}}))}
  st='Visible ticker: interval width (x) versus absolute median deviation (y), TG20';et='Visible ticker: lower/upper interval misses, observed outcomes only';rt='Visible ticker: trailing up-to-20-observation coverage; partial initial windows';
 }
 await plot('diagnostic_scatter',scatter,st,{barmode:'overlay'});
 await plot('diagnostic_error',error,et);
 await plot('diagnostic_rolling',curves,rt);
}
