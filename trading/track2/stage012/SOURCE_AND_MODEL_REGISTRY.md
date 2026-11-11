# Source and model registry

Original bundle paths, folds, SHA256 and C3 association: `original_bundles.json`. Read-only reference/code identities, bytes and mtimes: `audits/source_identity_before.json`. All4 are original executed C-A, own original O1 restricted FT16 recipe and own C3; Phase2 is never used for inference.

Independent Phase2 identities remain in `replication/phase2/PHASE2_FROZEN_MANIFEST.json` (recipes under artifacts/, checkpoints under its frozen namespace). It is an independent modeling-layer replication with inherited preprocessing, not original. Phase3 evidence manifest and source register are bound in our audit. COP mask-before-floor and additional Phase2 Q2 guard prevent mixing.

Historical source locations and differing price bases are described in DATA_AVAILABILITY_CONTRACT.2024-01 exact paths exist; no new source values were read. The prior trading proposal was not found in the bounded repository filename search; current authorization supplies the superseding decisions. No missing checkpoint or recipe was observed. Missing causal original feature-snapshot producer is T2-001. Phase3 full original native tensors were not archived/comparable. No substitute bundle used.

Static project import closure and external import names: `audits/dependency_inventory.json` (AST only, no workflow invocation).

| Independent Phase2 archive path | SHA256 from frozen manifest |
|---|---|
| replication/phase2/artifacts/F21_refit_recipe.json | e7f78b4708e638b2c0b0c10132d3d5ba85c1a5a12ebcebd5d3b493da65ed972a |
| replication/phase2/artifacts/F22_refit_recipe.json | c852509f70dbf847cc5d97fcb6967b2b7f1041a4cfc60ae2d45691a3e4447c18 |
| replication/phase2/artifacts/F23_refit_recipe.json | 4f454977ba7d085d1e6d6422c016cea9fab7e39133c03293a71b198d512b7f24 |
| replication/phase2/artifacts/F24_refit_recipe.json | d42b4b4160f18f7864068babea00ced85dd8a99e0862d36301b282929577546b |
| replication/phase2/artifacts/run/F21/initial/final_state.pt | 61c9ebeac459fa8ef8bcdce51905c36b9f203a00be4912f548314e63cbd8b4ff |
| replication/phase2/artifacts/run/F21/initial/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F21/initial/selected_state.pt | d42b669ab1778673098bc6d02a7212b658115b54424e5999b624d08430f98571 |
| replication/phase2/artifacts/run/F21/refit/final_state.pt | 1c1853257cc22d3a6469f4efe71a2750ed1ca1a1a68bdb1a9aaa186542fffb44 |
| replication/phase2/artifacts/run/F21/refit/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F21/refit/latest_refit_state.pt | 41f245d4cba68191c3e810013b0d1ae425376a62397108b29dfac8ce50901377 |
| replication/phase2/artifacts/run/F22/initial/final_state.pt | ef1cef745fe65112367382f1e8befb9ab92baa119d7edf42b50d8af92ef0abf6 |
| replication/phase2/artifacts/run/F22/initial/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F22/initial/selected_state.pt | 68e9c8848326cc0218a253889ed10fc77e2d366a6307e1dc25ce8fadfeced847 |
| replication/phase2/artifacts/run/F22/refit/final_state.pt | be827599417abdb3d79b6e3261734f9fb26278c603169df4a97164fe968f514b |
| replication/phase2/artifacts/run/F22/refit/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F22/refit/latest_refit_state.pt | 594438431cf027ad1218641ec20975fd1ce5542166200b46b98b07c5e547814e |
| replication/phase2/artifacts/run/F23/initial/final_state.pt | ad85e9760d5ca71f171739376658674ffe4079da6140b9d702d5e51eedda245e |
| replication/phase2/artifacts/run/F23/initial/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F23/initial/selected_state.pt | 823a81375a343d28c8ea9796ee52d87c45e94c78554a491f9778bc4ae476fdb6 |
| replication/phase2/artifacts/run/F23/refit/final_state.pt | a834f988c1a52479a5fe3abca0129a74a7e6e989b854e1e7a0cbc57b52c806d5 |
| replication/phase2/artifacts/run/F23/refit/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F23/refit/latest_refit_state.pt | c814f9420502b1b16e3e02dee8aaeeee059c161a5a0778680503090dad227b9a |
| replication/phase2/artifacts/run/F24/initial/final_state.pt | bce4c97165ca940292b1776c4d6f01f7b91b7a0cfd54aac9e4425351f4f941f5 |
| replication/phase2/artifacts/run/F24/initial/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F24/initial/selected_state.pt | a16f6f785423415d31d03536c643ee22f3084596dd39afb0cbc68289a96b0602 |
| replication/phase2/artifacts/run/F24/refit/final_state.pt | 4f055a94e43dea78c3465b51e6e992975747ca099d74f8979fbe8fde9616289e |
| replication/phase2/artifacts/run/F24/refit/initial_state.pt | 77fc2fb21457ff705031a789884a8d8d56764297f247c322d3ff5562d807b411 |
| replication/phase2/artifacts/run/F24/refit/latest_refit_state.pt | 40e89d22102deb798b455b3b69c530bbf200d8e2850c4686286e77f14caa3944 |

Bound source-policy and numerical-read receipt hashes: `audits/historical_source_contract_refs.json`. These identify prior permitted source reads; no data partitions were scanned again.
