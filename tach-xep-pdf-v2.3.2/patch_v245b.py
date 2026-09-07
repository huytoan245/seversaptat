from pathlib import Path
import hashlib
root=Path('tach-xep-pdf-v2.3.2')
p=root/'TachXepTrangPDF.cs'
raw=p.read_bytes()
expected_base='7051ace6f2d9de56553e268d2e8bf6a88bcdc67a15a8610e2c04f215f83398d6'
if hashlib.sha256(raw).hexdigest()!=expected_base:
    raise SystemExit('unexpected v2.4.5 source before compact-pane hardening')
s=raw.decode('utf-8-sig')
repls=[
    ('internal const string Version = "2.4.3";', 'internal const string Version = "2.4.5";'),
    ('ConfigureRightPaneRatio(inner, 0.14, 190, 260);', 'ConfigureRightPaneRatio(inner, 0.13, 160, 230);'),
    ('"Tách & Xếp Trang PDF v2.4.3", MessageBoxButtons.OK', '"Tách & Xếp Trang PDF v2.4.5", MessageBoxButtons.OK'),
]
for old,new in repls:
    if old not in s: raise SystemExit('v245b marker missing: '+old)
    s=s.replace(old,new,1)
out=s.encode('utf-8-sig')
expected_final='4cbaed909d82dd3b32b301bd21dac544023f52215e3ec67fb1dd674f473f28fc'
actual=hashlib.sha256(out).hexdigest()
if actual!=expected_final: raise SystemExit('v245b checksum mismatch actual='+actual)
p.write_bytes(out)
print('PATCH_V245B_COMPACT_PANE_DIAGNOSTICS_OK source_sha256='+actual)
