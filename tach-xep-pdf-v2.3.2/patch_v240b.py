from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
old='''                    try { File.Replace(tmp,_sourcePath,null,true); } catch { if (File.Exists(_sourcePath)) File.Delete(_sourcePath); File.Move(tmp,_sourcePath); }\n                    _sourceWasOverwritten=false;'''
new='''                    try { File.Replace(tmp,_sourcePath,null,true); }\n                    catch\n                    {\n                        string rollback = _sourcePath + ".restore.rollback"; if(File.Exists(rollback)) File.Delete(rollback);\n                        if(File.Exists(_sourcePath)) File.Move(_sourcePath,rollback);\n                        try { File.Move(tmp,_sourcePath); if(File.Exists(rollback)) File.Delete(rollback); }\n                        catch { if(File.Exists(_sourcePath)) File.Delete(_sourcePath); if(File.Exists(rollback)) File.Move(rollback,_sourcePath); throw; }\n                    }\n                    _sourceWasOverwritten=false;'''
if old not in s: raise SystemExit('unsafe restore fallback marker missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V240B_ROLLBACK_SAFE_OK')