from pathlib import Path

root = Path('tach-xep-pdf-v2.3.2')
p = root / 'TachXepTrangPDF.cs'
s = p.read_text(encoding='utf-8-sig')

# v2.6.1 is a surgical Preview input patch on top of the verified v2.6.0 source.
# It MUST NOT rewrite page selection/render/cache/order/export logic.
old_version = 'private const string AppVersion = "2.6.0";'
if old_version not in s:
    raise SystemExit('v2.6.0 source marker missing')
s = s.replace(old_version, 'private const string AppVersion = "2.6.1";', 1)

# Pan state is UI-only. It stores viewport coordinates and never participates in PDF state/history.
field_marker = '        private Panel _previewScroll;\n'
if field_marker not in s:
    raise SystemExit('previewScroll field marker missing')
pan_fields = '''        private bool _previewPanning;\n        private Point _previewPanStartMouse;\n        private Point _previewPanStartScroll;\n'''
s = s.replace(field_marker, field_marker + pan_fields, 1)

# Wire drag-pan to the EXISTING SmoothPreviewPanel + PictureBox. No replacement of preview controls.
wire_marker = '            _preview = new PictureBox(); _preview.BackColor = Color.White; _preview.SizeMode = PictureBoxSizeMode.Zoom; _preview.Location = new Point(16, 16); _previewScroll.Controls.Add(_preview);\n'
if wire_marker not in s:
    raise SystemExit('preview construction marker missing')
wire = wire_marker + '''            // v2.6.1: viewport-only drag pan. Reuse the existing SmoothPreviewPanel/AutoScroll\n            // so page selection, real-page cache, atomic preview swap and renderer stay untouched.\n            _previewScroll.MouseDown += PreviewPanMouseDown; _previewScroll.MouseMove += PreviewPanMouseMove; _previewScroll.MouseUp += PreviewPanMouseUp; _previewScroll.MouseCaptureChanged += PreviewPanCaptureChanged;\n            _preview.MouseDown += PreviewPanMouseDown; _preview.MouseMove += PreviewPanMouseMove; _preview.MouseUp += PreviewPanMouseUp; _preview.MouseCaptureChanged += PreviewPanCaptureChanged;\n'''
s = s.replace(wire_marker, wire, 1)

# Add UI-only pan helpers immediately before SetPreview. They do not render, select, mutate history,
# change document status, or touch the preview cache.
helper_marker = '        private void SetPreview(Bitmap b)\n'
if helper_marker not in s:
    raise SystemExit('SetPreview marker missing')
helpers = r'''        private bool CanPanPreview()
        {
            if (_previewScroll == null || _preview == null || _previewMaster == null) return false;
            return _previewScroll.HorizontalScroll.Visible || _previewScroll.VerticalScroll.Visible
                || _preview.Width > _previewScroll.ClientSize.Width || _preview.Height > _previewScroll.ClientSize.Height;
        }

        private static int ScrollMaximum(ScrollProperties scroll)
        {
            if (scroll == null) return 0;
            return Math.Max(0, scroll.Maximum - scroll.LargeChange + 1);
        }

        private void SetPreviewPanPosition(int x, int y)
        {
            if (_previewScroll == null || _previewScroll.IsDisposed) return;
            int maxX = ScrollMaximum(_previewScroll.HorizontalScroll);
            int maxY = ScrollMaximum(_previewScroll.VerticalScroll);
            int nx = Math.Max(0, Math.Min(maxX, x));
            int ny = Math.Max(0, Math.Min(maxY, y));
            _previewScroll.AutoScrollPosition = new Point(nx, ny);
        }

        private void UpdatePreviewPanCursor()
        {
            if (_previewScroll == null || _preview == null) return;
            Cursor c = _previewPanning ? Cursors.SizeAll : (CanPanPreview() ? Cursors.Hand : Cursors.Default);
            _previewScroll.Cursor = c;
            _preview.Cursor = c;
        }

        private void PreviewPanMouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left || !CanPanPreview()) return;
            _previewPanning = true;
            _previewPanStartMouse = Control.MousePosition;
            _previewPanStartScroll = new Point(_previewScroll.HorizontalScroll.Value, _previewScroll.VerticalScroll.Value);
            Control c = sender as Control;
            if (c != null) c.Capture = true;
            UpdatePreviewPanCursor();
        }

        private void PreviewPanMouseMove(object sender, MouseEventArgs e)
        {
            if (!_previewPanning || _previewScroll == null) return;
            Point now = Control.MousePosition;
            int dx = now.X - _previewPanStartMouse.X;
            int dy = now.Y - _previewPanStartMouse.Y;
            SetPreviewPanPosition(_previewPanStartScroll.X - dx, _previewPanStartScroll.Y - dy);
        }

        private void PreviewPanMouseUp(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left) return;
            Control c = sender as Control;
            if (c != null) c.Capture = false;
            _previewPanning = false;
            UpdatePreviewPanCursor();
        }

        private void PreviewPanCaptureChanged(object sender, EventArgs e)
        {
            Control c = sender as Control;
            if (c != null && c.Capture) return;
            if (_previewPanning) { _previewPanning = false; UpdatePreviewPanCursor(); }
        }

'''
s = s.replace(helper_marker, helpers + helper_marker, 1)

# At fit-or-smaller, reset viewport only. At zoomed sizes, preserve current pan. This does not
# trigger rendering and prevents a stale scrollbar offset after pressing "Vừa cửa sổ".
zoom_finally = '            finally { _previewScroll.ResumeLayout(false); }\n        }\n\n        protected override void OnResize(EventArgs e)\n'
if zoom_finally not in s:
    raise SystemExit('ApplyZoom closing marker missing')
zoom_replacement = '''            finally { _previewScroll.ResumeLayout(false); }\n            if (_zoom.Value <= 100) SetPreviewPanPosition(0, 0);\n            UpdatePreviewPanCursor();\n        }\n\n        protected override void OnResize(EventArgs e)\n'''
s = s.replace(zoom_finally, zoom_replacement, 1)

# Extend the existing workflow smoke with a pan-isolation regression. It deliberately verifies
# that panning changes only scroll offsets and that page navigation still resolves the selected page.
smoke_anchor = '''                _btnFitStable.PerformClick(); Application.DoEvents();\n                if (_zoom.Value != 100) throw new InvalidOperationException("Workflow smoke: fit-to-window did not restore 100%.");\n\n'''
if smoke_anchor not in s:
    raise SystemExit('workflow zoom/fit smoke anchor missing')
pan_smoke = r'''                // v2.6.1 Preview-pan regression: scroll viewport only; never mutate document/page/cache state.
                SetZoomPercent(143); Application.DoEvents();
                int panSelectedIndex = SelectedIndex;
                string panSelectedKey = _previewModelKey;
                DocumentProcessingState panProcessingState = _activeDocument == null ? DocumentProcessingState.NotProcessed : _activeDocument.ProcessingState;
                int panUndoCount = _undo.Count, panRedoCount = _redo.Count, panCacheCount;
                lock (_previewCacheSync) panCacheCount = _previewCache.Count;
                int panMaxX = ScrollMaximum(_previewScroll.HorizontalScroll), panMaxY = ScrollMaximum(_previewScroll.VerticalScroll);
                if (panMaxX <= 0 && panMaxY <= 0) throw new InvalidOperationException("Workflow smoke: zoom 143% did not expose a pannable viewport.");
                SetPreviewPanPosition(Math.Min(64, panMaxX), Math.Min(64, panMaxY)); Application.DoEvents();
                bool panMoved = (panMaxX > 0 && _previewScroll.HorizontalScroll.Value > 0) || (panMaxY > 0 && _previewScroll.VerticalScroll.Value > 0);
                if (!panMoved) throw new InvalidOperationException("Workflow smoke: preview viewport did not pan.");
                int panCacheAfter; lock (_previewCacheSync) panCacheAfter = _previewCache.Count;
                if (SelectedIndex != panSelectedIndex || _previewModelKey != panSelectedKey || _undo.Count != panUndoCount || _redo.Count != panRedoCount || panCacheAfter != panCacheCount)
                    throw new InvalidOperationException("Workflow smoke: panning changed page/history/cache state.");
                if (_activeDocument != null && _activeDocument.ProcessingState != panProcessingState)
                    throw new InvalidOperationException("Workflow smoke: panning changed PDF processing status.");

                SelectAdjacent(1); Application.DoEvents();
                int navAfterPan = SelectedIndex;
                if (navAfterPan != panSelectedIndex + 1 || _preview.Image == null) throw new InvalidOperationException("Workflow smoke: page-down failed after panning.");
                string navAfterPanKey = ModelKey(_list.Items[navAfterPan].Tag);
                long navWait = Environment.TickCount64;
                while (_previewModelKey != navAfterPanKey && Environment.TickCount64 - navWait < 5000) { Application.DoEvents(); Thread.Sleep(15); }
                if (_previewModelKey != navAfterPanKey) throw new InvalidOperationException("Workflow smoke: preview did not follow page-down after panning.");
                SelectAdjacent(-1); Application.DoEvents();
                navWait = Environment.TickCount64;
                while (_previewModelKey != panSelectedKey && Environment.TickCount64 - navWait < 5000) { Application.DoEvents(); Thread.Sleep(15); }
                if (SelectedIndex != panSelectedIndex || _previewModelKey != panSelectedKey || _preview.Image == null)
                    throw new InvalidOperationException("Workflow smoke: preview did not return to the original page after panning.");
                _btnFitStable.PerformClick(); Application.DoEvents();
                if (_zoom.Value != 100 || _previewScroll.HorizontalScroll.Value != 0 || _previewScroll.VerticalScroll.Value != 0)
                    throw new InvalidOperationException("Workflow smoke: fit-to-window did not reset pan viewport.");

'''
s = s.replace(smoke_anchor, smoke_anchor + pan_smoke, 1)

p.write_text(s, encoding='utf-8-sig')

# Launcher identity must be distinct so v2.6.1 extracts to its own runtime folder and never
# reuses a stale v2.6.0 payload.
launcher = root / 'launcher.cpp'
ls = launcher.read_text(encoding='utf-8-sig')
if 'v2.6.0' not in ls:
    raise SystemExit('launcher v2.6.0 marker missing')
launcher.write_text(ls.replace('v2.6.0', 'v2.6.1'), encoding='utf-8-sig')

print('PATCH_V261_PREVIEW_PAN_ISOLATED_OK')
