from pathlib import Path
root=Path('tach-xep-pdf-v2.3.2'); p=root/'TachXepTrangPDF.cs'; s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('v270 merge marker missing: '+label)
    s=s.replace(old,new,1)

marker='        private async Task ExportPdfAsync(bool overwriteOriginal)\n'
if marker not in s: raise SystemExit('v270 merge export marker missing')
block=r'''        private void ReopenRuntimeAfterWorkFileChange()
        {
            _pdf = new PdfSession(_workPath); _previewPdf = new PdfSession(_workPath); _prefetchPdf = new PdfSession(_workPath);
            if (_activeDocument != null) { _activeDocument.WorkPath=_workPath; _activeDocument.OriginalWorkPath=_originalWorkPath; _activeDocument.PageCount=_pdf.PageCount; }
        }

        private static void ReplaceWorkFileSafely(string tempPath, string workPath)
        {
            try { File.Replace(tempPath,workPath,null,true); }
            catch { File.Copy(tempPath,workPath,true); try { File.Delete(tempPath); } catch { } }
        }

        private async Task MergePdfIntoCurrentAsync(int insertAfterModelIndex)
        {
            if (_busy || _pdf==null || _activeDocument==null) return;
            string[] addFiles;
            using(OpenFileDialog dlg=new OpenFileDialog())
            {
                dlg.Filter="Tài liệu PDF (*.pdf)|*.pdf"; dlg.Title=_isSplit ? "Ghép PDF vào tài liệu sau khi đã cắt" : "Ghép PDF vào tài liệu gốc đang chỉnh sửa"; dlg.Multiselect=true;
                if(dlg.ShowDialog(this)!=DialogResult.OK) return; addFiles=dlg.FileNames;
            }
            if(addFiles==null || addFiles.Length==0) return;
            try { await MergePdfFilesCoreAsync(addFiles,insertAfterModelIndex); }
            catch(Exception ex) { MessageBox.Show(this,ex.Message,"Ghép thêm PDF",MessageBoxButtons.OK,MessageBoxIcon.Error); }
        }

        private async Task MergePdfFilesCoreAsync(string[] addFiles,int insertAfterModelIndex)
        {
            if (_busy || _pdf==null || _activeDocument==null) return;
            if(addFiles==null || addFiles.Length==0) return;
            int oldPhysicalCount=_pdf.PageCount; int oldSelected=SelectedIndex;
            string rollback=Path.Combine(_sessionDir,"work-before-merge-"+Guid.NewGuid().ToString("N")+".pdf");
            string temp=Path.Combine(_sessionDir,"work-merge-"+Guid.NewGuid().ToString("N")+".pdf");
            PushHistory(); SetBusy(true,"Đang ghép thêm PDF...");
            try
            {
                File.Copy(_workPath,rollback,true); CloseActiveRuntimeForSwitch();
                int added=await Task.Run(delegate { return PdfPageComposer.AppendPdfs(_workPath,addFiles,temp); });
                ReplaceWorkFileSafely(temp,_workPath); ReopenRuntimeAfterWorkFileChange();
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
                try { File.Delete(rollback); } catch { }
            }
            catch(Exception ex)
            {
                AppDiagnostics.LogException("MERGE_PDF_FAIL",ex); try { CloseActiveRuntimeForSwitch(); } catch { }
                try { if(File.Exists(rollback)) File.Copy(rollback,_workPath,true); } catch { }
                try { ReopenRuntimeAfterWorkFileChange(); } catch { }
                if(_undo.Count>0) { AppSnapshot before=_undo.Pop(); RestoreSnapshot(before); }
                throw new InvalidOperationException("Chưa ghép được PDF. Tài liệu đang làm đã được đưa về trạng thái trước thao tác ghép. "+ex.Message,ex);
            }
            finally
            {
                try { if(File.Exists(temp))File.Delete(temp); } catch { } try { if(File.Exists(rollback))File.Delete(rollback); } catch { }
                SetBusy(false,null); if(_list!=null && _list.Items.Count>0) RestoreListFocus(Math.Max(0,Math.Min(_list.Items.Count-1,oldSelected)));
            }
        }

        private void ShowExtractChoiceMenu(Control anchor)
        {
            if(_pdf==null || anchor==null) return; ContextMenuStrip menu=UiTheme.Menu();
            menu.Items.Add("Tách riêng trang đang chọn",null,async delegate { await ExtractSelectedPageAsync(); });
            menu.Items.Add("Tách nhiều trang liên tục...",null,async delegate { await ExtractRangeWithDialogAsync(); });
            Point at = anchor is Button ? new Point(0,anchor.Height) : anchor.PointToClient(Cursor.Position); menu.Show(anchor,at);
        }

        private async Task ExtractSelectedPageAsync()
        {
            int idx=SelectedIndex; if(_busy || _pdf==null || idx<0) return; await ExtractPagesAsync(new List<int>{idx},"trang_"+(idx+1).ToString());
        }

        private async Task ExtractRangeWithDialogAsync()
        {
            int count=_isSplit?_outputs.Count:_sources.Count; if(_busy || _pdf==null || count<=0) return; int selected=Math.Max(1,SelectedIndex+1);
            using(PageRangeDialog dlg=new PageRangeDialog(count,selected))
            {
                if(dlg.ShowDialog(this)!=DialogResult.OK) return; List<int> indexes=new List<int>(); for(int page=dlg.FromPage;page<=dlg.ToPage;page++) indexes.Add(page-1);
                await ExtractPagesAsync(indexes,"trang_"+dlg.FromPage.ToString()+"-"+dlg.ToPage.ToString());
            }
        }

        private async Task ExtractPagesAsync(IList<int> modelIndexes,string suffix)
        {
            if(modelIndexes==null || modelIndexes.Count==0 || _pdf==null) return; string target;
            using(SaveFileDialog dlg=new SaveFileDialog())
            {
                dlg.Filter="Tài liệu PDF (*.pdf)|*.pdf"; dlg.Title=modelIndexes.Count==1?"Tách trang ra PDF mới":"Tách nhiều trang ra PDF mới";
                string baseName=string.IsNullOrEmpty(_sourcePath)?"Tai_lieu":Path.GetFileNameWithoutExtension(_sourcePath); dlg.FileName=baseName+"_"+suffix+".pdf";
                if(dlg.ShowDialog(this)!=DialogResult.OK)return; target=dlg.FileName;
            }
            if(!string.IsNullOrEmpty(_sourcePath) && string.Equals(Path.GetFullPath(target),Path.GetFullPath(_sourcePath),StringComparison.OrdinalIgnoreCase))
            {
                MessageBox.Show(this,"Không thể dùng chức năng Tách trang để ghi đè PDF nguồn. Hãy chọn một tên file khác.","Tách trang",MessageBoxButtons.OK,MessageBoxIcon.Information); return;
            }
            try
            {
                await ExtractPagesToPathAsync(modelIndexes,target);
                MessageBox.Show(this,"Đã tạo PDF mới gồm "+modelIndexes.Count.ToString()+" trang.\r\n\r\nTài liệu đang chỉnh sửa không bị thay đổi.\r\n"+target,"Tách trang",MessageBoxButtons.OK,MessageBoxIcon.Information);
            }
            catch(Exception ex) { AppDiagnostics.LogException("EXTRACT_PDF_FAIL",ex); MessageBox.Show(this,"Chưa tách được trang.\r\n\r\n"+ex.Message,"Tách trang",MessageBoxButtons.OK,MessageBoxIcon.Error); }
        }

        private async Task ExtractPagesToPathAsync(IList<int> modelIndexes,string target)
        {
            if(modelIndexes==null || modelIndexes.Count==0 || _pdf==null) throw new InvalidOperationException("Chưa chọn trang để tách.");
            int count=_isSplit?_outputs.Count:_sources.Count; List<int> indexes=modelIndexes.Where(delegate(int x){return x>=0 && x<count;}).Distinct().ToList();
            if(indexes.Count==0)throw new ArgumentOutOfRangeException("modelIndexes");
            int beforeUndo=_undo.Count, beforeRedo=_redo.Count; DocumentProcessingState beforeStatus=_activeDocument==null?DocumentProcessingState.NotProcessed:_activeDocument.ProcessingState;
            SetBusy(true,"Đang tách trang ra PDF mới...");
            try
            {
                await Task.Run(delegate { SimplePdfWriter.WriteFromFactory(target,indexes.Count,delegate(int i){return BuildExportPage(indexes[i]);},null); }); ValidateGeneratedPdf(target,indexes.Count);
                if((_isSplit?_outputs.Count:_sources.Count)!=count || _undo.Count!=beforeUndo || _redo.Count!=beforeRedo) throw new InvalidOperationException("Tách trang đã làm thay đổi mô hình tài liệu đang chỉnh sửa.");
                if(_activeDocument!=null && _activeDocument.ProcessingState!=beforeStatus) throw new InvalidOperationException("Tách trang đã làm thay đổi trạng thái xử lý của tệp."); SetStatus("Đã tách "+indexes.Count.ToString()+" trang ra PDF mới: "+target);
            }
            finally { SetBusy(false,null); RestoreListFocus(SelectedIndex); }
        }

'''
s=s.replace(marker,block+marker,1)
start=s.find('        private void RestoreOriginalPdf()\n'); end=s.find('        private void PushHistory()\n',start)
if start<0 or end<0: raise SystemExit('v270 merge restore boundary missing')
restore=r'''        private void RestoreOriginalPdf()
        {
            MarkActiveDocumentInProgress();
            if (_busy || _pdf == null) return;
            if (MessageBox.Show(this, "Đưa PDF về đúng trạng thái khi vừa mở file?\r\n\r\nMọi chỉnh sửa, kể cả các PDF đã ghép trong phiên, sẽ bị hủy. Nếu đã Lưu vào file gốc, file vật lý cũng được phục hồi.\r\n\r\nChức năng này khác nút Làm lại (Redo).", "Khôi phục PDF gốc", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) != DialogResult.Yes) { RestoreListFocus(SelectedIndex); return; }
            SetBusy(true, "Đang khôi phục PDF gốc...");
            try
            {
                string immutableOriginal=(!string.IsNullOrEmpty(_originalWorkPath)&&File.Exists(_originalWorkPath))?_originalWorkPath:_originalBackupPath;
                if(string.IsNullOrEmpty(immutableOriginal)||!File.Exists(immutableOriginal)) throw new FileNotFoundException("Không tìm thấy bản PDF bất biến lúc mở file.");
                if (_sourceWasOverwritten)
                {
                    string tmp = Path.Combine(Path.GetDirectoryName(_sourcePath), "." + Path.GetFileName(_sourcePath) + ".restore.tmp.pdf"); File.Copy(immutableOriginal,tmp,true); ValidateGeneratedPdf(tmp,1);
                    try { File.Replace(tmp,_sourcePath,null,true); } catch { File.Copy(tmp,_sourcePath,true); try{File.Delete(tmp);}catch{} }
                    _sourceWasOverwritten=false; if (_activeDocument != null) _activeDocument.SourceWasOverwritten = false;
                }
                CloseActiveRuntimeForSwitch(); File.Copy(immutableOriginal,_workPath,true); ReopenRuntimeAfterWorkFileChange();
                _sources.Clear(); _outputs.Clear(); _undo.Clear(); _redo.Clear(); _isSplit=false;
                for(int i=0;i<_pdf.PageCount;i++) _sources.Add(new SourceFace { OriginalSourceIndex=i, Rotation=0, CutPercent=50.0, ImportedFullPage=false });
                _modeDetached.Checked=true; _modeBound.Checked=false; _dirLtr.Checked=true; _dirRtl.Checked=false; if(_zoom!=null)_zoom.Value=100; BeginThumbnailBuild(); RefreshList(0);
                SetStatus("Đã khôi phục PDF về đúng trạng thái khi vừa mở file, bao gồm loại bỏ mọi trang đã ghép trong phiên.");
            }
            catch(Exception ex) { AppDiagnostics.LogException("RESTORE_ORIGINAL_FAIL",ex); MessageBox.Show(this,"Chưa khôi phục được PDF gốc.\r\n\r\n"+ex.Message,"Khôi phục PDF gốc",MessageBoxButtons.OK,MessageBoxIcon.Error); }
            finally { SetBusy(false,null); RestoreListFocus(0); }
        }

'''
s=s[:start]+restore+s[end:]
s=s.replace('                        if (p.NeedsReview) text += " · ⚠ CẦN KIỂM TRA";', '                        if (p.ImportedFullPage) text += " · PDF ghép";\n                        if (p.NeedsReview) text += " · ⚠ CẦN KIỂM TRA";',1)
p.write_text(s,encoding='utf-8-sig'); print('PATCH_V270_MERGE_EXTRACT_OK')