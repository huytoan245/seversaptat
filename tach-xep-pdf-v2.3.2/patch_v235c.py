from pathlib import Path
p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# ImageList has a fixed 104x78 cell; letterbox into that cell instead of stretching scans.
marker = '        internal static double HorizontalLineScore(Bitmap src)\n'
helper = '''        internal static Bitmap FitCanvas(Bitmap src, int width, int height)\n        {\n            width = Math.Max(1, width); height = Math.Max(1, height);\n            Bitmap dst = new Bitmap(width, height, PixelFormat.Format24bppRgb);\n            using (Graphics g = Graphics.FromImage(dst))\n            {\n                g.Clear(Color.White); g.InterpolationMode = InterpolationMode.HighQualityBicubic;\n                double scale = Math.Min(width / (double)Math.Max(1, src.Width), height / (double)Math.Max(1, src.Height));\n                int w = Math.Max(1, (int)Math.Round(src.Width * scale)); int h = Math.Max(1, (int)Math.Round(src.Height * scale));\n                g.DrawImage(src, new Rectangle((width - w) / 2, (height - h) / 2, w, h));\n            }\n            return dst;\n        }\n\n'''
if marker not in s: raise SystemExit('ImageOps marker not found')
s = s.replace(marker, helper + marker, 1)
old = '''                        using (Bitmap b = pdf.RenderPageMax(i, 180))\n                        {\n                            Bitmap copy = new Bitmap(b);'''
new = '''                        using (Bitmap b = pdf.RenderPageMax(i, 180))\n                        using (Bitmap fitted = ImageOps.FitCanvas(b, 104, 78))\n                        {\n                            Bitmap copy = new Bitmap(fitted);'''
if old not in s: raise SystemExit('base thumbnail block not found')
s = s.replace(old, new, 1)
old = '''            using (Bitmap raw = new Bitmap(_thumbs.Images[baseKey]))\n            using (Bitmap oriented = ImageOps.Rotate(raw, s.Rotation))\n                _thumbs.Images.Add(key, new Bitmap(oriented));'''
new = '''            using (Bitmap raw = new Bitmap(_thumbs.Images[baseKey]))\n            using (Bitmap oriented = ImageOps.Rotate(raw, s.Rotation))\n            using (Bitmap fitted = ImageOps.FitCanvas(oriented, _thumbs.ImageSize.Width, _thumbs.ImageSize.Height))\n                _thumbs.Images.Add(key, new Bitmap(fitted));'''
if old not in s: raise SystemExit('source thumbnail block not found')
s = s.replace(old, new, 1)
old = '''            using (Bitmap raw = new Bitmap(_thumbs.Images[baseKey]))\n            using (Bitmap spread = ImageOps.Rotate(raw, p.SourceRotation))\n            using (Bitmap half = ImageOps.CropHalf(spread, p.Half, p.CutPercent))\n            using (Bitmap final = ImageOps.Rotate(half, p.ExtraRotation))\n                _thumbs.Images.Add(key, new Bitmap(final));'''
new = '''            using (Bitmap raw = new Bitmap(_thumbs.Images[baseKey]))\n            using (Bitmap spread = ImageOps.Rotate(raw, p.SourceRotation))\n            using (Bitmap half = ImageOps.CropHalf(spread, p.Half, p.CutPercent))\n            using (Bitmap final = ImageOps.Rotate(half, p.ExtraRotation))\n            using (Bitmap fitted = ImageOps.FitCanvas(final, _thumbs.ImageSize.Width, _thumbs.ImageSize.Height))\n                _thumbs.Images.Add(key, new Bitmap(fitted));'''
if old not in s: raise SystemExit('output thumbnail block not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V235C_THUMBS_OK')
