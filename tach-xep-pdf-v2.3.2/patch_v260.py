from pathlib import Path
import re

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# -----------------------------------------------------------------------------
# v2.6.0 - per-file workflow status + reliable four-button page navigation.
# This patch deliberately sits on top of v2.5.0 and does not rewrite PDF/order logic.
# -----------------------------------------------------------------------------
if 'private const string AppVersion = "2.5.0";' not in s:
    raise SystemExit('v2.5.0 source marker missing')
s = s.replace('private const string AppVersion = "2.5.0";', 'private const string AppVersion = "2.6.0";', 1)

# Strongly typed per-document status. It lives with DocumentWorkspace, so switching PDFs
# cannot mix status just as it cannot mix undo/order/cut state.
main_marker = '    internal sealed class DocumentWorkspace\n'
if main_marker not in s:
    raise SystemExit('DocumentWorkspace marker missing')
status_enum = '''    internal enum DocumentProcessingState\n    {\n        NotProcessed = 0,\n        InProgress = 1,\n        Completed = 2\n    }\n\n'''
s = s.replace(main_marker, status_enum + main_marker, 1)
field_marker = '        internal string LastError = "";\n'
if field_marker not in s:
    raise SystemExit('DocumentWorkspace LastError marker missing')
s = s.replace(field_marker, field_marker + '        internal DocumentProcessingState ProcessingState = DocumentProcessingState.NotProcessed;\n', 1)

# File list now has a dedicated status column. Keep the filename/page-count column intact.
old_file_columns = '_fileList.Columns.Add("Tệp PDF", 200); _fileList.SelectedIndexChanged += FileSelectionChanged; fileLayout.Controls.Add(_fileList, 0, 2);\n            _fileList.Resize += delegate { if (_fileList.Columns.Count > 0) _fileList.Columns[0].Width = Math.Max(80, _fileList.ClientSize.Width - 5); };'
new_file_columns = '_fileList.Columns.Add("Tệp PDF", 150); _fileList.Columns.Add("Trạng thái", 108); _fileList.SelectedIndexChanged += FileSelectionChanged; fileLayout.Controls.Add(_fileList, 0, 2);\n            _fileList.Resize += delegate { UpdateFileListColumnWidths(); };'
if old_file_columns not in s:
    raise SystemExit('v2.5.0 file-list columns marker missing')
s = s.replace(old_file_columns, new_file_columns, 1)

# Replace the display updater with a two-column status-aware version.
start = s.find('        private void RefreshFileListItem(DocumentWorkspace doc)\n')
end = s.find('        private void SelectDocumentInFileList(DocumentWorkspace doc)\n', start)
if start < 0 or end < 0:
    raise SystemExit('RefreshFileListItem method boundary missing')
new_refresh = r'''        private static string GetDocumentStatusText(DocumentWorkspace doc)
        {
            if (doc == null) return "Chưa xử lý";
            switch (doc.ProcessingState)
            {
                case DocumentProcessingState.Completed: return "Đã hoàn thành";
                case DocumentProcessingState.InProgress: return "Đang xử lý";
                default: return "Chưa xử lý";
            }
        }

        private void UpdateFileListColumnWidths()
        {
            if (_fileList == null || _fileList.IsDisposed || _fileList.Columns.Count < 2) return;
            int statusPreferred = TextRenderer.MeasureText("Đã hoàn thành", _fileList.Font).Width + 22;
            statusPreferred = Math.Max(96, Math.Min(132, statusPreferred));
            int available = Math.Max(120, _fileList.ClientSize.Width - 6);
            int statusWidth = Math.Min(statusPreferred, Math.Max(88, available / 2));
            int nameWidth = Math.Max(80, available - statusWidth);
            _fileList.Columns[0].Width = nameWidth;
            _fileList.Columns[1].Width = statusWidth;
        }

        private void RefreshFileListItem(DocumentWorkspace doc)
        {
            if (_fileList == null || doc == null) return;
            for (int i = 0; i < _fileList.Items.Count; i++)
            {
                if (!object.ReferenceEquals(_fileList.Items[i].Tag, doc)) continue;
                ListViewItem item = _fileList.Items[i];
                string name = Path.GetFileName(doc.SourcePath);
                if (!string.IsNullOrEmpty(doc.LastError)) name = "⚠ " + name;
                if (doc.PageCount > 0) name += "  •  " + doc.PageCount.ToString() + " mặt";
                item.Text = name;
                while (item.SubItems.Count < 2) item.SubItems.Add("");
                item.SubItems[1].Text = GetDocumentStatusText(doc);
                item.ToolTipText = string.IsNullOrEmpty(doc.LastError)
                    ? doc.SourcePath + "\r\nTrạng thái: " + GetDocumentStatusText(doc)
                    : doc.SourcePath + "\r\n" + doc.LastError + "\r\nTrạng thái: " + GetDocumentStatusText(doc);
                break;
            }
            UpdateFileListColumnWidths();
        }

        private void MarkActiveDocumentInProgress()
        {
            if (_activeDocument == null) return;
            if (_activeDocument.ProcessingState != DocumentProcessingState.InProgress)
            {
                _activeDocument.ProcessingState = DocumentProcessingState.InProgress;
                RefreshFileListItem(_activeDocument);
            }
        }

        private void MarkActiveDocumentCompleted()
        {
            if (_activeDocument == null) return;
            _activeDocument.ProcessingState = DocumentProcessingState.Completed;
            RefreshFileListItem(_activeDocument);
        }

'''
s = s[:start] + new_refresh + s[end:]

# A newly added but unopened PDF must immediately say "Chưa xử lý".
old_add_item = 'ListViewItem item = new ListViewItem(Path.GetFileName(full)); item.Tag = doc; item.ToolTipText = full; _fileList.Items.Add(item);'
new_add_item = 'ListViewItem item = new ListViewItem(Path.GetFileName(full)); item.Tag = doc; item.ToolTipText = full; item.SubItems.Add(GetDocumentStatusText(doc)); _fileList.Items.Add(item); UpdateFileListColumnWidths();'
if old_add_item not in s:
    raise SystemExit('AddPdfPaths list-item marker missing')
s = s.replace(old_add_item, new_add_item, 1)

# Opening/activating a PDF means work has started, unless it has already been exported and
# has not been edited since. Merely switching back to a completed file must not erase completion.
old_active_tail = '_activeDocument = doc; doc.PageCount = _pdf.PageCount; doc.LastError = "";\n            _fileLabel.Text = "File đang mở: " + Path.GetFileName(_sourcePath);'
new_active_tail = '_activeDocument = doc; doc.PageCount = _pdf.PageCount; doc.LastError = ""; if (doc.ProcessingState == DocumentProcessingState.NotProcessed) doc.ProcessingState = DocumentProcessingState.InProgress;\n            _fileLabel.Text = "File đang mở: " + Path.GetFileName(_sourcePath);'
if old_active_tail not in s:
    raise SystemExit('OpenWorkspaceRuntime active-document marker missing')
s = s.replace(old_active_tail, new_active_tail, 1)

# Any edit after a completed export makes that file an active work item again. PushHistory is
# the common mutation boundary used by split/order/rotate/delete/manual-cut operations.
push_marker = '        private void PushHistory()\n        {\n'
if push_marker not in s:
    raise SystemExit('PushHistory marker missing')
s = s.replace(push_marker, push_marker + '            MarkActiveDocumentInProgress();\n', 1)

# Undo/Redo and restoring the original also invalidate a previous completed output.
for sig in ['        private void Undo()\n        {\n', '        private void Redo()\n        {\n', '        private void RestoreOriginalPdf()\n        {\n']:
    if sig not in s:
        raise SystemExit('state-changing method marker missing: ' + sig.strip())
    s = s.replace(sig, sig + '            MarkActiveDocumentInProgress();\n', 1)

# Mark completion ONLY inside ExportPdfAsync after a proven-success SetStatus call. This avoids
# false "Đã hoàn thành" when the Save dialog is cancelled or export throws.
export_sig = '        private async Task ExportPdfAsync(bool saveToOriginal)\n'
export_start = s.find(export_sig)
if export_start < 0:
    raise SystemExit('ExportPdfAsync signature missing')
brace = s.find('{', export_start)
if brace < 0:
    raise SystemExit('ExportPdfAsync opening brace missing')
depth = 0
export_end = -1
for i in range(brace, len(s)):
    ch = s[i]
    if ch == '{': depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            export_end = i + 1
            break
if export_end < 0:
    raise SystemExit('ExportPdfAsync closing brace missing')
export_body = s[export_start:export_end]
lines = export_body.splitlines(True)
patched_success = 0
for idx, line in enumerate(lines):
    if 'SetStatus(' not in line:
        continue
    if ('Đã xuất' in line) or ('Đã lưu vào file gốc' in line):
        indent = line[:len(line) - len(line.lstrip())]
        lines[idx] = line + indent + 'MarkActiveDocumentCompleted();\n'
        patched_success += 1
if patched_success < 1:
    statuses = [x.strip() for x in export_body.splitlines() if 'SetStatus(' in x]
    raise SystemExit('No successful ExportPdfAsync status marker found. Seen: ' + ' || '.join(statuses))
new_export_body = ''.join(lines)
s = s[:export_start] + new_export_body + s[export_end:]

# Runtime layout fix for the screenshot regression: all four page-order buttons are protected.
# At normal width they stay on one row. If the user narrows column 2, the row grows so the last
# button wraps visibly instead of being clipped below a fixed-height row.
helper_marker = '        private static void ClampSplitterForResize(SplitContainer split, int panel1Min, int panel2Min)\n'
if helper_marker not in s:
    raise SystemExit('splitter helper insertion marker missing')
nav_helper = r'''        private void LayoutPageNavigationButtons()
        {
            Button upOne = FindControlByText(this, "Lên 1") as Button;
            Button downOne = FindControlByText(this, "Xuống 1") as Button;
            Button toFirst = FindControlByText(this, "Lên đầu") as Button;
            Button toLast = FindControlByText(this, "Xuống cuối") as Button;
            if (upOne == null || downOne == null || toFirst == null || toLast == null) return;
            FlowLayoutPanel nav = upOne.Parent as FlowLayoutPanel;
            if (nav == null || !object.ReferenceEquals(nav, downOne.Parent) || !object.ReferenceEquals(nav, toFirst.Parent) || !object.ReferenceEquals(nav, toLast.Parent)) return;

            Button[] buttons = new Button[] { upOne, downOne, toFirst, toLast };
            int required = nav.Padding.Horizontal;
            for (int i = 0; i < buttons.Length; i++)
            {
                Button b = buttons[i];
                Size text = TextRenderer.MeasureText(b.Text ?? "", b.Font, new Size(int.MaxValue, int.MaxValue), TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix);
                b.AutoSize = false; b.Width = Math.Max(58, text.Width + b.Padding.Horizontal + 18); b.Height = Math.Max(32, b.Height);
                b.Margin = new Padding(i == 0 ? 0 : 4, 0, 0, 4);
                required += b.Width + b.Margin.Horizontal;
            }
            nav.AutoScroll = false;
            nav.WrapContents = nav.ClientSize.Width > 0 && required > nav.ClientSize.Width;
            int targetHeight = nav.WrapContents ? Math.Max(72, nav.GetPreferredSize(new Size(Math.Max(80, nav.ClientSize.Width), 0)).Height + 4) : Math.Max(38, buttons[0].Height + 6);
            TableLayoutPanel table = nav.Parent as TableLayoutPanel;
            if (table != null)
            {
                int row = table.GetRow(nav);
                if (row >= 0 && row < table.RowStyles.Count)
                {
                    table.RowStyles[row].SizeType = SizeType.Absolute;
                    table.RowStyles[row].Height = targetHeight;
                }
            }
            else if (nav.Height != targetHeight) nav.Height = targetHeight;
        }

'''
s = s.replace(helper_marker, nav_helper + helper_marker, 1)

# Run navigation layout every responsive pass and after the page-order splitter is dragged.
zoom_call = '                    ApplyZoom();\n'
# Limit replacement to the v2.5 responsive-layout block.
resp_start = s.find('            Action applyResponsiveLayout = delegate\n')
resp_end = s.find('            };', resp_start)
if resp_start < 0 or resp_end < 0:
    raise SystemExit('responsive-layout block missing')
segment = s[resp_start:resp_end + len('            };')]
if zoom_call not in segment:
    raise SystemExit('ApplyZoom in responsive-layout block missing')
segment = segment.replace(zoom_call, '                    LayoutPageNavigationButtons();\n' + zoom_call, 1)
s = s[:resp_start] + segment + s[resp_end + len('            };'):]

outer_hook_marker = '            SplitContainer outer = new SplitContainer(); outer.Dock = DockStyle.Fill; outer.Orientation = Orientation.Vertical; outer.SplitterWidth = 6; outer.IsSplitterFixed = false; fileOuter.Panel2.Controls.Add(outer);\n'
if outer_hook_marker not in s:
    raise SystemExit('outer splitter construction marker missing')
s = s.replace(outer_hook_marker, outer_hook_marker + '            outer.SplitterMoved += delegate { if (IsHandleCreated && !IsDisposed) BeginInvoke(new Action(LayoutPageNavigationButtons)); };\n', 1)

# Extend workflow smoke: prove untouched/in-progress/completed statuses are independent, and prove
# the fourth navigation button is present in the same navigation group.
pass_marker = '                AppDiagnostics.Log("WORKFLOW_SMOKE", "PASS");'
last_pass = s.rfind(pass_marker)
if last_pass < 0:
    raise SystemExit('WORKFLOW_SMOKE final PASS marker missing')
status_smoke = r'''                // v2.6.0 workflow-status regression.
                if (secondWorkspace.ProcessingState != DocumentProcessingState.InProgress) throw new InvalidOperationException("Workflow smoke: active PDF is not marked Đang xử lý.");
                string pdfPath3 = Path.Combine(dir, "workflow-smoke-unprocessed.pdf");
                File.Copy(pdfPath2, pdfPath3, true);
                AddPdfPaths(new string[] { pdfPath3 }, false); Application.DoEvents();
                DocumentWorkspace untouched = FindDocumentByPath(pdfPath3);
                if (untouched == null || untouched.ProcessingState != DocumentProcessingState.NotProcessed) throw new InvalidOperationException("Workflow smoke: untouched PDF did not stay Chưa xử lý.");
                MarkActiveDocumentCompleted(); Application.DoEvents();
                if (secondWorkspace.ProcessingState != DocumentProcessingState.Completed || GetDocumentStatusText(secondWorkspace) != "Đã hoàn thành") throw new InvalidOperationException("Workflow smoke: completed status did not persist on the active PDF.");
                MarkActiveDocumentInProgress();
                if (secondWorkspace.ProcessingState != DocumentProcessingState.InProgress || GetDocumentStatusText(untouched) != "Chưa xử lý") throw new InvalidOperationException("Workflow smoke: per-file status isolation failed.");
                LayoutPageNavigationButtons(); Application.DoEvents();
                Button smokeLast = FindControlByText(this, "Xuống cuối") as Button;
                if (smokeLast == null || !smokeLast.Visible) throw new InvalidOperationException("Workflow smoke: Xuống cuối button is not visible.");

'''
s = s[:last_pass] + status_smoke + s[last_pass:]

# UI smoke: explicitly require the status header and every navigation button to be fully visible.
required_marker = '                            "TỆP ĐANG XỬ LÝ",\n'
if required_marker not in s:
    raise SystemExit('UI smoke file-header marker missing')
s = s.replace(required_marker, required_marker + '                            "Trạng thái",\n', 1)

smoke_layout_anchor = '                            if (c4.Width > Math.Max(280, form.ClientSize.Width / 4)) throw new InvalidOperationException("Manual cut column is too wide by default.");\n'
if smoke_layout_anchor not in s:
    raise SystemExit('UI smoke four-column anchor missing')
nav_smoke = '''                            foreach (string navText in new string[]{"Lên 1","Xuống 1","Lên đầu","Xuống cuối"}) { AssertUiControlVisible(form, navText); AssertButtonTextFits(form, navText); }\n'''
s = s.replace(smoke_layout_anchor, smoke_layout_anchor + nav_smoke, 1)

# Keep diagnostics/launcher version aligned with managed app and release directory.
s = s.replace('startup-v2.5.0.log', 'startup-v2.6.0.log').replace('Version = "2.5.0"', 'Version = "2.6.0"')
launcher = Path('tach-xep-pdf-v2.3.2/launcher.cpp')
if launcher.exists():
    ls = launcher.read_text(encoding='utf-8-sig')
    ls2 = ls.replace('2.5.0', '2.6.0')
    if ls2 == ls:
        raise SystemExit('launcher v2.5.0 marker missing')
    launcher.write_text(ls2, encoding='utf-8-sig')

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V260_STATUS_AND_BOTTOM_NAV_OK success_markers=' + str(patched_success))
