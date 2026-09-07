from pathlib import Path
p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

s = s.replace('private const string AppVersion = "2.3.4";', 'private const string AppVersion = "2.3.5";', 1)
s = s.replace('2.3.4', '2.3.5')
s = s.replace('        private TrackBar _zoom;\n', '        private NumericUpDown _zoom;\n', 1)

# Header: keep title/author only; file name moves directly above Open PDF.
s = s.replace('            header.Height = 86;', '            header.Height = 60;', 1)
s = s.replace('''            headerGrid.RowCount = 3;\n            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));\n            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 52));\n            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));\n            headerGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));\n            headerGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 26));\n            headerGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));''', '''            headerGrid.RowCount = 2;\n            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));\n            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 52));\n            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));\n            headerGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));\n            headerGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));''', 1)
old = '''            _fileLabel = new Label();\n            _fileLabel.Text = "File đang xử lý: Chưa mở tài liệu";\n            _fileLabel.Font = new Font("Segoe UI", 10f, FontStyle.Bold);\n            _fileLabel.ForeColor = Color.FromArgb(35, 35, 35);\n            _fileLabel.AutoEllipsis = true;\n            _fileLabel.Dock = DockStyle.Fill;\n            _fileLabel.TextAlign = ContentAlignment.MiddleCenter;\n            headerGrid.Controls.Add(_fileLabel, 1, 2);\n\n            _selectionLabel = new Label();\n            _selectionLabel.Text = "Đang chọn: -";\n            _selectionLabel.Dock = DockStyle.Fill;\n            _selectionLabel.TextAlign = ContentAlignment.MiddleRight;\n            _selectionLabel.Padding = new Padding(0, 0, 12, 0);\n            headerGrid.Controls.Add(_selectionLabel, 2, 2);'''
if old not in s: raise SystemExit('header file block not found')
s = s.replace(old, '', 1)

s = s.replace('            toolbar.Height = 146;', '            toolbar.Height = 172;', 1)
old = '''            toolbarGrid.RowCount = 2;\n            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));\n            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));\n            toolbar.Controls.Add(toolbarGrid);\n\n            FlowLayoutPanel actions = new FlowLayoutPanel();'''
new = '''            toolbarGrid.RowCount = 3;\n            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 27));\n            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));\n            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));\n            toolbar.Controls.Add(toolbarGrid);\n\n            TableLayoutPanel fileRow = new TableLayoutPanel();\n            fileRow.Dock = DockStyle.Fill; fileRow.ColumnCount = 2; fileRow.RowCount = 1;\n            fileRow.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 68));\n            fileRow.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 32));\n            toolbarGrid.Controls.Add(fileRow, 0, 0);\n\n            _fileLabel = new Label(); _fileLabel.Text = "File đang mở: Chưa mở tài liệu";\n            _fileLabel.Font = new Font("Segoe UI", 10f, FontStyle.Bold); _fileLabel.ForeColor = Color.FromArgb(35, 35, 35);\n            _fileLabel.AutoEllipsis = true; _fileLabel.Dock = DockStyle.Fill; _fileLabel.TextAlign = ContentAlignment.MiddleLeft;\n            fileRow.Controls.Add(_fileLabel, 0, 0);\n            _selectionLabel = new Label(); _selectionLabel.Text = "Đang chọn: -"; _selectionLabel.Dock = DockStyle.Fill;\n            _selectionLabel.TextAlign = ContentAlignment.MiddleRight; _selectionLabel.Padding = new Padding(0, 0, 8, 0);\n            fileRow.Controls.Add(_selectionLabel, 1, 0);\n\n            FlowLayoutPanel actions = new FlowLayoutPanel();'''
if old not in s: raise SystemExit('toolbar grid block not found')
s = s.replace(old, new, 1)
s = s.replace('toolbarGrid.Controls.Add(actions, 0, 0);', 'toolbarGrid.Controls.Add(actions, 0, 1);', 1)
s = s.replace('toolbarGrid.Controls.Add(settings, 0, 1);', 'toolbarGrid.Controls.Add(settings, 0, 2);', 1)

# Direction after manual area, next to undo/redo; swap Redo and Undo.
old = '''            settings.ColumnCount = 3;\n            settings.RowCount = 1;\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 420));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 285));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));'''
new = '''            settings.ColumnCount = 3;\n            settings.RowCount = 1;\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 420));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 285));'''
if old not in s: raise SystemExit('settings columns not found')
s = s.replace(old, new, 1)
s = s.replace('settings.Controls.Add(direction, 1, 0);', 'settings.Controls.Add(direction, 2, 0);', 1)
s = s.replace('settings.Controls.Add(manual, 2, 0);', 'settings.Controls.Add(manual, 1, 0);', 1)
old = '''            _btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Margin = new Padding(0, 0, 5, 0); _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo);\n            _btnRedo = MakeButton("Làm lại", 86, false); _btnRedo.Margin = new Padding(0); _btnRedo.Click += delegate { Redo(); }; manualButtons.Controls.Add(_btnRedo);'''
new = '''            _btnRedo = MakeButton("Làm lại", 86, false); _btnRedo.Margin = new Padding(0, 0, 5, 0); _btnRedo.Click += delegate { Redo(); }; manualButtons.Controls.Add(_btnRedo);\n            _btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Margin = new Padding(0); _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo);'''
if old not in s: raise SystemExit('undo redo block not found')
s = s.replace(old, new, 1)

# Right guide pane 10-15% instead of fixed center width.
old = '''            Shown += delegate\n            {\n                ConfigureSplitterSafe(outer, 330, 250, 680);\n                ConfigureSplitterSafe(inner, 760, 420, 240);\n            };'''
new = '''            Shown += delegate\n            {\n                ConfigureSplitterSafe(outer, 330, 250, 680);\n                ConfigureRightPaneRatio(inner, 0.14, 170, 250);\n                ApplyZoom();\n            };\n            inner.Resize += delegate { ConfigureRightPaneRatio(inner, 0.14, 170, 250); };'''
if old not in s: raise SystemExit('shown splitter block not found')
s = s.replace(old, new, 1)
marker = '        private Button MakeButton(string text, int width, bool prominent)\n'
helper = '''        private static void ConfigureRightPaneRatio(SplitContainer split, double ratio, int minRight, int maxRight)\n        {\n            if (split == null || split.IsDisposed) return;\n            int total = split.Orientation == Orientation.Vertical ? split.ClientSize.Width : split.ClientSize.Height;\n            if (total <= split.SplitterWidth + 2) return;\n            split.Panel1MinSize = 0; split.Panel2MinSize = 0;\n            int right = (int)Math.Round(total * Math.Max(0.10, Math.Min(0.15, ratio)));\n            right = Math.Max(minRight, Math.Min(maxRight, right));\n            if (total < 700) right = Math.Max(120, Math.Min(right, (int)Math.Round(total * 0.15)));\n            int distance = Math.Max(1, Math.Min(total - split.SplitterWidth - 1, total - split.SplitterWidth - right));\n            if (Math.Abs(split.SplitterDistance - distance) > 1) split.SplitterDistance = distance;\n            if (total >= 420 + minRight + split.SplitterWidth) { split.Panel1MinSize = 420; split.Panel2MinSize = Math.Min(minRight, Math.Max(0, total - split.SplitterWidth - 420)); }\n        }\n\n'''
if marker not in s: raise SystemExit('MakeButton marker not found')
s = s.replace(marker, helper + marker, 1)

s = s.replace('_fileLabel.Text = "File đang xử lý: " + Path.GetFileName(_sourcePath);', '_fileLabel.Text = "File đang mở: " + Path.GetFileName(_sourcePath);')
s = s.replace('_fileLabel.Text = "File đang xử lý: Chưa mở tài liệu";', '_fileLabel.Text = "File đang mở: Chưa mở tài liệu";')

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V235A_LAYOUT_OK')
