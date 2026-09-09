from pathlib import Path
root=Path('tach-xep-pdf-v2.3.2'); p=root/'TachXepTrangPDF.cs'; s=p.read_text(encoding='utf-8-sig')
pass_marker='                AppDiagnostics.Log("WORKFLOW_SMOKE", "PASS");'
pos=s.rfind(pass_marker)
if pos<0: raise SystemExit('v270 tests WORKFLOW_SMOKE PASS marker missing')
smoke=r'''                // v2.7.0 feature regression: both merge modes, both extraction modes, list lifecycle.
                Action<Task,string> waitSmokeTask = delegate(Task task,string name)
                {
                    AppDiagnostics.Log("WORKFLOW_SMOKE_V270", name+" BEGIN"); long started=Environment.TickCount64;
                    while(!task.IsCompleted && Environment.TickCount64-started<15000){Application.DoEvents();Thread.Sleep(10);}
                    if(!task.IsCompleted) throw new TimeoutException("Workflow smoke timeout at "+name+" after 15 seconds.");
                    task.GetAwaiter().GetResult(); AppDiagnostics.Log("WORKFLOW_SMOKE_V270", name+" PASS");
                };
                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","CREATE_MERGE_FIXTURE BEGIN");
                string mergePart = Path.Combine(dir,"workflow-smoke-merge-2.pdf");
                SimplePdfWriter.WriteFromFactory(mergePart,2,delegate(int index)
                {
                    using(Bitmap b=new Bitmap(420,300,PixelFormat.Format24bppRgb)) using(Graphics g=Graphics.FromImage(b))
                    { g.Clear(Color.White); using(Font f=UiTheme.Font(18f,FontStyle.Bold)) g.DrawString("MERGE "+(index+1).ToString(),f,Brushes.Black,20,20); using(MemoryStream ms=new MemoryStream()){b.Save(ms,ImageFormat.Jpeg);return new SimplePdfWriter.ImagePage{Jpeg=ms.ToArray(),PixelWidth=b.Width,PixelHeight=b.Height,Dpi=120.0};} }
                },null);
                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","CREATE_MERGE_FIXTURE PASS");

                ActivateDocument(secondWorkspace); Application.DoEvents();
                int originalSecondCount=_sources.Count; int[] originalSecondOrder=_sources.Select(delegate(SourceFace x){return x.OriginalSourceIndex;}).ToArray();
                Task mergeUnsplitTask=MergePdfFilesCoreAsync(new string[]{mergePart},-1); waitSmokeTask(mergeUnsplitTask,"MERGE_BEFORE_SPLIT");
                if(_isSplit || _sources.Count!=originalSecondCount+2 || _pdf.PageCount!=originalSecondCount+2) throw new InvalidOperationException("Workflow smoke: merge before split did not append two source pages.");
                if(!_sources.Take(originalSecondCount).Select(delegate(SourceFace x){return x.OriginalSourceIndex;}).SequenceEqual(originalSecondOrder)) throw new InvalidOperationException("Workflow smoke: merge changed existing source order/identity.");
                if(_sources.Skip(originalSecondCount).Any(delegate(SourceFace x){return x.ImportedFullPage;})) throw new InvalidOperationException("Workflow smoke: pre-split merge incorrectly marked pages as full-page imports.");
                PdfSession sourceBeforeSave=new PdfSession(pdfPath2); if(sourceBeforeSave.PageCount!=originalSecondCount) throw new InvalidOperationException("Workflow smoke: merge modified source PDF before Save original."); sourceBeforeSave=null;
                string mergedModelExport=Path.Combine(dir,"workflow-smoke-merged-model-export.pdf"); List<int> mergedIndexes=Enumerable.Range(0,_sources.Count).ToList();
                Task mergedExportTask=ExtractPagesToPathAsync(mergedIndexes,mergedModelExport); waitSmokeTask(mergedExportTask,"EXPORT_MERGED_MODEL");
                PdfSession mergedExportPdf=new PdfSession(mergedModelExport); if(mergedExportPdf.PageCount!=originalSecondCount+2) throw new InvalidOperationException("Workflow smoke: current merged model would not export all pages for Save original."); mergedExportPdf=null;

                string extractSingle=Path.Combine(dir,"workflow-smoke-extract-single.pdf"); int modelCountBeforeExtract=_sources.Count, undoBeforeExtract=_undo.Count, redoBeforeExtract=_redo.Count;
                Task extractOneTask=ExtractPagesToPathAsync(new List<int>{2},extractSingle); waitSmokeTask(extractOneTask,"EXTRACT_SINGLE");
                PdfSession extractOnePdf=new PdfSession(extractSingle); if(extractOnePdf.PageCount!=1) throw new InvalidOperationException("Workflow smoke: single-page extraction count mismatch."); extractOnePdf=null;
                if(_sources.Count!=modelCountBeforeExtract || _undo.Count!=undoBeforeExtract || _redo.Count!=redoBeforeExtract) throw new InvalidOperationException("Workflow smoke: single extraction mutated active document.");

                string extractRange=Path.Combine(dir,"workflow-smoke-extract-range.pdf"); List<int> inclusiveIndexes=new List<int>{3,4,5,6,7};
                Task extractRangeTask=ExtractPagesToPathAsync(inclusiveIndexes,extractRange); waitSmokeTask(extractRangeTask,"EXTRACT_RANGE_4_8");
                PdfSession extractRangePdf=new PdfSession(extractRange); if(extractRangePdf.PageCount!=5) throw new InvalidOperationException("Workflow smoke: inclusive 4-8 extraction did not create five pages."); extractRangePdf=null;

                ActivateDocument(firstWorkspace); Application.DoEvents(); int beforeSplitMerge=_outputs.Count;
                Task mergeSplitTask=MergePdfFilesCoreAsync(new string[]{mergePart},-1); waitSmokeTask(mergeSplitTask,"MERGE_AFTER_SPLIT");
                if(!_isSplit || _outputs.Count!=beforeSplitMerge+2 || _outputs.Skip(_outputs.Count-2).Any(delegate(OutputPage x){return x.Half!=-1 || !x.ImportedFullPage;})) throw new InvalidOperationException("Workflow smoke: merge after split did not preserve imported full pages.");
                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","REBUILD_SPLIT BEGIN"); SplitAndArrange(); Application.DoEvents(); AppDiagnostics.Log("WORKFLOW_SMOKE_V270","REBUILD_SPLIT PASS");
                if(_outputs.Count!=beforeSplitMerge+2 || _outputs.Skip(_outputs.Count-2).Any(delegate(OutputPage x){return x.Half!=-1 || !x.ImportedFullPage;})) throw new InvalidOperationException("Workflow smoke: imported full pages were split in half on rebuild.");
                if(string.IsNullOrEmpty(_originalWorkPath) || !File.Exists(_originalWorkPath)) throw new InvalidOperationException("Workflow smoke: immutable original work copy missing after merge.");

                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","LIST_LIFECYCLE BEGIN");
                string preserveSource=firstWorkspace.SourcePath; ActivateDocument(secondWorkspace); Application.DoEvents(); RemoveDocumentWorkspace(firstWorkspace); Application.DoEvents();
                if(!File.Exists(preserveSource)) throw new InvalidOperationException("Workflow smoke: remove-one deleted a source PDF.");
                foreach(DocumentWorkspace d in _documents) d.ProcessingState=DocumentProcessingState.Completed;
                string newFolder=Path.Combine(dir,"new-folder"); Directory.CreateDirectory(newFolder); string newFolderPdf=Path.Combine(newFolder,"new-folder.pdf"); File.Copy(pdfPath2,newFolderPdf,true);
                if(!PrepareDocumentListForOpen(new string[]{newFolderPdf})) throw new InvalidOperationException("Workflow smoke: completed folder switch was rejected.");
                if(_documents.Count!=0 || _fileList.Items.Count!=0) throw new InvalidOperationException("Workflow smoke: old folder list did not auto-clear.");
                if(!File.Exists(pdfPath2)) throw new InvalidOperationException("Workflow smoke: clear-all deleted a source PDF.");
                AddPdfPaths(new string[]{newFolderPdf},true); Application.DoEvents();
                if(_documents.Count!=1 || !string.Equals(SafeDirectoryOf(_activeDocument.SourcePath),SafeDirectoryOf(newFolderPdf),StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Workflow smoke: new folder was not activated after auto-clear.");
                AppDiagnostics.Log("WORKFLOW_SMOKE_V270","LIST_LIFECYCLE PASS");

'''
s=s[:pos]+smoke+s[pos:]
p.write_text(s,encoding='utf-8-sig'); print('PATCH_V270_TESTS_OK')