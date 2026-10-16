# Proposed HF20 amendment v2

SHA256 `bfc0eac3b504a9ae428e365e96fd9043bb1c43eedbff661310c42f3dac511c77`; full proposal `configs/hf20_hourly_native_v2.json`.

Only daily-close validity and disclosed retention acceptance change. Use a genuine previous regular session15:30 last-full-hour close even if an earlier hour is missing. Daily volume still needs all6full hours; no reconstructed/imputed price or volume, no repairs. All16formulas,48scheduled steps,20names, chronology, target, source, clock, held-out lock and rights restrictions remain. Version FT1 as V2.

Original actual training822/1154=71.2305%; development366/382=95.8115%. Source-key/validity-mask diagnostic predicts training998/1154=86.4818% (499sessions) and unchanged development366/382 (183sessions). Inner training expected872/1028=84.8249%; inner validation110/126 over55sessions. Actual values must be rebuilt and verified after approval.

Proposed acceptance: fulltrain>=85%, innertrain>=84%, development>=90%and>=100sessions, inner tail>=50sessions and>=25origins/type. Preserve the original failed90% training verdict. This is a research-design amendment requiring live approval under package§7.2; no fitting is authorized.
