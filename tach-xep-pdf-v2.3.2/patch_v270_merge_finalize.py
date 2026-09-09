from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
old_focus='''                int newCount=_isSplit?_outputs.Count:_sources.Count; int focus=Math.Max(0,Math.Min(newCount-1,insertAt)); AppDiagnostics.Log("MERGE_CORE","REFRESH_LIST BEGIN"); RefreshList(focus); RestoreListFocus(focus); AppDiagnostics.Log("MERGE_CORE","REFRESH_LIST PASS");'''
new_focus='''                int newCount=_isSplit?_outputs.Count:_sources.Count; int focus=Math.Max(0,Math.Min(newCount-1,insertAt)); AppDiagnostics.Log("MERGE_CORE","REFRESH_LIST BEGIN"); RefreshList(focus); AppDiagnostics.Log("MERGE_CORE","REFRESH_LIST PASS");'''
if old_focus not in s:
    raise SystemExit('v270 merge queued focus block missing')
s=s.replace(old_focus,new_focus,1)
old='''            finally\n            {\n                try { if(File.Exists(baseCopy)) File.Delete(baseCopy); } catch { }\n                SetBusy(false,null); if(_list!=null && _list.Items.Count>0) RestoreListFocus(Math.Max(0,Math.Min(_list.Items.Count-1,oldSelected)));\n            }'''
new='''            finally\n            {\n                try { if(File.Exists(baseCopy)) File.Delete(baseCopy); } catch { }\n                // RefreshList already selected the inserted page. Avoid asynchronous focus callbacks\n                // from the core merge path; they can re-enter the message loop and are unnecessary.\n                AppDiagnostics.Log("MERGE_CORE","FINALIZE_UI BEGIN");\n                SetBusy(false,null);\n                AppDiagnostics.Log("MERGE_CORE","FINALIZE_UI PASS");\n            }'''
if old not in s:
    raise SystemExit('v270 merge finalize block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_MERGE_FINALIZE_OK')
