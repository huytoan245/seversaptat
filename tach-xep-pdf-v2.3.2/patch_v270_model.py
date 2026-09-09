from pathlib import Path
import re
root=Path('tach-xep-pdf-v2.3.2')
p=root/'TachXepTrangPDF.cs'
s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('v270 model marker missing: '+label)
    s=s.replace(old,new,1)

rep('private const string AppVersion = "2.6.1";','private const string AppVersion = "2.7.0";','version')
if 'using PdfSharp.Pdf.IO;' not in s:
    rep('using Windows.Storage.Streams;\n','using Windows.Storage.Streams;\nusing PdfSharp.Pdf.IO;\n','pdfsharp using')
rep('        internal bool NeedsReview;\n        internal string ReviewReason = "";\n\n        internal SourceFace Clone()',
    '        internal bool NeedsReview;\n        internal string ReviewReason = "";\n        internal bool ImportedFullPage;\n\n        internal SourceFace Clone()','SourceFace flag')
rep('            x.ReviewReason = ReviewReason;\n            return x;\n        }\n    }\n\n    internal sealed class OutputPage',
    '            x.ReviewReason = ReviewReason;\n            x.ImportedFullPage = ImportedFullPage;\n            return x;\n        }\n    }\n\n    internal sealed class OutputPage','SourceFace clone')
rep('        internal int LogicalPageNumber;\n\n        internal OutputPage Clone()',
    '        internal int LogicalPageNumber;\n        internal bool ImportedFullPage;\n\n        internal OutputPage Clone()','OutputPage flag')
rep('            x.LogicalPageNumber = LogicalPageNumber;\n            return x;',
    '            x.LogicalPageNumber = LogicalPageNumber;\n            x.ImportedFullPage = ImportedFullPage;\n            return x;','OutputPage clone')

rep('        internal string WorkPath = "";\n        internal int PageCount;',
    '        internal string WorkPath = "";\n        internal string OriginalWorkPath = "";\n        internal int PageCount;','workspace original path')
rep('        private string _workPath = "";\n        private PdfSession _pdf;',
    '        private string _workPath = "";\n        private string _originalWorkPath = "";\n        private PdfSession _pdf;','runtime original path')

composer_marker='    internal sealed class OnnxOrientationAnalyzer : IDisposable\n'
if composer_marker not in s: raise SystemExit('v270 model composer marker missing')
composer=r'''    internal static class PdfPageComposer
    {
        internal static int AppendPdfs(string basePdfPath, IEnumerable<string> appendPaths, string outputPath)
        {
            if (string.IsNullOrWhiteSpace(basePdfPath) || !File.Exists(basePdfPath)) throw new FileNotFoundException("Không tìm thấy PDF đang xử lý.", basePdfPath);
            List<string> inputs = appendPaths == null ? new List<string>() : appendPaths.Where(delegate(string x) { return !string.IsNullOrWhiteSpace(x) && File.Exists(x); }).ToList();
            if (inputs.Count == 0) throw new InvalidOperationException("Chưa chọn PDF để ghép.");
            int added = 0;
            using (PdfSharp.Pdf.PdfDocument output = new PdfSharp.Pdf.PdfDocument())
            {
                using (PdfSharp.Pdf.PdfDocument current = PdfReader.Open(basePdfPath, PdfDocumentOpenMode.Import))
                    for (int i=0;i<current.PageCount;i++) output.AddPage(current.Pages[i]);
                for (int f=0;f<inputs.Count;f++)
                {
                    using (PdfSharp.Pdf.PdfDocument part = PdfReader.Open(inputs[f], PdfDocumentOpenMode.Import))
                        for (int i=0;i<part.PageCount;i++) { output.AddPage(part.Pages[i]); added++; }
                }
                if (added <= 0) throw new InvalidDataException("PDF ghép không có trang hợp lệ.");
                output.Save(outputPath);
            }
            return added;
        }
    }

'''
s=s.replace(composer_marker,composer+composer_marker,1)

old_ensure=r'''        private void EnsureWorkspaceCopy(DocumentWorkspace doc)
        {
            if (doc == null) throw new ArgumentNullException("doc");
            if (string.IsNullOrEmpty(doc.SourcePath) || !File.Exists(doc.SourcePath)) throw new FileNotFoundException("Không tìm thấy tệp PDF nguồn.", doc.SourcePath);
            if (!string.IsNullOrEmpty(doc.WorkPath) && File.Exists(doc.WorkPath)) return;
            doc.SessionDir = AppDiagnostics.CreateSessionDirectory(); doc.WorkPath = Path.Combine(doc.SessionDir, "work.pdf");
            File.Copy(doc.SourcePath, doc.WorkPath, true);
        }
'''
new_ensure=r'''        private void EnsureWorkspaceCopy(DocumentWorkspace doc)
        {
            if (doc == null) throw new ArgumentNullException("doc");
            if (string.IsNullOrEmpty(doc.SourcePath) || !File.Exists(doc.SourcePath)) throw new FileNotFoundException("Không tìm thấy tệp PDF nguồn.", doc.SourcePath);
            if (!string.IsNullOrEmpty(doc.WorkPath) && File.Exists(doc.WorkPath))
            {
                if (string.IsNullOrEmpty(doc.OriginalWorkPath) || !File.Exists(doc.OriginalWorkPath))
                {
                    if (string.IsNullOrEmpty(doc.SessionDir)) doc.SessionDir = Path.GetDirectoryName(doc.WorkPath);
                    doc.OriginalWorkPath = Path.Combine(doc.SessionDir, "original-at-open.pdf");
                    File.Copy(doc.SourcePath, doc.OriginalWorkPath, true);
                }
                return;
            }
            doc.SessionDir = AppDiagnostics.CreateSessionDirectory();
            doc.OriginalWorkPath = Path.Combine(doc.SessionDir, "original-at-open.pdf");
            doc.WorkPath = Path.Combine(doc.SessionDir, "work.pdf");
            File.Copy(doc.SourcePath, doc.OriginalWorkPath, true);
            File.Copy(doc.OriginalWorkPath, doc.WorkPath, true);
        }
'''
rep(old_ensure,new_ensure,'EnsureWorkspaceCopy')
rep('            _sourcePath = doc.SourcePath; _sessionDir = doc.SessionDir; _workPath = doc.WorkPath;\n',
    '            _sourcePath = doc.SourcePath; _sessionDir = doc.SessionDir; _workPath = doc.WorkPath; _originalWorkPath = doc.OriginalWorkPath;\n','OpenWorkspace paths')
rep('            _activeDocument.PageCount = _pdf.PageCount;\n            _activeDocument.Snapshot',
    '            _activeDocument.PageCount = _pdf.PageCount; _activeDocument.OriginalWorkPath = _originalWorkPath;\n            _activeDocument.Snapshot','Persist path')

start=s.find('        private void SplitAndArrange()\n'); end=s.find('        private async Task AutoRotateAsync()\n',start)
if start<0 or end<0: raise SystemExit('v270 model SplitAndArrange boundary missing')
new_split=r'''        private void SplitAndArrange()
        {
            if (_busy) return;
            if (_pdf == null || _sources.Count == 0) return;
            PushHistory(); _outputs.Clear();
            int splitFaceCount = _sources.Count(delegate(SourceFace x) { return !x.ImportedFullPage; });
            int totalPages = splitFaceCount * 2;
            List<OutputPage> importedFull = new List<OutputPage>();
            int splitOrdinal = 0;
            for (int i = 0; i < _sources.Count; i++)
            {
                SourceFace src = _sources[i];
                if (src.ImportedFullPage)
                {
                    importedFull.Add(new OutputPage { SourceId=src.Id, OriginalSourceIndex=src.OriginalSourceIndex, SourceRotation=src.Rotation, Half=-1, CutPercent=50.0, ExtraRotation=0, NeedsReview=src.NeedsReview, ReviewReason=src.ReviewReason, ImportedFullPage=true });
                    continue;
                }
                int sourceOrder = splitOrdinal++;
                OutputPage left = new OutputPage { SourceId = src.Id, OriginalSourceIndex = src.OriginalSourceIndex, SourceRotation = src.Rotation, Half = 0, CutPercent = src.CutPercent, ExtraRotation = 0, NeedsReview = src.NeedsReview, ReviewReason = src.ReviewReason };
                OutputPage right = new OutputPage { SourceId = src.Id, OriginalSourceIndex = src.OriginalSourceIndex, SourceRotation = src.Rotation, Half = 1, CutPercent = src.CutPercent, ExtraRotation = 0, NeedsReview = src.NeedsReview, ReviewReason = src.ReviewReason };
                OutputPage first = _dirLtr.Checked ? left : right; OutputPage second = _dirLtr.Checked ? right : left;
                if (_modeDetached.Checked)
                {
                    if (sourceOrder % 2 == 0) { first.LogicalPageNumber = totalPages - sourceOrder; second.LogicalPageNumber = sourceOrder + 1; }
                    else { first.LogicalPageNumber = sourceOrder + 1; second.LogicalPageNumber = totalPages - sourceOrder; }
                    _outputs.Add(first); _outputs.Add(second);
                }
                else { first.LogicalPageNumber = sourceOrder * 2 + 1; second.LogicalPageNumber = sourceOrder * 2 + 2; _outputs.Add(first); _outputs.Add(second); }
            }
            if (_modeDetached.Checked) _outputs.Sort(delegate(OutputPage a, OutputPage b) { return a.LogicalPageNumber.CompareTo(b.LogicalPageNumber); });
            _outputs.AddRange(importedFull);
            _isSplit = true; _redo.Clear(); RefreshList(0); RestoreListFocus(0);
            SetStatus("Đã chia " + splitFaceCount.ToString() + " mặt quét; giữ nguyên " + importedFull.Count.ToString() + " trang PDF đã ghép sau khi chia. Thứ tự nguồn không bị thay đổi bởi thao tác xoay.");
        }

'''
s=s[:start]+new_split+s[end:]

rep('                        File.Copy(_workPath, _originalBackupPath, true);',
    '                        string immutableOriginal = (!string.IsNullOrEmpty(_originalWorkPath) && File.Exists(_originalWorkPath)) ? _originalWorkPath : _workPath;\n                        File.Copy(immutableOriginal, _originalBackupPath, true);','immutable backup')

s=s.replace('internal const string Version = "2.6.1";','internal const string Version = "2.7.0";',1)
s=s.replace('startup-v2.6.1.log','startup-v2.7.0.log')
s=s.replace('_sourcePath = ""; _workPath = ""; _sessionDir = ""; _sourceWasOverwritten = false;', '_sourcePath = ""; _workPath = ""; _originalWorkPath = ""; _sessionDir = ""; _sourceWasOverwritten = false;')

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_MODEL_OK')