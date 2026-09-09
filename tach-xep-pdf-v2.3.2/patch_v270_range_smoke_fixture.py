from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

old_range='''                string extractRange=Path.Combine(dir,"workflow-smoke-extract-range.pdf"); List<int> inclusiveIndexes=new List<int>{3,4,5,6,7};\n                Task extractRangeTask=ExtractPagesToPathAsync(inclusiveIndexes,extractRange); waitSmokeTask(extractRangeTask,"EXTRACT_RANGE_4_8");\n                PdfSession extractRangePdf=new PdfSession(extractRange); if(extractRangePdf.PageCount!=5) throw new InvalidOperationException("Workflow smoke: inclusive 4-8 extraction did not create five pages."); extractRangePdf=null;\n\n'''
if old_range not in s:
    raise SystemExit('v270 old range smoke block missing')
s=s.replace(old_range,'',1)

old_activate='''                ActivateDocument(firstWorkspace); Application.DoEvents(); int beforeSplitMerge=_outputs.Count;\n'''
new_activate='''                ActivateDocument(firstWorkspace); Application.DoEvents();\n                // Test the literal inclusive range 4-8 on a fixture that actually has at least eight\n                // model pages. The previous smoke ran this against a seven-page unsplit document,\n                // so index 7 (page 8) was correctly filtered out and the test falsely expected 5.\n                if(!_isSplit || _outputs.Count<8) throw new InvalidOperationException("Workflow smoke fixture must have at least 8 split pages for inclusive 4-8 extraction.");\n                string extractRange=Path.Combine(dir,"workflow-smoke-extract-range.pdf"); List<int> inclusiveIndexes=new List<int>{3,4,5,6,7};\n                Task extractRangeTask=ExtractPagesToPathAsync(inclusiveIndexes,extractRange); waitSmokeTask(extractRangeTask,"EXTRACT_RANGE_4_8");\n                PdfSession extractRangePdf=new PdfSession(extractRange); if(extractRangePdf.PageCount!=5) throw new InvalidOperationException("Workflow smoke: inclusive 4-8 extraction did not create five pages. Actual="+extractRangePdf.PageCount.ToString()); extractRangePdf=null;\n                int beforeSplitMerge=_outputs.Count;\n'''
if old_activate not in s:
    raise SystemExit('v270 firstWorkspace activation marker missing')
s=s.replace(old_activate,new_activate,1)

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_RANGE_SMOKE_FIXTURE_OK')
