# Frozen inference integration

Original model loaded: all four annual `restricted_final.pt`, exactly6572 parameters, original ComponentMAG constructor, eval(), requires_grad_(False), torch.inference_mode(), fresh stock/window forward without recurrent state. Only main forward result is decoded by original hf20_mag_c3_io.decode; training auxiliary layer weights are present but never used for alpha. No optimizer, seed helper, fit, calibration fit or preflight invoked.

`original_bundles.json` binds checkpoint, original O1 restricted recipe, original C-A C3 coefficients and phase receipt by SHA256. Registry validates stock order, original path association, recipe cutoff, C3 scale and legal ET year. IDs are SHA256; F24 cannot predict2021. Identical predictions on synthetic tensors are determinism witnesses, not historical forecast parity.

Historical integration PARTIAL: original `hf20_mag_designa.source_components` constructs historical M2 through signed return arrays and reads saved endpoint/role data. `View` requires r and evaluation rows. It was deliberately not invoked. Original complete native/scaled tensor archive was NOT_COMPARABLE in Phase3. A causal input-only snapshot producer with independently reviewed matured M2 lineage remains required; no Phase2 replacement was used. This is HISTORICAL_SNAPSHOT_BOUNDARY_NOT_IMPLEMENTED, not ORIGINAL_BUNDLE_NOT_LOADABLE. No real-key forecast parity or real-data dry-run is claimed.

Dependency inventory: standard Python dataclasses/json/hashlib/datetime/zoneinfo, installed numpy/pandas/torch/exchange_calendars, original hf20_s4_clock sessions/endpoint, hf20_s2c_ca.ComponentMAG and hf20_mag_c3_io.decode plus their existing transitive imports. No dependency installation/change.
