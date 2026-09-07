from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# Final v2.3.5 layout hardening: keep the guide pane at ~12% of the whole window,
# not 12% of the already-shrunken inner splitter. This also makes the setting
# deterministic after DPI/layout changes and after maximize/restore.
old_calls = 'ConfigureRightPaneRatio(inner, 0.14, 170, 250)'
new_calls = 'ConfigureRightPaneRatio(inner, 0.12, 120, 260)'
count = s.count(old_calls)
if count != 2:
    raise SystemExit(f'expected two right-pane ratio calls, found {count}')
s = s.replace(old_calls, new_calls)

inner_anchor = '            SplitContainer inner = new SplitContainer(); inner.Dock = DockStyle.Fill; inner.Orientation = Orientation.Vertical; inner.SplitterWidth = 6; outer.Panel2.Controls.Add(inner);'
inner_new = inner_anchor + '\n            inner.FixedPanel = FixedPanel.Panel2;'
if inner_anchor not in s:
    raise SystemExit('inner splitter anchor not found')
s = s.replace(inner_anchor, inner_new, 1)

old_helper = '''        private static void ConfigureRightPaneRatio(SplitContainer split, double ratio, int minRight, int maxRight)\n        {\n            if (split == null || split.IsDisposed) return;\n            int total = split.Orientation == Orientation.Vertical ? split.ClientSize.Width : split.ClientSize.Height;\n            if (total <= split.SplitterWidth + 2) return;\n            split.Panel1MinSize = 0; split.Panel2MinSize = 0;\n            int right = (int)Math.Round(total * Math.Max(0.10, Math.Min(0.15, ratio)));\n            right = Math.Max(minRight, Math.Min(maxRight, right));\n            if (total < 700) right = Math.Max(120, Math.Min(right, (int)Math.Round(total * 0.15)));\n            int distance = Math.Max(1, Math.Min(total - split.SplitterWidth - 1, total - split.SplitterWidth - right));\n            if (Math.Abs(split.SplitterDistance - distance) > 1) split.SplitterDistance = distance;\n            if (total >= 420 + minRight + split.SplitterWidth) { split.Panel1MinSize = 420; split.Panel2MinSize = Math.Min(minRight, Math.Max(0, total - split.SplitterWidth - 420)); }\n        }'''
new_helper = '''        private static void ConfigureRightPaneRatio(SplitContainer split, double ratio, int minRight, int maxRight)\n        {\n            if (split == null || split.IsDisposed) return;\n            int total = split.Orientation == Orientation.Vertical ? split.ClientSize.Width : split.ClientSize.Height;\n            if (total <= split.SplitterWidth + 2) return;\n\n            // User requirement is 10-15% of the WINDOW width. Using the inner splitter width\n            // made the pane inconsistent because the left thumbnail column had already been removed.\n            Form host = split.FindForm();\n            int basis = host != null && host.ClientSize.Width > 0 ? host.ClientSize.Width : total;\n            double safeRatio = Math.Max(0.10, Math.Min(0.15, ratio));\n            int right = (int)Math.Round(basis * safeRatio);\n            right = Math.Max(minRight, Math.Min(maxRight, right));\n\n            // Never sacrifice the preview below its usable minimum.\n            int minCenter = 420;\n            int maxByCenter = Math.Max(1, total - split.SplitterWidth - minCenter);\n            right = Math.Min(right, maxByCenter);\n            right = Math.Max(1, right);\n\n            split.Panel1MinSize = 0;\n            split.Panel2MinSize = 0;\n            int distance = total - split.SplitterWidth - right;\n            distance = Math.Max(1, Math.Min(total - split.SplitterWidth - 1, distance));\n            if (Math.Abs(split.SplitterDistance - distance) > 1) split.SplitterDistance = distance;\n\n            if (total >= minCenter + minRight + split.SplitterWidth)\n            {\n                split.Panel1MinSize = minCenter;\n                split.Panel2MinSize = Math.Min(minRight, Math.Max(0, total - split.SplitterWidth - minCenter));\n            }\n        }'''
if old_helper not in s:
    raise SystemExit('right pane helper not found')
s = s.replace(old_helper, new_helper, 1)

old_shown = '''            Shown += delegate\n            {\n                ConfigureSplitterSafe(outer, 330, 250, 680);\n                ConfigureRightPaneRatio(inner, 0.12, 120, 260);\n                ApplyZoom();\n            };\n            inner.Resize += delegate { ConfigureRightPaneRatio(inner, 0.12, 120, 260); };'''
new_shown = '''            Action applyResponsiveLayout = delegate\n            {\n                if (IsDisposed) return;\n                ConfigureSplitterSafe(outer, 330, 250, 680);\n                ConfigureRightPaneRatio(inner, 0.12, 120, 260);\n                ApplyZoom();\n            };\n            Shown += delegate\n            {\n                if (IsHandleCreated) BeginInvoke(new Action(applyResponsiveLayout));\n            };\n            Resize += delegate\n            {\n                if (IsHandleCreated && !IsDisposed) BeginInvoke(new Action(applyResponsiveLayout));\n            };'''
if old_shown not in s:
    raise SystemExit('responsive shown/resize block not found')
s = s.replace(old_shown, new_shown, 1)

# Reduce preview flicker: only change bounds when needed and suspend layout while doing so.
old_zoom_tail = '''            int w = Math.Max(1, (int)Math.Round(_previewMaster.Width * scale)); int h = Math.Max(1, (int)Math.Round(_previewMaster.Height * scale));\n            int x = w < aw ? margin + (aw - w) / 2 : margin; int y = h < ah ? margin + (ah - h) / 2 : margin;\n            _preview.SizeMode = PictureBoxSizeMode.Zoom; _preview.Size = new Size(w, h); _preview.Location = new Point(x, y);'''
new_zoom_tail = '''            int w = Math.Max(1, (int)Math.Round(_previewMaster.Width * scale)); int h = Math.Max(1, (int)Math.Round(_previewMaster.Height * scale));\n            int x = w < aw ? margin + (aw - w) / 2 : margin; int y = h < ah ? margin + (ah - h) / 2 : margin;\n            Rectangle wanted = new Rectangle(x, y, w, h);\n            _previewScroll.SuspendLayout();\n            try\n            {\n                _preview.SizeMode = PictureBoxSizeMode.Zoom;\n                if (_preview.Bounds != wanted) _preview.Bounds = wanted;\n            }\n            finally { _previewScroll.ResumeLayout(false); }'''
if old_zoom_tail not in s:
    raise SystemExit('zoom bounds tail not found')
s = s.replace(old_zoom_tail, new_zoom_tail, 1)

# Strengthen smoke checks: guide must be narrow but still readable; file label must be above Open PDF;
# Redo must be to the left of Undo; fit button must be actionable without a loaded PDF.
old_smoke = '''                            Control guide = FindControlByText(form, "HƯỚNG DẪN");\n                            if (guide != null && guide.Width > form.ClientSize.Width * 0.17) throw new InvalidOperationException("Right info pane too wide: " + guide.Width.ToString());\n                        }'''
new_smoke = '''                            Control guide = FindControlByText(form, "HƯỚNG DẪN");\n                            if (guide != null)\n                            {\n                                double gr = guide.Width / (double)Math.Max(1, form.ClientSize.Width);\n                                if (gr > 0.15) throw new InvalidOperationException("Right info pane too wide: " + guide.Width.ToString());\n                                if (gr < 0.055) throw new InvalidOperationException("Right info pane too narrow: " + guide.Width.ToString());\n                            }\n                            Control fileLabel = FindControlByText(form, "File đang mở: Chưa mở tài liệu");\n                            Control openButton = FindControlByText(form, "Mở PDF");\n                            if (fileLabel == null || openButton == null || fileLabel.RectangleToScreen(fileLabel.ClientRectangle).Bottom > openButton.RectangleToScreen(openButton.ClientRectangle).Top + 2)\n                                throw new InvalidOperationException("File label is not directly above Open PDF.");\n                            Control redo = FindControlByText(form, "Làm lại"); Control undo = FindControlByText(form, "Hoàn tác");\n                            if (redo == null || undo == null || redo.RectangleToScreen(redo.ClientRectangle).Left >= undo.RectangleToScreen(undo.ClientRectangle).Left)\n                                throw new InvalidOperationException("Redo/Undo order is incorrect.");\n                            Button fitButton = FindControlByText(form, "Vừa cửa sổ") as Button;\n                            if (fitButton == null) throw new InvalidOperationException("Fit-to-window button missing.");\n                            fitButton.PerformClick();\n                        }'''
if old_smoke not in s:
    raise SystemExit('UI smoke guide block not found')
s = s.replace(old_smoke, new_smoke, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V235F_FINAL_UI_HARDENING_OK')
