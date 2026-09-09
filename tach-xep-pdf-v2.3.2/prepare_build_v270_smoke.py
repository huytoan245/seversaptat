from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')
needle="& python (Join-Path $Project 'patch_v270_launcher.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_launcher.py failed' } }"
replacement="& python (Join-Path $Project 'patch_v270_launcher.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_launcher.py failed' }; & python (Join-Path $Project 'patch_v270_smoke_pump.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_smoke_pump.py failed' } }"
if needle not in s:
    raise SystemExit('v2.7.0 final launcher chain marker missing for smoke pump')
s=s.replace(needle,replacement,1)

# Ensure the patch source itself is captured in the generated release source snapshot when possible.
snapshot="(Join-Path $Project 'patch_v270_launcher.py'), (Join-Path $Project 'prepare_build_v270.py'),"
if snapshot in s:
    s=s.replace(snapshot,"(Join-Path $Project 'patch_v270_launcher.py'), (Join-Path $Project 'patch_v270_smoke_pump.py'), (Join-Path $Project 'prepare_build_v270.py'), (Join-Path $Project 'prepare_build_v270_smoke.py'),",1)

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V270_BOUNDED_SMOKE_PUMP_OK')
