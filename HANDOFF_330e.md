# Handoff: F30 330e work — instructions for the next Claude Code session

You are picking up work started in a cloud session. Read this file fully, then `AgentReadMe.md`,
`source/docs/PORTING.md` and `source/docs/SIGNALS.md`. Branch: `main-eq0933` (same content as `main`
at commit `c35afc3` plus this file).

## The owner and the car

- F30 **330e**, B46/B48-family 2.0 petrol + e-motor, plug-in hybrid. Stock tune: **no MHD+, no Bootmod3,
  no xDrive Control, no HUD Gauges.** Do not install or enable any of those.
- Owner is an engineer. Metric units, terse answers, label facts vs estimates vs opinions, give
  confidence levels, never invent DIDs, scalings or citations. Reply in the language they write in.
- Corporate Windows PC without admin rights may be the ENET machine — use `py -3`, no installs that need admin.

## Hard rules

1. **Read-only on the car.** Car parked, ignition on / iDrive awake. Only `01` and `22` reads via
   `source/tools/probe_signals.py` (it enforces this). No `2E`, `31`, `14` (clear), coding or flashing.
   The "Read all modules" button only reads; clearing stays engine-only.
2. Do not write decoders or a battery page from guesses. Every new DID needs: address, request,
   full response, test conditions, and an independent reading (ISTA/ESYS/dash value) to confirm scaling.
3. No model identifiers in commit messages, code or docs. (Commit `c35afc3` contains a
   `Co-Authored-By: Claude Haiku 5.5` line — leave it unless the owner asks to rewrite `main`.)
4. Commit to `main-eq0933`; don't push to `main` or force-push without the owner's say-so.

## State of the code

Done and pushed:
- `probe_signals.py` accepts `--ecu 07` (SME, HV battery), `3A` / `1A` (EME, e-motor), plus `12` DME, `18` EGS.
- Engine Fault Codes → **Read all modules**: one functional request to `DF`, 25 s timeout, falls back to a
  per-address sweep, names from `source/native/src/ecu_names.h`.
- Host tests (`make -C source/native test`): all pass except
  `test_transport.py::test_fast_channels_and_staggered_slow_updates` (~258/s vs limit 215).
  It fails identically on the commit before the fault-code work, so it is pre-existing / environment timing.
  Re-run it on a normal Linux/macOS box; if it still fails there, investigate separately.

Not done (blocked on car data):
- Battery / hybrid page.
- Coolant decode (`gauge_core.c:39`, DID `0x4300`): this DME returns 2 bytes and the existing K/10 decode
  matches OBD `0105` at two points (41.05 vs 41 °C, 83.55 vs 83 °C, 2026-11-17). Decoder needs no change;
  fixtures added to `native/tests/test_core.c` and noted in SIGNALS.md (not yet compiled: no C compiler on
  the owner's Windows PC — run `make -C source/native test` on Linux/macOS).
- Rail pressure (`gauge_core.c:37`, DID `0x56D7`, /50 bar) — answers (47.6 and 180.6 bar at RPM 0 by /50);
  scaling unconfirmed, needs an ISTA reading.
- Oil pressure (`586F`) read 0.946 bar twice with the engine off — possibly absolute, unconfirmed.
- Ethanol request removed from `plugin.cpp` and `collector.c` (it was `2C 88 01`, MHD-only, not a `22` read).
- Units default / timing decode — check against owner preference (metric) and real data.

Car facts found 2026-11-17: gateway 169.254.39.69 (not 169.254.21.3), EME at `3A` (`1A` times out).

Install status (2026-11-18, nothing installed yet):
- Head unit SSH at 169.254.199.99, OpenSSH 5.2 QNX, RSA host key only (needs `HostKeyAlgorithms=+ssh-rsa`).
  Login is root + password held by the unlock tool (bavarian-ssh-client); no key on the PC is accepted.
  The tool needs internet and ENET at the same time; "No such host is known" means the PC had no DNS.
- `packages/dashboard.zip` (built at b240814) BoostDeck still sends `2C 88 01` on every page open and every
  30 s. Don't install it unchanged. Owner chose to patch the single `--ethanol` string in
  `BoostDeck/libBoostDeck.so` (file offset 0x4aec) to the same-length `--session` (6 bytes change; sha256
  9119468d… → 33376c67ab000c134f97a95b81541e328cc78100f8ef81694ec8f55641c0555a). Patch only the plugin,
  never the collector. The patched set (BoostDeck, ShiftDeck, EngineCodes + gateway-ip.txt) is staged on the
  owner's PC outside the repo. Readback must be checked against the staged hash list, not the package's.
  Read-only reviews of the binaries found: the string has one reference (argv[4] of the only spawn); the
  packaged collector accepts a repeated `--session` and then sends only the eight DME `22` reads, `22 DA12` to
  EGS 0x18, and the MOST wrapper. `--session` is a loopback lease lock, not UDS `10 xx`. The packaged collector
  was built with `NATIVE_FAST` (35 ms loop tick).
- Packaged EngineCodes predates "Read all modules"; packaged ShiftDeck sends only `01 0C` / `01 0D`.
- All three workers fall back to the head unit's MOST tunnel (`31 01 0F0B` wrapper around the read) after
  failed HSFZ connects, so `gateway-ip.txt` = 169.254.39.69 must be in each app folder. The owner accepted
  this fallback for the packaged install (2026-11-19). Removing it needs a rebuild.

## Step 1 — probe the car (owner runs, you interpret)

Owner connects ENET cable. Find the PC's link-local address (`ipconfig`, 169.254.x.x) and the gateway
(reference build uses `169.254.21.3`; confirm). Then, from `source/`:

```
py -3 tools/probe_signals.py --local <PC_IP> --gateway <GW_IP> --ecu 12 22f150 224300 2256d7 22586f
py -3 tools/probe_signals.py --local <PC_IP> --gateway <GW_IP> --ecu 07 22ddbc 22ddc0 22ddb4 22dd69 22dfa0 22dfa9 22dd7b
py -3 tools/probe_signals.py --local <PC_IP> --gateway <GW_IP> --ecu 3a 22dea6
py -3 tools/probe_signals.py --local <PC_IP> --gateway <GW_IP> --ecu 1a 22dea6
```

Max 12 requests per call. Output is one JSON line per request (`data`, or `nrc`, or `error`).
Save all output to a file with the conditions (SoC on dash, ambient/coolant temp, engine running or not).

What each tells you:
- `22F150` on 0x12: DME software/variant → decides which SGBD (and thus coolant/rail decoding) applies.
- SME 0x07 DIDs: candidates from research against BMW SGBD `SME_F15` (F-series PHEV), **not verified on an F30 330e**.
  `DDB4` = pack voltage (confirmed on-car only on a G05 45e). `DFA0` = cell voltages, /10000 V, offsets 6/8/10.
  Meanings of the others must be established from the SGBD + response length + independent reading.
- EME: whichever of 0x3A / 0x1A answers is the address (research says 0x3A for F-series). `DEA6` = e-motor temps.
- NRC `31` = DID not supported; `22` = conditions not correct (try with ignition fully on / READY); timeout on
  a whole address = wrong address.

## Step 2 — fix decoders

For each confirmed DID: update `source/native/src/gauge_core.c` / `collector.c`, add a de-identified
positive fixture and an invalid-length fixture under `source/native/tests/`, update `SIGNALS.md`, run
`make -C source/native test` and `python3 source/tools/test_probe_signals.py`.

## Step 3 — battery page (only after Step 1 data)

Read-only page over HSFZ (SME/EME don't answer through the MOST tunnel). Show only values with confirmed
scaling. No redline figure is known for this engine; don't invent one.

## Step 4 — build and install

Needs QNX SDP 6.5 host tools (ARM GCC 4.4.2) on Linux and the two private framework libs pulled from the
owner's head unit (`libAppFramework.A.so`, `libCoreFramework.A.so`, verify hashes per `AgentReadMe.md`).
Build with `source/native/build.sh` (`NBTEVO_FRAMEWORKS_DIR` points to the libs). Install per
`AgentReadMe.md` → "Stage and verify": back up existing plugins outside `Plugins`, verify bytes after upload,
restart iDrive while parked. Do not include MhdMaps / Bootmod3Suite / XDriveControl / HUD packages.
