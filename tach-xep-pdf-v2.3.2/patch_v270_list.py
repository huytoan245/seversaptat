from pathlib import Path
root=Path('tach-xep-pdf-v2.3.2'); p=root/'TachXepTrangPDF.cs'; s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('v270 list marker missing: '+label)
    s=s.replace(old,new,1)

marker='        private void AddPdfPaths(string[] paths, bool activateFirst)\n'
if marker not in s: raise SystemExit('v270 list AddPdfPaths marker missing')
block=r'''        private static string SafeDirectoryOf(string path)
        {
            try { return Path.GetFullPath(Path.GetDirectoryName(path) ?? "").TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar); }
            catch { return ""; }
        }

        private bool PrepareDocumentListForOpen(string[] newPaths)
        {
            if (newPaths == null || newPaths.Length == 0 || _documents.Count == 0) return true;
            string first = newPaths.FirstOrDefault(delegate(string x) { return !string.IsNullOrWhiteSpace(x); });
            if (string.IsNullOrEmpty(first)) return false;
            string newDir = SafeDirectoryOf(first);
            DocumentWorkspace anchor = _activeDocument ?? _documents[0]; string oldDir = SafeDirectoryOf(anchor.SourcePath);
            if (string.Equals(newDir, oldDir, StringComparison.OrdinalIgnoreCase)) return true;
            bool allCompleted = _documents.All(delegate(DocumentWorkspace d) { return d.ProcessingState == DocumentProcessingState.Completed; });
            if (allCompleted) { ClearAllDocumentsCore(); SetStatus("Đã chuyển sang thư mục mới; danh sách tệp đã hoàn thành của thư mục cũ được tự động xóa."); return true; }
            DialogResult answer = MessageBox.Show(this,
                "Bạn đang mở PDF ở một thư mục khác, nhưng danh sách hiện tại vẫn còn tệp chưa hoàn thành.\r\n\r\nXóa danh sách cũ và chuyển sang thư mục mới?\r\n\r\nPDF nguồn trên ổ đĩa sẽ không bị xóa.",
                "Chuyển thư mục PDF", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (answer != DialogResult.Yes) return false; ClearAllDocumentsCore(); return true;
        }

        private void DeleteSessionDirectoryLater(string dir)
        {
            if (string.IsNullOrEmpty(dir)) return; Task.Run(delegate { try { Thread.Sleep(80); if (Directory.Exists(dir)) Directory.Delete(dir,true); } catch { } });
        }

        private void ResetNoDocumentUi()
        {
            _activeDocument=null; _sources.Clear(); _outputs.Clear(); _undo.Clear(); _redo.Clear(); _isSplit=false;
            _sourcePath=""; _workPath=""; _originalWorkPath=""; _sessionDir=""; _sourceWasOverwritten=false; _originalBackupPath="";
            if (_list!=null) _list.Items.Clear(); if (_thumbs!=null) _thumbs.Images.Clear(); ClearPreviewCache();
            if (_preview!=null) { Image old=_preview.Image; _preview.Image=null; if(old!=null) try{old.Dispose();}catch{} };
            if (_fileLabel!=null) _fileLabel.Text="File đang mở: Chưa mở tài liệu"; if (_selectionLabel!=null) _selectionLabel.Text="Đang chọn: -"; UpdateButtons();
        }

        private void RemoveDocumentWorkspace(DocumentWorkspace doc)
        {
            if (doc == null) return;
            bool wasActive = object.ReferenceEquals(doc,_activeDocument); string dir = doc.SessionDir; _suspendDocumentSelection=true;
            try
            {
                if (wasActive) { try { PersistActiveDocumentState(); } catch { } try { CloseActiveRuntimeForSwitch(); } catch { } }
                if(_fileList!=null) for(int i=_fileList.Items.Count-1;i>=0;i--) if(object.ReferenceEquals(_fileList.Items[i].Tag,doc)) _fileList.Items.RemoveAt(i);
                int oldIndex=_documents.IndexOf(doc); _documents.Remove(doc); if (wasActive) ResetNoDocumentUi();
                if (_documents.Count>0 && _activeDocument==null) { int nextIndex=Math.Max(0,Math.Min(_documents.Count-1,oldIndex)); _suspendDocumentSelection=false; ActivateDocument(_documents[nextIndex]); _suspendDocumentSelection=true; }
            }
            finally { _suspendDocumentSelection=false; }
            DeleteSessionDirectoryLater(dir);
        }

        private void RemoveSelectedFileFromList()
        {
            if (_busy || _fileList==null || _fileList.SelectedItems.Count==0) return; DocumentWorkspace doc=_fileList.SelectedItems[0].Tag as DocumentWorkspace; if(doc==null) return;
            if (MessageBox.Show(this,"Xóa tệp này khỏi danh sách làm việc?\r\n\r\nPDF nguồn trên ổ đĩa không bị xóa.","Xóa tệp khỏi danh sách",MessageBoxButtons.YesNo,MessageBoxIcon.Question)!=DialogResult.Yes) return; RemoveDocumentWorkspace(doc);
        }

        private void ClearAllDocumentsCore()
        {
            List<string> dirs=_documents.Select(delegate(DocumentWorkspace d){return d.SessionDir;}).Where(delegate(string x){return !string.IsNullOrEmpty(x);}).Distinct(StringComparer.OrdinalIgnoreCase).ToList(); _suspendDocumentSelection=true;
            try { try { PersistActiveDocumentState(); } catch { } try { CloseActiveRuntimeForSwitch(); } catch { } _documents.Clear(); if(_fileList!=null)_fileList.Items.Clear(); ResetNoDocumentUi(); }
            finally { _suspendDocumentSelection=false; }
            foreach(string dir in dirs) DeleteSessionDirectoryLater(dir);
        }

        private void ClearAllDocumentsFromButton()
        {
            if (_busy || _documents.Count==0) return;
            if (MessageBox.Show(this,"Xóa toàn bộ danh sách tệp khỏi phiên làm việc?\r\n\r\nCác PDF nguồn trên ổ đĩa không bị xóa.","Xóa toàn bộ danh sách",MessageBoxButtons.YesNo,MessageBoxIcon.Question)!=DialogResult.Yes) return; ClearAllDocumentsCore(); SetStatus("Đã xóa toàn bộ danh sách tệp khỏi phiên làm việc.");
        }

        private void FileListMouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button!=MouseButtons.Right || _fileList==null) return; ListViewItem item=_fileList.GetItemAt(e.X,e.Y); if(item==null) return;
            _suspendDocumentSelection=true; try { foreach(ListViewItem x in _fileList.Items)x.Selected=false; item.Selected=true; item.Focused=true; } finally { _suspendDocumentSelection=false; }
        }

        private void PageListMouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button!=MouseButtons.Right || _list==null) return; ListViewItem item=_list.GetItemAt(e.X,e.Y); if(item==null) return;
            _suspendSelection=true; try { foreach(ListViewItem x in _list.Items)x.Selected=false; item.Selected=true; item.Focused=true; } finally { _suspendSelection=false; }
            UpdateSelectionLabel(); UpdateCutControl(); LoadSelectedPreviewAsync(); UpdateButtons();
        }

        private void ActivateSelectedFileFromContext()
        {
            if (_fileList==null || _fileList.SelectedItems.Count==0) return; DocumentWorkspace doc=_fileList.SelectedItems[0].Tag as DocumentWorkspace; if(doc!=null && !object.ReferenceEquals(doc,_activeDocument)) ActivateDocument(doc);
        }

'''
s=s.replace(marker,block+marker,1)
rep('                if (dlg.ShowDialog(this) != DialogResult.OK) return;\n                AddPdfPaths(dlg.FileNames, true);','                if (dlg.ShowDialog(this) != DialogResult.OK) return;\n                if (!PrepareDocumentListForOpen(dlg.FileNames)) return;\n                AddPdfPaths(dlg.FileNames, true);','OpenPdf folder switch')
p.write_text(s,encoding='utf-8-sig'); print('PATCH_V270_LIST_OK')