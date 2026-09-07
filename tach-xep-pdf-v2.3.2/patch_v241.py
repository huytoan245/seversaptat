from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

# Version
s=s.replace('private const string AppVersion = "2.4.0";','private const string AppVersion = "2.4.1";',1)

# Cleaner/modern toolbar: remove wasted third settings column and the huge AI status label from the action strip.
s=s.replace('''            _autoRotateStatus.AutoSize = false;\n            _autoRotateStatus.Size = new Size(560, 36);\n            _autoRotateStatus.TextAlign = ContentAlignment.MiddleLeft;\n            _autoRotateStatus.ForeColor = Color.FromArgb(90, 90, 90);\n            _autoRotateStatus.Margin = new Padding(0, 0, 0, 0);\n            actions.Controls.Add(_autoRotateStatus);''','''            _autoRotateStatus.AutoSize = false;\n            _autoRotateStatus.Size = new Size(1, 1);\n            _autoRotateStatus.Visible = false;\n            _autoRotateStatus.ForeColor = Color.FromArgb(90, 90, 90);''',1)
old='''            settings.ColumnCount = 3;\n            settings.RowCount = 1;\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 420));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 285));'''
new='''            settings.ColumnCount = 2;\n            settings.RowCount = 1;\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 390));\n            settings.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));'''
if old not in s: raise SystemExit('settings column block missing')
s=s.replace(old,new,1)

# Remove clipped "Chỉnh tay" prefix and reclaim room; make manual row DPI-safe.
s=s.replace('manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 38));','manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 46));',1)
s=s.replace('''            Label man = new Label(); man.Text = "Chỉnh tay:"; man.AutoSize = false; man.Size = new Size(68, 34); man.TextAlign = ContentAlignment.MiddleLeft; manualButtons.Controls.Add(man);''','''            manualButtons.Padding = new Padding(0, 2, 0, 0);''',1)
s=s.replace('cutRow.Padding = new Padding(68, 2, 0, 0);','cutRow.Padding = new Padding(0, 2, 0, 0);',1)

# Replace the old GroupBox direction block inside the flow row with a modern inline panel; avoids clipped title at DPI scaling.
old='''            settings.Controls.Remove(direction); direction.Dock = DockStyle.None; direction.Text = "CHIỀU CẮT"; direction.Size = new Size(255, 36); direction.Margin = new Padding(0); _dirLtr.Location = new Point(10, 12); _dirRtl.Location = new Point(130, 12); manualButtons.Controls.Add(direction);'''
new='''            settings.Controls.Remove(direction); direction.Visible = false; direction.Controls.Remove(_dirLtr); direction.Controls.Remove(_dirRtl);\n            FlowLayoutPanel directionInline = new FlowLayoutPanel(); directionInline.WrapContents = false; directionInline.AutoSize = false; directionInline.Size = new Size(300, 38); directionInline.Margin = new Padding(4, 0, 0, 0); directionInline.Padding = new Padding(4, 3, 0, 0);\n            Label dirLabel = new Label(); dirLabel.Text = "Chiều cắt:"; dirLabel.AutoSize = false; dirLabel.Size = new Size(72, 30); dirLabel.TextAlign = ContentAlignment.MiddleLeft; directionInline.Controls.Add(dirLabel);\n            _dirLtr.AutoSize = false; _dirLtr.Size = new Size(104, 30); _dirLtr.Margin = new Padding(0); directionInline.Controls.Add(_dirLtr);\n            _dirRtl.AutoSize = false; _dirRtl.Size = new Size(104, 30); _dirRtl.Margin = new Padding(0); directionInline.Controls.Add(_dirRtl);\n            manualButtons.Controls.Add(directionInline);'''
if old not in s: raise SystemExit('direction group marker missing')
s=s.replace(old,new,1)

# Stable preview controls must live INSIDE centerLayout row 0, not as an overlay sibling.
start='''            // v2.4.0: stable preview toolbar like the proven v2.1.0 workflow.\n            previewTop.Visible = false; centerLayout.RowStyles[0] = new RowStyle(SizeType.Absolute, 0); centerLayout.Padding = new Padding(0, 46, 0, 0);'''
end='''            _toolTip.SetToolTip(_btnFitStable, "Mặc định khi mở PDF: hiển thị toàn bộ trang vừa cửa sổ, đúng tỷ lệ gốc.");'''
si=s.find(start)
if si<0: raise SystemExit('stable preview start missing')
ei=s.find(end,si)
if ei<0: raise SystemExit('stable preview end missing')
ei += len(end)
newblock='''            // v2.4.1: preview toolbar is a real layout row, always visible and never covered by Dock/BringToFront.\n            centerLayout.Padding = new Padding(0); centerLayout.RowStyles[0] = new RowStyle(SizeType.Absolute, 48); previewTop.Visible = true;\n            previewTop.Controls.Clear(); previewTop.ColumnStyles.Clear(); previewTop.ColumnCount = 2; previewTop.RowCount = 1;\n            previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 125)); previewTop.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));\n            Label stableTitle = new Label(); stableTitle.Text = "XEM TRƯỚC"; stableTitle.Font = new Font("Segoe UI", 11f, FontStyle.Bold); stableTitle.Dock = DockStyle.Fill; stableTitle.TextAlign = ContentAlignment.MiddleLeft; stableTitle.Padding = new Padding(8,0,0,0); previewTop.Controls.Add(stableTitle,0,0);\n            FlowLayoutPanel stableZoom = new FlowLayoutPanel(); stableZoom.Dock = DockStyle.Fill; stableZoom.WrapContents = false; stableZoom.AutoScroll = true; stableZoom.FlowDirection = FlowDirection.LeftToRight; stableZoom.Padding = new Padding(0,7,0,0); previewTop.Controls.Add(stableZoom,1,0);\n            _btnFitStable = MakeButton("Vừa màn hình", 118, false); _btnFitStable.Height = 32; _btnFitStable.Margin = new Padding(0,0,10,0); _btnFitStable.Click += delegate { SetZoomPercent(100); }; stableZoom.Controls.Add(_btnFitStable);\n            Label stableZl = new Label(); stableZl.Text = "Thu phóng:"; stableZl.AutoSize = false; stableZl.Size = new Size(76,32); stableZl.TextAlign = ContentAlignment.MiddleRight; stableZoom.Controls.Add(stableZl);\n            Button zminus = MakeButton("−", 36, false); zminus.Height=32; zminus.Margin=new Padding(4,0,4,0); zminus.Click += delegate { SetZoomPercent((int)_zoom.Value - 25); }; stableZoom.Controls.Add(zminus);\n            _zoom.Width = 72; _zoom.Height = 30; _zoom.Margin = new Padding(0,2,2,0); stableZoom.Controls.Add(_zoom);\n            Label stablePct = new Label(); stablePct.Text = "%"; stablePct.AutoSize=false; stablePct.Size=new Size(22,32); stablePct.TextAlign=ContentAlignment.MiddleLeft; stableZoom.Controls.Add(stablePct);\n            Button zplus = MakeButton("+", 36, false); zplus.Height=32; zplus.Margin=new Padding(0,0,10,0); zplus.Click += delegate { SetZoomPercent((int)_zoom.Value + 25); }; stableZoom.Controls.Add(zplus);\n            foreach (int zp in new int[] {125,150,200}) { int z=zp; Button qb=MakeButton(z.ToString()+"%",60,false); qb.Height=32; qb.Margin=new Padding(0,0,5,0); qb.Click += delegate { SetZoomPercent(z); }; stableZoom.Controls.Add(qb); }\n            _toolTip.SetToolTip(_btnFitStable, "Hiển thị trọn trang PDF trong vùng xem, giữ đúng tỷ lệ gốc. Đây là chế độ mặc định khi mở file.");'''
s=s[:si]+newblock+s[ei:]

# Aspect-safe PDF renderer: NEVER force both width and height. Microsoft Windows.Data.Pdf preserves aspect ratio when the other dimension is unspecified.
old='''                Windows.Foundation.Rect r = page.Dimensions.MediaBox;\n                double w = Math.Max(1.0, r.Width);\n                double h = Math.Max(1.0, r.Height);\n                double scale = 1.0;\n                if (dpi > 0.0)\n                    scale = dpi / 96.0;\n                else if (maxDimension > 0)\n                    scale = Math.Max(0.05, Math.Min(4.0, maxDimension / Math.Max(w, h)));\n\n                uint dw = (uint)Math.Max(1, Math.Round(w * scale));\n                uint dh = (uint)Math.Max(1, Math.Round(h * scale));\n                PdfPageRenderOptions opts = new PdfPageRenderOptions();\n                opts.DestinationWidth = dw;\n                opts.DestinationHeight = dh;\n                opts.IsIgnoringHighContrast = true;'''
new='''                Windows.Foundation.Size ps = page.Size;\n                double w = Math.Max(1.0, ps.Width);\n                double h = Math.Max(1.0, ps.Height);\n                double scale = 1.0;\n                if (dpi > 0.0) scale = dpi / 96.0;\n                else if (maxDimension > 0) scale = Math.Max(0.05, Math.Min(6.0, maxDimension / Math.Max(w, h)));\n\n                uint dw = (uint)Math.Max(1, Math.Round(w * scale));\n                PdfPageRenderOptions opts = new PdfPageRenderOptions();\n                // Only DestinationWidth is specified. Windows computes height and preserves the PDF page's effective aspect ratio, including /Rotate metadata.\n                opts.DestinationWidth = dw;\n                opts.IsIgnoringHighContrast = true;'''
if old not in s: raise SystemExit('renderer forcing both dimensions marker missing')
s=s.replace(old,new,1)

# Effective display size must also respect PDF rotation metadata.
old='''                    Windows.Foundation.Rect r = page.Dimensions.MediaBox;\n                    return new SizeF((float)r.Width, (float)r.Height);'''
new='''                    Windows.Foundation.Size ps = page.Size;\n                    return new SizeF((float)ps.Width, (float)ps.Height);'''
if old not in s: raise SystemExit('GetPageDipSize marker missing')
s=s.replace(old,new,1)

# Make PDF writer capable of creating a /Rotate regression sample without affecting normal exports.
s=s.replace('''            internal double Dpi;\n        }''','''            internal double Dpi;\n            internal int PdfRotation;\n        }''',1)
old='''                    WriteObj(bw, fs, offsets, pageObj,\n                        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 " + F(pw) + " " + F(ph) + "] /Resources << /XObject << /Im0 " + imgObj.ToString() + " 0 R >> >> /Contents " + contentObj.ToString() + " 0 R >>");'''
new='''                    int pdfRot = ImageOps.NormRotation(p.PdfRotation); string rotateEntry = pdfRot == 0 ? "" : " /Rotate " + pdfRot.ToString();\n                    WriteObj(bw, fs, offsets, pageObj,\n                        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 " + F(pw) + " " + F(ph) + "]" + rotateEntry + " /Resources << /XObject << /Im0 " + imgObj.ToString() + " 0 R >> >> /Contents " + contentObj.ToString() + " 0 R >>");'''
if old not in s: raise SystemExit('PDF writer page object marker missing')
s=s.replace(old,new,1)

# Add a rotated-page metadata regression: ratio must swap and renderer must not stretch it.
needle='''                    AppDiagnostics.Log("SELFTEST", "PASS");'''
extra='''                    string rotatedPdfPath = Path.Combine(testDir, "self-test-rotate90.pdf");\n                    SimplePdfWriter.WriteFromFactory(rotatedPdfPath, 1, delegate(int index)\n                    {\n                        using (Bitmap b = new Bitmap(96, 128, PixelFormat.Format24bppRgb))\n                        {\n                            using (Graphics g = Graphics.FromImage(b)) { g.Clear(Color.White); g.DrawString("ROTATE", SystemFonts.DefaultFont, Brushes.Black, 8, 8); }\n                            using (MemoryStream ms = new MemoryStream()) { b.Save(ms, ImageFormat.Jpeg); return new SimplePdfWriter.ImagePage { Jpeg=ms.ToArray(), PixelWidth=b.Width, PixelHeight=b.Height, Dpi=96.0, PdfRotation=90 }; }\n                        }\n                    }, null);\n                    using (PdfSession rotatedPdf = new PdfSession(rotatedPdfPath))\n                    {\n                        SizeF rsz = rotatedPdf.GetPageDipSize(0);\n                        using (Bitmap rb = rotatedPdf.RenderPageMax(0, 400))\n                        {\n                            double expected = rsz.Width / Math.Max(1.0, rsz.Height); double actual = rb.Width / (double)Math.Max(1, rb.Height);\n                            if (Math.Abs(expected-actual) > 0.02) throw new InvalidDataException("Rotated PDF preview was stretched: expected="+expected.ToString("0.000")+" actual="+actual.ToString("0.000"));\n                        }\n                    }\n                    AppDiagnostics.Log("SELFTEST", "PASS");'''
if needle not in s: raise SystemExit('selftest pass marker missing')
s=s.replace(needle,extra,1)

# Modern button styling and enough internal padding so labels never look truncated.
old='''            Button b = new Button(); b.Text = text; b.Width = width; b.Height = 38; b.TabStop = false; b.FlatStyle = FlatStyle.Flat;\n            b.FlatAppearance.BorderColor = prominent ? Color.FromArgb(45, 110, 180) : Color.FromArgb(190, 195, 202);\n            b.BackColor = prominent ? Color.FromArgb(235, 244, 255) : Color.White;\n            b.Font = new Font("Segoe UI", 9.5f, FontStyle.Bold);\n            return b;'''
new='''            Button b = new Button(); b.Text = text; b.Width = width; b.Height = 38; b.TabStop = false; b.FlatStyle = FlatStyle.Flat; b.UseVisualStyleBackColor = false;\n            b.FlatAppearance.BorderSize = 1; b.Padding = new Padding(5,0,5,0);\n            b.FlatAppearance.BorderColor = prominent ? Color.FromArgb(37, 99, 235) : Color.FromArgb(203, 213, 225);\n            b.BackColor = prominent ? Color.FromArgb(37, 99, 235) : Color.White; b.ForeColor = prominent ? Color.White : Color.FromArgb(30,41,59);\n            b.FlatAppearance.MouseOverBackColor = prominent ? Color.FromArgb(29,78,216) : Color.FromArgb(241,245,249);\n            b.FlatAppearance.MouseDownBackColor = prominent ? Color.FromArgb(30,64,175) : Color.FromArgb(226,232,240);\n            b.Font = new Font("Segoe UI", 9.25f, FontStyle.Bold);\n            return b;'''
if old not in s: raise SystemExit('MakeButton marker missing')
s=s.replace(old,new,1)

# UI smoke now verifies the controls are ACTUALLY visible, not merely present in a hidden tree.
s=s.replace('"Vừa cửa sổ",','"Vừa màn hình",',1)
s=s.replace('Button fitButton = FindControlByText(form, "Vừa cửa sổ") as Button;','Button fitButton = FindControlByText(form, "Vừa màn hình") as Button;',1)
old='''                            Button fitButton = FindControlByText(form, "Vừa màn hình") as Button;\n                            if (fitButton == null) throw new InvalidOperationException("Fit-to-window button missing.");\n                            fitButton.PerformClick();'''
new='''                            Button fitButton = FindControlByText(form, "Vừa màn hình") as Button;\n                            if (fitButton == null || !fitButton.Visible) throw new InvalidOperationException("Visible fit-to-window button missing.");\n                            Rectangle fitRc = fitButton.RectangleToScreen(fitButton.ClientRectangle); Rectangle formRc = form.RectangleToScreen(form.ClientRectangle); if(!formRc.IntersectsWith(fitRc)) throw new InvalidOperationException("Fit-to-window button outside viewport.");\n                            fitButton.PerformClick();\n                            foreach(string ztxt in new string[]{"125%","150%","200%"}) AssertUiControlVisible(form, ztxt);\n                            Control clipped = FindControlByText(form, "Chỉnh tay:"); if(clipped != null && clipped.Visible) throw new InvalidOperationException("Legacy clipped manual label is still visible.");'''
if old not in s: raise SystemExit('UI smoke fit block missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8-sig')
launcher=Path('tach-xep-pdf-v2.3.2/launcher.cpp')
if launcher.exists():
    ls=launcher.read_text(encoding='utf-8-sig'); ls2=ls.replace('2.4.0','2.4.1')
    if ls2==ls: raise SystemExit('launcher version marker missing')
    launcher.write_text(ls2,encoding='utf-8-sig')
print('PATCH_V241_VISIBLE_ZOOM_ASPECT_SAFE_OK')