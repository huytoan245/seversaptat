from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# -----------------------------------------------------------------------------
# v2.5.0 - DPI-safe UI + multi-PDF workspace.
# The business logic for split/order/rotate/export is intentionally preserved.
# We add a document workspace shell around the proven single-document engine.
# -----------------------------------------------------------------------------
if 'private const string AppVersion = "2.4.5";' not in s:
    raise SystemExit('v2.4.5 source marker missing')
s = s.replace('private const string AppVersion = "2.4.5";', 'private const string AppVersion = "2.5.0";', 1)

# Per-document state. Only one PDF runtime is active at a time to keep memory bounded;
# inactive documents retain their immutable work-copy + model/history state.
main_marker = '    internal sealed class MainForm : Form\n'
if main_marker not in s:
    raise SystemExit('MainForm marker missing')
doc_class = '''    internal sealed class DocumentWorkspace\n    {\n        internal Guid Id = Guid.NewGuid();\n        internal string SourcePath = "";\n        internal string SessionDir = "";\n        internal string WorkPath = "";\n        internal int PageCount;\n        internal bool Initialized;\n        internal AppSnapshot Snapshot;\n        internal readonly Stack<AppSnapshot> Undo = new Stack<AppSnapshot>();\n        internal readonly Stack<AppSnapshot> Redo = new Stack<AppSnapshot>();\n        internal bool SourceWasOverwritten;\n        internal string OriginalBackupPath = "";\n        internal int ZoomPercent = 100;\n        internal string LastError = "";\n    }\n\n'''
s = s.replace(main_marker, doc_class + main_marker, 1)

field_marker = '        private string _originalBackupPath = "";\n'
if field_marker not in s:
    raise SystemExit('document field insertion marker missing')
s = s.replace(field_marker, field_marker + '''        private readonly List<DocumentWorkspace> _documents = new List<DocumentWorkspace>();\n        private DocumentWorkspace _activeDocument;\n        private ListView _fileList;\n        private bool _suspendDocumentSelection;\n        private bool _applyingResponsiveLayout;\n''', 1)

# Explicit DPI autoscaling. The app already uses PerMonitorV2 at startup; this makes the
# Form/control scaling contract explicit for monitors with 125/150/175/200% scaling.
ctor_marker = '            MinimumSize = new Size(1100, 700);\n            Font = new Font("Segoe UI", 9.5f);\n'
if ctor_marker not in s:
    raise SystemExit('constructor DPI marker missing')
s = s.replace(ctor_marker, '            MinimumSize = new Size(1100, 700);\n            AutoScaleMode = AutoScaleMode.Dpi; AutoScaleDimensions = new SizeF(96f, 96f);\n            Font = new Font("Segoe UI", 9.5f);\n', 1)

# Top action row must wrap instead of hiding/truncating controls on a different DPI.
s = s.replace('            actions.WrapContents = false;\n            actions.AutoScroll = true;\n', '            actions.WrapContents = true;\n            actions.AutoScroll = false;\n', 1)

# The Open button keeps its familiar name but now accepts multiple PDFs.
s = s.replace('Button open = MakeButton("Mở PDF", 100, true); open.Margin = new Padding(0, 0, 8, 0); open.Click += delegate { OpenPdf(); }; actions.Controls.Add(open);',
              'Button open = MakeButton("Mở PDF", 100, true); open.Margin = new Padding(0, 0, 8, 0); open.Click += delegate { OpenPdf(); }; actions.Controls.Add(open); _toolTip = _toolTip ?? new ToolTip(); _toolTip.SetToolTip(open, "Có thể chọn một hoặc nhiều tệp PDF cùng lúc.");', 1)

# Direction controls were fixed-width in v2.4.5, which can clip at another DPI/font metric.
old_direction = '''            FlowLayoutPanel directionInline = new FlowLayoutPanel(); directionInline.WrapContents = false; directionInline.AutoSize = false; directionInline.Size = new Size(300, 38); directionInline.Margin = new Padding(4, 0, 0, 0); directionInline.Padding = new Padding(4, 3, 0, 0);\n            Label dirLabel = new Label(); dirLabel.Text = "Chiều cắt:"; dirLabel.AutoSize = false; dirLabel.Size = new Size(72, 30); dirLabel.TextAlign = ContentAlignment.MiddleLeft; directionInline.Controls.Add(dirLabel);\n            _dirLtr.AutoSize = false; _dirLtr.Size = new Size(104, 30); _dirLtr.Margin = new Padding(0); directionInline.Controls.Add(_dirLtr);\n            _dirRtl.AutoSize = false; _dirRtl.Size = new Size(104, 30); _dirRtl.Margin = new Padding(0); directionInline.Controls.Add(_dirRtl);'''
new_direction = '''            FlowLayoutPanel directionInline = new FlowLayoutPanel(); directionInline.WrapContents = false; directionInline.AutoSize = true; directionInline.AutoSizeMode = AutoSizeMode.GrowAndShrink; directionInline.Margin = new Padding(4, 0, 0, 0); directionInline.Padding = new Padding(4, 4, 0, 0);\n            Label dirLabel = new Label(); dirLabel.Text = "Chiều cắt:"; dirLabel.AutoSize = true; dirLabel.Margin = new Padding(0, 7, 8, 0); directionInline.Controls.Add(dirLabel);\n            _dirLtr.AutoSize = true; _dirLtr.Margin = new Padding(0, 5, 10, 0); directionInline.Controls.Add(_dirLtr);\n            _dirRtl.AutoSize = true; _dirRtl.Margin = new Padding(0, 5, 0, 0); directionInline.Controls.Add(_dirRtl);'''
if old_direction not in s:
    raise SystemExit('direction inline marker missing')
s = s.replace(old_direction, new_direction, 1)

# Add the new far-left file column. Keep current page-order pane, preview and cut pane unchanged
# inside their existing split containers so the proven PDF logic stays untouched.
old_split = '''            SplitContainer outer = new SplitContainer(); outer.Dock = DockStyle.Fill; outer.Orientation = Orientation.Vertical; outer.SplitterWidth = 6; root.Controls.Add(outer, 0, 1);\n            SplitContainer inner = new SplitContainer(); inner.Dock = DockStyle.Fill; inner.Orientation = Orientation.Vertical; inner.SplitterWidth = 6; outer.Panel2.Controls.Add(inner);\n            inner.FixedPanel = FixedPanel.Panel2; inner.Panel2Collapsed = false;'''
new_split = '''            SplitContainer fileOuter = new SplitContainer(); fileOuter.Dock = DockStyle.Fill; fileOuter.Orientation = Orientation.Vertical; fileOuter.SplitterWidth = 6; fileOuter.IsSplitterFixed = false; root.Controls.Add(fileOuter, 0, 1);\n            SplitContainer outer = new SplitContainer(); outer.Dock = DockStyle.Fill; outer.Orientation = Orientation.Vertical; outer.SplitterWidth = 6; outer.IsSplitterFixed = false; fileOuter.Panel2.Controls.Add(outer);\n            SplitContainer inner = new SplitContainer(); inner.Dock = DockStyle.Fill; inner.Orientation = Orientation.Vertical; inner.SplitterWidth = 6; inner.IsSplitterFixed = false; outer.Panel2.Controls.Add(inner);\n            inner.Panel2Collapsed = false;'''
if old_split not in s:
    raise SystemExit('body split-container marker missing')
s = s.replace(old_split, new_split, 1)

# Replace fixed width-only responsive logic with measured, wrap-aware layout. Splitter ratios are
# applied once; later resizes only clamp invalid distances, so user drag positions are respected.
old_responsive = '''            // Apply splitter limits only after the form has a real client size.\n            Action applyResponsiveLayout = delegate\n            {\n                if (IsDisposed) return;\n                // v2.4.5: keep the maximized chrome compact so the PDF gets more vertical space,\n                // but reserve a taller toolbar on normal/narrow windows so no command is clipped.\n                bool compactChrome = ClientSize.Width >= 1380;\n                float topHeight = compactChrome ? 184f : 218f;\n                root.RowStyles[0].Height = topHeight;\n                header.Height = 52;\n                toolbar.Height = compactChrome ? 132 : 166;\n                manualButtons.WrapContents = !compactChrome;\n                ConfigureSplitterSafe(outer, 330, 250, 760);\n                if (!inner.Panel2Collapsed) ConfigureRightPaneRatio(inner, 0.14, 215, 260);\n                ApplyZoom();\n            };'''
new_responsive = '''            // v2.5.0: runtime-measured layout. Do not assume 96-DPI text width.\n            // Initial splitter ratios are set once; after the user drags a divider, resize only clamps\n            // impossible positions and never resets the user's chosen column widths.\n            bool splittersInitialized = false;\n            Action applyResponsiveLayout = delegate\n            {\n                if (IsDisposed || _applyingResponsiveLayout) return;\n                _applyingResponsiveLayout = true;\n                try\n                {\n                    header.Height = 52; actions.WrapContents = true; actions.AutoScroll = false; manualButtons.WrapContents = true;\n                    int actionWidth = Math.Max(280, actions.ClientSize.Width - actions.Padding.Horizontal);\n                    int manualWidth = Math.Max(280, manualButtons.ClientSize.Width - manualButtons.Padding.Horizontal);\n                    int actionHeight = Math.Max(44, actions.GetPreferredSize(new Size(actionWidth, 0)).Height + 4);\n                    int settingsHeight = Math.Max(64, manualButtons.GetPreferredSize(new Size(manualWidth, 0)).Height + 8);\n                    toolbarGrid.RowStyles[1].SizeType = SizeType.Absolute; toolbarGrid.RowStyles[1].Height = actionHeight;\n                    toolbarGrid.RowStyles[2].SizeType = SizeType.Absolute; toolbarGrid.RowStyles[2].Height = settingsHeight;\n                    toolbar.Height = 25 + actionHeight + settingsHeight + 8;\n                    root.RowStyles[0].SizeType = SizeType.Absolute; root.RowStyles[0].Height = header.Height + toolbar.Height;\n\n                    if (!splittersInitialized)\n                    {\n                        ConfigureSplitterSafe(fileOuter, 220, 160, 820);\n                        ConfigureSplitterSafe(outer, 320, 260, 560);\n                        if (!inner.Panel2Collapsed) ConfigureRightPaneRatio(inner, 0.14, 200, 235);\n                        splittersInitialized = true;\n                    }\n                    else\n                    {\n                        ClampSplitterForResize(fileOuter, 150, 700);\n                        ClampSplitterForResize(outer, 240, 480);\n                        if (!inner.Panel2Collapsed) ClampRightPaneForResize(inner, 190, 360);\n                    }\n                    ApplyZoom();\n                }\n                finally { _applyingResponsiveLayout = false; }\n            };'''
if old_responsive not in s:
    raise SystemExit('responsive layout marker missing')
s = s.replace(old_responsive, new_responsive, 1)

# Insert file-list pane immediately before the existing page-order pane.
left_marker = '            Panel leftPane = outer.Panel1; leftPane.Padding = new Padding(10);\n'
if left_marker not in s:
    raise SystemExit('left page pane marker missing')
file_pane = '''            Panel filePane = fileOuter.Panel1; filePane.Padding = new Padding(8); filePane.BackColor = Color.FromArgb(248, 249, 251);\n            TableLayoutPanel fileLayout = new TableLayoutPanel(); fileLayout.Dock = DockStyle.Fill; fileLayout.ColumnCount = 1; fileLayout.RowCount = 3;\n            fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 30)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 28)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); filePane.Controls.Add(fileLayout);\n            Label fileTitle = new Label(); fileTitle.Text = "TỆP ĐANG XỬ LÝ"; fileTitle.Font = new Font("Segoe UI", 10.5f, FontStyle.Bold); fileTitle.Dock = DockStyle.Fill; fileTitle.TextAlign = ContentAlignment.MiddleLeft; fileLayout.Controls.Add(fileTitle, 0, 0);\n            Label fileHint = new Label(); fileHint.Text = "Mở PDF có thể chọn nhiều tệp"; fileHint.Dock = DockStyle.Fill; fileHint.ForeColor = Color.DimGray; fileHint.AutoEllipsis = true; fileLayout.Controls.Add(fileHint, 0, 1);\n            _fileList = new ListView(); _fileList.Dock = DockStyle.Fill; _fileList.View = View.Details; _fileList.FullRowSelect = true; _fileList.HideSelection = false; _fileList.MultiSelect = false; _fileList.ShowItemToolTips = true; _fileList.BackColor = Color.White; _fileList.BorderStyle = BorderStyle.FixedSingle; _fileList.Columns.Add("Tệp PDF", 200); _fileList.SelectedIndexChanged += FileSelectionChanged; fileLayout.Controls.Add(_fileList, 0, 2);\n            _fileList.Resize += delegate { if (_fileList.Columns.Count > 0) _fileList.Columns[0].Width = Math.Max(80, _fileList.ClientSize.Width - 5); };\n\n'''
s = s.replace(left_marker, file_pane + left_marker, 1)

# Page list should follow the width the user gives column 2. Navigation wraps if the pane is narrowed.
s = s.replace('FlowLayoutPanel navRow = new FlowLayoutPanel(); navRow.Dock = DockStyle.Fill; navRow.WrapContents = false;',
              'FlowLayoutPanel navRow = new FlowLayoutPanel(); navRow.Dock = DockStyle.Fill; navRow.WrapContents = true;', 1)
list_marker = '_list = new ListView(); _list.Dock = DockStyle.Fill; _list.View = View.Details; _list.FullRowSelect = true; _list.HideSelection = false; _list.MultiSelect = false; _list.SmallImageList = _thumbs; _list.Columns.Add("Trang", 285); _list.AllowDrop = true;'
if list_marker not in s:
    raise SystemExit('page list marker missing')
s = s.replace(list_marker, list_marker.replace('_list.AllowDrop = true;', '_list.AllowDrop = true; _list.Resize += delegate { if (_list.Columns.Count > 0) _list.Columns[0].Width = Math.Max(120, _list.ClientSize.Width - 5); };'), 1)

# Add splitter clamp helpers before MakeButton. They preserve a user's drag positions.
make_marker = '        private Button MakeButton(string text, int width, bool prominent)\n'
if make_marker not in s:
    raise SystemExit('MakeButton marker missing')
helpers = '''        private static void ClampSplitterForResize(SplitContainer split, int panel1Min, int panel2Min)\n        {\n            if (split == null || split.IsDisposed) return;\n            int total = split.Orientation == Orientation.Vertical ? split.ClientSize.Width : split.ClientSize.Height;\n            if (total <= split.SplitterWidth + 2) return;\n            split.Panel1MinSize = 0; split.Panel2MinSize = 0;\n            int min = Math.Max(1, Math.Min(panel1Min, total - split.SplitterWidth - 1));\n            int max = Math.Max(min, total - split.SplitterWidth - Math.Max(1, panel2Min));\n            int wanted = Math.Max(min, Math.Min(max, split.SplitterDistance));\n            if (wanted != split.SplitterDistance) split.SplitterDistance = wanted;\n            if (total >= panel1Min + panel2Min + split.SplitterWidth) { split.Panel1MinSize = panel1Min; split.Panel2MinSize = panel2Min; }\n        }\n\n        private static void ClampRightPaneForResize(SplitContainer split, int minRight, int minLeft)\n        {\n            if (split == null || split.IsDisposed) return;\n            int total = split.Orientation == Orientation.Vertical ? split.ClientSize.Width : split.ClientSize.Height;\n            if (total <= split.SplitterWidth + 2) return;\n            split.Panel1MinSize = 0; split.Panel2MinSize = 0;\n            int right = total - split.SplitterWidth - split.SplitterDistance;\n            int maxRight = Math.Max(1, total - split.SplitterWidth - minLeft);\n            right = Math.Max(Math.Min(minRight, maxRight), Math.Min(maxRight, right));\n            int wanted = total - split.SplitterWidth - right; wanted = Math.Max(1, Math.Min(total - split.SplitterWidth - 1, wanted));\n            if (wanted != split.SplitterDistance) split.SplitterDistance = wanted;\n            if (total >= minLeft + minRight + split.SplitterWidth) { split.Panel1MinSize = minLeft; split.Panel2MinSize = minRight; }\n        }\n\n'''
s = s.replace(make_marker, helpers + make_marker, 1)

# Root cause of clipped text: MakeButton trusted a 96-DPI magic width. Measure the real rendered
# text at runtime and allocate enough width at the current monitor DPI/font metrics.
old_make = '''        private Button MakeButton(string text, int width, bool prominent)\n        {\n            Button b = new Button(); b.Text = text; b.Width = width; b.Height = 38; b.TabStop = false; b.FlatStyle = FlatStyle.Flat; b.UseVisualStyleBackColor = false;\n            b.FlatAppearance.BorderSize = 1; b.Padding = new Padding(5,0,5,0);\n            b.FlatAppearance.BorderColor = prominent ? Color.FromArgb(37, 99, 235) : Color.FromArgb(203, 213, 225);\n            b.BackColor = prominent ? Color.FromArgb(37, 99, 235) : Color.White; b.ForeColor = prominent ? Color.White : Color.FromArgb(30,41,59);\n            b.FlatAppearance.MouseOverBackColor = prominent ? Color.FromArgb(29,78,216) : Color.FromArgb(241,245,249);\n            b.FlatAppearance.MouseDownBackColor = prominent ? Color.FromArgb(30,64,175) : Color.FromArgb(226,232,240);\n            b.Font = new Font("Segoe UI", 9.25f, FontStyle.Bold);\n            return b;\n        }'''
new_make = '''        private Button MakeButton(string text, int width, bool prominent)\n        {\n            Button b = new Button(); b.Text = text; b.Height = 38; b.TabStop = false; b.FlatStyle = FlatStyle.Flat; b.UseVisualStyleBackColor = false; b.AutoEllipsis = false; b.UseCompatibleTextRendering = false;\n            b.FlatAppearance.BorderSize = 1; b.Padding = new Padding(5,0,5,0);\n            b.FlatAppearance.BorderColor = prominent ? Color.FromArgb(37, 99, 235) : Color.FromArgb(203, 213, 225);\n            b.BackColor = prominent ? Color.FromArgb(37, 99, 235) : Color.White; b.ForeColor = prominent ? Color.White : Color.FromArgb(30,41,59);\n            b.FlatAppearance.MouseOverBackColor = prominent ? Color.FromArgb(29,78,216) : Color.FromArgb(241,245,249);\n            b.FlatAppearance.MouseDownBackColor = prominent ? Color.FromArgb(30,64,175) : Color.FromArgb(226,232,240);\n            b.Font = new Font("Segoe UI", 9.25f, FontStyle.Bold);\n            Size measured = TextRenderer.MeasureText(text ?? "", b.Font, new Size(int.MaxValue, int.MaxValue), TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix);\n            b.Width = Math.Max(width, measured.Width + b.Padding.Horizontal + 22);\n            b.Height = Math.Max(38, measured.Height + 14);\n            return b;\n        }'''
if old_make not in s:
    raise SystemExit('MakeButton implementation marker missing')
s = s.replace(old_make, new_make, 1)

# -----------------------------------------------------------------------------
# Multi-document workspace methods. Keep LoadPdf(string) for regression tests and callers.
# -----------------------------------------------------------------------------
open_start = s.find('        private void OpenPdf()\n')
thumb_start = s.find('        private void BeginThumbnailBuild()\n', open_start)
if open_start < 0 or thumb_start < 0:
    raise SystemExit('OpenPdf/BeginThumbnailBuild method boundary missing')
workspace_methods = r'''        private static AppSnapshot CloneAppSnapshot(AppSnapshot src)
        {
            if (src == null) return null;
            AppSnapshot copy = new AppSnapshot(); copy.IsSplit = src.IsSplit; copy.DetachedMode = src.DetachedMode; copy.LeftToRight = src.LeftToRight; copy.SelectedIndex = src.SelectedIndex;
            for (int i = 0; i < src.Sources.Count; i++) copy.Sources.Add(src.Sources[i].Clone());
            for (int i = 0; i < src.Outputs.Count; i++) copy.Outputs.Add(src.Outputs[i].Clone());
            return copy;
        }

        private static void CopySnapshotStack(Stack<AppSnapshot> from, Stack<AppSnapshot> to)
        {
            to.Clear(); if (from == null) return; AppSnapshot[] a = from.ToArray();
            for (int i = a.Length - 1; i >= 0; i--) to.Push(CloneAppSnapshot(a[i]));
        }

        private DocumentWorkspace FindDocumentByPath(string path)
        {
            string full = Path.GetFullPath(path);
            for (int i = 0; i < _documents.Count; i++) if (string.Equals(_documents[i].SourcePath, full, StringComparison.OrdinalIgnoreCase)) return _documents[i];
            return null;
        }

        private void RefreshFileListItem(DocumentWorkspace doc)
        {
            if (_fileList == null || doc == null) return;
            for (int i = 0; i < _fileList.Items.Count; i++)
            {
                if (!object.ReferenceEquals(_fileList.Items[i].Tag, doc)) continue;
                string name = Path.GetFileName(doc.SourcePath);
                if (!string.IsNullOrEmpty(doc.LastError)) name = "⚠ " + name;
                else if (doc.PageCount > 0) name += "  •  " + doc.PageCount.ToString() + " mặt";
                _fileList.Items[i].Text = name;
                _fileList.Items[i].ToolTipText = string.IsNullOrEmpty(doc.LastError) ? doc.SourcePath : doc.SourcePath + "\r\n" + doc.LastError;
                break;
            }
        }

        private void SelectDocumentInFileList(DocumentWorkspace doc)
        {
            if (_fileList == null || doc == null) return;
            _suspendDocumentSelection = true;
            try
            {
                for (int i = 0; i < _fileList.Items.Count; i++)
                {
                    bool selected = object.ReferenceEquals(_fileList.Items[i].Tag, doc);
                    _fileList.Items[i].Selected = selected; _fileList.Items[i].Focused = selected;
                    if (selected) _fileList.EnsureVisible(i);
                }
            }
            finally { _suspendDocumentSelection = false; }
        }

        private void PersistActiveDocumentState()
        {
            if (_activeDocument == null || !_activeDocument.Initialized || _pdf == null) return;
            _activeDocument.PageCount = _pdf.PageCount;
            _activeDocument.Snapshot = CloneAppSnapshot(CaptureCurrent());
            CopySnapshotStack(_undo, _activeDocument.Undo); CopySnapshotStack(_redo, _activeDocument.Redo);
            _activeDocument.SourceWasOverwritten = _sourceWasOverwritten; _activeDocument.OriginalBackupPath = _originalBackupPath;
            _activeDocument.ZoomPercent = _zoom == null ? 100 : _zoom.Value; _activeDocument.LastError = "";
            RefreshFileListItem(_activeDocument);
        }

        private void CloseActiveRuntimeForSwitch()
        {
            try { if (_thumbCts != null) _thumbCts.Cancel(); } catch { }
            try { if (_previewCts != null) _previewCts.Cancel(); } catch { }
            try { if (_prefetchCts != null) _prefetchCts.Cancel(); } catch { }
            if (_previewCts != null) { _previewCts.Dispose(); _previewCts = null; }
            if (_prefetchCts != null) { _prefetchCts.Dispose(); _prefetchCts = null; }
            _thumbCts = null; Interlocked.Increment(ref _previewTicket); _previewModelKey = "";
            if (_previewMaster != null) { try { _previewMaster.Dispose(); } catch { } _previewMaster = null; }
            ClearPreviewCache();
            if (_preview != null) _preview.Image = null;
            _pdf = null; _previewPdf = null; _prefetchPdf = null;
            if (_list != null) _list.Items.Clear(); if (_thumbs != null) _thumbs.Images.Clear();
        }

        private void EnsureWorkspaceCopy(DocumentWorkspace doc)
        {
            if (doc == null) throw new ArgumentNullException("doc");
            if (string.IsNullOrEmpty(doc.SourcePath) || !File.Exists(doc.SourcePath)) throw new FileNotFoundException("Không tìm thấy tệp PDF nguồn.", doc.SourcePath);
            if (!string.IsNullOrEmpty(doc.WorkPath) && File.Exists(doc.WorkPath)) return;
            doc.SessionDir = AppDiagnostics.CreateSessionDirectory(); doc.WorkPath = Path.Combine(doc.SessionDir, "work.pdf");
            File.Copy(doc.SourcePath, doc.WorkPath, true);
        }

        private void OpenWorkspaceRuntime(DocumentWorkspace doc)
        {
            EnsureWorkspaceCopy(doc);
            _sourcePath = doc.SourcePath; _sessionDir = doc.SessionDir; _workPath = doc.WorkPath;
            _pdf = new PdfSession(_workPath); _previewPdf = new PdfSession(_workPath); _prefetchPdf = new PdfSession(_workPath);
            if (_pdf.PageCount <= 0) throw new InvalidDataException("PDF không có trang.");

            _sources.Clear(); _outputs.Clear(); _undo.Clear(); _redo.Clear();
            _sourceWasOverwritten = doc.SourceWasOverwritten; _originalBackupPath = doc.OriginalBackupPath;
            if (doc.Initialized && doc.Snapshot != null)
            {
                AppSnapshot state = doc.Snapshot;
                for (int i = 0; i < state.Sources.Count; i++) _sources.Add(state.Sources[i].Clone());
                for (int i = 0; i < state.Outputs.Count; i++) _outputs.Add(state.Outputs[i].Clone());
                _isSplit = state.IsSplit; _modeDetached.Checked = state.DetachedMode; _modeBound.Checked = !state.DetachedMode; _dirLtr.Checked = state.LeftToRight; _dirRtl.Checked = !state.LeftToRight;
                CopySnapshotStack(doc.Undo, _undo); CopySnapshotStack(doc.Redo, _redo);
            }
            else
            {
                _isSplit = false; _modeDetached.Checked = true; _modeBound.Checked = false; _dirLtr.Checked = true; _dirRtl.Checked = false;
                for (int i = 0; i < _pdf.PageCount; i++) _sources.Add(new SourceFace { OriginalSourceIndex = i, Rotation = 0, CutPercent = 50.0 });
                doc.Initialized = true; doc.PageCount = _pdf.PageCount; doc.ZoomPercent = 100;
            }

            _activeDocument = doc; doc.PageCount = _pdf.PageCount; doc.LastError = "";
            _fileLabel.Text = "File đang mở: " + Path.GetFileName(_sourcePath);
            if (_zoom != null) _zoom.Value = Math.Max(_zoom.Minimum, Math.Min(_zoom.Maximum, doc.ZoomPercent));
            int preferred = doc.Snapshot == null ? 0 : doc.Snapshot.SelectedIndex;
            RefreshList(preferred); BeginThumbnailBuild(); RefreshFileListItem(doc); SelectDocumentInFileList(doc);
            SetStatus("Đang xử lý " + Path.GetFileName(_sourcePath) + " • " + _pdf.PageCount.ToString() + " mặt quét • " + (_documents.IndexOf(doc) + 1).ToString() + "/" + _documents.Count.ToString() + " tệp.");
        }

        private void ActivateDocument(DocumentWorkspace doc)
        {
            if (doc == null || _busy || object.ReferenceEquals(doc, _activeDocument)) return;
            DocumentWorkspace previous = _activeDocument;
            SetBusy(true, "Đang chuyển tệp PDF...");
            try
            {
                PersistActiveDocumentState();
                CloseActiveRuntimeForSwitch();
                OpenWorkspaceRuntime(doc);
            }
            catch (Exception ex)
            {
                AppDiagnostics.LogException("DOCUMENT_SWITCH_FAIL", ex); doc.LastError = ex.Message; RefreshFileListItem(doc);
                CloseActiveRuntimeForSwitch(); _activeDocument = null;
                bool recovered = false;
                if (previous != null && previous.Initialized)
                {
                    try { OpenWorkspaceRuntime(previous); recovered = true; } catch (Exception rex) { AppDiagnostics.LogException("DOCUMENT_RECOVER_FAIL", rex); }
                }
                if (!recovered)
                {
                    _sources.Clear(); _outputs.Clear(); _undo.Clear(); _redo.Clear(); _isSplit = false; _sourcePath = ""; _workPath = ""; _sessionDir = "";
                    _fileLabel.Text = "File đang mở: Chưa mở tài liệu"; _selectionLabel.Text = "Đang chọn: -";
                }
                MessageBox.Show(this, "Không mở được PDF.\r\n\r\n" + ex.Message, "Lỗi mở PDF", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally { SetBusy(false, null); UpdateButtons(); }
        }

        private void FileSelectionChanged(object sender, EventArgs e)
        {
            if (_suspendDocumentSelection || _busy || _fileList == null || _fileList.SelectedItems.Count == 0) return;
            DocumentWorkspace doc = _fileList.SelectedItems[0].Tag as DocumentWorkspace; if (doc != null) ActivateDocument(doc);
        }

        private void AddPdfPaths(string[] paths, bool activateFirst)
        {
            if (paths == null || paths.Length == 0) return;
            DocumentWorkspace first = null;
            _suspendDocumentSelection = true;
            try
            {
                foreach (string raw in paths)
                {
                    if (string.IsNullOrWhiteSpace(raw)) continue;
                    string full;
                    try { full = Path.GetFullPath(raw); } catch { continue; }
                    if (!File.Exists(full) || !string.Equals(Path.GetExtension(full), ".pdf", StringComparison.OrdinalIgnoreCase)) continue;
                    DocumentWorkspace doc = FindDocumentByPath(full);
                    if (doc == null)
                    {
                        doc = new DocumentWorkspace { SourcePath = full };
                        _documents.Add(doc);
                        ListViewItem item = new ListViewItem(Path.GetFileName(full)); item.Tag = doc; item.ToolTipText = full; _fileList.Items.Add(item);
                    }
                    if (first == null) first = doc;
                }
            }
            finally { _suspendDocumentSelection = false; }
            if (activateFirst && first != null)
            {
                if (object.ReferenceEquals(first, _activeDocument)) SelectDocumentInFileList(first);
                else ActivateDocument(first);
            }
            if (_documents.Count > 0 && _activeDocument == null && first != null && !activateFirst) ActivateDocument(first);
        }

        private void OpenPdf()
        {
            if (_busy) return;
            using (OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "Tài liệu PDF (*.pdf)|*.pdf"; dlg.Title = "Chọn một hoặc nhiều tài liệu PDF"; dlg.Multiselect = true;
                if (dlg.ShowDialog(this) != DialogResult.OK) return;
                AddPdfPaths(dlg.FileNames, true);
            }
        }

        // Kept for smoke tests and compatibility with the proven single-document flow.
        private void LoadPdf(string path) { AddPdfPaths(new string[] { path }, true); }

'''
s = s[:open_start] + workspace_methods + s[thumb_start:]

# Busy state must lock the file selector too, preventing state switches during export/AI/edits.
old_busy = '            _list.Enabled = !busy;\n'
if old_busy not in s:
    raise SystemExit('SetBusy list marker missing')
s = s.replace(old_busy, '            _list.Enabled = !busy; if (_fileList != null) _fileList.Enabled = !busy;\n', 1)

# Keep active document restore flags synchronized immediately after a successful overwrite/restore.
s = s.replace('SetStatus("Đã lưu vào file gốc. Bản gốc an toàn: " + _originalBackupPath); _sourceWasOverwritten = true;',
              'SetStatus("Đã lưu vào file gốc. Bản gốc an toàn: " + _originalBackupPath); _sourceWasOverwritten = true; if (_activeDocument != null) { _activeDocument.SourceWasOverwritten = true; _activeDocument.OriginalBackupPath = _originalBackupPath; }', 1)
s = s.replace('_sourceWasOverwritten=false;\n                }', '_sourceWasOverwritten=false; if (_activeDocument != null) _activeDocument.SourceWasOverwritten = false;\n                }', 1)

# Multi-file workflow smoke: prove per-file page count/state survives switching.
smoke_insert_marker = '''                _btnFitStable.PerformClick(); Application.DoEvents();\n                if (_zoom.Value != 100) throw new InvalidOperationException("Workflow smoke: fit-to-window did not restore 100%.");\n\n                AppDiagnostics.Log("WORKFLOW_SMOKE", "PASS");'''
if smoke_insert_marker not in s:
    raise SystemExit('workflow smoke final marker missing')
smoke_multi = '''                _btnFitStable.PerformClick(); Application.DoEvents();\n                if (_zoom.Value != 100) throw new InvalidOperationException("Workflow smoke: fit-to-window did not restore 100%.");\n\n                // v2.5.0 multi-file regression: add another PDF, switch away and back, and verify\n                // that the first document's split/cut/order state remains isolated and intact.\n                DocumentWorkspace firstWorkspace = _activeDocument;\n                string pdfPath2 = Path.Combine(dir, "workflow-smoke-second.pdf");\n                SimplePdfWriter.WriteFromFactory(pdfPath2, 5, delegate(int index)\n                {\n                    using (Bitmap b = new Bitmap(500, 360, PixelFormat.Format24bppRgb))\n                    using (Graphics g = Graphics.FromImage(b))\n                    {\n                        g.Clear(Color.White); using (Font f = new Font("Segoe UI", 22f, FontStyle.Bold)) g.DrawString("FILE 2 - " + (index + 1).ToString(), f, Brushes.Black, 30, 30);\n                        using (MemoryStream ms = new MemoryStream()) { b.Save(ms, ImageFormat.Jpeg); return new SimplePdfWriter.ImagePage { Jpeg = ms.ToArray(), PixelWidth = b.Width, PixelHeight = b.Height, Dpi = 120.0 }; }\n                    }\n                }, null);\n                AddPdfPaths(new string[] { pdfPath2 }, true); Application.DoEvents();\n                if (_documents.Count != 2 || _fileList.Items.Count != 2) throw new InvalidOperationException("Workflow smoke: multi-file list did not contain two documents.");\n                if (_activeDocument == null || object.ReferenceEquals(_activeDocument, firstWorkspace) || _sources.Count != 5 || _isSplit) throw new InvalidOperationException("Workflow smoke: second PDF did not load as an isolated 5-page document.");\n                DocumentWorkspace secondWorkspace = _activeDocument;\n                ActivateDocument(firstWorkspace); Application.DoEvents();\n                if (!object.ReferenceEquals(_activeDocument, firstWorkspace) || !_isSplit || _outputs.Count != 28) throw new InvalidOperationException("Workflow smoke: first PDF split state was lost after switching files.");\n                bool cutPersisted = false; foreach (OutputPage op in _outputs) if (op.SourceId == sourceId && Math.Abs(op.CutPercent - 53.5) <= 0.01) { cutPersisted = true; break; }\n                if (!cutPersisted) throw new InvalidOperationException("Workflow smoke: per-file manual cut state was lost after switching files.");\n                ActivateDocument(secondWorkspace); Application.DoEvents();\n                if (!object.ReferenceEquals(_activeDocument, secondWorkspace) || _sources.Count != 5 || _isSplit) throw new InvalidOperationException("Workflow smoke: second PDF state was contaminated by first PDF.");\n\n                AppDiagnostics.Log("WORKFLOW_SMOKE", "PASS");'''
s = s.replace(smoke_insert_marker, smoke_multi, 1)

# Cleanup now owns every workspace session directory, not only the currently active one.
cleanup_start = s.find('        private void CleanupSession()\n')
program_start = s.find('    internal static class Program\n', cleanup_start)
if cleanup_start < 0 or program_start < 0:
    raise SystemExit('CleanupSession boundary missing')
new_cleanup = r'''        private void CleanupSession()
        {
            try { PersistActiveDocumentState(); } catch { }
            try { CloseActiveRuntimeForSwitch(); } catch { }
            List<string> dirs = new List<string>();
            for (int i = 0; i < _documents.Count; i++) if (!string.IsNullOrEmpty(_documents[i].SessionDir)) dirs.Add(_documents[i].SessionDir);
            _documents.Clear(); _activeDocument = null; _sources.Clear(); _outputs.Clear(); _undo.Clear(); _redo.Clear(); _isSplit = false;
            _sourcePath = ""; _workPath = ""; _sessionDir = ""; _sourceWasOverwritten = false; _originalBackupPath = "";
            if (_list != null) _list.Items.Clear(); if (_thumbs != null) _thumbs.Images.Clear(); if (_fileList != null) _fileList.Items.Clear();
            if (_fileLabel != null) _fileLabel.Text = "File đang mở: Chưa mở tài liệu"; if (_selectionLabel != null) _selectionLabel.Text = "Đang chọn: -";
            if (dirs.Count > 0) Task.Run(delegate { foreach (string d in dirs) try { Thread.Sleep(50); if (Directory.Exists(d)) Directory.Delete(d, true); } catch { } });
            GC.Collect(); GC.WaitForPendingFinalizers();
        }
    }

'''
# Preserve class closing then Program marker: program_start currently points after MainForm's closing brace.
s = s[:cleanup_start] + new_cleanup + s[program_start:]

# UI smoke must cover the new four-column geometry and button text fit.
req_marker = '                            "THỨ TỰ TRANG",\n                            "XEM TRƯỚC",\n'
if req_marker not in s:
    raise SystemExit('UI smoke required array marker missing')
s = s.replace(req_marker, '                            "TỆP ĐANG XỬ LÝ",\n                            "THỨ TỰ TRANG",\n                            "XEM TRƯỚC",\n', 1)

# Add a button text-fit assertion helper before AssertUiControlVisible.
assert_marker = '        private static void AssertUiControlVisible(Form form, string text)\n'
if assert_marker not in s:
    raise SystemExit('AssertUiControlVisible marker missing')
textfit_helper = '''        private static void AssertButtonTextFits(Form form, string text)\n        {\n            Button b = FindControlByText(form, text) as Button; if (b == null) throw new InvalidOperationException("UI button missing: " + text);\n            Size need = TextRenderer.MeasureText(b.Text ?? "", b.Font, new Size(int.MaxValue, int.MaxValue), TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix);\n            int available = Math.Max(0, b.ClientSize.Width - b.Padding.Horizontal - 8);\n            if (available < need.Width) throw new InvalidOperationException("Button text clipped: " + text + " need=" + need.Width.ToString() + " available=" + available.ToString());\n        }\n\n'''
s = s.replace(assert_marker, textfit_helper + assert_marker, 1)

smoke_loop = '                            foreach (string text in required) AssertUiControlVisible(form, text);\n'
if smoke_loop not in s:
    raise SystemExit('UI smoke loop marker missing')
smoke_checks = '''                            foreach (string text in required) AssertUiControlVisible(form, text);\n                            foreach (string btxt in new string[]{"Mở PDF","TỰ XOAY THÔNG MINH","TỰ CHIA & SẮP XẾP","Xuất PDF","Lưu vào file gốc","Khôi phục PDF gốc","↶ Xoay trái 90°","↷ Xoay phải 90°","Xoay 180°","Xóa trang PDF","Làm lại","Hoàn tác"}) AssertButtonTextFits(form, btxt);\n                            Control col1 = FindControlByText(form, "TỆP ĐANG XỬ LÝ"); Control col2 = FindControlByText(form, "THỨ TỰ TRANG"); Control col3 = FindControlByText(form, "XEM TRƯỚC"); Control col4 = FindControlByText(form, "CHỈNH ĐƯỜNG CẮT");\n                            if (col1 == null || col2 == null || col3 == null || col4 == null) throw new InvalidOperationException("Four-column workspace headers missing.");\n                            Rectangle c1=col1.RectangleToScreen(col1.ClientRectangle), c2=col2.RectangleToScreen(col2.ClientRectangle), c3=col3.RectangleToScreen(col3.ClientRectangle), c4=col4.RectangleToScreen(col4.ClientRectangle);\n                            if (!(c1.Left < c2.Left && c2.Left < c3.Left && c3.Left < c4.Left)) throw new InvalidOperationException("Four-column workspace order is incorrect.");\n                            if (c4.Width > Math.Max(280, form.ClientSize.Width / 4)) throw new InvalidOperationException("Manual cut column is too wide by default.");\n'''
s = s.replace(smoke_loop, smoke_checks, 1)

# Launcher/runtime identity must match managed app and cache folder.
launcher = Path('tach-xep-pdf-v2.3.2/launcher.cpp')
if launcher.exists():
    ls = launcher.read_text(encoding='utf-8-sig')
    ls2 = ls.replace('2.4.5', '2.5.0')
    if ls2 == ls:
        raise SystemExit('launcher 2.4.5 marker missing')
    launcher.write_text(ls2, encoding='utf-8-sig')

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V250_MULTI_PDF_DPI_SAFE_UI_OK')
