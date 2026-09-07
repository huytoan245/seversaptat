from pathlib import Path
import hashlib

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
raw = p.read_bytes()
expected = '4cbaed909d82dd3b32b301bd21dac544023f52215e3ec67fb1dd674f473f28fc'
if hashlib.sha256(raw).hexdigest() != expected:
    raise SystemExit('unexpected source before v2.4.5c diagnostics patch')
s = raw.decode('utf-8-sig')
old = '''            if (!fr.Contains(cr)) throw new InvalidOperationException("UI control clipped/outside form: " + text + " bounds=" + cr.ToString());'''
new = '''            if (!fr.Contains(cr))
            {
                StringBuilder chain = new StringBuilder();
                Control q = c;
                while (q != null)
                {
                    Rectangle qr = q.RectangleToScreen(q.ClientRectangle);
                    if (chain.Length > 0) chain.Append(" <- ");
                    chain.Append(q.GetType().Name).Append("[").Append(q.Name).Append("]=").Append(qr.ToString());
                    q = q.Parent;
                }
                throw new InvalidOperationException("UI control clipped/outside form: " + text + " control=" + cr.ToString() + " form=" + fr.ToString() + " chain=" + chain.ToString());
            }'''
if old not in s:
    raise SystemExit('AssertUiControlVisible marker missing')
s = s.replace(old, new, 1)
out = s.encode('utf-8-sig')
actual = hashlib.sha256(out).hexdigest()
expected_final = 'd2171c5af3ccb08f7496f4d61fabb29fe575aca3a1fa1e07fea9548ad4cbfaea'
if actual != expected_final:
    raise SystemExit('v2.4.5c checksum mismatch: ' + actual)
p.write_bytes(out)
print('PATCH_V245C_UI_GEOMETRY_DIAGNOSTICS_OK source_sha256=' + actual)
