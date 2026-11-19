# F30 330e NBT EVO app install — status 2026-11-19

**Result: not installed. Blocked at head-unit login.** Nothing has been written to the head unit.

Read `HANDOFF_330e.md` and `AgentReadMe.md` first. This file is the install state only.

## Checked and OK

| Check | Result |
| --- | --- |
| Branch `main-eq0933` | Clean before this file. No changes since 2026-11-19 07:39. |
| Staged install set (first PC, outside the repo) | All 18 files match the hash list below. |
| BoostDeck patch | `libBoostDeck.so` sha256 `33376c67…c0555a` (`--ethanol` → `--session`). |
| `gateway-ip.txt` (×3) | `169.254.39.69` in BoostDeck, ShiftDeck, EngineCodes. |
| PC ENET adapter | 169.254.45.57/16 on the first PC. Another PC gets its own link-local address. |
| Gateway 169.254.39.69 | Ping OK (0–1 ms). |
| Head unit 169.254.199.99 | Ping OK. SSH banner `OpenSSH_5.2 QNX_Secure_Shell-20090621-hpn13v6`. |
| Head-unit host key | RSA 2048 `SHA256:ccBSjAKu0zGcw8z2GuJpODkfbHkHFg+6hJRdU9HjB2Q`, same as the key pinned on 2026-11-18. |

## Install set

- Install: **BoostDeck** (patched), **ShiftDeck**, **EngineCodes**.
- Left out (stock tune): MhdMaps, Bootmod3Suite, XDriveControl, HUD Gauges.
- All three workers still contain the MOST fallback (`31 01 0F0B` wrapper), used only if HSFZ fails. The owner accepted this on 2026-11-19.
- EngineCodes has a manual two-step Clear (`14 FF FF FF`).

## Blocker

Login: root@169.254.199.99, password only, host key pinned.

```
root@169.254.199.99's password:
Permission denied, please try again.   (x2)
root@169.254.199.99: Permission denied (publickey,password,keyboard-interactive).
Connection failed.
```

The owner started a second attempt, which was also refusing the password.

- The password being typed is not the head unit's root password.
- The head unit accepts `publickey,password,keyboard-interactive`. No key on the first PC is authorized.
- The password is held by the unlock tool (Bavarian SSH Client) and is not copyable. Do not extract it from the tool.

### To unblock (pick one)

1. Get the root login, or a way to add a public key, from the Bavarian SSH Client author (ssh.bavarian-aa.uk).
2. If the unlock tool can open a shell or file transfer to the unit itself, use it to add a public key from the ENET PC to the head unit. Then the install continues over plain SSH.
3. If the owner set a new password on the head unit, type exactly that one.

Stop retrying blind passwords. Each attempt is logged on the unit.

## Continue on another PC

### 1. Rebuild the install set (outside the repo)

The patched files are not in git. Rebuild them from `packages/dashboard.zip` (Git Bash):

```sh
mkdir -p ~/install_stage_330e/apps && cd ~/install_stage_330e/apps
unzip -q /path/to/ID6_apps_prerelease_f30_330e/packages/dashboard.zip 'BoostDeck/*' 'ShiftDeck/*' 'EngineCodes/*'
printf 'session' | dd of=BoostDeck/libBoostDeck.so bs=1 seek=$((0x4aee)) conv=notrunc
for d in BoostDeck ShiftDeck EngineCodes; do printf '169.254.39.69\n' > $d/gateway-ip.txt; done
sha256sum -c ../SHA256SUMS   # save the list below as ~/install_stage_330e/SHA256SUMS first
```

The `dd` line changes 6 bytes (`--ethanol` → `--session` at file offset 0x4aec). Tested 2026-11-19: it reproduces the staged hash. Patch only the plugin, never the collector.

Expected hashes (run from `apps/`, also use for the readback after upload):

```
1e2f159530a01421987c466c9e701e302c2e06499c02696e7f4ab5f3c42004fe *BoostDeck/BoostDeck.manifest
7a211a7eddae5d96a520599afe38ff125b5224e51fe1073d8de279db6d150638 *BoostDeck/BoostDeck.xml
4c0eebea8c7a937a45ef6f7ba66774ac0ddb1f5a1ec3d6f7835c8943488ccdfc *BoostDeck/BoostDeck_ALL_Images.zip
d647740e2769075ea36b9407640dd6a44aecfbf494804ae83afc2c7f8bced049 *BoostDeck/boostdeck-collector-qnx
2998ae526b69c2c11330e100d9091e015fbd9ba3cef8ac45aa788156b5bbfeec *BoostDeck/gateway-ip.txt
33376c67ab000c134f97a95b81541e328cc78100f8ef81694ec8f55641c0555a *BoostDeck/libBoostDeck.so
947de895c902f15bb9203444572eed352a575987998c46bb3f6a30ca8d235507 *EngineCodes/EngineCodes.manifest
3a7f5e3990f33c7a5dbbcaf3cd5df6530e2c5d95ad573cb6a5c84e939f7f2dcc *EngineCodes/EngineCodes.xml
08ebedd59bfa3eb4b9c887740f6e18728df12acefded8705a296d3402a1a1b3c *EngineCodes/EngineCodes_ALL_Images.zip
bea1ce62fdb529669181830470a2b0591f55e568c9b98308721dffa7b2187ac6 *EngineCodes/engine-codes-qnx
2998ae526b69c2c11330e100d9091e015fbd9ba3cef8ac45aa788156b5bbfeec *EngineCodes/gateway-ip.txt
e6008da6d171005ab08217b8fd670994b132d06e600e5cd9864d3ee1f9f7b184 *EngineCodes/libEngineCodes.so
fe2c649983f61d4a64f21d55fe0c38fafcd2b204ca8b48ba6515dbf7e287673f *ShiftDeck/ShiftDeck.manifest
f6271213c81b160075f9dea632f2c3e4f6093e07b0e4f8290d0c30b963056738 *ShiftDeck/ShiftDeck.xml
12ff702d008594f534d8a79475240a2f281d292657f05e5395ee85459ab45c17 *ShiftDeck/ShiftDeck_ALL_Images.zip
2998ae526b69c2c11330e100d9091e015fbd9ba3cef8ac45aa788156b5bbfeec *ShiftDeck/gateway-ip.txt
a94fe2599ca0399d46f9e04b46d5d7b5fb55d0ae212f2b1863f75a9dd02f553f *ShiftDeck/libShiftDeck.so
1654f8d5c63aba5cfefe1054597e809bf3abafdec67877f0c1068e1a0277d680 *ShiftDeck/shift-deck-qnx
```

Unpatched `BoostDeck/libBoostDeck.so` from the package (for rollback reference): `9119468d1930a9326007b8aff6924e8264cae49e945679ee51d13c870b49e60c`.

### 2. Pin the head-unit host key

Save this line as `hu_known` and pass it with `-o UserKnownHostsFile=… -o StrictHostKeyChecking=yes`:

```
169.254.199.99 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAtuXhwEjQjFuZhKdo1YH1QRulRzzyoUZIxdgz//q8NA4Z+jwsH71DGsDkWDklIHP2g505VuDmzjz3No6iFpdfHArInzaz7Wh67OtWvg7yEgxhdDNugaup/q0Yjaadx+PSfVF3JE6cAMH/87xOF/HUU0sMYPEW36YV18C96mYRCDwI1OgM93ygHHd7ZmkC5LBgjLQpgi8shNqCBLKYLML82w0B9h7ULEZMolckO2CY8SCtvURVckLmgIg9a4F7laxywFy7kLuoY17erOB/4b6xbkSO46H2wKGr/SKLnSBnvUBY8FKljDgLCRr42fwHBRQk3FOBpiMPG/RiMWpEbZjJvw==
```

Shared connection, the owner types the password (Git Bash `ssh`):

```sh
ssh -fN -M -S /tmp/hucm.sock -o ControlPersist=60m -o HostKeyAlgorithms=+ssh-rsa \
  -o PubkeyAuthentication=no -o UserKnownHostsFile=/path/to/hu_known -o GlobalKnownHostsFile=/dev/null \
  -o StrictHostKeyChecking=yes -o ServerAliveInterval=15 root@169.254.199.99
```

## Steps after login (per AgentReadMe)

1. Read-only: `uname -a` (OMAP vs Jacinto), NBTevo software code, LayerManager screen 0 resolution, sha256 of `/opt/hmi/ID5/lib/libAppFramework.A.so` and `libCoreFramework.A.so`.
   Reference values: `NBTevo_N18032I`, 1280 × 480, `93f4c7ab…c2123` and `64ba154c…3ee0`. **Any mismatch → stop, porting workflow, no install.**
2. List `/var/opt/hmi/data/ID5/Plugins`, check name and connector-ID conflicts.
3. Back up any app being replaced to a dated folder outside `Plugins`.
4. Upload the three folders to a staging dir outside `Plugins`, `chmod +x` the workers (`boostdeck-collector-qnx`, `shift-deck-qnx`, `engine-codes-qnx`), sha256 readback against the list above (not the package list).
5. Move into `Plugins`, verify final paths and bytes.
6. Owner holds the volume knob until iDrive goes dark (parked), then checks the menus and live readings. No ECU-changing command (EngineCodes Clear) without separate authorization.
