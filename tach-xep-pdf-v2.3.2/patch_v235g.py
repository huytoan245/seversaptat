from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# Preview reliability: capture the current PDF session so a fast file switch can never
# render the old selected model against the newly opened PDF. Keep the ticket guard too.
old_preview = '''        private async void LoadSelectedPreviewAsync()\n        {\n            int idx = SelectedIndex;\n            if (idx < 0 || _pdf == null) { SetPreview(null); return; }\n            int ticket = Interlocked.Increment(ref _previewTicket);\n            object model = _list.Items[idx].Tag;\n            try\n            {\n                Bitmap rendered = await Task.Run(delegate\n                {\n                    if (model is SourceFace)\n                    {\n                        SourceFace s = (SourceFace)model;\n                        using (Bitmap raw = _pdf.RenderPageMax(s.OriginalSourceIndex, 1800))\n                            return ImageOps.Rotate(raw, s.Rotation);\n                    }\n                    else\n                    {\n                        OutputPage p = (OutputPage)model;\n                        using (Bitmap raw = _pdf.RenderPageMax(p.OriginalSourceIndex, 1800))\n                        using (Bitmap spread = ImageOps.Rotate(raw, p.SourceRotation))\n                        using (Bitmap half = ImageOps.CropHalf(spread, p.Half, p.CutPercent))\n                            return ImageOps.Rotate(half, p.ExtraRotation);\n                    }\n                });\n                if (ticket != _previewTicket) { rendered.Dispose(); return; }\n                SetPreview(rendered);\n            }\n            catch { if (ticket == _previewTicket) SetPreview(null); }\n        }'''
new_preview = '''        private async void LoadSelectedPreviewAsync()\n        {\n            int idx = SelectedIndex;\n            PdfSession pdf = _pdf;\n            if (idx < 0 || pdf == null) { SetPreview(null); return; }\n            int ticket = Interlocked.Increment(ref _previewTicket);\n            object model = _list.Items[idx].Tag;\n            try\n            {\n                Bitmap rendered = await Task.Run(delegate\n                {\n                    if (model is SourceFace)\n                    {\n                        SourceFace s = (SourceFace)model;\n                        using (Bitmap raw = pdf.RenderPageMax(s.OriginalSourceIndex, 1800))\n                            return ImageOps.Rotate(raw, s.Rotation);\n                    }\n                    else\n                    {\n                        OutputPage p = (OutputPage)model;\n                        using (Bitmap raw = pdf.RenderPageMax(p.OriginalSourceIndex, 1800))\n                        using (Bitmap spread = ImageOps.Rotate(raw, p.SourceRotation))\n                        using (Bitmap half = ImageOps.CropHalf(spread, p.Half, p.CutPercent))\n                            return ImageOps.Rotate(half, p.ExtraRotation);\n                    }\n                });\n                if (ticket != _previewTicket || pdf != _pdf) { rendered.Dispose(); return; }\n                SetPreview(rendered);\n            }\n            catch (Exception ex)\n            {\n                AppDiagnostics.LogException("PREVIEW_RENDER_FAIL", ex);\n                if (ticket == _previewTicket && pdf == _pdf) SetPreview(null);\n            }\n        }'''
if old_preview not in s:
    raise SystemExit('preview async block not found')
s = s.replace(old_preview, new_preview, 1)

# Avoid a PictureBox briefly holding a disposed Image during rapid page navigation.
old_set = '''        private void SetPreview(Bitmap b)\n        {\n            if (_previewMaster != null) { _previewMaster.Dispose(); _previewMaster = null; }\n            _previewMaster = b;\n            _preview.Image = _previewMaster;\n            ApplyZoom();\n        }'''
new_set = '''        private void SetPreview(Bitmap b)\n        {\n            if (_preview != null) _preview.Image = null;\n            if (_previewMaster != null) { _previewMaster.Dispose(); _previewMaster = null; }\n            _previewMaster = b;\n            if (_preview != null) _preview.Image = _previewMaster;\n            ApplyZoom();\n        }'''
if old_set not in s:
    raise SystemExit('SetPreview block not found')
s = s.replace(old_set, new_set, 1)

# Thumbnail errors used to be swallowed silently. Keep the UI tolerant but record diagnostics.
old_thumb_catch = '''                    catch { }\n                }\n                BeginInvoke(new Action(delegate { if (_progress.Value >= _progress.Maximum) _progress.Value = 0; }));'''
new_thumb_catch = '''                    catch (Exception ex) { AppDiagnostics.LogException("THUMBNAIL_RENDER_FAIL", ex); }\n                }\n                try { BeginInvoke(new Action(delegate { if (_progress.Value >= _progress.Maximum) _progress.Value = 0; })); }\n                catch (InvalidOperationException) { }'''
if old_thumb_catch not in s:
    raise SystemExit('thumbnail catch block not found')
s = s.replace(old_thumb_catch, new_thumb_catch, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V235G_PREVIEW_SESSION_SAFETY_OK')
