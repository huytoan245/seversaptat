from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
old='''            finally\n            {\n                try { if(File.Exists(baseCopy)) File.Delete(baseCopy); } catch { }\n                SetBusy(false,null); if(_list!=null && _list.Items.Count>0) RestoreListFocus(Math.Max(0,Math.Min(_list.Items.Count-1,oldSelected)));\n            }'''
new='''            finally\n            {\n                try { if(File.Exists(baseCopy)) File.Delete(baseCopy); } catch { }\n                // The successful path already selected/focused the inserted page. Do not queue a\n                // second focus operation back to the old page from finally: under UI smoke this\n                // can re-enter the message loop and it is also wrong UX for a real merge.\n                AppDiagnostics.Log("MERGE_CORE","FINALIZE_UI BEGIN");\n                SetBusy(false,null);\n                AppDiagnostics.Log("MERGE_CORE","FINALIZE_UI PASS");\n            }'''
if old not in s:
    raise SystemExit('v270 merge finalize block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_MERGE_FINALIZE_OK')
