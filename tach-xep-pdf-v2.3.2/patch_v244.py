from pathlib import Path
import hashlib

root = Path('tach-xep-pdf-v2.3.2')
p = root / 'TachXepTrangPDF.cs'
raw = p.read_bytes()
expected_base = 'fceb99ece38533a4dec08b5dff034c9b902e38b58b2cf9cd6c9d8ad56c48f4ad'
if hashlib.sha256(raw).hexdigest() != expected_base:
    raise SystemExit('unexpected v2.4.3 reconstructed source before v2.4.4 patch')

s = raw.decode('utf-8-sig')
s = s.replace('private const string AppVersion = "2.4.3";', 'private const string AppVersion = "2.4.4";', 1)

marker = '''    internal sealed class MainForm : Form\n    {'''
insert = '''    internal sealed class SmoothPreviewPanel : Panel\n    {\n        internal SmoothPreviewPanel()\n        {\n            SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.OptimizedDoubleBuffer | ControlStyles.UserPaint, true);\n            UpdateStyles();\n        }\n    }\n\n    internal sealed class MainForm : Form\n    {'''
if marker not in s:
    raise SystemExit('MainForm marker missing')
s = s.replace(marker, insert, 1)

s = s.replace('KeyPreview = true;\n            BuildUi();',
              'KeyPreview = true;\n            SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.OptimizedDoubleBuffer, true);\n            UpdateStyles();\n            BuildUi();', 1)
s = s.replace('_previewScroll = new Panel(); _previewScroll.Dock = DockStyle.Fill;',
              '_previewScroll = new SmoothPreviewPanel(); _previewScroll.Dock = DockStyle.Fill;', 1)

s = s.replace('Button left = MakeButton("↶ Xoay trái", 105, false);',
              'Button left = MakeButton("↶ Xoay trái 90°", 138, false);', 1)
s = s.replace('Button right = MakeButton("↷ Xoay phải", 108, false);',
              'Button right = MakeButton("↷ Xoay phải 90°", 142, false);', 1)
s = s.replace('Button del = MakeButton("Xóa", 74, false);',
              'Button del = MakeButton("Xóa trang PDF", 118, false);', 1)

needle = '''            bool entered = false;\n            try\n            {\n                await _previewRenderGate.WaitAsync(token);'''
repl = '''            bool entered = false;\n            try\n            {\n                // Smooth v2.1-style transition: avoid unnecessary HQ repaint while the user\n                // is rapidly moving through pages. The latest selected page wins.\n                await Task.Delay(70, token);\n                await _previewRenderGate.WaitAsync(token);'''
if needle not in s:
    raise SystemExit('preview render gate marker missing')
s = s.replace(needle, repl, 1)

old = '''        private void SetPreview(Bitmap b)\n        {\n            if (_preview != null) _preview.Image = null;\n            if (_previewMaster != null) { _previewMaster.Dispose(); _previewMaster = null; }\n            _previewMaster = b;\n            if (_preview != null) _preview.Image = _previewMaster;\n            ApplyZoom();\n        }'''
new = '''        private void SetPreview(Bitmap b)\n        {\n            // v2.4.4: atomic preview swap. Never insert a blank/dark frame between pages.\n            Bitmap old = _previewMaster;\n            if (_previewScroll != null) _previewScroll.SuspendLayout();\n            try\n            {\n                _previewMaster = b;\n                if (_preview != null) _preview.Image = b;\n                ApplyZoom();\n                if (_preview != null) _preview.Invalidate();\n            }\n            finally\n            {\n                if (_previewScroll != null) _previewScroll.ResumeLayout(false);\n            }\n            if (old != null && !object.ReferenceEquals(old, b)) old.Dispose();\n        }'''
if old not in s:
    raise SystemExit('SetPreview v2.4.3 marker missing')
s = s.replace(old, new, 1)

old = '''                AppDiagnostics.LogException("PREVIEW_RENDER_FAIL", ex);\n                if (!token.IsCancellationRequested && ticket == _previewTicket && pdf == (_previewPdf ?? _pdf)) SetPreview(null);'''
new = '''                AppDiagnostics.LogException("PREVIEW_RENDER_FAIL", ex);\n                if (!token.IsCancellationRequested && ticket == _previewTicket && pdf == (_previewPdf ?? _pdf) && _previewMaster == null) SetPreview(null);'''
if old not in s:
    raise SystemExit('preview render failure marker missing')
s = s.replace(old, new, 1)

needle = '''                if (_list.TopItem == null || _list.TopItem.Index != 0) throw new InvalidOperationException("Workflow smoke: page 1 is not kept visible when page 2 is selected.");\n                string selectedKey = ModelKey(_list.Items[SelectedIndex].Tag);'''
repl = '''                if (_list.TopItem == null || _list.TopItem.Index != 0) throw new InvalidOperationException("Workflow smoke: page 1 is not kept visible when page 2 is selected.");\n                if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank after selecting page 2.");\n                SelectAdjacent(1); Application.DoEvents(); if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank during rapid page-down.");\n                SelectAdjacent(-1); Application.DoEvents(); if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank during rapid page-up.");\n                string selectedKey = ModelKey(_list.Items[SelectedIndex].Tag);'''
if needle not in s:
    raise SystemExit('workflow smoke transition marker missing')
s = s.replace(needle, repl, 1)

needle = '''                            "Áp dụng đường cắt"\n                        };'''
repl = '''                            "Áp dụng đường cắt",\n                            "↶ Xoay trái 90°",\n                            "↷ Xoay phải 90°",\n                            "Xóa trang PDF"\n                        };'''
if needle not in s:
    raise SystemExit('UI smoke required-label marker missing')
s = s.replace(needle, repl, 1)

out = s.encode('utf-8-sig')
actual = hashlib.sha256(out).hexdigest()
expected_final = '289457e966797187c573839c63798526ef97c8082c68fba2aa8a26634e176bfe'
if actual != expected_final:
    raise SystemExit('v2.4.4 source patch checksum mismatch actual=' + actual)
p.write_bytes(out)

launcher = root / 'launcher.cpp'
ls = launcher.read_text(encoding='utf-8-sig')
ls2 = ls.replace('2.4.3', '2.4.4')
if ls2 == ls:
    raise SystemExit('launcher v2.4.3 marker missing')
launcher.write_text(ls2, encoding='utf-8-sig')
print('PATCH_V244_SMOOTH_PREVIEW_OK')
