from pathlib import Path

root = Path('tach-xep-pdf-v2.3.2')
cs_path = root / 'TachXepTrangPDF.cs'
launcher_path = root / 'launcher.cpp'

s = cs_path.read_text(encoding='utf-8-sig')

# 1) Constructor-time Resize can fire before BuildUi has created preview controls.
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

# 2) SplitContainer min sizes were assigned during BuildUi while the controls could still have
# their small design-time/default width. WinForms can throw before the form is shown.
old_split = '''            SplitContainer outer = new SplitContainer(); outer.Dock = DockStyle.Fill; outer.Orientation = Orientation.Vertical; outer.SplitterDistance = 330; outer.SplitterWidth = 6; outer.Panel1MinSize = 250; outer.Panel2MinSize = 500; Controls.Add(outer);\n            SplitContainer inner = new SplitContainer(); inner.Dock = DockStyle.Fill; inner.Orientation = Orientation.Vertical; inner.SplitterDistance = 760; inner.SplitterWidth = 6; inner.Panel1MinSize = 420; inner.Panel2MinSize = 240; outer.Panel2.Controls.Add(inner);'''
new_split = '''            SplitContainer outer = new SplitContainer(); outer.Dock = DockStyle.Fill; outer.Orientation = Orientation.Vertical; outer.SplitterWidth = 6; Controls.Add(outer);\n            SplitContainer inner = new SplitContainer(); inner.Dock = DockStyle.Fill; inner.Orientation = Orientation.Vertical; inner.SplitterWidth = 6; outer.Panel2.Controls.Add(inner);\n\n            // Apply splitter limits only after the form has a real client size.\n            Shown += delegate\n            {\n                ConfigureSplitterSafe(outer, 330, 250, 680);\n                ConfigureSplitterSafe(inner, 760, 420, 240);\n            };'''
if old_split not in s:
    raise SystemExit('Expected SplitContainer construction block not found')
s = s.replace(old_split, new_split, 1)

make_button_marker = '''        private Button MakeButton(string text, int width, bool prominent)\n        {'''
helper = '''        private static void ConfigureSplitterSafe(SplitContainer split, int preferredDistance, int panel1Min, int panel2Min)\n        {\n            if (split == null || split.IsDisposed) return;\n            int total = split.Orientation == Orientation.Vertical ? split.ClientSize.Width : split.ClientSize.Height;\n            if (total <= split.SplitterWidth + 2) return;\n\n            // Reset limits first so configuration cannot fail because of a stale/default size.\n            split.Panel1MinSize = 0;\n            split.Panel2MinSize = 0;\n\n            int maxDistance = Math.Max(1, total - split.SplitterWidth - 1);\n            int distance = Math.Max(1, Math.Min(preferredDistance, maxDistance));\n\n            if (total >= panel1Min + panel2Min + split.SplitterWidth)\n            {\n                distance = Math.Max(panel1Min, Math.Min(preferredDistance, total - panel2Min - split.SplitterWidth));\n                split.SplitterDistance = distance;\n                split.Panel1MinSize = panel1Min;\n                split.Panel2MinSize = panel2Min;\n            }\n            else\n            {\n                // Extremely small/transient size: stay usable without throwing.\n                split.SplitterDistance = Math.Max(1, Math.Min(total / 2, maxDistance));\n            }\n        }\n\n        private Button MakeButton(string text, int width, bool prominent)\n        {'''
if make_button_marker not in s:
    raise SystemExit('MakeButton marker not found')
s = s.replace(make_button_marker, helper, 1)

# Add a real startup UI smoke mode. Show/DoEvents triggers Shown + layout + splitter setup.
marker = '''            AppDiagnostics.Initialize();\n\n            // Headless first-run/offline verification. The portable launcher forwards this flag.'''
ui_smoke = '''            AppDiagnostics.Initialize();\n\n            // Startup regression: construct and briefly show the real WinForms MainForm.\n            // This catches constructor/layout/Resize/SplitContainer regressions that engine tests miss.\n            if (args != null && args.Length >= 1 && args[0] == "--ui-smoke")\n            {\n                try\n                {\n                    Application.SetHighDpiMode(HighDpiMode.PerMonitorV2);\n                    Application.EnableVisualStyles();\n                    Application.SetCompatibleTextRenderingDefault(false);\n                    AppDiagnostics.Log("UI_SMOKE", "Constructing MainForm");\n                    using (MainForm form = new MainForm())\n                    {\n                        form.Show();\n                        Application.DoEvents();\n                        form.PerformLayout();\n                        form.Width += 1;\n                        Application.DoEvents();\n                        form.Width -= 1;\n                        Application.DoEvents();\n                        form.Hide();\n                    }\n                    AppDiagnostics.Log("UI_SMOKE", "PASS");\n                    return 0;\n                }\n                catch (Exception ex)\n                {\n                    AppDiagnostics.LogException("UI_SMOKE_FAIL", ex);\n                    return 52;\n                }\n            }\n\n            // Headless first-run/offline verification. The portable launcher forwards this flag.'''
if marker not in s:
    raise SystemExit('Program startup marker not found')
s = s.replace(marker, ui_smoke, 1)

# Bump app-visible/runtime version after v2.3.2 reconstruction.
s = s.replace('2.3.2', '2.3.3')

cs_path.write_text(s, encoding='utf-8-sig')

launcher = launcher_path.read_text(encoding='utf-8-sig')
launcher = launcher.replace('2.3.2', '2.3.3')
launcher_path.write_text(launcher, encoding='utf-8-sig')

print('PATCH_V233_STARTUP_RESIZE_SPLITTER_AND_UI_SMOKE_OK')
