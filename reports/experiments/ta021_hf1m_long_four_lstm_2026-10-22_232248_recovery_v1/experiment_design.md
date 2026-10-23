# Package021 export-repair continuation proposal

Exact proposal SHA256: `c556d5b93e5389e40f063a669e706d2014db4ca6eed558d593f910b586c27cfe`.
Execution SHA256: `95ec1c58f8c7f5b4a73803f3fe7a9795c3c9dee4ffc8fcbe3722566296e985a5`.
Original approved proposal: `5b6cfd698f6fc741e42be799642f5f447bbe6b11e8c0fc06b34ab0bd6fe31803`.

The original C0/42 start33 ran12 calibration epochs (1,896optimizer steps), selected epoch1,
and saved checkpoint `44dd1b45b910a716b59826b2139b6b3ecda84bf0965831a1458ec7fa0299b895`.
Prediction export then failed because pandas reindex/reset_index dropped the ticker level name.
The original FAILED_AFTER_START event remains immutable. There was no refit or further start.

The fixed exporter names both MultiIndex levels explicitly. Zero-step export recovered all
88,560inner-training and15,320inner-validation rows, with exact source targets and named keys.
The numerical model, objective, loader, recipes and selection rule are unchanged.

Requested continuation: reload the saved selected C0/42 calibration checkpoint without any
calibration replay, seed fresh42 weights/optimizer, complete exactly the already-selected
one refit epoch (187steps), and save/audit the four permitted phase/partition predictions.
Then run the original three unstarted combinations T2/42 → C0/123 → T2/123, unchanged D6g.
Keep the original failure; append RESUMED_EXISTING_START at33 and only three new STARTED events
33→34→35→36/200 in a linked successor journal. There is no refunded or additional start.
The seed42 pair must pass independent audit before seed123 begins. No further retry is granted.

Limitation: all12 calibration epoch summaries, including pre/postclip distributions and step
counts, survived; in-memory per-batch calibration rows did not. Do not replay fitting to invent
those missing rows. Refit and the three remaining runs will preserve their available telemetry.

The earlier exact execution hash has changed, and Package021 forbids silently retrying after
an error. A separate live response is therefore required for this concrete continuation.
Until then no optimization or additional model start is permitted. Source/input contract,
20stocks, partitions, CPU4 threads, private-use rights/clock assumptions and24h deadline remain
as in the original proposal (expires 2026-10-24T03:29:05.960964+00:00). No2026 numerics/trading/Git operations.
