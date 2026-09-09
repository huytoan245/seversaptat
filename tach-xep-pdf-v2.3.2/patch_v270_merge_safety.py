from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# Prefetch is an optimization only: session/list changes must never be allowed to break
# the foreground Preview transition. Snapshot items defensively and contain scheduling races.
start = s.find('        private void SchedulePreviewPrefetch(int centerIndex)\n')
end = s.find('        private async void LoadSelectedPreviewAsync()\n', start)
if start < 0 or end < 0:
    raise SystemExit('v2.7.0 SchedulePreviewPrefetch boundary missing')
new_prefetch = r'''        private void SchedulePreviewPrefetch(int centerIndex)
        {
            try
            {
                PdfSession pdf = _prefetchPdf;
                if (pdf == null || _list == null || _list.IsDisposed || centerIndex < 0) return;
                List<object> nearby = new List<object>();
                int[] offsets = new int[] { 1, -1, 2, -2 };
                int count = _list.Items.Count;
                for (int i = 0; i < offsets.Length; i++)
                {
                    int idx = centerIndex + offsets[i];
                    if (idx < 0 || idx >= count || idx >= _list.Items.Count) continue;
                    ListViewItem item = _list.Items[idx];
                    if (item != null && item.Tag != null) nearby.Add(item.Tag);
                }
                if (nearby.Count == 0 || pdf != _prefetchPdf) return;
                CancellationTokenSource next = new CancellationTokenSource();
                CancellationTokenSource old = Interlocked.Exchange(ref _prefetchCts, next);
                if (old != null) { try { old.Cancel(); } catch { } try { old.Dispose(); } catch { } }
                CancellationToken token = next.Token;
                Task.Run(delegate
                {
                    for (int i = 0; i < nearby.Count; i++)
                    {
                        if (token.IsCancellationRequested || pdf != _prefetchPdf) break;
                        object model = nearby[i];
                        if (model == null) continue;
                        string key = PreviewCacheKey(model);
                        Bitmap cached;
                        if (TryGetCachedPreview(key, out cached)) { if (cached != null) cached.Dispose(); continue; }
                        Bitmap rendered = null;
                        try
                        {
                            rendered = RenderPreviewBitmap(pdf, model, 1500);
                            if (rendered != null && !token.IsCancellationRequested && pdf == _prefetchPdf) PutPreviewCache(key, rendered);
                        }
                        catch (Exception ex) { AppDiagnostics.LogException("PREVIEW_PREFETCH_FAIL", ex); }
                        finally { if (rendered != null) rendered.Dispose(); }
                    }
                }, token);
            }
            catch (Exception ex)
            {
                AppDiagnostics.LogException("PREVIEW_PREFETCH_SCHEDULE_FAIL", ex);
            }
        }

'''
s = s[:start] + new_prefetch + s[end:]

# Merge must never replace a work file that an in-flight WinRT PDF renderer may still hold.
# Compose a new immutable revision, then switch the active runtime to that revision. The old
# work revision remains untouched and is therefore a reliable rollback source.
start = s.find('        private async Task MergePdfFilesCoreAsync(string[] addFiles,int insertAfterModelIndex)\n')
end = s.find('        private void ShowExtractChoiceMenu(Control anchor)\n', start)
if start < 0 or end < 0:
    raise SystemExit('v2.7.0 MergePdfFilesCoreAsync boundary missing')
new_merge = r'''        private async Task MergePdfFilesCoreAsync(string[] addFiles,int insertAfterModelIndex)
        {
            if (_busy || _pdf==null || _activeDocument==null) return;
            if(addFiles==null || addFiles.Length==0) return;
            int oldPhysicalCount=_pdf.PageCount; int oldSelected=SelectedIndex;
            string oldWorkPath=_workPath;
            string baseCopy=Path.Combine(_sessionDir,"merge-base-"+Guid.NewGuid().ToString("N")+".pdf");
            string newWorkPath=Path.Combine(_sessionDir,"work-merged-"+Guid.NewGuid().ToString("N")+".pdf");
            PushHistory(); SetBusy(true,"Đang ghép thêm PDF...");
            try
            {
                // Read from a stable copy so PDFsharp never competes with Windows.Data.Pdf handles.
                File.Copy(oldWorkPath,baseCopy,true);
                int added=await Task.Run(delegate { return PdfPageComposer.AppendPdfs(baseCopy,addFiles,newWorkPath); });
                if(added<=0 || !File.Exists(newWorkPath)) throw new InvalidDataException("PDF ghép không tạo được bản làm việc mới.");

                // Switch runtime by path; do not replace/overwrite a file that an old preview task may hold.
                CloseActiveRuntimeForSwitch();
                _workPath=newWorkPath;
                if(_activeDocument!=null) _activeDocument.WorkPath=_workPath;
                ReopenRuntimeAfterWorkFileChange();
                if(_pdf.PageCount!=oldPhysicalCount+added) throw new InvalidDataException("Số trang sau khi ghép không khớp.");

                int targetCount=_isSplit?_outputs.Count:_sources.Count;
                int insertAt=insertAfterModelIndex>=0 ? Math.Max(0,Math.Min(targetCount,insertAfterModelIndex+1)) : targetCount;
                if(!_isSplit)
                {
                    for(int j=0;j<added;j++) _sources.Insert(insertAt+j,new SourceFace { OriginalSourceIndex=oldPhysicalCount+j, Rotation=0, CutPercent=50.0, ImportedFullPage=false });
                }
                else
                {
                    for(int j=0;j<added;j++)
                    {
                        SourceFace sf=new SourceFace { OriginalSourceIndex=oldPhysicalCount+j, Rotation=0, CutPercent=50.0, ImportedFullPage=true };
                        _sources.Add(sf);
                        _outputs.Insert(insertAt+j,new OutputPage { SourceId=sf.Id, OriginalSourceIndex=sf.OriginalSourceIndex, SourceRotation=0, Half=-1, CutPercent=50.0, ExtraRotation=0, ImportedFullPage=true });
                    }
                }
                _redo.Clear(); MarkActiveDocumentInProgress(); ClearPreviewCache(); BeginThumbnailBuild();
                int newCount=_isSplit?_outputs.Count:_sources.Count; int focus=Math.Max(0,Math.Min(newCount-1,insertAt)); RefreshList(focus); RestoreListFocus(focus);
                SetStatus("Đã ghép thêm "+added.ToString()+" trang PDF. "+(_isSplit?"Các trang mới được giữ nguyên dạng trang đầy đủ trong bản đã cắt.":"Các trang mới đã trở thành một phần của bản gốc đang chỉnh sửa; bấm Lưu vào file gốc để ghi kết quả vào PDF nguồn."));
            }
            catch(Exception ex)
            {
                AppDiagnostics.LogException("MERGE_PDF_FAIL",ex);
                try { CloseActiveRuntimeForSwitch(); } catch { }
                _workPath=oldWorkPath;
                if(_activeDocument!=null) _activeDocument.WorkPath=oldWorkPath;
                try { ReopenRuntimeAfterWorkFileChange(); } catch(Exception reopenEx) { AppDiagnostics.LogException("MERGE_ROLLBACK_REOPEN_FAIL",reopenEx); }
                if(_undo.Count>0) { AppSnapshot before=_undo.Pop(); RestoreSnapshot(before); }
                try { if(File.Exists(newWorkPath)) File.Delete(newWorkPath); } catch { }
                throw new InvalidOperationException("Chưa ghép được PDF. Tài liệu đang làm đã được đưa về trạng thái trước thao tác ghép. "+ex.Message,ex);
            }
            finally
            {
                try { if(File.Exists(baseCopy)) File.Delete(baseCopy); } catch { }
                SetBusy(false,null); if(_list!=null && _list.Items.Count>0) RestoreListFocus(Math.Max(0,Math.Min(_list.Items.Count-1,oldSelected)));
            }
        }

'''
s = s[:start] + new_merge + s[end:]

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V270_MERGE_SAFETY_OK')
