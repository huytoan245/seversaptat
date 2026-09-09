from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
old_preview='''            using (Bitmap raw = pdf.RenderPageMax(op.OriginalSourceIndex, maxDimension))\n            using (Bitmap spread = ImageOps.Rotate(raw, op.SourceRotation))\n            using (Bitmap half = ImageOps.CropHalf(spread, op.Half, op.CutPercent))\n                return ImageOps.Rotate(half, op.ExtraRotation);'''
new_preview='''            using (Bitmap raw = pdf.RenderPageMax(op.OriginalSourceIndex, maxDimension))\n            using (Bitmap spread = ImageOps.Rotate(raw, op.SourceRotation))\n            {\n                if (op.ImportedFullPage || op.Half < 0) return ImageOps.Rotate(spread, op.ExtraRotation);\n                using (Bitmap half = ImageOps.CropHalf(spread, op.Half, op.CutPercent))\n                    return ImageOps.Rotate(half, op.ExtraRotation);\n            }'''
if old_preview not in s: raise SystemExit('v270 full-page preview marker missing')
s=s.replace(old_preview,new_preview,1)
old_export='''                    using (Bitmap raw = _pdf.RenderPageDpi(p.OriginalSourceIndex, ExportDpi))\n                    using (Bitmap spread = ImageOps.Rotate(raw, p.SourceRotation))\n                    using (Bitmap half = ImageOps.CropHalf(spread, p.Half, p.CutPercent)) final = ImageOps.Rotate(half, p.ExtraRotation);'''
new_export='''                    using (Bitmap raw = _pdf.RenderPageDpi(p.OriginalSourceIndex, ExportDpi))\n                    using (Bitmap spread = ImageOps.Rotate(raw, p.SourceRotation))\n                    {\n                        if (p.ImportedFullPage || p.Half < 0) final = ImageOps.Rotate(spread, p.ExtraRotation);\n                        else using (Bitmap half = ImageOps.CropHalf(spread, p.Half, p.CutPercent)) final = ImageOps.Rotate(half, p.ExtraRotation);\n                    }'''
if old_export not in s: raise SystemExit('v270 full-page export marker missing')
s=s.replace(old_export,new_export,1)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_FULLPAGE_RENDER_OK')
