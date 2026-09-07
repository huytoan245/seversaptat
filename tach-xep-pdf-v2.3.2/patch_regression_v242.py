from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/regression_test.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('Vừa màn hình','Vừa cửa sổ')
# The restored interaction is a TrackBar slider; keep the regression text contract aligned with the visible UI.
if 'Vừa màn hình' in s:
    raise SystemExit('v2.4.1 fit label remains in regression test')
p.write_text(s,encoding='utf-8-sig')
print('PATCH_REGRESSION_V242_OK')
