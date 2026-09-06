from pathlib import Path

root = Path('tach-xep-pdf-v2.3.2')
cs_path = root / 'TachXepTrangPDF.cs'
launcher_path = root / 'launcher.cpp'
s = cs_path.read_text(encoding='utf-8-sig')

# v2.3.4: responsive/deterministic WinForms layout. The v2.3.3 UI used Dock=Fill controls
# with BringToFront, which covered header/toolbar panes. It also placed toolbar controls at
# absolute coordinates, causing clipping with DPI scaling. Replace those specific regions.

old_toolbar = '''            Panel toolbar = new Panel();
            toolbar.Dock = DockStyle.Fill;
            toolbar.BackColor = Color.FromArgb(248, 249, 251);
            topShell.Controls.Add(toolbar);
            toolbar.BringToFront();
            header.BringToFront();

            int x = 16, y = 10;
            Button open = MakeButton("Mở PDF", 100, true); open.Location = new Point(x, y); open.Click += delegate { OpenPdf(); }; toolbar.Controls.Add(open); x += 108;
            _btnAuto = MakeButton("TỰ XOAY THÔNG MINH", 188, true); _btnAuto.Location = new Point(x, y); _btnAuto.Click += async delegate { await AutoRotateAsync(); }; toolbar.Controls.Add(_btnAuto); x += 196;
            _btnSplit = MakeButton("TỰ CHIA & SẮP XẾP", 190, true); _btnSplit.Location = new Point(x, y); _btnSplit.Click += delegate { SplitAndArrange(); }; toolbar.Controls.Add(_btnSplit); x += 198;
            _btnExport = MakeButton("Xuất PDF", 112, true); _btnExport.Location = new Point(x, y); _btnExport.Click += async delegate { await ExportPdfAsync(false); }; toolbar.Controls.Add(_btnExport); x += 120;
            _btnSaveOriginal = MakeButton("Lưu vào file gốc", 150, false); _btnSaveOriginal.Location = new Point(x, y); _btnSaveOriginal.Click += async delegate { await ExportPdfAsync(true); }; toolbar.Controls.Add(_btnSaveOriginal);

            _autoRotateStatus = new Label();
            _autoRotateStatus.Text = "Tự xoay: AI ONNX chuyên dụng + phân tích bố cục + đối chiếu toàn tài liệu; chạy hoàn toàn offline.";
            _autoRotateStatus.Location = new Point(840, 12);
            _autoRotateStatus.Size = new Size(570, 44);
            _autoRotateStatus.ForeColor = Color.FromArgb(90, 90, 90);
            toolbar.Controls.Add(_autoRotateStatus);

            GroupBox scan = new GroupBox(); scan.Text = "CÁCH QUÉT TÀI LIỆU"; scan.Location = new Point(16, 58); scan.Size = new Size(420, 76); toolbar.Controls.Add(scan);
            _modeDetached = new RadioButton(); _modeDetached.Text = "Đã tháo ghim (Mặc định)"; _modeDetached.Checked = true; _modeDetached.Location = new Point(14, 26); _modeDetached.AutoSize = true; scan.Controls.Add(_modeDetached);
            _modeBound = new RadioButton(); _modeBound.Text = "Scan khi còn đóng quyển"; _modeBound.Location = new Point(205, 26); _modeBound.AutoSize = true; scan.Controls.Add(_modeBound);
            _modeDetached.CheckedChanged += delegate { if (_modeDetached.Checked) ModeChanged(); };
            _modeBound.CheckedChanged += delegate { if (_modeBound.Checked) ModeChanged(); };

            GroupBox direction = new GroupBox(); direction.Text = "CHIỀU CẮT"; direction.Location = new Point(445, 58); direction.Size = new Size(285, 76); toolbar.Controls.Add(direction);
            _dirLtr = new RadioButton(); _dirLtr.Text = "Trái → Phải"; _dirLtr.Checked = true; _dirLtr.Location = new Point(14, 26); _dirLtr.AutoSize = true; direction.Controls.Add(_dirLtr);
            _dirRtl = new RadioButton(); _dirRtl.Text = "Phải → Trái"; _dirRtl.Location = new Point(145, 26); _dirRtl.AutoSize = true; direction.Controls.Add(_dirRtl);
            _dirLtr.CheckedChanged += delegate { if (_dirLtr.Checked) DirectionChanged(); };
            _dirRtl.CheckedChanged += delegate { if (_dirRtl.Checked) DirectionChanged(); };

            Panel manual = new Panel(); manual.Location = new Point(742, 64); manual.Size = new Size(680, 68); toolbar.Controls.Add(manual);
            Label man = new Label(); man.Text = "Chỉnh tay:"; man.Location = new Point(0, 7); man.AutoSize = true; manual.Controls.Add(man);
            int mx = 70;
            Button left = MakeButton("↶ Xoay trái", 105, false); left.Location = new Point(mx, 0); left.Click += delegate { RotateSelected(-90); }; manual.Controls.Add(left); mx += 110;
            Button right = MakeButton("↷ Xoay phải", 108, false); right.Location = new Point(mx, 0); right.Click += delegate { RotateSelected(90); }; manual.Controls.Add(right); mx += 113;
            Button flip = MakeButton("Xoay 180°", 105, false); flip.Location = new Point(mx, 0); flip.Click += delegate { RotateSelected(180); }; manual.Controls.Add(flip); mx += 110;
            Button del = MakeButton("Xóa", 74, false); del.Location = new Point(mx, 0); del.Click += delegate { DeleteSelected(); }; manual.Controls.Add(del); mx += 80;
            _btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Location = new Point(mx, 0); _btnUndo.Click += delegate { Undo(); }; manual.Controls.Add(_btnUndo); mx += 96;
            _btnRedo = MakeButton("Làm lại", 86, false); _btnRedo.Location = new Point(mx, 0); _btnRedo.Click += delegate { Redo(); }; manual.Controls.Add(_btnRedo);

            Label cutLabel = new Label(); cutLabel.Text = "Tỷ lệ cắt mặt đang chọn:"; cutLabel.Location = new Point(70, 38); cutLabel.AutoSize = true; manual.Controls.Add(cutLabel);
            _cut = new NumericUpDown(); _cut.DecimalPlaces = 1; _cut.Minimum = 30; _cut.Maximum = 70; _cut.Increment = 0.5M; _cut.Value = 50; _cut.Location = new Point(230, 34); _cut.Width = 70; _cut.ValueChanged += CutChangedHandler; manual.Controls.Add(_cut);
            Label pct = new Label(); pct.Text = "% (mặc định 50/50)"; pct.Location = new Point(305, 38); pct.AutoSize = true; manual.Controls.Add(pct);'''

new_toolbar = '''            Panel toolbar = new Panel();
            toolbar.Dock = DockStyle.Bottom;
            toolbar.Height = 146;
            toolbar.BackColor = Color.FromArgb(248, 249, 251);
            toolbar.Padding = new Padding(12, 6, 12, 6);
            topShell.Controls.Add(toolbar);

            TableLayoutPanel toolbarGrid = new TableLayoutPanel();
            toolbarGrid.Dock = DockStyle.Fill;
            toolbarGrid.ColumnCount = 1;
            toolbarGrid.RowCount = 2;
            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
            toolbarGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            toolbar.Controls.Add(toolbarGrid);

            FlowLayoutPanel actions = new FlowLayoutPanel();
            actions.Dock = DockStyle.Fill;
            actions.WrapContents = false;
            actions.AutoScroll = true;
            actions.FlowDirection = FlowDirection.LeftToRight;
            actions.Padding = new Padding(0, 2, 0, 0);
            toolbarGrid.Controls.Add(actions, 0, 0);

            Button open = MakeButton("Mở PDF", 100, true); open.Margin = new Padding(0, 0, 8, 0); open.Click += delegate { OpenPdf(); }; actions.Controls.Add(open);
            _btnAuto = MakeButton("TỰ XOAY THÔNG MINH", 188, true); _btnAuto.Margin = new Padding(0, 0, 8, 0); _btnAuto.Click += async delegate { await AutoRotateAsync(); }; actions.Controls.Add(_btnAuto);
            _btnSplit = MakeButton("TỰ CHIA & SẮP XẾP", 190, true); _btnSplit.Margin = new Padding(0, 0, 8, 0); _btnSplit.Click += delegate { SplitAndArrange(); }; actions.Controls.Add(_btnSplit);
            _btnExport = MakeButton("Xuất PDF", 112, true); _btnExport.Margin = new Padding(0, 0, 8, 0); _btnExport.Click += async delegate { await ExportPdfAsync(false); }; actions.Controls.Add(_btnExport);
            _btnSaveOriginal = MakeButton("Lưu vào file gốc", 150, false); _btnSaveOriginal.Margin = new Padding(0, 0, 12, 0); _btnSaveOriginal.Click += async delegate { await ExportPdfAsync(true); }; actions.Controls.Add(_btnSaveOriginal);

            _autoRotateStatus = new Label();
            _autoRotateStatus.Text = "Tự xoay AI ONNX offline • Không đổi thứ tự nguồn • Trang chưa chắc chắn sẽ được đánh dấu CẦN KIỂM TRA";
            _autoRotateStatus.AutoSize = false;
            _autoRotateStatus.Size = new Size(560, 36);
            _autoRotateStatus.TextAlign = ContentAlignment.MiddleLeft;
            _autoRotateStatus.ForeColor = Color.FromArgb(90, 90, 90);
            _autoRotateStatus.Margin = new Padding(0, 0, 0, 0);
            actions.Controls.Add(_autoRotateStatus);

            TableLayoutPanel settings = new TableLayoutPanel();
            settings.Dock = DockStyle.Fill;
            settings.ColumnCount = 3;
            settings.RowCount = 1;
            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 420));
            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 285));
            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
            toolbarGrid.Controls.Add(settings, 0, 1);

            GroupBox scan = new GroupBox(); scan.Text = "CÁCH QUÉT TÀI LIỆU"; scan.Dock = DockStyle.Fill; scan.Margin = new Padding(0, 0, 8, 0); settings.Controls.Add(scan, 0, 0);
            _modeDetached = new RadioButton(); _modeDetached.Text = "Đã tháo ghim (Mặc định)"; _modeDetached.Checked = true; _modeDetached.Location = new Point(14, 25); _modeDetached.AutoSize = true; scan.Controls.Add(_modeDetached);
            _modeBound = new RadioButton(); _modeBound.Text = "Scan khi còn đóng quyển"; _modeBound.Location = new Point(205, 25); _modeBound.AutoSize = true; scan.Controls.Add(_modeBound);
            _modeDetached.CheckedChanged += delegate { if (_modeDetached.Checked) ModeChanged(); };
            _modeBound.CheckedChanged += delegate { if (_modeBound.Checked) ModeChanged(); };

            GroupBox direction = new GroupBox(); direction.Text = "CHIỀU CẮT"; direction.Dock = DockStyle.Fill; direction.Margin = new Padding(0, 0, 8, 0); settings.Controls.Add(direction, 1, 0);
            _dirLtr = new RadioButton(); _dirLtr.Text = "Trái → Phải"; _dirLtr.Checked = true; _dirLtr.Location = new Point(14, 25); _dirLtr.AutoSize = true; direction.Controls.Add(_dirLtr);
            _dirRtl = new RadioButton(); _dirRtl.Text = "Phải → Trái"; _dirRtl.Location = new Point(145, 25); _dirRtl.AutoSize = true; direction.Controls.Add(_dirRtl);
            _dirLtr.CheckedChanged += delegate { if (_dirLtr.Checked) DirectionChanged(); };
            _dirRtl.CheckedChanged += delegate { if (_dirRtl.Checked) DirectionChanged(); };

            Panel manual = new Panel(); manual.Dock = DockStyle.Fill; manual.Margin = new Padding(0); settings.Controls.Add(manual, 2, 0);
            FlowLayoutPanel manualButtons = new FlowLayoutPanel(); manualButtons.Dock = DockStyle.Top; manualButtons.Height = 38; manualButtons.WrapContents = false; manualButtons.AutoScroll = true; manual.Controls.Add(manualButtons);
            Label man = new Label(); man.Text = "Chỉnh tay:"; man.AutoSize = false; man.Size = new Size(68, 34); man.TextAlign = ContentAlignment.MiddleLeft; manualButtons.Controls.Add(man);
            Button left = MakeButton("↶ Xoay trái", 105, false); left.Margin = new Padding(0, 0, 5, 0); left.Click += delegate { RotateSelected(-90); }; manualButtons.Controls.Add(left);
            Button right = MakeButton("↷ Xoay phải", 108, false); right.Margin = new Padding(0, 0, 5, 0); right.Click += delegate { RotateSelected(90); }; manualButtons.Controls.Add(right);
            Button flip = MakeButton("Xoay 180°", 105, false); flip.Margin = new Padding(0, 0, 5, 0); flip.Click += delegate { RotateSelected(180); }; manualButtons.Controls.Add(flip);
            Button del = MakeButton("Xóa", 74, false); del.Margin = new Padding(0, 0, 5, 0); del.Click += delegate { DeleteSelected(); }; manualButtons.Controls.Add(del);
            _btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Margin = new Padding(0, 0, 5, 0); _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo);
            _btnRedo = MakeButton("Làm lại", 86, false); _btnRedo.Margin = new Padding(0); _btnRedo.Click += delegate { Redo(); }; manualButtons.Controls.Add(_btnRedo);

            FlowLayoutPanel cutRow = new FlowLayoutPanel(); cutRow.Dock = DockStyle.Fill; cutRow.WrapContents = false; cutRow.Padding = new Padding(68, 2, 0, 0); manual.Controls.Add(cutRow); cutRow.SendToBack();
            Label cutLabel = new Label(); cutLabel.Text = "Tỷ lệ cắt mặt đang chọn:"; cutLabel.AutoSize = true; cutLabel.Margin = new Padding(0, 6, 5, 0); cutRow.Controls.Add(cutLabel);
            _cut = new NumericUpDown(); _cut.DecimalPlaces = 1; _cut.Minimum = 30; _cut.Maximum = 70; _cut.Increment = 0.5M; _cut.Value = 50; _cut.Width = 70; _cut.Margin = new Padding(0, 2, 5, 0); _cut.ValueChanged += CutChangedHandler; cutRow.Controls.Add(_cut);
            Label pct = new Label(); pct.Text = "% (mặc định 50/50)"; pct.AutoSize = true; pct.Margin = new Padding(0, 6, 0, 0); cutRow.Controls.Add(pct);'''

if old_toolbar not in s:
    raise SystemExit('Expected v2.3.3 toolbar block not found')
s = s.replace(old_toolbar, new_toolbar, 1)

# Body panes: eliminate Dock=Fill + BringToFront overlays by using explicit table rows.
old_left_start = '''            Panel leftPane = outer.Panel1; leftPane.Padding = new Padding(10);
            Label ltitle = new Label(); ltitle.Text = "THỨ TỰ TRANG"; ltitle.Font = new Font("Segoe UI", 11f, FontStyle.Bold); ltitle.Dock = DockStyle.Top; ltitle.Height = 28; leftPane.Controls.Add(ltitle);
            Label lhint = new Label(); lhint.Text = "↑/↓: di chuyển trang • Kéo thả để sắp xếp • Chuột phải: Lên đầu/Xuống cuối"; lhint.Dock = DockStyle.Top; lhint.Height = 46; lhint.ForeColor = Color.DimGray; leftPane.Controls.Add(lhint); lhint.BringToFront();'''
new_left_start = '''            Panel leftPane = outer.Panel1; leftPane.Padding = new Padding(10);
            TableLayoutPanel leftLayout = new TableLayoutPanel(); leftLayout.Dock = DockStyle.Fill; leftLayout.ColumnCount = 1; leftLayout.RowCount = 3; leftLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 28)); leftLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 46)); leftLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); leftPane.Controls.Add(leftLayout);
            Label ltitle = new Label(); ltitle.Text = "THỨ TỰ TRANG"; ltitle.Font = new Font("Segoe UI", 11f, FontStyle.Bold); ltitle.Dock = DockStyle.Fill; ltitle.TextAlign = ContentAlignment.MiddleLeft; leftLayout.Controls.Add(ltitle, 0, 0);
            Label lhint = new Label(); lhint.Text = "↑/↓: di chuyển trang • Kéo thả để sắp xếp • Chuột phải: Lên đầu/Xuống cuối"; lhint.Dock = DockStyle.Fill; lhint.ForeColor = Color.DimGray; leftLayout.Controls.Add(lhint, 0, 1);'''
if old_left_start not in s:
    raise SystemExit('Expected left pane header block not found')
s = s.replace(old_left_start, new_left_start, 1)

old_list_add = '''            _list = new ListView(); _list.Dock = DockStyle.Fill; _list.View = View.Details; _list.FullRowSelect = true; _list.HideSelection = false; _list.MultiSelect = false; _list.SmallImageList = _thumbs; _list.Columns.Add("Trang", 285); _list.AllowDrop = true; _list.BackColor = Color.White; _list.BorderStyle = BorderStyle.FixedSingle; _list.KeyDown += ListKeyDown; _list.SelectedIndexChanged += ListSelectionChanged; _list.ItemDrag += ListItemDrag; _list.DragEnter += ListDragEnter; _list.DragOver += ListDragOver; _list.DragDrop += ListDragDrop; leftPane.Controls.Add(_list); _list.BringToFront();'''
new_list_add = '''            _list = new ListView(); _list.Dock = DockStyle.Fill; _list.View = View.Details; _list.FullRowSelect = true; _list.HideSelection = false; _list.MultiSelect = false; _list.SmallImageList = _thumbs; _list.Columns.Add("Trang", 285); _list.AllowDrop = true; _list.BackColor = Color.White; _list.BorderStyle = BorderStyle.FixedSingle; _list.KeyDown += ListKeyDown; _list.SelectedIndexChanged += ListSelectionChanged; _list.ItemDrag += ListItemDrag; _list.DragEnter += ListDragEnter; _list.DragOver += ListDragOver; _list.DragDrop += ListDragDrop; leftLayout.Controls.Add(_list, 0, 2);'''
if old_list_add not in s:
    raise SystemExit('Expected list add block not found')
s = s.replace(old_list_add, new_list_add, 1)

old_center = '''            Panel center = inner.Panel1; center.Padding = new Padding(8);
            Panel previewTop = new Panel(); previewTop.Dock = DockStyle.Top; previewTop.Height = 38; center.Controls.Add(previewTop);'''
new_center = '''            Panel center = inner.Panel1; center.Padding = new Padding(8);
            TableLayoutPanel centerLayout = new TableLayoutPanel(); centerLayout.Dock = DockStyle.Fill; centerLayout.ColumnCount = 1; centerLayout.RowCount = 2; centerLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 38)); centerLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); center.Controls.Add(centerLayout);
            Panel previewTop = new Panel(); previewTop.Dock = DockStyle.Fill; centerLayout.Controls.Add(previewTop, 0, 0);'''
if old_center not in s:
    raise SystemExit('Expected center header block not found')
s = s.replace(old_center, new_center, 1)

old_preview_add = '''            _previewScroll = new Panel(); _previewScroll.Dock = DockStyle.Fill; _previewScroll.AutoScroll = true; _previewScroll.BackColor = Color.FromArgb(45, 48, 52); center.Controls.Add(_previewScroll); _previewScroll.BringToFront();'''
new_preview_add = '''            _previewScroll = new Panel(); _previewScroll.Dock = DockStyle.Fill; _previewScroll.AutoScroll = true; _previewScroll.BackColor = Color.FromArgb(45, 48, 52); centerLayout.Controls.Add(_previewScroll, 0, 1);'''
if old_preview_add not in s:
    raise SystemExit('Expected preview scroll add block not found')
s = s.replace(old_preview_add, new_preview_add, 1)

old_info = '''            Panel info = inner.Panel2; info.Padding = new Padding(12); info.BackColor = Color.White;
            Label ih = new Label(); ih.Text = "THÔNG TIN & HƯỚNG DẪN"; ih.Font = new Font("Segoe UI", 11f, FontStyle.Bold); ih.Dock = DockStyle.Top; ih.Height = 30; info.Controls.Add(ih);'''
new_info = '''            Panel info = inner.Panel2; info.Padding = new Padding(12); info.BackColor = Color.White;
            TableLayoutPanel infoLayout = new TableLayoutPanel(); infoLayout.Dock = DockStyle.Fill; infoLayout.ColumnCount = 1; infoLayout.RowCount = 2; infoLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 30)); infoLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); info.Controls.Add(infoLayout);
            Label ih = new Label(); ih.Text = "THÔNG TIN & HƯỚNG DẪN"; ih.Font = new Font("Segoe UI", 11f, FontStyle.Bold); ih.Dock = DockStyle.Fill; ih.TextAlign = ContentAlignment.MiddleLeft; infoLayout.Controls.Add(ih, 0, 0);'''
if old_info not in s:
    raise SystemExit('Expected info header block not found')
s = s.replace(old_info, new_info, 1)

old_help_add = '''            info.Controls.Add(help); help.BringToFront();'''
new_help_add = '''            infoLayout.Controls.Add(help, 0, 1);'''
if old_help_add not in s:
    raise SystemExit('Expected help add block not found')
s = s.replace(old_help_add, new_help_add, 1)

# Version/runtime isolation.
s = s.replace('2.3.3', '2.3.4')
cs_path.write_text(s, encoding='utf-8-sig')

launcher = launcher_path.read_text(encoding='utf-8-sig').replace('2.3.3', '2.3.4')
launcher_path.write_text(launcher, encoding='utf-8-sig')
print('PATCH_V234_RESPONSIVE_UI_OK')
