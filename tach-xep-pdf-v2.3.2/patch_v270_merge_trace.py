from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('v270 merge trace marker missing: '+label)
    s=s.replace(old,new,1)

rep('                File.Copy(oldWorkPath,baseCopy,true);\n                int added=await Task.Run(delegate { return PdfPageComposer.AppendPdfs(baseCopy,addFiles,newWorkPath); });',
    '                AppDiagnostics.Log("MERGE_CORE","COPY_BASE BEGIN"); File.Copy(oldWorkPath,baseCopy,true); AppDiagnostics.Log("MERGE_CORE","COPY_BASE PASS");\n                AppDiagnostics.Log("MERGE_CORE","COMPOSE BEGIN"); int added=await Task.Run(delegate { return PdfPageComposer.AppendPdfs(baseCopy,addFiles,newWorkPath); }); AppDiagnostics.Log("MERGE_CORE","COMPOSE PASS pages="+added.ToString());',
    'copy/compose')
rep('                CloseActiveRuntimeForSwitch();\n                _workPath=newWorkPath;',
    '                AppDiagnostics.Log("MERGE_CORE","CLOSE_OLD_RUNTIME BEGIN"); CloseActiveRuntimeForSwitch(); AppDiagnostics.Log("MERGE_CORE","CLOSE_OLD_RUNTIME PASS");\n                _workPath=newWorkPath;',
    'close runtime')
rep('                ReopenRuntimeAfterWorkFileChange();\n                if(_pdf.PageCount!=oldPhysicalCount+added)',
    '                AppDiagnostics.Log("MERGE_CORE","REOPEN_NEW_RUNTIME BEGIN"); ReopenRuntimeAfterWorkFileChange(); AppDiagnostics.Log("MERGE_CORE","REOPEN_NEW_RUNTIME PASS pages="+_pdf.PageCount.ToString());\n                if(_pdf.PageCount!=oldPhysicalCount+added)',
    'reopen runtime')
rep('                _redo.Clear(); MarkActiveDocumentInProgress(); ClearPreviewCache(); BeginThumbnailBuild();\n                int newCount=_isSplit?_outputs.Count:_sources.Count; int focus=Math.Max(0,Math.Min(newCount-1,insertAt)); RefreshList(focus); RestoreListFocus(focus);',
    '                AppDiagnostics.Log("MERGE_CORE","MODEL_UPDATE PASS"); _redo.Clear(); MarkActiveDocumentInProgress(); ClearPreviewCache();\n                AppDiagnostics.Log("MERGE_CORE","THUMBNAIL_BEGIN"); BeginThumbnailBuild(); AppDiagnostics.Log("MERGE_CORE","THUMBNAIL_SCHEDULED");\n                int newCount=_isSplit?_outputs.Count:_sources.Count; int focus=Math.Max(0,Math.Min(newCount-1,insertAt)); AppDiagnostics.Log("MERGE_CORE","REFRESH_LIST BEGIN"); RefreshList(focus); RestoreListFocus(focus); AppDiagnostics.Log("MERGE_CORE","REFRESH_LIST PASS");',
    'model/thumb/refresh')
rep('                SetStatus("Đã ghép thêm "+added.ToString()+" trang PDF. "+(_isSplit?',
    '                AppDiagnostics.Log("MERGE_CORE","SUCCESS"); SetStatus("Đã ghép thêm "+added.ToString()+" trang PDF. "+(_isSplit?',
    'success')

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_MERGE_TRACE_OK')
