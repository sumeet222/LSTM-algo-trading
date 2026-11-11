# Single metadata exception audit

UTC: 2026-11-03T12:37:23.826421+00:00.

The user authorized only the hash mismatch of `replication/phase2/.DS_Store`. The original manifest and failed gate/witness remain intact. All other **232** frozen files match, with no additional missing or extra Phase2 files. All **348** admitted pre-2025 files freshly match bytes and hashes; path/month/family identities reconcile against the frozen manifest, input manifest and postrun immutability receipt. Coverage is exactly 174 monthly files per family from 2010-07 through 2024-12.

No substantive scientific dependency on `.DS_Store` was found in the bounded code/configuration and recorded-event inspection. Scientific readers use literal admitted source paths or named Phase2 geometry artifacts. None of the 39 provenance receipts records `.DS_Store` access or a module origin referring to it. The freeze utility inventories every file via `PHASE.rglob`, so inclusion in an audit inventory does not imply use as a feature, label, model or calibration input. This conclusion is procedural and code-inferred, not an OS-level guarantee.

Three distinct identities are retained:

- Manifest expected: `9aac4a413b64844a3421cc8559c0945311e9b54362c9935fde6a5e7464bde046`.
- Original failed gate observed: `77ef9beb43df6065b818ee38da6557d23e082637bad735bc6e32c55099181b9a`.
- Continuation observed: `40e05edea1150c86288110905314a29852e327bf188df5a0d9413c52fc2a7c70`.

Each is 6,148 bytes. The reviewer did not write this file. Its further change between observations is disclosed; cause and timing are not established. We do **not** claim the full 233-file freeze or this metadata file remained unchanged across sessions.

The hash checks alone do not authorize unsealing. An independently confirmed **additional provenance gap** is recorded in `QUALIFIED_SEAL_GATE.json` and `.md`; it is outside the metadata exception. Original results remain sealed.
