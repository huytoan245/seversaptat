from pathlib import Path
import hashlib

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
raw = p.read_bytes()
expected = 'd2171c5af3ccb08f7496f4d61fabb29fe575aca3a1fa1e07fea9548ad4cbfaea'
if hashlib.sha256(raw).hexdigest() != expected:
    raise SystemExit('unexpected source before v2.4.5d cut-pane layout patch')
s = raw.decode('utf-8-sig')

old = 'ConfigureRightPaneRatio(inner, 0.13, 160, 230);'
new = 'ConfigureRightPaneRatio(inner, 0.14, 215, 260);'
if old not in s:
    raise SystemExit('right-pane ratio marker missing')
s = s.replace(old, new, 1)

old = '''            Panel info = inner.Panel2; info.Padding = new Padding(10); info.BackColor = Color.White;
            TableLayoutPanel cutPanel = new TableLayoutPanel(); cutPanel.Dock = DockStyle.Fill; cutPanel.ColumnCount = 1; cutPanel.RowCount = 7;'''
new = '''            Panel info = inner.Panel2; info.Padding = new Padding(8); info.BackColor = Color.White;
            TableLayoutPanel cutPanel = new TableLayoutPanel(); cutPanel.Dock = DockStyle.Fill; cutPanel.ColumnCount = 1; cutPanel.RowCount = 7;
            // Explicit percent column is critical: an implicit AutoSize column grows to the title's
            // preferred width and can push controls outside the SplitterPanel on narrow/DPI-scaled windows.
            cutPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));'''
if old not in s:
    raise SystemExit('cut-panel construction marker missing')
s = s.replace(old, new, 1)

old = '''            Label cutTitle = new Label(); cutTitle.Text = "CHỈNH ĐƯỜNG CẮT"; cutTitle.Font = new Font("Segoe UI", 10.5f, FontStyle.Bold); cutTitle.Dock = DockStyle.Fill;'''
new = '''            Label cutTitle = new Label(); cutTitle.Text = "CHỈNH ĐƯỜNG CẮT"; cutTitle.AutoSize = false; cutTitle.Font = new Font("Segoe UI", 10.5f, FontStyle.Bold); cutTitle.Dock = DockStyle.Fill;'''
if old not in s:
    raise SystemExit('cut title marker missing')
s = s.replace(old, new, 1)

out = s.encode('utf-8-sig')
actual = hashlib.sha256(out).hexdigest()
expected_final = 'ea3b16c54c2437f480194b2eb97147e662138b2f09cfafcdef01c3f047a6a452'
if actual != expected_final:
    raise SystemExit('v2.4.5d checksum mismatch: ' + actual)
p.write_bytes(out)
print('PATCH_V245D_CUT_PANE_CONSTRAINED_LAYOUT_OK source_sha256=' + actual)
