from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('internal const string Version = "2.3.5";','internal const string Version = "2.4.1";',1)
s=s.replace('startup-v2.3.5.log','startup-v2.4.1.log')
s=s.replace('Tách & Xếp Trang PDF v2.3.5','Tách & Xếp Trang PDF v2.4.1')
# Also mirror UI-smoke exception to the executable directory so CI can always retrieve it.
old='''                catch (Exception ex)\n                {\n                    AppDiagnostics.LogException("UI_SMOKE_FAIL", ex);\n                    return 52;\n                }'''
new='''                catch (Exception ex)\n                {\n                    AppDiagnostics.LogException("UI_SMOKE_FAIL", ex);\n                    try { File.WriteAllText(Path.Combine(AppContext.BaseDirectory, "ui-smoke-failure.txt"), ex.ToString(), Encoding.UTF8); } catch { }\n                    return 52;\n                }'''
if old not in s: raise SystemExit('UI smoke catch marker missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V241C_DIAGNOSTICS_OK')