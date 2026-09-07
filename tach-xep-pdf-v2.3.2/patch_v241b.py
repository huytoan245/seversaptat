from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
old='''                    using (PdfSession rotatedPdf = new PdfSession(rotatedPdfPath))\n                    {\n                        SizeF rsz = rotatedPdf.GetPageDipSize(0);\n                        using (Bitmap rb = rotatedPdf.RenderPageMax(0, 400))\n                        {\n                            double expected = rsz.Width / Math.Max(1.0, rsz.Height); double actual = rb.Width / (double)Math.Max(1, rb.Height);\n                            if (Math.Abs(expected-actual) > 0.02) throw new InvalidDataException("Rotated PDF preview was stretched: expected="+expected.ToString("0.000")+" actual="+actual.ToString("0.000"));\n                        }\n                    }'''
new='''                    PdfSession rotatedPdf = new PdfSession(rotatedPdfPath);\n                    SizeF rsz = rotatedPdf.GetPageDipSize(0);\n                    using (Bitmap rb = rotatedPdf.RenderPageMax(0, 400))\n                    {\n                        double expected = rsz.Width / Math.Max(1.0, rsz.Height); double actual = rb.Width / (double)Math.Max(1, rb.Height);\n                        if (Math.Abs(expected-actual) > 0.02) throw new InvalidDataException("Rotated PDF preview was stretched: expected="+expected.ToString("0.000")+" actual="+actual.ToString("0.000"));\n                    }'''
if old not in s: raise SystemExit('rotated PdfSession using block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V241B_SELFTEST_SESSION_OK')