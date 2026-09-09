from pathlib import Path
import re
root=Path('tach-xep-pdf-v2.3.2'); p=root/'TachXepTrangPDF.cs'; s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('v270 ui marker missing: '+label)
    s=s.replace(old,new,1)

theme_marker='    internal sealed class SmoothPreviewPanel : Panel\n'
theme=r'''    internal static class UiTheme
    {
        internal static readonly Color AppBackground = Color.FromArgb(244, 247, 251);
        internal static readonly Color Surface = Color.White;
        internal static readonly Color SurfaceMuted = Color.FromArgb(248, 250, 252);
        internal static readonly Color Border = Color.FromArgb(226, 232, 240);
        internal static readonly Color Text = Color.FromArgb(30, 41, 59);
        internal static readonly Color MutedText = Color.FromArgb(100, 116, 139);
        internal static readonly Color Accent = Color.FromArgb(37, 99, 235);
        internal static readonly Color AccentHover = Color.FromArgb(29, 78, 216);
        internal static readonly Color AccentDown = Color.FromArgb(30, 64, 175);
        internal static readonly Color SecondaryHover = Color.FromArgb(241, 245, 249);
        internal static readonly string FontName = DetectFontName();
        private static string DetectFontName()
        {
            try { using (Font f = new Font("Segoe UI Variable Text", 9f, FontStyle.Regular, GraphicsUnit.Point)) if (string.Equals(f.Name, "Segoe UI Variable Text", StringComparison.OrdinalIgnoreCase)) return "Segoe UI Variable Text"; } catch { }
            return "Segoe UI";
        }
        internal static Font Font(float size, FontStyle style = FontStyle.Regular)
        {
            try { return new Font(FontName, size, style, GraphicsUnit.Point); } catch { return new Font("Segoe UI", size, style, GraphicsUnit.Point); }
        }
        internal static void StyleList(ListView list)
        {
            if (list == null) return; list.BackColor = Surface; list.ForeColor = Text; list.BorderStyle = BorderStyle.None; list.Font = Font(9.25f);
        }
        internal static ContextMenuStrip Menu()
        {
            ContextMenuStrip menu = new ContextMenuStrip(); menu.ShowImageMargin = false; menu.BackColor = Surface; menu.ForeColor = Text; menu.Font = Font(9.25f); menu.Padding = new Padding(4); return menu;
        }
    }

    internal sealed class FluentButton : Button
    {
        internal FluentButton(bool primary)
        {
            FlatStyle = FlatStyle.Flat; FlatAppearance.BorderSize = 0; UseVisualStyleBackColor = false; UseCompatibleTextRendering = false; AutoEllipsis = false; Cursor = Cursors.Hand; TabStop = false;
            BackColor = primary ? UiTheme.Accent : UiTheme.Surface; ForeColor = primary ? Color.White : UiTheme.Text;
            FlatAppearance.MouseOverBackColor = primary ? UiTheme.AccentHover : UiTheme.SecondaryHover; FlatAppearance.MouseDownBackColor = primary ? UiTheme.AccentDown : UiTheme.Border;
        }
    }

    internal sealed class PageRangeDialog : Form
    {
        private readonly NumericUpDown _from = new NumericUpDown(); private readonly NumericUpDown _to = new NumericUpDown();
        internal int FromPage { get { return (int)_from.Value; } } internal int ToPage { get { return (int)_to.Value; } }
        internal PageRangeDialog(int pageCount, int selectedPage)
        {
            Text = "Tách nhiều trang"; StartPosition = FormStartPosition.CenterParent; FormBorderStyle = FormBorderStyle.FixedDialog; MaximizeBox = false; MinimizeBox = false; ShowInTaskbar = false;
            ClientSize = new Size(410, 188); Font = UiTheme.Font(9.5f); BackColor = UiTheme.AppBackground;
            TableLayoutPanel table = new TableLayoutPanel(); table.Dock = DockStyle.Fill; table.Padding = new Padding(18); table.ColumnCount = 2; table.RowCount = 4;
            table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 45)); table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 55));
            table.RowStyles.Add(new RowStyle(SizeType.Absolute, 38)); table.RowStyles.Add(new RowStyle(SizeType.Absolute, 38)); table.RowStyles.Add(new RowStyle(SizeType.Absolute, 38)); table.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); Controls.Add(table);
            Label hint = new Label(); hint.Text = "Ví dụ: từ trang 4 đến trang 8 sẽ tách đủ 4, 5, 6, 7, 8."; hint.Dock = DockStyle.Fill; hint.ForeColor = UiTheme.MutedText; hint.AutoEllipsis = true; table.Controls.Add(hint,0,0); table.SetColumnSpan(hint,2);
            Label lf = new Label(); lf.Text = "Từ trang:"; lf.Dock = DockStyle.Fill; lf.TextAlign = ContentAlignment.MiddleLeft; table.Controls.Add(lf,0,1);
            Label lt = new Label(); lt.Text = "Đến trang:"; lt.Dock = DockStyle.Fill; lt.TextAlign = ContentAlignment.MiddleLeft; table.Controls.Add(lt,0,2);
            int max = Math.Max(1,pageCount), selected = Math.Max(1,Math.Min(max,selectedPage)); _from.Minimum=1; _from.Maximum=max; _from.Value=selected; _from.Dock=DockStyle.Fill; table.Controls.Add(_from,1,1); _to.Minimum=1; _to.Maximum=max; _to.Value=selected; _to.Dock=DockStyle.Fill; table.Controls.Add(_to,1,2);
            FlowLayoutPanel buttons = new FlowLayoutPanel(); buttons.Dock=DockStyle.Fill; buttons.FlowDirection=FlowDirection.RightToLeft; buttons.WrapContents=false; table.Controls.Add(buttons,0,3); table.SetColumnSpan(buttons,2);
            FluentButton ok = new FluentButton(true); ok.Text="Tách ra PDF mới"; ok.Width=138; ok.Height=36; ok.Font=UiTheme.Font(9.25f,FontStyle.Bold); ok.DialogResult=DialogResult.OK; buttons.Controls.Add(ok);
            FluentButton cancel = new FluentButton(false); cancel.Text="Hủy"; cancel.Width=82; cancel.Height=36; cancel.Font=UiTheme.Font(9.25f,FontStyle.Bold); cancel.DialogResult=DialogResult.Cancel; buttons.Controls.Add(cancel); AcceptButton=ok; CancelButton=cancel;
        }
        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (DialogResult == DialogResult.OK && _from.Value > _to.Value) { MessageBox.Show(this,"Trang bắt đầu không được lớn hơn trang kết thúc.","Tách nhiều trang",MessageBoxButtons.OK,MessageBoxIcon.Information); e.Cancel=true; return; } base.OnFormClosing(e);
        }
    }

'''
rep(theme_marker,theme+theme_marker,'theme insertion')
parts=s.split('    internal static class UiTheme',1)
if len(parts)==2:
    prefix,rest=parts; end_theme=rest.find('    internal sealed class SmoothPreviewPanel')
    if end_theme<0: raise SystemExit('v270 ui SmoothPreviewPanel after theme missing')
    theme_part=rest[:end_theme]; app_part=rest[end_theme:]
    app_part=re.sub(r'new Font\("Segoe UI",\s*([0-9.]+f)(?:,\s*(FontStyle\.[A-Za-z]+))?\)', lambda m: 'UiTheme.Font('+m.group(1)+((', '+m.group(2)) if m.group(2) else '')+')', app_part)
    s=prefix+'    internal static class UiTheme'+theme_part+app_part
s=s.replace('            Font = new Font("Segoe UI", 9.5f);\n            BackColor = Color.FromArgb(243, 246, 250);','            Font = UiTheme.Font(9.5f);\n            BackColor = UiTheme.AppBackground;',1)
s=s.replace('            Font = UiTheme.Font(9.5f);\n            BackColor = Color.FromArgb(243, 246, 250);','            Font = UiTheme.Font(9.5f);\n            BackColor = UiTheme.AppBackground;',1)
open_line='            Button open = MakeButton("Mở PDF", 100, true); open.Margin = new Padding(0, 0, 8, 0); open.Click += delegate { OpenPdf(); }; actions.Controls.Add(open); _toolTip = _toolTip ?? new ToolTip(); _toolTip.SetToolTip(open, "Có thể chọn một hoặc nhiều tệp PDF cùng lúc.");\n'
new_open=open_line+'            Button mergeTop = MakeButton("Ghép thêm PDF", 126, false); mergeTop.Margin = new Padding(0,0,8,0); mergeTop.Click += async delegate { await MergePdfIntoCurrentAsync(-1); }; actions.Controls.Add(mergeTop);\n            Button extractTop = MakeButton("Tách trang...", 112, false); extractTop.Margin = new Padding(0,0,8,0); extractTop.Click += delegate { ShowExtractChoiceMenu(extractTop); }; actions.Controls.Add(extractTop);\n'
rep(open_line,new_open,'top merge/extract')
s=s.replace('ConfigureRightPaneRatio(inner, 0.14, 200, 235);','ConfigureRightPaneRatio(inner, 0.115, 172, 210);')
s=s.replace('ClampRightPaneForResize(inner, 190, 360);','ClampRightPaneForResize(inner, 168, 390);')
old_file='''            TableLayoutPanel fileLayout = new TableLayoutPanel(); fileLayout.Dock = DockStyle.Fill; fileLayout.ColumnCount = 1; fileLayout.RowCount = 3;
            fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 30)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 28)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); filePane.Controls.Add(fileLayout);
            Label fileTitle = new Label(); fileTitle.Text = "TỆP ĐANG XỬ LÝ"; fileTitle.Font = UiTheme.Font(10.5f, FontStyle.Bold); fileTitle.Dock = DockStyle.Fill; fileTitle.TextAlign = ContentAlignment.MiddleLeft; fileLayout.Controls.Add(fileTitle, 0, 0);
            Label fileHint = new Label(); fileHint.Text = "Mở PDF có thể chọn nhiều tệp"; fileHint.Dock = DockStyle.Fill; fileHint.ForeColor = Color.DimGray; fileHint.AutoEllipsis = true; fileLayout.Controls.Add(fileHint, 0, 1);
            _fileList = new ListView(); _fileList.Dock = DockStyle.Fill; _fileList.View = View.Details; _fileList.FullRowSelect = true; _fileList.HideSelection = false; _fileList.MultiSelect = false; _fileList.ShowItemToolTips = true; _fileList.BackColor = Color.White; _fileList.BorderStyle = BorderStyle.FixedSingle; _fileList.Columns.Add("Tệp PDF", 150); _fileList.Columns.Add("Trạng thái", 108); _fileList.SelectedIndexChanged += FileSelectionChanged; fileLayout.Controls.Add(_fileList, 0, 2);
            _fileList.Resize += delegate { UpdateFileListColumnWidths(); };
'''
new_file='''            TableLayoutPanel fileLayout = new TableLayoutPanel(); fileLayout.Dock = DockStyle.Fill; fileLayout.ColumnCount = 1; fileLayout.RowCount = 4;
            fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 30)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 28)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 40)); fileLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); filePane.Controls.Add(fileLayout);
            Label fileTitle = new Label(); fileTitle.Text = "TỆP ĐANG XỬ LÝ"; fileTitle.Font = UiTheme.Font(10.5f, FontStyle.Bold); fileTitle.ForeColor=UiTheme.Text; fileTitle.Dock = DockStyle.Fill; fileTitle.TextAlign = ContentAlignment.MiddleLeft; fileLayout.Controls.Add(fileTitle, 0, 0);
            Label fileHint = new Label(); fileHint.Text = "Chuột phải lên tệp để mở thao tác nhanh"; fileHint.Dock = DockStyle.Fill; fileHint.ForeColor = UiTheme.MutedText; fileHint.AutoEllipsis = true; fileLayout.Controls.Add(fileHint, 0, 1);
            FlowLayoutPanel fileActions = new FlowLayoutPanel(); fileActions.Dock=DockStyle.Fill; fileActions.WrapContents=false; fileActions.Padding=new Padding(0,2,0,2); fileLayout.Controls.Add(fileActions,0,2);
            Button removeFile = MakeButton("Xóa tệp", 78, false); removeFile.Height=32; removeFile.Margin=new Padding(0,0,5,0); removeFile.Click += delegate { RemoveSelectedFileFromList(); }; fileActions.Controls.Add(removeFile);
            Button clearFiles = MakeButton("Xóa tất cả", 92, false); clearFiles.Height=32; clearFiles.Margin=new Padding(0); clearFiles.Click += delegate { ClearAllDocumentsFromButton(); }; fileActions.Controls.Add(clearFiles);
            _fileList = new ListView(); _fileList.Dock = DockStyle.Fill; _fileList.View = View.Details; _fileList.FullRowSelect = true; _fileList.HideSelection = false; _fileList.MultiSelect = false; _fileList.ShowItemToolTips = true; _fileList.Columns.Add("Tệp PDF", 150); _fileList.Columns.Add("Trạng thái", 108); _fileList.SelectedIndexChanged += FileSelectionChanged; _fileList.MouseDown += FileListMouseDown; UiTheme.StyleList(_fileList); fileLayout.Controls.Add(_fileList, 0, 3);
            _fileList.Resize += delegate { UpdateFileListColumnWidths(); };
            ContextMenuStrip fileMenu = UiTheme.Menu(); fileMenu.Items.Add("Mở / chuyển tới tệp", null, delegate { ActivateSelectedFileFromContext(); }); fileMenu.Items.Add("Ghép thêm PDF vào tệp này...", null, async delegate { ActivateSelectedFileFromContext(); await MergePdfIntoCurrentAsync(-1); }); fileMenu.Items.Add("Tách trang từ tệp này...", null, delegate { ActivateSelectedFileFromContext(); ShowExtractChoiceMenu(_fileList); }); fileMenu.Items.Add(new ToolStripSeparator()); fileMenu.Items.Add("Xóa tệp khỏi danh sách", null, delegate { RemoveSelectedFileFromList(); }); _fileList.ContextMenuStrip=fileMenu;
'''
rep(old_file,new_file,'file pane')
rep('_list.BackColor = Color.White; _list.BorderStyle = BorderStyle.FixedSingle; _list.KeyDown += ListKeyDown;', 'UiTheme.StyleList(_list); _list.KeyDown += ListKeyDown; _list.MouseDown += PageListMouseDown;','page list style')
old_cms='''            ContextMenuStrip cms = new ContextMenuStrip();
            cms.Items.Add("Lên đầu", null, delegate { MoveSelectedToEdge(true); });
            cms.Items.Add("Xuống cuối", null, delegate { MoveSelectedToEdge(false); });
            cms.Items.Add(new ToolStripSeparator());
            cms.Items.Add("Xóa trang", null, delegate { DeleteSelected(); });
            _list.ContextMenuStrip = cms;
'''
new_cms='''            ContextMenuStrip cms = UiTheme.Menu();
            cms.Items.Add("Ghép thêm PDF sau trang này...", null, async delegate { await MergePdfIntoCurrentAsync(SelectedIndex); });
            cms.Items.Add("Tách riêng trang đang chọn...", null, async delegate { await ExtractSelectedPageAsync(); });
            cms.Items.Add("Tách nhiều trang...", null, async delegate { await ExtractRangeWithDialogAsync(); });
            cms.Items.Add(new ToolStripSeparator());
            cms.Items.Add("Xoay trái 90°", null, delegate { RotateSelected(-90); }); cms.Items.Add("Xoay phải 90°", null, delegate { RotateSelected(90); }); cms.Items.Add("Xoay 180°", null, delegate { RotateSelected(180); }); cms.Items.Add("Xóa trang", null, delegate { DeleteSelected(); });
            cms.Items.Add(new ToolStripSeparator()); cms.Items.Add("Lên đầu", null, delegate { MoveSelectedToEdge(true); }); cms.Items.Add("Xuống cuối", null, delegate { MoveSelectedToEdge(false); }); _list.ContextMenuStrip = cms;
'''
rep(old_cms,new_cms,'page context menu')
s=s.replace('info.Padding = new Padding(8); info.BackColor = Color.White;', 'info.Padding = new Padding(7); info.BackColor = UiTheme.Surface;')
s=s.replace('cutHelp.Text = "Mặc định luôn chia đúng 50%.\\r\\nNếu mặt scan bị lệch, chỉnh riêng mặt đang chọn rồi bấm Áp dụng.";', 'cutHelp.Text = "Mặc định 50%. Nếu scan lệch, chỉnh mặt đang chọn rồi bấm Áp dụng.";')
s=s.replace('cutNote.Text = "Có thể chỉnh cả trước và sau khi chia.\\r\\nChỉ thay đường cắt của mặt nguồn; không thay đổi thứ tự trang.";', 'cutNote.Text = "Chỉnh được trước/sau khi chia. Không đổi thứ tự trang.";')
s=s.replace('topShell.BackColor = Color.White;', 'topShell.BackColor = UiTheme.Surface;'); s=s.replace('header.BackColor = Color.White;', 'header.BackColor = UiTheme.Surface;'); s=s.replace('toolbar.BackColor = Color.FromArgb(248, 249, 251);', 'toolbar.BackColor = UiTheme.SurfaceMuted;'); s=s.replace('statusBar.BackColor = Color.White;', 'statusBar.BackColor = UiTheme.Surface;'); s=s.replace('filePane.BackColor = Color.FromArgb(248, 249, 251);', 'filePane.BackColor = UiTheme.SurfaceMuted;')
old_make='''        private Button MakeButton(string text, int width, bool prominent)
        {
            Button b = new Button(); b.Text = text; b.Height = 38; b.TabStop = false; b.FlatStyle = FlatStyle.Flat; b.UseVisualStyleBackColor = false; b.AutoEllipsis = false; b.UseCompatibleTextRendering = false;
            b.FlatAppearance.BorderSize = 1; b.Padding = new Padding(5,0,5,0);
            b.FlatAppearance.BorderColor = prominent ? Color.FromArgb(37, 99, 235) : Color.FromArgb(203, 213, 225);
            b.BackColor = prominent ? Color.FromArgb(37, 99, 235) : Color.White; b.ForeColor = prominent ? Color.White : Color.FromArgb(30,41,59);
            b.FlatAppearance.MouseOverBackColor = prominent ? Color.FromArgb(29,78,216) : Color.FromArgb(241,245,249);
            b.FlatAppearance.MouseDownBackColor = prominent ? Color.FromArgb(30,64,175) : Color.FromArgb(226,232,240);
            b.Font = UiTheme.Font(9.25f, FontStyle.Bold);
            Size measured = TextRenderer.MeasureText(text ?? "", b.Font, new Size(int.MaxValue, int.MaxValue), TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix);
            b.Width = Math.Max(width, measured.Width + b.Padding.Horizontal + 22);
            b.Height = Math.Max(38, measured.Height + 14);
            return b;
        }
'''
new_make='''        private Button MakeButton(string text, int width, bool prominent)
        {
            FluentButton b = new FluentButton(prominent); b.Text = text; b.Height = 38; b.AutoEllipsis = false; b.Padding = new Padding(8,0,8,0); b.Font = UiTheme.Font(9.25f, FontStyle.Bold);
            Size measured = TextRenderer.MeasureText(text ?? "", b.Font, new Size(int.MaxValue, int.MaxValue), TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix); b.Width = Math.Max(width, measured.Width + b.Padding.Horizontal + 24); b.Height = Math.Max(38, measured.Height + 14); return b;
        }
'''
rep(old_make,new_make,'MakeButton')
p.write_text(s,encoding='utf-8-sig'); print('PATCH_V270_UI_OK')