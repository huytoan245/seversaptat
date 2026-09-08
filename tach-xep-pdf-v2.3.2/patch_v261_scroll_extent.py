from pathlib import Path
p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

start = s.find('        private void ApplyZoom()\n')
end = s.find('        protected override void OnResize(EventArgs e)\n', start)
if start < 0 or end < 0:
    raise SystemExit('ApplyZoom boundary missing')
seg = s[start:end]
old = '''            Rectangle wanted = new Rectangle(x, y, w, h);\n            _previewScroll.SuspendLayout();\n'''
new = '''            Rectangle wanted = new Rectangle(x, y, w, h);\n            // v2.6.1: explicitly define scrollable canvas size. This makes native WinForms\n            // scrollbars/pan deterministic without changing render/cache/page-selection logic.\n            Size scrollExtent = _zoom.Value > 100 ? new Size(Math.Max(1, w + margin * 2), Math.Max(1, h + margin * 2)) : Size.Empty;\n            if (_previewScroll.AutoScrollMinSize != scrollExtent) _previewScroll.AutoScrollMinSize = scrollExtent;\n            _previewScroll.SuspendLayout();\n'''
if old not in seg:
    raise SystemExit('ApplyZoom scroll extent insertion marker missing')
seg = seg.replace(old, new, 1)
if 'finally { _previewScroll.ResumeLayout(false); }' not in seg:
    raise SystemExit('ApplyZoom ResumeLayout marker missing')
seg = seg.replace('finally { _previewScroll.ResumeLayout(false); }', 'finally { _previewScroll.ResumeLayout(true); }', 1)
s = s[:start] + seg + s[end:]

old_smoke = '''                int panUndoCount = _undo.Count, panRedoCount = _redo.Count, panCacheCount;\n                lock (_previewCacheSync) panCacheCount = _previewCache.Count;\n'''
new_smoke = '''                int panUndoCount = _undo.Count, panRedoCount = _redo.Count;\n                int panPreviewTicket = _previewTicket;\n'''
if old_smoke not in s:
    raise SystemExit('pan smoke declaration marker missing')
s = s.replace(old_smoke, new_smoke, 1)
old_check = '''                int panCacheAfter; lock (_previewCacheSync) panCacheAfter = _previewCache.Count;\n                if (SelectedIndex != panSelectedIndex || _previewModelKey != panSelectedKey || _undo.Count != panUndoCount || _redo.Count != panRedoCount || panCacheAfter != panCacheCount)\n                    throw new InvalidOperationException("Workflow smoke: panning changed page/history/cache state.");\n'''
new_check = '''                if (SelectedIndex != panSelectedIndex || _previewModelKey != panSelectedKey || _undo.Count != panUndoCount || _redo.Count != panRedoCount || _previewTicket != panPreviewTicket)\n                    throw new InvalidOperationException("Workflow smoke: panning changed page/history/preview-request state.");\n'''
if old_check not in s:
    raise SystemExit('pan smoke cache equality marker missing')
s = s.replace(old_check, new_check, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V261_SCROLL_EXTENT_OK')
