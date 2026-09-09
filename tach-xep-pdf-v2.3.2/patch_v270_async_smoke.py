from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

old_sig='        internal int RunWorkflowSmoke()\n'
new_sig='        internal async Task<int> RunWorkflowSmokeAsync()\n'
if old_sig not in s:
    raise SystemExit('v270 sync workflow smoke signature missing')
s=s.replace(old_sig,new_sig,1)

# Remove the nested DoEvents-based task waiter. The workflow itself is now async and runs
# under a real WinForms Application.Run message loop in --ui-smoke.
start=s.find('                Action<Task,string> waitSmokeTask = delegate(Task task,string name)\n')
end=s.find('                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","CREATE_MERGE_FIXTURE BEGIN");\n',start)
if start<0 or end<0:
    raise SystemExit('v270 waitSmokeTask block boundary missing')
s=s[:start]+s[end:]

replacements={
'''                Task mergeUnsplitTask=MergePdfFilesCoreAsync(new string[]{mergePart},-1); waitSmokeTask(mergeUnsplitTask,"MERGE_BEFORE_SPLIT");''':
'''                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","MERGE_BEFORE_SPLIT BEGIN");\n                await MergePdfFilesCoreAsync(new string[]{mergePart},-1);\n                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","MERGE_BEFORE_SPLIT PASS");''',
'''                Task mergedExportTask=ExtractPagesToPathAsync(mergedIndexes,mergedModelExport); waitSmokeTask(mergedExportTask,"EXPORT_MERGED_MODEL");''':
'''                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","EXPORT_MERGED_MODEL BEGIN");\n                await ExtractPagesToPathAsync(mergedIndexes,mergedModelExport);\n                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","EXPORT_MERGED_MODEL PASS");''',
'''                Task extractOneTask=ExtractPagesToPathAsync(new List<int>{2},extractSingle); waitSmokeTask(extractOneTask,"EXTRACT_SINGLE");''':
'''                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","EXTRACT_SINGLE BEGIN");\n                await ExtractPagesToPathAsync(new List<int>{2},extractSingle);\n                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","EXTRACT_SINGLE PASS");''',
'''                Task extractRangeTask=ExtractPagesToPathAsync(inclusiveIndexes,extractRange); waitSmokeTask(extractRangeTask,"EXTRACT_RANGE_4_8");''':
'''                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","EXTRACT_RANGE_4_8 BEGIN");\n                await ExtractPagesToPathAsync(inclusiveIndexes,extractRange);\n                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","EXTRACT_RANGE_4_8 PASS");''',
'''                Task mergeSplitTask=MergePdfFilesCoreAsync(new string[]{mergePart},-1); waitSmokeTask(mergeSplitTask,"MERGE_AFTER_SPLIT");''':
'''                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","MERGE_AFTER_SPLIT BEGIN");\n                await MergePdfFilesCoreAsync(new string[]{mergePart},-1);\n                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","MERGE_AFTER_SPLIT PASS");'''
}
for old,new in replacements.items():
    if old not in s:
        raise SystemExit('v270 async workflow call marker missing: '+old[:60])
    s=s.replace(old,new,1)

old_main='''                        int workflowCode = form.RunWorkflowSmoke();\n                        if (workflowCode != 0) throw new InvalidOperationException("Workflow smoke failed: " + workflowCode.ToString());\n                        form.Hide();'''
new_main='''                        int workflowCode = -1;\n                        Exception workflowException = null;\n                        form.BeginInvoke(new Action(async delegate\n                        {\n                            try\n                            {\n                                workflowCode = await form.RunWorkflowSmokeAsync();\n                            }\n                            catch (Exception ex)\n                            {\n                                workflowException = ex;\n                            }\n                            finally\n                            {\n                                Application.ExitThread();\n                            }\n                        }));\n                        Application.Run();\n                        if (workflowException != null) throw new InvalidOperationException("Workflow smoke async message-loop failure.", workflowException);\n                        if (workflowCode != 0) throw new InvalidOperationException("Workflow smoke failed: " + workflowCode.ToString());\n                        form.Hide();'''
if old_main not in s:
    raise SystemExit('v270 UI smoke workflow invocation marker missing')
s=s.replace(old_main,new_main,1)

if 'waitSmokeTask' in s:
    raise SystemExit('v270 obsolete waitSmokeTask remained after async conversion')
if 'RunWorkflowSmoke();' in s:
    raise SystemExit('v270 obsolete sync workflow invocation remained')

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_ASYNC_UI_SMOKE_OK')
