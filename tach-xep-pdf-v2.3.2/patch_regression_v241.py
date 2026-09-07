from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/regression_test.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('Vừa cửa sổ','Vừa màn hình')
if 'Vừa cửa sổ' in s: raise SystemExit('legacy fit label remains in regression test')
p.write_text(s,encoding='utf-8-sig')
print('PATCH_REGRESSION_V241_OK')