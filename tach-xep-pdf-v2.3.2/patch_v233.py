from pathlib import Path

root = Path('tach-xep-pdf-v2.3.2')
cs_path = root / 'TachXepTrangPDF.cs'
launcher_path = root / 'launcher.cpp'

s = cs_path.read_text(encoding='utf-8-sig')

old_resize = '        protected override void OnResize(EventArgs e) { base.OnResize(e); ApplyZoom(); }'
new_resize = '''        protected override void OnResize(EventArgs e)\n        {\n            base.OnResize(e);\n            // WinForms can raise Resize while the constructor is still setting Width/Height,\n            // before BuildUi() creates the preview controls. Do not touch them until ready.\n            if (_previewScroll == null || _preview == null || _zoom == null) return;\n            ApplyZoom();\n        }'''
if old_resize not in s:
    raise SystemExit('Expected OnResize implementation not found')
s = s.replace(old_resize, new_resize, 1)

old_apply = '''        private void ApplyZoom()\n        {\n            if (_previewMaster == null || _previewScroll.ClientSize.Width <= 20 || _previewScroll.ClientSize.Height <= 20) { _preview.Size = new Size(10, 10); return; }'''
new_apply = '''        private void ApplyZoom()\n        {\n            if (_previewScroll == null || _preview == null || _zoom == null) return;\n            if (_previewMaster == null || _previewScroll.ClientSize.Width <= 20 || _previewScroll.ClientSize.Height <= 20) { _preview.Size = new Size(10, 10); return; }'''
if old_apply not in s:
    raise SystemExit('Expected ApplyZoom implementation not found')
s = s.replace(old_apply, new_apply, 1)

marker = '''            AppDiagnostics.Initialize();\n\n            // Headless first-run/offline verification. The portable launcher forwards this flag.'''
ui_smoke = '''            AppDiagnostics.Initialize();\n\n            // Startup regression: construct the real WinForms MainForm without showing it.\n            // This catches constructor/layout/Resize regressions that headless engine tests miss.\n            if (args != null && args.Length >= 1 && args[0] == "--ui-smoke")\n            {\n                try\n                {\n                    Application.SetHighDpiMode(HighDpiMode.PerMonitorV2);\n                    Application.EnableVisualStyles();\n                    Application.SetCompatibleTextRenderingDefault(false);\n                    AppDiagnostics.Log("UI_SMOKE", "Constructing MainForm");\n                    using (MainForm form = new MainForm())\n                    {\n                        form.CreateControl();\n                        IntPtr h = form.Handle;\n                        form.PerformLayout();\n                        form.Width += 1;\n                        form.Width -= 1;\n                    }\n                    AppDiagnostics.Log("UI_SMOKE", "PASS");\n                    return 0;\n                }\n                catch (Exception ex)\n                {\n                    AppDiagnostics.LogException("UI_SMOKE_FAIL", ex);\n                    return 52;\n                }\n            }\n\n            // Headless first-run/offline verification. The portable launcher forwards this flag.'''
if marker not in s:
    raise SystemExit('Program startup marker not found')
s = s.replace(marker, ui_smoke, 1)

# Bump app-visible/runtime version after v2.3.2 reconstruction.
s = s.replace('2.3.2', '2.3.3')

cs_path.write_text(s, encoding='utf-8-sig')

launcher = launcher_path.read_text(encoding='utf-8-sig')
launcher = launcher.replace('2.3.2', '2.3.3')
launcher_path.write_text(launcher, encoding='utf-8-sig')

print('PATCH_V233_STARTUP_RESIZE_AND_UI_SMOKE_OK')
