from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
# The old preview row is cleared at runtime, but its legacy label remained in source before the smoke-test array.
# Normalize every remaining textual reference so smoke tests validate the actual v2.4.1 control.
s=s.replace('Vừa cửa sổ','Vừa màn hình')
if 'Vừa cửa sổ' in s: raise SystemExit('legacy fit label still present')
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V241D_FIT_LABEL_OK')