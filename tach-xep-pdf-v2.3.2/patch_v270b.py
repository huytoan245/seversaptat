from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

anchor = '''                AddPdfPaths(new string[] { newFolderPdf }, true); Application.DoEvents();
                if (_documents.Count != 1 || _activeDocument == null) throw new InvalidOperationException("Workflow smoke: new folder PDF did not open after auto-clear.");

                AppDiagnostics.Log("WORKFLOW_SMOKE", "PASS");'''
if anchor not in s:
    raise SystemExit('v2.7.0 folder-switch smoke anchor missing')

replacement = '''                AddPdfPaths(new string[] { newFolderPdf }, true); Application.DoEvents();
                if (_documents.Count != 1 || _activeDocument == null) throw new InvalidOperationException("Workflow smoke: new folder PDF did not open after auto-clear.");

                // v2.7.0b: removing one item and clearing the whole session must NEVER delete source PDFs.
                DocumentWorkspace keepActive = _activeDocument;
                string removePdf = Path.Combine(newFolder, "remove-from-list.pdf"); File.Copy(newFolderPdf, removePdf, true);
                AddPdfPaths(new string[] { removePdf }, false); Application.DoEvents();
                DocumentWorkspace removeDoc = FindDocumentByPath(removePdf);
                if (removeDoc == null || _documents.Count != 2 || _fileList.Items.Count != 2) throw new InvalidOperationException("Workflow smoke: remove-one setup failed.");
                RemoveDocumentWorkspace(removeDoc, false); Application.DoEvents();
                if (_documents.Count != 1 || _fileList.Items.Count != 1 || FindDocumentByPath(removePdf) != null) throw new InvalidOperationException("Workflow smoke: remove-one did not remove only the workspace item.");
                if (!File.Exists(removePdf) || !File.Exists(newFolderPdf)) throw new InvalidOperationException("Workflow smoke: remove-one deleted a source PDF.");
                if (!object.ReferenceEquals(_activeDocument, keepActive)) throw new InvalidOperationException("Workflow smoke: removing an inactive item changed the active document.");

                ClearAllDocumentsCore(); Application.DoEvents();
                if (_documents.Count != 0 || _fileList.Items.Count != 0 || _activeDocument != null) throw new InvalidOperationException("Workflow smoke: clear-all core did not empty the session.");
                if (!File.Exists(removePdf) || !File.Exists(newFolderPdf)) throw new InvalidOperationException("Workflow smoke: clear-all deleted a source PDF.");
                AddPdfPaths(new string[] { newFolderPdf }, true); Application.DoEvents();
                if (_documents.Count != 1 || _activeDocument == null) throw new InvalidOperationException("Workflow smoke: app could not reopen a source after clear-all.");

                AppDiagnostics.Log("WORKFLOW_SMOKE", "PASS");'''
s = s.replace(anchor, replacement, 1)
p.write_text(s, encoding='utf-8-sig')
print('PATCH_V270B_LIST_REMOVE_CLEAR_REGRESSION_OK')
