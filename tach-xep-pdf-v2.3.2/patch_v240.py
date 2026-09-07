from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

# Version/state
s=s.replace('private const string AppVersion = "2.3.5";','private const string AppVersion = "2.4.0";',1)
s=s.replace('private bool _busy;','private bool _busy;\n        private bool _sourceWasOverwritten;\n        private string _originalBackupPath = "";',1)
s=s.replace('private Button _btnSaveOriginal;','private Button _btnSaveOriginal;\n        private Button _btnRestoreOriginal;\n        private Button _btnFitStable;\n        private ToolTip _toolTip;',1)
s=s.replace('BackColor = Color.FromArgb(245, 247, 250);','BackColor = Color.FromArgb(243, 246, 250);',1)

# Add restore button and concise tooltips; keep Redo separate.
needle='_btnSaveOriginal = MakeButton("Lưu vào file gốc", 150, false); _btnSaveOriginal.Margin = new Padding(0, 0, 12, 0); _btnSaveOriginal.Click += async delegate { await ExportPdfAsync(true); }; actions.Controls.Add(_btnSaveOriginal);'
repl='_btnSaveOriginal = MakeButton("Lưu vào file gốc", 146, false); _btnSaveOriginal.Margin = new Padding(0, 0, 8, 0); _btnSaveOriginal.Click += async delegate { await ExportPdfAsync(true); }; actions.Controls.Add(_btnSaveOriginal);\n            _btnRestoreOriginal = MakeButton("Khôi phục PDF gốc", 154, false); _btnRestoreOriginal.Margin = new Padding(0, 0, 8, 0); _btnRestoreOriginal.Click += delegate { RestoreOriginalPdf(); }; actions.Controls.Add(_btnRestoreOriginal);\n            _toolTip = new ToolTip(); _toolTip.SetToolTip(_btnRestoreOriginal, "Đưa PDF về trạng thái khi vừa mở file. Khác nút Làm lại/Redo.");'
if needle not in s: raise SystemExit('save button marker missing')
s=s.replace(needle,repl,1)

# Move cut direction group immediately after Undo in the manual row.
needle='_btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Margin = new Padding(0); _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo);'
repl='_btnUndo = MakeButton("Hoàn tác", 90, false); _btnUndo.Margin = new Padding(0, 0, 8, 0); _btnUndo.Click += delegate { Undo(); }; manualButtons.Controls.Add(_btnUndo);\n            settings.Controls.Remove(direction); direction.Dock = DockStyle.None; direction.Text = "CHIỀU CẮT"; direction.Size = new Size(255, 36); direction.Margin = new Padding(0); _dirLtr.Location = new Point(10, 12); _dirRtl.Location = new Point(130, 12); manualButtons.Controls.Add(direction);\n            _toolTip.SetToolTip(_btnRedo, "Làm lại thao tác vừa Hoàn tác (Ctrl+Y). Không khôi phục toàn bộ PDF.");'
if needle not in s: raise SystemExit('undo marker missing')
s=s.replace(needle,repl,1)

# Remove third column completely by collapsing it; preview takes full body width.
s=s.replace('inner.FixedPanel = FixedPanel.Panel2;','inner.FixedPanel = FixedPanel.Panel2; inner.Panel2Collapsed = true; inner.SplitterWidth = 1;',1)
s=s.replace('ConfigureRightPaneRatio(inner, 0.12, 120, 260);','if (!inner.Panel2Collapsed) ConfigureRightPaneRatio(inner, 0.12, 120, 260);',1)

# Make keyboard hint accurate.
s=s.replace('↑/↓: di chuyển trang • Kéo thả để sắp xếp • Chuột phải: Lên đầu/Xuống cuối','↑/↓: chọn trang • Ctrl+↑/↓: đổi thứ tự • Kéo thả để sắp xếp',1)

# Add a guaranteed visible preview toolbar, independent of the old hidden row.
anchor='_preview = new PictureBox(); _preview.BackColor = Color.White; _preview.SizeMode = PictureBoxSizeMode.Zoom; _preview.Location = new Point(16, 16); _previewScroll.Controls.Add(_preview);'
extra='''_preview = new PictureBox(); _preview.BackColor = Color.White; _preview.SizeMode = PictureBoxSizeMode.Zoom; _preview.Location = new Point(16, 16); _previewScroll.Controls.Add(_preview);\n\n            // v2.4.0: stable preview toolbar like the proven v2.1.0 workflow.\n            previewTop.Visible = false; centerLayout.RowStyles[0] = new RowStyle(SizeType.Absolute, 0); centerLayout.Padding = new Padding(0, 46, 0, 0);\n            Panel stablePreviewTop = new Panel(); stablePreviewTop.Dock = DockStyle.Top; stablePreviewTop.Height = 46; stablePreviewTop.BackColor = Color.White; center.Controls.Add(stablePreviewTop); stablePreviewTop.BringToFront();\n            Label stableTitle = new Label(); stableTitle.Text = "XEM TRƯỚC"; stableTitle.Font = new Font("Segoe UI", 11f, FontStyle.Bold); stableTitle.Dock = DockStyle.Left; stableTitle.Width = 120; stableTitle.TextAlign = ContentAlignment.MiddleLeft; stableTitle.Padding = new Padding(8,0,0,0); stablePreviewTop.Controls.Add(stableTitle);\n            FlowLayoutPanel stableZoom = new FlowLayoutPanel(); stableZoom.Dock = DockStyle.Right; stableZoom.Width = 600; stableZoom.WrapContents = false; stableZoom.Padding = new Padding(0,6,8,0); stablePreviewTop.Controls.Add(stableZoom);\n            _btnFitStable = MakeButton("Vừa cửa sổ", 108, false); _btnFitStable.Height = 32; _btnFitStable.Margin = new Padding(0,0,8,0); _btnFitStable.Click += delegate { SetZoomPercent(100); }; stableZoom.Controls.Add(_btnFitStable);\n            Label stableZl = new Label(); stableZl.Text = "Thu phóng:"; stableZl.AutoSize = false; stableZl.Size = new Size(74,32); stableZl.TextAlign = ContentAlignment.MiddleRight; stableZoom.Controls.Add(stableZl);\n            Button zminus = MakeButton("−", 34, false); zminus.Height=32; zminus.Margin=new Padding(4,0,4,0); zminus.Click += delegate { SetZoomPercent((int)_zoom.Value - 25); }; stableZoom.Controls.Add(zminus);\n            stableZoom.Controls.Add(_zoom); _zoom.Margin = new Padding(0,2,2,0);\n            Label stablePct = new Label(); stablePct.Text = "%"; stablePct.AutoSize=false; stablePct.Size=new Size(22,32); stablePct.TextAlign=ContentAlignment.MiddleLeft; stableZoom.Controls.Add(stablePct);\n            Button zplus = MakeButton("+", 34, false); zplus.Height=32; zplus.Margin=new Padding(0,0,8,0); zplus.Click += delegate { SetZoomPercent((int)_zoom.Value + 25); }; stableZoom.Controls.Add(zplus);\n            foreach (int zp in new int[] {125,150,200}) { int z=zp; Button qb=MakeButton(z.ToString()+"%",58,false); qb.Height=32; qb.Margin=new Padding(0,0,4,0); qb.Click += delegate { SetZoomPercent(z); }; stableZoom.Controls.Add(qb); }\n            _toolTip.SetToolTip(_btnFitStable, "Mặc định khi mở PDF: hiển thị toàn bộ trang vừa cửa sổ, đúng tỷ lệ gốc.");'''
if anchor not in s: raise SystemExit('preview anchor missing')
s=s.replace(anchor,extra,1)

# Preview 100% means fit-to-window; render higher resolution but preserve page ratio.
s=s.replace('scale = Math.Min(1.0, maxDimension / Math.Max(w, h));','scale = Math.Max(0.05, Math.Min(4.0, maxDimension / Math.Max(w, h)));',1)
old='''        private void ApplyZoom()\n        {\n            if (_previewScroll == null || _preview == null || _zoom == null) return;\n            if (_previewMaster == null || _previewScroll.ClientSize.Width <= 20 || _previewScroll.ClientSize.Height <= 20) { _preview.Size = new Size(10, 10); return; }'''
new='''        private void SetZoomPercent(int value)\n        {\n            if (_zoom == null) return; int v = Math.Max((int)_zoom.Minimum, Math.Min((int)_zoom.Maximum, value));\n            if (_zoom.Value != v) _zoom.Value = v; else ApplyZoom();\n        }\n\n        private void ApplyZoom()\n        {\n            if (_previewScroll == null || _preview == null || _zoom == null) return;\n            if (_previewMaster == null || _previewScroll.ClientSize.Width <= 20 || _previewScroll.ClientSize.Height <= 20) { _preview.Size = new Size(10, 10); return; }'''
if old not in s: raise SystemExit('ApplyZoom head missing')
s=s.replace(old,new,1)

# Default fit when every PDF opens.
s=s.replace('_modeDetached.Checked = true; _dirLtr.Checked = true;\n                RefreshList(0);','_modeDetached.Checked = true; _dirLtr.Checked = true; _sourceWasOverwritten = false; _originalBackupPath = ""; if (_zoom != null) _zoom.Value = 100;\n                RefreshList(0);',1)

# Preserve only the true original before the first overwrite in this session.
old='''                    string backupDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "TachXepTrangPDF", "Backups");\n                    Directory.CreateDirectory(backupDir);\n                    string backup = Path.Combine(backupDir, Path.GetFileNameWithoutExtension(target) + "_" + DateTime.Now.ToString("yyyyMMdd_HHmmss") + ".pdf");\n                    File.Copy(target, backup, true);'''
new='''                    if (string.IsNullOrEmpty(_originalBackupPath) || !File.Exists(_originalBackupPath))\n                    {\n                        string backupDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "TachXepTrangPDF", "Backups", DateTime.Now.ToString("yyyyMMdd"));\n                        Directory.CreateDirectory(backupDir); _originalBackupPath = Path.Combine(backupDir, Path.GetFileNameWithoutExtension(target) + "_original_" + DateTime.Now.ToString("HHmmss_fff") + ".pdf");\n                        File.Copy(_workPath, _originalBackupPath, true);\n                    }'''
if old not in s: raise SystemExit('backup marker missing')
s=s.replace(old,new,1)
s=s.replace('SetStatus("Đã lưu vào file gốc. Backup: " + backup);','SetStatus("Đã lưu vào file gốc. Bản gốc an toàn: " + _originalBackupPath); _sourceWasOverwritten = true;',1)

# Restore original is deliberately NOT Redo.
marker='        private void PushHistory()\n'
method='''        private void RestoreOriginalPdf()\n        {\n            if (_busy || _pdf == null) return;\n            if (MessageBox.Show(this, "Đưa PDF về đúng trạng thái khi vừa mở file?\\r\\n\\r\\nMọi chỉnh sửa trong phiên sẽ bị hủy. Nếu đã Lưu vào file gốc, file vật lý cũng được phục hồi.\\r\\n\\r\\nChức năng này khác nút Làm lại (Redo).", "Khôi phục PDF gốc", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) != DialogResult.Yes) { RestoreListFocus(SelectedIndex); return; }\n            SetBusy(true, "Đang khôi phục PDF gốc...");\n            try\n            {\n                if (_sourceWasOverwritten)\n                {\n                    string from = (!string.IsNullOrEmpty(_originalBackupPath) && File.Exists(_originalBackupPath)) ? _originalBackupPath : _workPath;\n                    if (string.IsNullOrEmpty(from) || !File.Exists(from)) throw new FileNotFoundException("Không tìm thấy bản gốc an toàn.");\n                    string tmp = Path.Combine(Path.GetDirectoryName(_sourcePath), "." + Path.GetFileName(_sourcePath) + ".restore.tmp.pdf"); File.Copy(from,tmp,true); ValidateGeneratedPdf(tmp,_pdf.PageCount);\n                    try { File.Replace(tmp,_sourcePath,null,true); } catch { if (File.Exists(_sourcePath)) File.Delete(_sourcePath); File.Move(tmp,_sourcePath); }\n                    _sourceWasOverwritten=false;\n                }\n                _sources.Clear(); _outputs.Clear(); _undo.Clear(); _redo.Clear(); _isSplit=false;\n                for(int i=0;i<_pdf.PageCount;i++) _sources.Add(new SourceFace { OriginalSourceIndex=i, Rotation=0, CutPercent=50.0 });\n                _modeDetached.Checked=true; _modeBound.Checked=false; _dirLtr.Checked=true; _dirRtl.Checked=false; if(_zoom!=null) _zoom.Value=100; RefreshList(0);\n                SetStatus("Đã khôi phục PDF về trạng thái ban đầu khi mở file.");\n            }\n            catch(Exception ex) { AppDiagnostics.LogException("RESTORE_ORIGINAL_FAIL",ex); MessageBox.Show(this,"Chưa khôi phục được PDF gốc.\\r\\n\\r\\n"+ex.Message,"Khôi phục PDF gốc",MessageBoxButtons.OK,MessageBoxIcon.Error); }\n            finally { SetBusy(false,null); RestoreListFocus(0); }\n        }\n\n'''
if marker not in s: raise SystemExit('PushHistory marker missing')
s=s.replace(marker,method+marker,1)

# Button state + cleanup.
s=s.replace('_btnSaveOriginal.Enabled = !busy && _pdf != null;','_btnSaveOriginal.Enabled = !busy && _pdf != null; _btnRestoreOriginal.Enabled = !busy && _pdf != null;',1)
s=s.replace('_btnSaveOriginal.Enabled = _btnExport.Enabled;','_btnSaveOriginal.Enabled = _btnExport.Enabled; _btnRestoreOriginal.Enabled = has;',1)
s=s.replace('_isSplit = false; _sourcePath = ""; _workPath = "";','_isSplit = false; _sourcePath = ""; _workPath = ""; _sourceWasOverwritten = false; _originalBackupPath = "";',1)

# UI smoke: third pane gone, preview controls and restore present.
s=s.replace('''                            "Vừa cửa sổ",\n                            "HƯỚNG DẪN"''','''                            "Vừa cửa sổ",\n                            "125%",\n                            "150%",\n                            "200%",\n                            "Khôi phục PDF gốc"''',1)
s=s.replace('''                            Control guide = FindControlByText(form, "HƯỚNG DẪN");\n                            if (guide != null)\n                            {\n                                double gr = guide.Width / (double)Math.Max(1, form.ClientSize.Width);\n                                if (gr > 0.15) throw new InvalidOperationException("Right info pane too wide: " + guide.Width.ToString());\n                                if (gr < 0.055) throw new InvalidOperationException("Right info pane too narrow: " + guide.Width.ToString());\n                            }''','''                            Control guide = FindControlByText(form, "HƯỚNG DẪN");\n                            if (guide != null && guide.Visible && guide.RectangleToScreen(guide.ClientRectangle).IntersectsWith(form.RectangleToScreen(form.ClientRectangle))) throw new InvalidOperationException("Third guide pane is still visible.");''',1)

# Self-test renderer ratio.
s=s.replace('''                    using (Bitmap rendered = pdf.RenderPageMax(0, 180))\n                    {\n                        if (rendered.Width <= 0 || rendered.Height <= 0) throw new InvalidDataException("PDF self-test render failed.");\n                    }''','''                    SizeF dip = pdf.GetPageDipSize(0);\n                    using (Bitmap rendered = pdf.RenderPageMax(0, 180))\n                    {\n                        if (rendered.Width <= 0 || rendered.Height <= 0) throw new InvalidDataException("PDF self-test render failed.");\n                        double er=dip.Width/Math.Max(1.0,dip.Height), ar=rendered.Width/(double)Math.Max(1,rendered.Height); if(Math.Abs(er-ar)>0.015) throw new InvalidDataException("PDF preview aspect ratio mismatch.");\n                    }''',1)

p.write_text(s,encoding='utf-8-sig')
launcher=Path('tach-xep-pdf-v2.3.2/launcher.cpp')
if launcher.exists():
    ls=launcher.read_text(encoding='utf-8-sig'); ls2=ls.replace('2.3.5','2.4.0')
    if ls2==ls: raise SystemExit('launcher version marker missing')
    launcher.write_text(ls2,encoding='utf-8-sig')
print('PATCH_V240_OK')