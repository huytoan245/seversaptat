from pathlib import Path
root=Path('tach-xep-pdf-v2.3.2')
p=root/'launcher.cpp'
s=p.read_text(encoding='utf-8-sig')
if 'v2.6.1' not in s:
    raise SystemExit('v2.7.0 launcher expected v2.6.1 identity marker missing')
s=s.replace('v2.6.1','v2.7.0')
required=['Runtime" / L"v2.7.0','Tach_Xep_Trang_PDF_v2.7.0.exe','launcher-v2.7.0.log','Launcher v2.7.0 start','PDF v2.7.0']
for marker in required:
    if marker not in s:
        raise SystemExit('v2.7.0 launcher identity marker missing: '+marker)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_LAUNCHER_IDENTITY_OK')

# The production app remains unchanged here; this patch only hardens the UI smoke harness.
# Execute the bounded message-pump patch at the end of the existing v2.7.0 chain so async
# UI continuations are exercised on the WinForms thread without Application.DoEvents() hangs.
smoke_patch=root/'patch_v270_smoke_pump.py'
if not smoke_patch.exists():
    raise SystemExit('v2.7.0 bounded smoke pump patch missing')
exec(compile(smoke_patch.read_text(encoding='utf-8-sig'),str(smoke_patch),'exec'),{})
