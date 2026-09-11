from pathlib import Path
import re
root=Path('tach-xep-pdf-v2.3.2')
p=root/'TachXepTrangPDF.cs'
s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit('v280 marker missing: '+label)
    s=s.replace(old,new,count)

# Version identity
rep('internal const string Version = "2.7.0";','internal const string Version = "2.8.0";','diag version')
rep('startup-v2.7.0.log','startup-v2.8.0.log','startup log')
rep('private const string AppVersion = "2.7.0";','private const string AppVersion = "2.8.0";','app version')

# Diagnostics + backup/session housekeeping
old='''        internal static string LogDirectory { get { return Path.Combine(BaseDirectory, "Logs"); } }\n        internal static string SessionDirectory { get { return Path.Combine(BaseDirectory, "Sessions"); } }\n        internal static string StartupLogPath { get { return Path.Combine(LogDirectory, "startup-v2.8.0.log"); } }\n\n        internal static void Initialize()\n        {\n            try\n            {\n                Directory.CreateDirectory(LogDirectory);\n                Directory.CreateDirectory(SessionDirectory);\n                Log("START", "App v" + Version + " | OS=" + Environment.OSVersion.VersionString + " | 64bit=" + Environment.Is64BitProcess.ToString() + " | Base=" + AppContext.BaseDirectory);\n            }\n            catch { }\n        }\n'''
new='''        internal static string LogDirectory { get { return Path.Combine(BaseDirectory, "Logs"); } }\n        internal static string SessionDirectory { get { return Path.Combine(BaseDirectory, "Sessions"); } }\n        internal static string BackupDirectory { get { return Path.Combine(BaseDirectory, "Backups"); } }\n        internal static string StartupLogPath { get { return Path.Combine(LogDirectory, "startup-v2.8.0.log"); } }\n        private static string BackupSessionCounterPath { get { return Path.Combine(BaseDirectory, "backup-cleanup-session-count.txt"); } }\n        private const int BackupCleanupEverySessions = 3;\n        private const int BackupKeepNewestFiles = 1;\n        private const long BackupMaxBytes = 2L * 1024L * 1024L * 1024L;\n\n        internal static void Initialize()\n        {\n            try\n            {\n                Directory.CreateDirectory(LogDirectory);\n                Directory.CreateDirectory(SessionDirectory);\n                Directory.CreateDirectory(BackupDirectory);\n                CleanupStaleSessionDirectories();\n                Log("START", "App v" + Version + " | OS=" + Environment.OSVersion.VersionString + " | 64bit=" + Environment.Is64BitProcess.ToString() + " | Base=" + AppContext.BaseDirectory);\n            }\n            catch { }\n        }\n\n        private static void CleanupStaleSessionDirectories()\n        {\n            try\n            {\n                if (!Directory.Exists(SessionDirectory)) return;\n                DateTime cutoff = DateTime.UtcNow.AddHours(-24);\n                foreach (string dir in Directory.GetDirectories(SessionDirectory))\n                {\n                    try { if (Directory.GetLastWriteTimeUtc(dir) < cutoff) Directory.Delete(dir, true); } catch { }\n                }\n            }\n            catch { }\n        }\n\n        internal static void RegisterClosedSessionAndMaybeCleanupBackups()\n        {\n            try\n            {\n                int count = 0;\n                if (File.Exists(BackupSessionCounterPath)) int.TryParse(File.ReadAllText(BackupSessionCounterPath).Trim(), out count);\n                count++;\n                long backupBytes = 0;\n                try { if (Directory.Exists(BackupDirectory)) backupBytes = Directory.GetFiles(BackupDirectory, "*.pdf", SearchOption.AllDirectories).Sum(delegate(string x) { try { return new FileInfo(x).Length; } catch { return 0L; } }); } catch { }\n                if (count >= BackupCleanupEverySessions || backupBytes > BackupMaxBytes)\n                {\n                    CleanupBackupsCore();\n                    count = 0;\n                }\n                File.WriteAllText(BackupSessionCounterPath, count.ToString(), Encoding.UTF8);\n            }\n            catch { }\n        }\n\n        private static void CleanupBackupsCore()\n        {\n            try\n            {\n                if (!Directory.Exists(BackupDirectory)) return;\n                List<FileInfo> files = Directory.GetFiles(BackupDirectory, "*.pdf", SearchOption.AllDirectories)\n                    .Select(delegate(string x) { return new FileInfo(x); })\n                    .Where(delegate(FileInfo x) { return x.Exists; })\n                    .OrderByDescending(delegate(FileInfo x) { return x.LastWriteTimeUtc; }).ToList();\n                long total = files.Sum(delegate(FileInfo x) { return x.Length; });\n                for (int i = BackupKeepNewestFiles; i < files.Count; i++)\n                {\n                    if (i >= BackupKeepNewestFiles || total > BackupMaxBytes)\n                    {\n                        try { long len = files[i].Length; files[i].Delete(); total = Math.Max(0, total - len); } catch { }\n                    }\n                }\n                foreach (string dir in Directory.GetDirectories(BackupDirectory, "*", SearchOption.AllDirectories).OrderByDescending(delegate(string x) { return x.Length; }))\n                    try { if (!Directory.EnumerateFileSystemEntries(dir).Any()) Directory.Delete(dir, false); } catch { }\n                Log("BACKUP_CLEANUP", "Automatic cleanup completed. Retained newest backup; max policy=" + BackupMaxBytes.ToString() + " bytes.");\n            }\n            catch (Exception ex) { LogException("BACKUP_CLEANUP_FAIL", ex); }\n        }\n'''
rep(old,new,'diagnostics cleanup')

# Theme group colors
rep('''        internal static readonly Color AccentDown = Color.FromArgb(30, 64, 175);\n        internal static readonly Color SecondaryHover = Color.FromArgb(241, 245, 249);\n''','''        internal static readonly Color AccentDown = Color.FromArgb(30, 64, 175);\n        internal static readonly Color SecondaryHover = Color.FromArgb(241, 245, 249);\n        internal static readonly Color Rotate = Color.FromArgb(79, 70, 229);\n        internal static readonly Color PageTools = Color.FromArgb(8, 145, 178);\n        internal static readonly Color Save = Color.FromArgb(22, 163, 74);\n        internal static readonly Color Restore = Color.FromArgb(217, 119, 6);\n        internal static readonly Color Danger = Color.FromArgb(220, 38, 38);\n        internal static readonly Color History = Color.FromArgb(71, 85, 105);\n        internal static readonly Color Completed = Color.FromArgb(22, 163, 74);\n        internal static readonly Color InProgress = Color.FromArgb(202, 138, 4);\n''','theme colors')

# Shared analyzer field and history limit
rep('''        private const string AppVersion = "2.8.0";\n        private const double ExportDpi = 200.0;\n''','''        private const string AppVersion = "2.8.0";\n        private const double ExportDpi = 200.0;\n        private const int HistoryLimit = 10;\n''','history constant')
rep('''        private ToolTip _toolTip;\n''','''        private ToolTip _toolTip;\n        private OnnxOrientationAnalyzer _orientationAnalyzer;\n''','analyzer field')

# Copy-on-write: one immutable session copy until a physical merge requires a revision file.
old='''            doc.SessionDir = AppDiagnostics.CreateSessionDirectory();\n            doc.OriginalWorkPath = Path.Combine(doc.SessionDir, "original-at-open.pdf");\n            doc.WorkPath = Path.Combine(doc.SessionDir, "work.pdf");\n            File.Copy(doc.SourcePath, doc.OriginalWorkPath, true);\n            File.Copy(doc.OriginalWorkPath, doc.WorkPath, true);\n'''
new='''            doc.SessionDir = AppDiagnostics.CreateSessionDirectory();\n            doc.OriginalWorkPath = Path.Combine(doc.SessionDir, "original-at-open.pdf");\n            File.Copy(doc.SourcePath, doc.OriginalWorkPath, true);\n            // v2.8 copy-on-write: read directly from the immutable session copy.\n            // A distinct work-merged revision is created only when a physical merge is required.\n            doc.WorkPath = doc.OriginalWorkPath;\n'''
rep(old,new,'copy-on-write')

# Toolbar no wrapping
rep('''            actions.WrapContents = true;\n            actions.AutoScroll = false;\n''','''            actions.WrapContents = false;\n            actions.AutoScroll = true;\n''','actions nowrap')
rep('''                    header.Height = 52; actions.WrapContents = true; actions.AutoScroll = false; manualButtons.WrapContents = true;\n''','''                    header.Height = 52; actions.WrapContents = false; actions.AutoScroll = true; manualButtons.WrapContents = false; manualButtons.AutoScroll = true;\n''','responsive nowrap')
rep('''                    int settingsHeight = Math.Max(64, manualButtons.GetPreferredSize(new Size(manualWidth, 0)).Height + 8);\n''','''                    int settingsHeight = Math.Max(94, manualButtons.GetPreferredSize(new Size(manualWidth, 0)).Height + 48);\n''','settings height')

# Save/restore top button colors
rep('''            _btnSaveOriginal = MakeButton("Lưu vào file gốc", 146, false); _btnSaveOriginal.Margin = new Padding(0, 0, 8, 0); _btnSaveOriginal.Click += async delegate { await ExportPdfAsync(true); }; actions.Controls.Add(_btnSaveOriginal);\n            _btnRestoreOriginal = MakeButton("Khôi phục PDF gốc", 154, false); _btnRestoreOriginal.Margin = new Padding(0, 0, 8, 0); _btnRestoreOriginal.Click += delegate { RestoreOriginalPdf(); }; actions.Controls.Add(_btnRestoreOriginal);\n''','''            _btnSaveOriginal = MakeButton("Lưu vào file gốc", 146, false); _btnSaveOriginal.Margin = new Padding(0, 0, 8, 0); _btnSaveOriginal.Click += async delegate { await ExportPdfAsync(true); }; actions.Controls.Add(_btnSaveOriginal); StyleGroupedButton(_btnSaveOriginal, UiTheme.Save);\n            _btnRestoreOriginal = MakeButton("Khôi phục PDF gốc", 154, false); _btnRestoreOriginal.Margin = new Padding(0, 0, 8, 0); _btnRestoreOriginal.Click += delegate { RestoreOriginalPdf(); }; actions.Controls.Add(_btnRestoreOriginal); StyleGroupedButton(_btnRestoreOriginal, UiTheme.Restore);\n''','save restore colors')

# Manual controls: two fixed rows + document tools under rotate.
old='''            TableLayoutPanel manualGrid = new TableLayoutPanel(); manualGrid.Dock = DockStyle.Fill; manualGrid.ColumnCount = 1; manualGrid.RowCount = 2; manualGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 0)); manual.Controls.Add(manualGrid);\n            FlowLayoutPanel manualButtons = new FlowLayoutPanel(); manualButtons.Dock = DockStyle.Fill; manualButtons.WrapContents = true; manualButtons.AutoScroll = false; manualGrid.Controls.Add(manualButtons, 0, 0);\n            manualButtons.Padding = new Padding(0, 2, 0, 0);\n            Button left = MakeButton("↶ Xoay trái 90°", 138, false); left.Margin = new Padding(0, 0, 5, 0); left.Click += delegate { RotateSelected(-90); }; manualButtons.Controls.Add(left);\n            Button right = MakeButton("↷ Xoay phải 90°", 142, false); right.Margin = new Padding(0, 0, 5, 0); right.Click += delegate { RotateSelected(90); }; manualButtons.Controls.Add(right);\n            Button flip = MakeButton("Xoay 180°", 105, false); flip.Margin = new Padding(0, 0, 5, 0); flip.Click += delegate { RotateSelected(180); }; manualButtons.Controls.Add(flip);\n            Button del = MakeButton("Xóa trang PDF", 118, false); del.Margin = new Padding(0, 0, 5, 0); del.Click += delegate { DeleteSelected(); }; manualButtons.Controls.Add(del);\n            _btnRedo = MakeButton("Làm lại", 86, false); _btnRedo.Margin = new Padding(0, 0, 5, 0); _btnRedo.Click += delegate { Redo(); }; manualButtons.Controls.Add(_btnRedo);\n            _btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Margin = new Padding(0, 0, 8, 0); _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo);\n'''
new='''            TableLayoutPanel manualGrid = new TableLayoutPanel(); manualGrid.Dock = DockStyle.Fill; manualGrid.ColumnCount = 1; manualGrid.RowCount = 3; manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 42)); manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 42)); manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 0)); manual.Controls.Add(manualGrid);\n            FlowLayoutPanel manualButtons = new FlowLayoutPanel(); manualButtons.Dock = DockStyle.Fill; manualButtons.WrapContents = false; manualButtons.AutoScroll = true; manualGrid.Controls.Add(manualButtons, 0, 0);\n            manualButtons.Padding = new Padding(0, 2, 0, 0);\n            Button left = MakeButton("Xoay trái 90°", 126, false); left.Margin = new Padding(0, 0, 5, 0); left.Click += delegate { RotateSelected(-90); }; manualButtons.Controls.Add(left); StyleGroupedButton(left, UiTheme.Rotate);\n            Button right = MakeButton("Xoay phải 90°", 130, false); right.Margin = new Padding(0, 0, 5, 0); right.Click += delegate { RotateSelected(90); }; manualButtons.Controls.Add(right); StyleGroupedButton(right, UiTheme.Rotate);\n            Button flip = MakeButton("Xoay 180°", 105, false); flip.Margin = new Padding(0, 0, 5, 0); flip.Click += delegate { RotateSelected(180); }; manualButtons.Controls.Add(flip); StyleGroupedButton(flip, UiTheme.Rotate);\n            Button del = MakeButton("Xóa trang PDF", 118, false); del.Margin = new Padding(0, 0, 5, 0); del.Click += delegate { DeleteSelected(); }; manualButtons.Controls.Add(del); StyleGroupedButton(del, UiTheme.Danger);\n            _btnUndo = MakeButton("Quay lại", 104, false); _btnUndo.Margin = new Padding(0, 0, 5, 0); _btnUndo.Image = CreateHistoryIcon(false); _btnUndo.TextImageRelation = TextImageRelation.ImageBeforeText; _btnUndo.ImageAlign = ContentAlignment.MiddleLeft; _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo); StyleGroupedButton(_btnUndo, UiTheme.History);\n            _btnRedo = MakeButton("Tiến lại", 104, false); _btnRedo.Margin = new Padding(0, 0, 8, 0); _btnRedo.Image = CreateHistoryIcon(true); _btnRedo.TextImageRelation = TextImageRelation.ImageBeforeText; _btnRedo.ImageAlign = ContentAlignment.MiddleLeft; _btnRedo.Click += delegate { Redo(); }; manualButtons.Controls.Add(_btnRedo); StyleGroupedButton(_btnRedo, UiTheme.History);\n\n            FlowLayoutPanel pageTools = new FlowLayoutPanel(); pageTools.Dock = DockStyle.Fill; pageTools.WrapContents = false; pageTools.AutoScroll = true; pageTools.Padding = new Padding(0,2,0,0); manualGrid.Controls.Add(pageTools,0,1);\n            Button mergeDirect = MakeButton("Ghép thêm PDF", 132, false); mergeDirect.Margin = new Padding(0,0,5,0); mergeDirect.Click += async delegate { await MergePdfIntoCurrentAsync(-1); }; pageTools.Controls.Add(mergeDirect); StyleGroupedButton(mergeDirect, UiTheme.PageTools);\n            Button extractDirect = MakeButton("Tách trang...", 116, false); extractDirect.Margin = new Padding(0,0,5,0); extractDirect.Click += delegate { ShowExtractChoiceMenu(extractDirect); }; pageTools.Controls.Add(extractDirect); StyleGroupedButton(extractDirect, UiTheme.PageTools);\n            Button reverseDirect = MakeButton("Đảo ngược thứ tự", 152, false); reverseDirect.Margin = new Padding(0,0,5,0); reverseDirect.Click += delegate { ReversePageOrder(); }; pageTools.Controls.Add(reverseDirect); StyleGroupedButton(reverseDirect, UiTheme.PageTools);\n'''
rep(old,new,'manual page tools')
rep('''            _toolTip.SetToolTip(_btnRedo, "Làm lại thao tác vừa Hoàn tác (Ctrl+Y). Không khôi phục toàn bộ PDF.");\n\n            FlowLayoutPanel cutRow = new FlowLayoutPanel(); cutRow.Dock = DockStyle.Fill; cutRow.Visible = false; manualGrid.Controls.Add(cutRow, 0, 1);\n''','''            _toolTip.SetToolTip(_btnUndo, "Quay lại tối đa 10 thao tác gần nhất (Ctrl+Z).");\n            _toolTip.SetToolTip(_btnRedo, "Tiến lại thao tác vừa Quay lại, tối đa 10 bước (Ctrl+Y).");\n\n            FlowLayoutPanel cutRow = new FlowLayoutPanel(); cutRow.Dock = DockStyle.Fill; cutRow.Visible = false; manualGrid.Controls.Add(cutRow, 0, 2);\n''','history tooltip + cut row')

# Context menu navigation first, then reverse/merge/extract.
old='''            ContextMenuStrip cms = UiTheme.Menu();\n            cms.Items.Add("Ghép thêm PDF sau trang này...", null, async delegate { await MergePdfIntoCurrentAsync(SelectedIndex); });\n            cms.Items.Add("Tách riêng trang đang chọn...", null, async delegate { await ExtractSelectedPageAsync(); });\n            cms.Items.Add("Tách nhiều trang...", null, async delegate { await ExtractRangeWithDialogAsync(); });\n            cms.Items.Add(new ToolStripSeparator());\n            cms.Items.Add("Xoay trái 90°", null, delegate { RotateSelected(-90); }); cms.Items.Add("Xoay phải 90°", null, delegate { RotateSelected(90); }); cms.Items.Add("Xoay 180°", null, delegate { RotateSelected(180); }); cms.Items.Add("Xóa trang", null, delegate { DeleteSelected(); });\n            cms.Items.Add(new ToolStripSeparator()); cms.Items.Add("Lên đầu", null, delegate { MoveSelectedToEdge(true); }); cms.Items.Add("Xuống cuối", null, delegate { MoveSelectedToEdge(false); }); _list.ContextMenuStrip = cms;\n'''
new='''            ContextMenuStrip cms = UiTheme.Menu();\n            cms.Items.Add("Lên đầu", null, delegate { MoveSelectedToEdge(true); });\n            cms.Items.Add("Xuống cuối", null, delegate { MoveSelectedToEdge(false); });\n            cms.Items.Add("Lên 1 trang", null, delegate { MoveSelectedBy(-1); });\n            cms.Items.Add("Xuống 1 trang", null, delegate { MoveSelectedBy(1); });\n            cms.Items.Add(new ToolStripSeparator());\n            cms.Items.Add("Đảo ngược thứ tự trang", null, delegate { ReversePageOrder(); });\n            cms.Items.Add("Ghép thêm PDF sau trang này...", null, async delegate { await MergePdfIntoCurrentAsync(SelectedIndex); });\n            cms.Items.Add("Tách riêng trang đang chọn...", null, async delegate { await ExtractSelectedPageAsync(); });\n            cms.Items.Add("Tách nhiều trang...", null, async delegate { await ExtractRangeWithDialogAsync(); });\n            cms.Items.Add(new ToolStripSeparator());\n            cms.Items.Add("Xoay trái 90°", null, delegate { RotateSelected(-90); }); cms.Items.Add("Xoay phải 90°", null, delegate { RotateSelected(90); }); cms.Items.Add("Xoay 180°", null, delegate { RotateSelected(180); }); cms.Items.Add("Xóa trang", null, delegate { DeleteSelected(); });\n            _list.ContextMenuStrip = cms;\n'''
rep(old,new,'context menu order')

# Preview quick zoom: retain slider, add +/- and preset combo without wrapping.
old='''            previewTop.Controls.Clear(); previewTop.ColumnStyles.Clear(); previewTop.RowStyles.Clear(); previewTop.ColumnCount = 5; previewTop.RowCount = 1;\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 120));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 88));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 56));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 116));\n            previewTop.RowStyles.Add(new RowStyle(SizeType.Percent, 100));\n            Label stableTitle = new Label(); stableTitle.Text = "XEM TRƯỚC"; stableTitle.Font = UiTheme.Font(11f, FontStyle.Bold); stableTitle.Dock = DockStyle.Fill; stableTitle.TextAlign = ContentAlignment.MiddleLeft; stableTitle.Padding = new Padding(8,0,0,0); previewTop.Controls.Add(stableTitle,0,0);\n            Label stableZl = new Label(); stableZl.Text = "Thu phóng:"; stableZl.Dock = DockStyle.Fill; stableZl.TextAlign = ContentAlignment.MiddleLeft; previewTop.Controls.Add(stableZl,1,0);\n            _zoom.Dock = DockStyle.Fill; _zoom.Margin = new Padding(0,5,8,2); _zoom.TickStyle = TickStyle.None; previewTop.Controls.Add(_zoom,2,0);\n            _zoomValueLabel = new Label(); _zoomValueLabel.Text = _zoom.Value.ToString() + "%"; _zoomValueLabel.Dock = DockStyle.Fill; _zoomValueLabel.TextAlign = ContentAlignment.MiddleCenter; previewTop.Controls.Add(_zoomValueLabel,3,0);\n            _btnFitStable = MakeButton("Vừa cửa sổ", 108, false); _btnFitStable.Dock = DockStyle.Fill; _btnFitStable.Height = 32; _btnFitStable.Margin = new Padding(4,6,8,6); _btnFitStable.Click += delegate { SetZoomPercent(100); }; previewTop.Controls.Add(_btnFitStable,4,0);\n'''
new='''            previewTop.Controls.Clear(); previewTop.ColumnStyles.Clear(); previewTop.RowStyles.Clear(); previewTop.ColumnCount = 6; previewTop.RowCount = 1;\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 110));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 82));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 54));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 190));\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 112));\n            previewTop.RowStyles.Add(new RowStyle(SizeType.Percent, 100));\n            Label stableTitle = new Label(); stableTitle.Text = "XEM TRƯỚC"; stableTitle.Font = UiTheme.Font(11f, FontStyle.Bold); stableTitle.Dock = DockStyle.Fill; stableTitle.TextAlign = ContentAlignment.MiddleLeft; stableTitle.Padding = new Padding(8,0,0,0); previewTop.Controls.Add(stableTitle,0,0);\n            Label stableZl = new Label(); stableZl.Text = "Thu phóng:"; stableZl.Dock = DockStyle.Fill; stableZl.TextAlign = ContentAlignment.MiddleLeft; previewTop.Controls.Add(stableZl,1,0);\n            _zoom.Dock = DockStyle.Fill; _zoom.Margin = new Padding(0,5,8,2); _zoom.TickStyle = TickStyle.None; previewTop.Controls.Add(_zoom,2,0);\n            _zoomValueLabel = new Label(); _zoomValueLabel.Text = _zoom.Value.ToString() + "%"; _zoomValueLabel.Dock = DockStyle.Fill; _zoomValueLabel.TextAlign = ContentAlignment.MiddleCenter; previewTop.Controls.Add(_zoomValueLabel,3,0);\n            FlowLayoutPanel zoomTools = new FlowLayoutPanel(); zoomTools.Dock = DockStyle.Fill; zoomTools.WrapContents = false; zoomTools.Margin = new Padding(0,5,0,4); zoomTools.Padding = new Padding(0); previewTop.Controls.Add(zoomTools,4,0);\n            Button zoomMinus = MakeButton("-", 34, false); zoomMinus.Height=30; zoomMinus.Margin=new Padding(0,0,3,0); zoomMinus.Click += delegate { SetZoomPercent((_zoom == null ? 100 : _zoom.Value) - 10); }; zoomTools.Controls.Add(zoomMinus);\n            ComboBox zoomQuick = new ComboBox(); zoomQuick.DropDownStyle=ComboBoxStyle.DropDownList; zoomQuick.Width=78; zoomQuick.Height=30; zoomQuick.Margin=new Padding(0,1,3,0); zoomQuick.Items.AddRange(new object[]{"100%","125%","150%","200%"}); zoomQuick.SelectedIndex=0; zoomQuick.SelectedIndexChanged += delegate { string z = zoomQuick.SelectedItem as string; int v; if(!string.IsNullOrEmpty(z) && int.TryParse(z.TrimEnd('%'),out v)) SetZoomPercent(v); }; zoomTools.Controls.Add(zoomQuick);\n            Button zoomPlus = MakeButton("+", 34, false); zoomPlus.Height=30; zoomPlus.Margin=new Padding(0); zoomPlus.Click += delegate { SetZoomPercent((_zoom == null ? 100 : _zoom.Value) + 10); }; zoomTools.Controls.Add(zoomPlus);\n            _btnFitStable = MakeButton("Vừa cửa sổ", 104, false); _btnFitStable.Dock = DockStyle.Fill; _btnFitStable.Height = 32; _btnFitStable.Margin = new Padding(2,6,6,6); _btnFitStable.Click += delegate { SetZoomPercent(100); }; previewTop.Controls.Add(_btnFitStable,5,0);\n'''
rep(old,new,'quick zoom')

# Add grouped style and icon drawing methods after MakeButton.
marker='''        private static AppSnapshot CloneAppSnapshot(AppSnapshot src)\n'''
helpers=r'''        private static void StyleGroupedButton(Button button, Color fill)
        {
            if (button == null) return;
            button.BackColor = fill; button.ForeColor = Color.White; button.FlatStyle = FlatStyle.Flat; button.FlatAppearance.BorderSize = 0;
            int r = Math.Max(0, fill.R - 18), g = Math.Max(0, fill.G - 18), b = Math.Max(0, fill.B - 18);
            button.FlatAppearance.MouseOverBackColor = Color.FromArgb(r, g, b);
            button.FlatAppearance.MouseDownBackColor = Color.FromArgb(Math.Max(0,r-14), Math.Max(0,g-14), Math.Max(0,b-14));
        }

        private static Bitmap CreateHistoryIcon(bool forward)
        {
            Bitmap icon = new Bitmap(20,20,PixelFormat.Format32bppArgb);
            using(Graphics g = Graphics.FromImage(icon))
            using(Pen pen = new Pen(Color.White,2.2f))
            using(SolidBrush brush = new SolidBrush(Color.White))
            {
                g.SmoothingMode = SmoothingMode.AntiAlias;
                RectangleF arc = new RectangleF(3.5f,3.5f,13f,13f);
                if (forward)
                {
                    g.DrawArc(pen,arc,205,280);
                    g.FillPolygon(brush,new PointF[]{new PointF(16.8f,4.0f),new PointF(11.7f,4.2f),new PointF(15.0f,8.0f)});
                }
                else
                {
                    g.DrawArc(pen,arc,55,280);
                    g.FillPolygon(brush,new PointF[]{new PointF(3.2f,4.0f),new PointF(8.3f,4.2f),new PointF(5.0f,8.0f)});
                }
            }
            return icon;
        }

'''
rep(marker,helpers+marker,'button helpers')

# Completed status green / in progress amber
old='''                item.SubItems[1].Text = GetDocumentStatusText(doc);\n                item.ToolTipText = string.IsNullOrEmpty(doc.LastError)\n'''
new='''                item.SubItems[1].Text = GetDocumentStatusText(doc);\n                item.UseItemStyleForSubItems = false;\n                item.SubItems[1].ForeColor = doc.ProcessingState == DocumentProcessingState.Completed ? UiTheme.Completed : (doc.ProcessingState == DocumentProcessingState.InProgress ? UiTheme.InProgress : UiTheme.MutedText);\n                item.ToolTipText = string.IsNullOrEmpty(doc.LastError)\n'''
rep(old,new,'status colors')

# Folder switch: remove completed automatically first, then warn only for remaining incomplete files.
start=s.find('        private bool PrepareDocumentListForOpen(string[] newPaths)\n')
end=s.find('        private void DeleteSessionDirectoryLater', start)
if start<0 or end<0: raise SystemExit('v280 PrepareDocumentListForOpen boundary missing')
new_method=r'''        private bool PrepareDocumentListForOpen(string[] newPaths)
        {
            if (newPaths == null || newPaths.Length == 0 || _documents.Count == 0) return true;
            string first = newPaths.FirstOrDefault(delegate(string x) { return !string.IsNullOrWhiteSpace(x); });
            if (string.IsNullOrEmpty(first)) return false;
            string newDir = SafeDirectoryOf(first);
            DocumentWorkspace anchor = _activeDocument ?? _documents[0]; string oldDir = SafeDirectoryOf(anchor.SourcePath);
            if (string.Equals(newDir, oldDir, StringComparison.OrdinalIgnoreCase)) return true;

            List<DocumentWorkspace> completed = _documents.Where(delegate(DocumentWorkspace d) { return d.ProcessingState == DocumentProcessingState.Completed; }).ToList();
            for (int i=0;i<completed.Count;i++) RemoveDocumentWorkspace(completed[i]);
            if (_documents.Count == 0)
            {
                SetStatus("Đã tự động loại các tệp hoàn thành của thư mục cũ trước khi chuyển thư mục.");
                return true;
            }

            DialogResult answer = MessageBox.Show(this,
                "Đã tự động loại các tệp đã hoàn thành. Danh sách hiện vẫn còn " + _documents.Count.ToString() + " tệp CHƯA HOÀN THÀNH.\r\n\r\nNếu tiếp tục, các tệp chưa hoàn thành sẽ chỉ bị xóa khỏi khung làm việc để nạp thư mục mới; PDF nguồn trên ổ đĩa không bị xóa.\r\n\r\nTiếp tục chuyển thư mục?",
                "Còn tệp chưa hoàn thành", MessageBoxButtons.YesNo, MessageBoxIcon.Warning);
            if (answer != DialogResult.Yes) return false;
            ClearAllDocumentsCore();
            return true;
        }

'''
s=s[:start]+new_method+s[end:]

# Reverse current model and preserve selected page identity as much as possible.
marker='''        private void MoveSelectedBy(int delta)\n'''
reverse=r'''        private void ReversePageOrder()
        {
            if (_busy || _pdf == null) return;
            int count = _isSplit ? _outputs.Count : _sources.Count;
            if (count <= 1) { RestoreListFocus(SelectedIndex); return; }
            int oldIndex = Math.Max(0, SelectedIndex);
            PushHistory();
            if (_isSplit) _outputs.Reverse(); else _sources.Reverse();
            _redo.Clear(); MarkActiveDocumentInProgress(); ClearPreviewCache();
            int newIndex = Math.Max(0, Math.Min(count - 1, count - 1 - oldIndex));
            RefreshList(newIndex); RestoreListFocus(newIndex);
            SetStatus("Đã đảo ngược thứ tự toàn bộ " + count.ToString() + " trang. Bấm Lưu vào file gốc để ghi thứ tự mới vào PDF nguồn.");
        }

'''
rep(marker,reverse+marker,'reverse method')

# History strict 10 for both directions.
rep('_undo.Push(s); if (_undo.Count > 80) TrimStack(_undo, 80); UpdateButtons();','_undo.Push(s); if (_undo.Count > HistoryLimit) TrimStack(_undo, HistoryLimit); UpdateButtons();','push history limit')
rep('''            if (_undo.Count == 0) { RestoreListFocus(SelectedIndex); return; } _redo.Push(CaptureCurrent()); AppSnapshot s = _undo.Pop(); RestoreSnapshot(s); UpdateButtons();\n''','''            if (_undo.Count == 0) { RestoreListFocus(SelectedIndex); return; } _redo.Push(CaptureCurrent()); if (_redo.Count > HistoryLimit) TrimStack(_redo, HistoryLimit); AppSnapshot s = _undo.Pop(); RestoreSnapshot(s); UpdateButtons();\n''','undo redo limit')
rep('''            if (_redo.Count == 0) { RestoreListFocus(SelectedIndex); return; } _undo.Push(CaptureCurrent()); AppSnapshot s = _redo.Pop(); RestoreSnapshot(s); UpdateButtons();\n''','''            if (_redo.Count == 0) { RestoreListFocus(SelectedIndex); return; } _undo.Push(CaptureCurrent()); if (_undo.Count > HistoryLimit) TrimStack(_undo, HistoryLimit); AppSnapshot s = _redo.Pop(); RestoreSnapshot(s); UpdateButtons();\n''','redo undo limit')

# Shared ONNX session and conservative adaptive spread analysis.
# Add helper to analyzer: full page first; only add halves when full-page confidence is not extremely strong.
old='''                regions.Add(Tuple.Create(new Bitmap(baseBitmap), spreadLike ? 0.40 : 1.0));\n                if (spreadLike)\n                {\n                    if (baseBitmap.Width >= baseBitmap.Height * 1.05)\n                    {\n                        int mid = baseBitmap.Width / 2;\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(0, 0, mid, baseBitmap.Height)), 0.30));\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(mid, 0, baseBitmap.Width - mid, baseBitmap.Height)), 0.30));\n                    }\n                    else if (baseBitmap.Height >= baseBitmap.Width * 1.05)\n                    {\n                        int mid = baseBitmap.Height / 2;\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(0, 0, baseBitmap.Width, mid)), 0.30));\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(0, mid, baseBitmap.Width, baseBitmap.Height - mid)), 0.30));\n                    }\n                }\n\n                double totalWeight = regions.Sum(x => x.Item2);\n'''
new='''                Bitmap whole = new Bitmap(baseBitmap);\n                regions.Add(Tuple.Create(whole, spreadLike ? 0.40 : 1.0));\n                bool needSpreadRegions = spreadLike;\n                double[] wholeProbs = null;\n                if (spreadLike)\n                {\n                    wholeProbs = RunModel(whole);\n                    double best = wholeProbs.Max(); double second = wholeProbs.OrderByDescending(delegate(double x) { return x; }).Skip(1).First();\n                    // Conservative fast path: skip the two extra inferences only when the whole spread is exceptionally clear.\n                    // This changes compute cost, not the PDF and not the accepted orientation threshold for ambiguous pages.\n                    needSpreadRegions = !(best >= 0.90 && best - second >= 0.48);\n                    if (!needSpreadRegions)\n                    {\n                        for (int i=0;i<Math.Min(wholeProbs.Length,_labels.Length);i++)\n                        {\n                            int correction=ImageOps.NormRotation(360-_labels[i]); result.Scores[correction]+=wholeProbs[i];\n                        }\n                    }\n                }\n                if (needSpreadRegions && spreadLike)\n                {\n                    if (baseBitmap.Width >= baseBitmap.Height * 1.05)\n                    {\n                        int mid = baseBitmap.Width / 2;\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(0, 0, mid, baseBitmap.Height)), 0.30));\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(mid, 0, baseBitmap.Width - mid, baseBitmap.Height)), 0.30));\n                    }\n                    else if (baseBitmap.Height >= baseBitmap.Width * 1.05)\n                    {\n                        int mid = baseBitmap.Height / 2;\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(0, 0, baseBitmap.Width, mid)), 0.30));\n                        regions.Add(Tuple.Create(CloneCrop(baseBitmap, new Rectangle(0, mid, baseBitmap.Width, baseBitmap.Height - mid)), 0.30));\n                    }\n                }\n\n                double totalWeight = regions.Sum(x => x.Item2);\n'''
rep(old,new,'adaptive analyzer')
# Avoid running whole model twice on fast path: condition model aggregation loop.
old='''                foreach (Tuple<Bitmap, double> region in regions)\n                {\n                    double[] probs = RunModel(region.Item1);\n                    double w = region.Item2 / totalWeight;\n                    for (int i = 0; i < Math.Min(probs.Length, _labels.Length); i++)\n                    {\n                        // Model label describes the current clockwise orientation.\n                        // The app needs the clockwise correction required to make it upright.\n                        int correction = ImageOps.NormRotation(360 - _labels[i]);\n                        result.Scores[correction] += probs[i] * w;\n                    }\n                }\n'''
new='''                if (!spreadLike || needSpreadRegions)\n                {\n                    foreach (Tuple<Bitmap, double> region in regions)\n                    {\n                        double[] probs = object.ReferenceEquals(region.Item1, whole) && wholeProbs != null ? wholeProbs : RunModel(region.Item1);\n                        double w = region.Item2 / totalWeight;\n                        for (int i = 0; i < Math.Min(probs.Length, _labels.Length); i++)\n                        {\n                            int correction = ImageOps.NormRotation(360 - _labels[i]);\n                            result.Scores[correction] += probs[i] * w;\n                        }\n                    }\n                }\n'''
rep(old,new,'adaptive aggregation')

# Main AutoRotate reuses one analyzer per app session; keep 1700px to avoid accuracy tradeoff.
rep('''            OnnxOrientationAnalyzer analyzer = null;\n            try\n            {\n                analyzer = new OnnxOrientationAnalyzer();\n                if (!analyzer.IsAvailable) throw new InvalidOperationException("Model AI hướng tài liệu không khởi tạo được.");\n''','''            OnnxOrientationAnalyzer analyzer = null;\n            try\n            {\n                if (_orientationAnalyzer == null || !_orientationAnalyzer.IsAvailable) _orientationAnalyzer = new OnnxOrientationAnalyzer();\n                analyzer = _orientationAnalyzer;\n                if (!analyzer.IsAvailable) throw new InvalidOperationException("Model AI hướng tài liệu không khởi tạo được.");\n''','reuse analyzer')
rep('''            finally\n            {\n                try { if (analyzer != null) analyzer.Dispose(); } catch { }\n                _progress.Value = 0; SetBusy(false, null); RestoreListFocus(SelectedIndex);\n            }\n''','''            finally\n            {\n                _progress.Value = 0; SetBusy(false, null); RestoreListFocus(SelectedIndex);\n            }\n''','do not dispose analyzer')


# Use lossless extraction whenever selected pages are full PDF pages. Cropped split pages keep the proven v2.7 raster fallback.
rep('                await Task.Run(delegate { SimplePdfWriter.WriteFromFactory(target,indexes.Count,delegate(int i){return BuildExportPage(indexes[i]);},null); }); ValidateGeneratedPdf(target,indexes.Count);',
    '                bool lossless = CanUseLosslessForIndexes(indexes);\n                await Task.Run(delegate { if(lossless) WriteLosslessSelectedPages(target,indexes); else SimplePdfWriter.WriteFromFactory(target,indexes.Count,delegate(int i){return BuildExportPage(indexes[i]);},null); }); ValidateGeneratedPdf(target,indexes.Count);',
    'lossless extract')

# Lossless full-page export path. No rasterization for reorder/reverse/rotation/merge-before-split.
marker='''        private async Task ExportPdfAsync(bool overwriteOriginal)\n'''
lossless=r'''        private bool CanUseLosslessForIndexes(IList<int> indexes)
        {
            if (indexes == null || indexes.Count == 0 || _pdf == null || string.IsNullOrEmpty(_workPath) || !File.Exists(_workPath)) return false;
            if (!_isSplit) return indexes.All(delegate(int i) { return i >= 0 && i < _sources.Count; });
            return indexes.All(delegate(int i) { return i >= 0 && i < _outputs.Count && (_outputs[i].ImportedFullPage || _outputs[i].Half < 0); });
        }

        private void WriteLosslessSelectedPages(string outputPath, IList<int> indexes)
        {
            using (PdfSharp.Pdf.PdfDocument input = PdfReader.Open(_workPath, PdfDocumentOpenMode.Import))
            using (PdfSharp.Pdf.PdfDocument output = new PdfSharp.Pdf.PdfDocument())
            {
                for (int k=0;k<indexes.Count;k++)
                {
                    int i=indexes[k]; int sourceIndex; int rotation;
                    if (!_isSplit) { SourceFace s=_sources[i]; sourceIndex=s.OriginalSourceIndex; rotation=s.Rotation; }
                    else { OutputPage p=_outputs[i]; sourceIndex=p.OriginalSourceIndex; rotation=p.SourceRotation+p.ExtraRotation; }
                    if(sourceIndex<0 || sourceIndex>=input.PageCount) throw new InvalidDataException("Chỉ số trang nguồn không hợp lệ khi tách lossless.");
                    PdfSharp.Pdf.PdfPage page=output.AddPage(input.Pages[sourceIndex]); page.Rotate=ImageOps.NormRotation(page.Rotate+rotation);
                }
                output.Save(outputPath);
            }
        }

        private bool CanUseLosslessFullPageExport()
        {
            if (_pdf == null || string.IsNullOrEmpty(_workPath) || !File.Exists(_workPath)) return false;
            if (!_isSplit) return _sources.Count > 0;
            if (_outputs.Count == 0) return false;
            return _outputs.All(delegate(OutputPage p) { return p.ImportedFullPage || p.Half < 0; });
        }

        private void WriteLosslessFullPagePdf(string outputPath)
        {
            using (PdfSharp.Pdf.PdfDocument input = PdfReader.Open(_workPath, PdfDocumentOpenMode.Import))
            using (PdfSharp.Pdf.PdfDocument output = new PdfSharp.Pdf.PdfDocument())
            {
                if (!_isSplit)
                {
                    for (int i=0;i<_sources.Count;i++)
                    {
                        SourceFace s = _sources[i];
                        if (s.OriginalSourceIndex < 0 || s.OriginalSourceIndex >= input.PageCount) throw new InvalidDataException("Chỉ số trang nguồn không hợp lệ khi xuất lossless.");
                        PdfSharp.Pdf.PdfPage page = output.AddPage(input.Pages[s.OriginalSourceIndex]);
                        page.Rotate = ImageOps.NormRotation(page.Rotate + s.Rotation);
                    }
                }
                else
                {
                    for (int i=0;i<_outputs.Count;i++)
                    {
                        OutputPage p = _outputs[i];
                        if (!(p.ImportedFullPage || p.Half < 0)) throw new InvalidOperationException("Trang cắt cần dùng bộ xuất tương thích v2.7.");
                        if (p.OriginalSourceIndex < 0 || p.OriginalSourceIndex >= input.PageCount) throw new InvalidDataException("Chỉ số trang nguồn không hợp lệ khi xuất lossless.");
                        PdfSharp.Pdf.PdfPage page = output.AddPage(input.Pages[p.OriginalSourceIndex]);
                        page.Rotate = ImageOps.NormRotation(page.Rotate + p.SourceRotation + p.ExtraRotation);
                    }
                }
                output.Save(outputPath);
            }
        }

'''
rep(marker,lossless+marker,'lossless methods')
old='''                await Task.Run(delegate\n                {\n                    SimplePdfWriter.WriteFromFactory(tempOut, exportCount, BuildExportPage, delegate(int done, int total)\n                    {\n                        try\n                        {\n                            BeginInvoke(new Action(delegate\n                            {\n                                _progress.Maximum = Math.Max(1, total);\n                                _progress.Value = Math.Min(_progress.Maximum, done);\n                                SetStatus("Đang xuất: " + done.ToString() + "/" + total.ToString());\n                            }));\n                        }\n                        catch { }\n                    });\n                });\n'''
new='''                bool lossless = CanUseLosslessFullPageExport();\n                await Task.Run(delegate\n                {\n                    if (lossless)\n                    {\n                        WriteLosslessFullPagePdf(tempOut);\n                    }\n                    else\n                    {\n                        SimplePdfWriter.WriteFromFactory(tempOut, exportCount, BuildExportPage, delegate(int done, int total)\n                        {\n                            try\n                            {\n                                if (done == total || done == 1 || done % 3 == 0) BeginInvoke(new Action(delegate\n                                {\n                                    _progress.Maximum = Math.Max(1, total);\n                                    _progress.Value = Math.Min(_progress.Maximum, done);\n                                    SetStatus("Đang xuất: " + done.ToString() + "/" + total.ToString());\n                                }));\n                            }\n                            catch { }\n                        });\n                    }\n                });\n                if (lossless) SetStatus("Đã xuất theo chế độ lossless: giữ nguyên nội dung PDF, chỉ thay thứ tự/góc xoay/trang ghép.");\n'''
rep(old,new,'lossless export call')

# Backup dir central constant
rep('''string backupDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "TachXepTrangPDF", "Backups", DateTime.Now.ToString("yyyyMMdd"));''','''string backupDir = Path.Combine(AppDiagnostics.BackupDirectory, DateTime.Now.ToString("yyyyMMdd"));''','backup directory')

# Restore immutable work when copy-on-write path equals original: never overwrite immutable original.
old='''                string workRestoreTemp = Path.Combine(_sessionDir,"work-restore-"+Guid.NewGuid().ToString("N")+".pdf");\n                File.Copy(immutableOriginal,workRestoreTemp,true);\n                ReplaceWorkFileSafely(workRestoreTemp,_workPath);\n                ReopenRuntimeAfterWorkFileChange();\n'''
new='''                if (string.Equals(Path.GetFullPath(_workPath), Path.GetFullPath(immutableOriginal), StringComparison.OrdinalIgnoreCase))\n                {\n                    _workPath = immutableOriginal;\n                    if (_activeDocument != null) _activeDocument.WorkPath = _workPath;\n                    ReopenRuntimeAfterWorkFileChange();\n                }\n                else\n                {\n                    string workRestoreTemp = Path.Combine(_sessionDir,"work-restore-"+Guid.NewGuid().ToString("N")+".pdf");\n                    File.Copy(immutableOriginal,workRestoreTemp,true);\n                    string restoredWork = Path.Combine(_sessionDir,"work-restored-"+Guid.NewGuid().ToString("N")+".pdf");\n                    File.Move(workRestoreTemp,restoredWork); _workPath=restoredWork; if(_activeDocument!=null)_activeDocument.WorkPath=_workPath;\n                    ReopenRuntimeAfterWorkFileChange();\n                }\n'''
rep(old,new,'restore copy-on-write')

# Cleanup shared analyzer and periodic backup cleanup at close.
old='''            if (dirs.Count > 0) Task.Run(delegate { foreach (string d in dirs) try { Thread.Sleep(50); if (Directory.Exists(d)) Directory.Delete(d, true); } catch { } });\n            GC.Collect(); GC.WaitForPendingFinalizers();\n'''
new='''            try { if (_orientationAnalyzer != null) { _orientationAnalyzer.Dispose(); _orientationAnalyzer = null; } } catch { }\n            if (dirs.Count > 0)\n            {\n                foreach (string d in dirs.Distinct(StringComparer.OrdinalIgnoreCase))\n                {\n                    for(int attempt=0;attempt<3;attempt++)\n                    {\n                        try { if (Directory.Exists(d)) Directory.Delete(d, true); break; }\n                        catch { GC.Collect(); GC.WaitForPendingFinalizers(); Thread.Sleep(60); }\n                    }\n                }\n            }\n            AppDiagnostics.RegisterClosedSessionAndMaybeCleanupBackups();\n            GC.Collect(); GC.WaitForPendingFinalizers();\n'''
rep(old,new,'cleanup session')

# Ensure button text displays current history counts without losing friendly names.
old='''        private void UpdateButtons()\n        {\n            bool has = _pdf != null; _btnUndo.Enabled = has && _undo.Count > 0; _btnRedo.Enabled = has && _redo.Count > 0; _btnAuto.Enabled = has; _btnSplit.Enabled = has && _sources.Count > 0; _btnExport.Enabled = has && (_isSplit ? _outputs.Count > 0 : _sources.Count > 0); _btnSaveOriginal.Enabled = _btnExport.Enabled; _btnRestoreOriginal.Enabled = has;\n        }\n'''
new='''        private void UpdateButtons()\n        {\n            bool has = _pdf != null; _btnUndo.Enabled = has && _undo.Count > 0; _btnRedo.Enabled = has && _redo.Count > 0; _btnAuto.Enabled = has; _btnSplit.Enabled = has && _sources.Count > 0; _btnExport.Enabled = has && (_isSplit ? _outputs.Count > 0 : _sources.Count > 0); _btnSaveOriginal.Enabled = _btnExport.Enabled; _btnRestoreOriginal.Enabled = has;\n            if (_btnUndo != null) _btnUndo.Text = "Quay lại" + (_undo.Count > 0 ? " (" + _undo.Count.ToString() + ")" : "");\n            if (_btnRedo != null) _btnRedo.Text = "Tiến lại" + (_redo.Count > 0 ? " (" + _redo.Count.ToString() + ")" : "");\n        }\n'''
rep(old,new,'history counts')

# UI smoke markers / workflow extension: test reverse and 10-step cap using model-only operations.
anchor='''                Guid movedId = ((OutputPage)_list.Items[SelectedIndex].Tag).Id;\n                MoveSelectedBy(1); Application.DoEvents();\n'''
insert=r'''                Guid reverseFirst = _outputs[0].Id, reverseLast = _outputs[_outputs.Count-1].Id;
                ReversePageOrder(); Application.DoEvents();
                if (_outputs[0].Id != reverseLast || _outputs[_outputs.Count-1].Id != reverseFirst) throw new InvalidOperationException("Workflow smoke: reverse page order failed.");
                Undo(); Application.DoEvents();
                if (_outputs[0].Id != reverseFirst || _outputs[_outputs.Count-1].Id != reverseLast) throw new InvalidOperationException("Workflow smoke: undo reverse failed.");
                Redo(); Application.DoEvents();
                if (_outputs[0].Id != reverseLast || _outputs[_outputs.Count-1].Id != reverseFirst) throw new InvalidOperationException("Workflow smoke: redo reverse failed.");
                Undo(); Application.DoEvents();
                for (int h=0; h<14; h++) { int r=h%4; RotateSelected(r==0?90:r==1?-90:r==2?180:90); Application.DoEvents(); }
                if (_undo.Count > HistoryLimit) throw new InvalidOperationException("Workflow smoke: undo history exceeded 10 steps.");
                int historyUndo = _undo.Count; for(int h=0;h<historyUndo;h++) { Undo(); Application.DoEvents(); }
                if(_redo.Count>HistoryLimit || _redo.Count!=historyUndo) throw new InvalidOperationException("Workflow smoke: redo history did not retain the 10 reversible steps.");
                int historyRedo = _redo.Count; for(int h=0;h<historyRedo;h++) { Redo(); Application.DoEvents(); }
                if(_undo.Count>HistoryLimit || _redo.Count!=0) throw new InvalidOperationException("Workflow smoke: redo replay failed.");

'''
rep(anchor,insert+anchor,'workflow reverse/history')

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V280_OK')

# Portable launcher identity v2.8.0
launcher=root/'launcher.cpp'
if launcher.exists():
    ls=launcher.read_text(encoding='utf-8-sig')
    if 'v2.7.0' not in ls: raise SystemExit('v280 launcher v2.7.0 marker missing')
    launcher.write_text(ls.replace('v2.7.0','v2.8.0'),encoding='utf-8-sig')
    print('PATCH_V280_LAUNCHER_OK')
