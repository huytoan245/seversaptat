from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# v2.4.2: restore the proven old preview interaction model instead of inventing another control set.
s = s.replace('2.4.1', '2.4.2')

# v2.3.5 had deliberately replaced the old TrackBar with NumericUpDown. Restore the old control type.
old = '        private NumericUpDown _zoom;\n'
new = '        private TrackBar _zoom;\n        private Label _zoomValueLabel;\n'
if old not in s:
    raise SystemExit('zoom field marker missing')
s = s.replace(old, new, 1)

# Restore continuous slider zoom. 100% means fit-to-window; dragging does not re-render PDF,
# it only resizes the already-rendered preview bitmap, so interaction stays smooth/offline.
old = '''            _zoom = new NumericUpDown(); _zoom.Minimum = 50; _zoom.Maximum = 300; _zoom.Increment = 25; _zoom.Value = 100; _zoom.TextAlign = HorizontalAlignment.Center; _zoom.Width = 70; _zoom.Margin = new Padding(4, 7, 2, 0); _zoom.ValueChanged += delegate { ApplyZoom(); }; previewTop.Controls.Add(_zoom, 3, 0);'''
new = '''            _zoom = new TrackBar(); _zoom.Minimum = 50; _zoom.Maximum = 250; _zoom.TickFrequency = 25; _zoom.SmallChange = 5; _zoom.LargeChange = 10; _zoom.Value = 100; _zoom.AutoSize = false; _zoom.Height = 38; _zoom.Margin = new Padding(0); _zoom.ValueChanged += delegate { ApplyZoom(); }; previewTop.Controls.Add(_zoom, 3, 0);'''
if old not in s:
    raise SystemExit('numeric zoom creation marker missing')
s = s.replace(old, new, 1)

# Replace the recent +/- + numeric + preset toolbar with the exact interaction pattern that worked well:
# XEM TRƯỚC | Thu phóng: [slider] | n% | Vừa cửa sổ.
# The version text in the source comment is already advanced above, hence v2.4.2 here.
start = '''            // v2.4.2: preview toolbar is a real layout row, always visible and never covered by Dock/BringToFront.\n            centerLayout.Padding = new Padding(0); centerLayout.RowStyles[0] = new RowStyle(SizeType.Absolute, 48); previewTop.Visible = true;'''
end = '''            _toolTip.SetToolTip(_btnFitStable, "Hiển thị trọn trang PDF trong vùng xem, giữ đúng tỷ lệ gốc. Đây là chế độ mặc định khi mở file.");'''
si = s.find(start)
if si < 0:
    raise SystemExit('v241 preview toolbar start missing')
ei = s.find(end, si)
if ei < 0:
    raise SystemExit('v241 preview toolbar end missing')
ei += len(end)
newblock = '''            // v2.4.2: restore the proven old PDF preview toolbar, but keep it inside the real layout row.\n            centerLayout.Padding = new Padding(0); centerLayout.RowStyles[0] = new RowStyle(SizeType.Absolute, 46); previewTop.Visible = true;\n            previewTop.Controls.Clear(); previewTop.ColumnStyles.Clear(); previewTop.RowStyles.Clear(); previewTop.ColumnCount = 5; previewTop.RowCount = 1;\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 120));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 88));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 56));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 116));\n            previewTop.RowStyles.Add(new RowStyle(SizeType.Percent, 100));\n            Label stableTitle = new Label(); stableTitle.Text = "XEM TRƯỚC"; stableTitle.Font = new Font("Segoe UI", 11f, FontStyle.Bold); stableTitle.Dock = DockStyle.Fill; stableTitle.TextAlign = ContentAlignment.MiddleLeft; stableTitle.Padding = new Padding(8,0,0,0); previewTop.Controls.Add(stableTitle,0,0);\n            Label stableZl = new Label(); stableZl.Text = "Thu phóng:"; stableZl.Dock = DockStyle.Fill; stableZl.TextAlign = ContentAlignment.MiddleLeft; previewTop.Controls.Add(stableZl,1,0);\n            _zoom.Dock = DockStyle.Fill; _zoom.Margin = new Padding(0,5,8,2); _zoom.TickStyle = TickStyle.None; previewTop.Controls.Add(_zoom,2,0);\n            _zoomValueLabel = new Label(); _zoomValueLabel.Text = _zoom.Value.ToString() + "%"; _zoomValueLabel.Dock = DockStyle.Fill; _zoomValueLabel.TextAlign = ContentAlignment.MiddleCenter; previewTop.Controls.Add(_zoomValueLabel,3,0);\n            _btnFitStable = MakeButton("Vừa cửa sổ", 108, false); _btnFitStable.Dock = DockStyle.Fill; _btnFitStable.Height = 32; _btnFitStable.Margin = new Padding(4,6,8,6); _btnFitStable.Click += delegate { SetZoomPercent(100); }; previewTop.Controls.Add(_btnFitStable,4,0);\n            _toolTip.SetToolTip(_btnFitStable, "Hiển thị trọn trang PDF trong vùng xem và giữ đúng tỷ lệ gốc. 100% = vừa cửa sổ.");\n            _toolTip.SetToolTip(_zoom, "Kéo thanh để thu nhỏ/phóng to trang xem trước. 100% = vừa cửa sổ.");'''
s = s[:si] + newblock + s[ei:]

# Keep the percentage text synchronized without re-rendering the PDF while the slider is dragged.
old = '''        private void ApplyZoom()\n        {\n            if (_previewScroll == null || _preview == null || _zoom == null) return;'''
new = '''        private void ApplyZoom()\n        {\n            if (_zoomValueLabel != null && _zoom != null) _zoomValueLabel.Text = _zoom.Value.ToString() + "%";\n            if (_previewScroll == null || _preview == null || _zoom == null) return;'''
if old not in s:
    raise SystemExit('ApplyZoom head marker missing')
s = s.replace(old, new, 1)

# Update UI smoke expectations: old slider workflow is intentionally the required UI again.
s = s.replace('"Vừa màn hình"', '"Vừa cửa sổ"')
old = '''                            "Vừa cửa sổ",\n                            "125%",\n                            "150%",\n                            "200%",\n                            "Khôi phục PDF gốc"'''
new = '''                            "Vừa cửa sổ",\n                            "Thu phóng:",\n                            "Khôi phục PDF gốc"'''
if old in s:
    s = s.replace(old, new, 1)

# Harden smoke test specifically for the slider, not just a text label existing somewhere.
needle = '''                            Button fitButton = FindControlByText(form, "Vừa cửa sổ") as Button;'''
if needle not in s:
    raise SystemExit('fit-button smoke marker missing')
insert = '''                            TrackBar zoomSlider = FindControlByType<TrackBar>(form);\n                            if (zoomSlider == null || !zoomSlider.Visible || zoomSlider.Minimum > 90 || zoomSlider.Maximum < 150) throw new InvalidOperationException("Visible PDF preview zoom slider missing.");\n                            zoomSlider.Value = 90;\n                            if (zoomSlider.Value != 90) throw new InvalidOperationException("PDF preview zoom slider cannot select 90 percent.");\n'''
s = s.replace(needle, insert + needle, 1)

# Add a small generic type finder used only by UI smoke.
marker = '''        private static Control FindControlByText(Control root, string text)\n'''
helper = '''        private static T FindControlByType<T>(Control root) where T : Control\n        {\n            if (root == null) return null;\n            T self = root as T; if (self != null) return self;\n            foreach (Control c in root.Controls) { T found = FindControlByType<T>(c); if (found != null) return found; }\n            return null;\n        }\n\n'''
if marker not in s:
    raise SystemExit('FindControlByText marker missing')
s = s.replace(marker, helper + marker, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V242_RESTORE_PROVEN_PREVIEW_SLIDER_OK')
