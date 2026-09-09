from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

old_work=r'''        private static void ReplaceWorkFileSafely(string tempPath, string workPath)
        {
            try { File.Replace(tempPath,workPath,null,true); }
            catch { File.Copy(tempPath,workPath,true); try { File.Delete(tempPath); } catch { } }
        }
'''
new_work=r'''        private static void ReplaceWorkFileSafely(string tempPath, string workPath)
        {
            try { File.Replace(tempPath,workPath,null,true); }
            catch
            {
                string rollback = workPath + ".replace.rollback";
                if (File.Exists(rollback)) File.Delete(rollback);
                if (File.Exists(workPath)) File.Move(workPath,rollback);
                try
                {
                    File.Move(tempPath,workPath);
                    if (File.Exists(rollback)) File.Delete(rollback);
                }
                catch
                {
                    if (File.Exists(workPath)) File.Delete(workPath);
                    if (File.Exists(rollback)) File.Move(rollback,workPath);
                    throw;
                }
            }
        }
'''
if old_work not in s: raise SystemExit('v270 restore-safe work replace marker missing')
s=s.replace(old_work,new_work,1)

old_source='''                    try { File.Replace(tmp,_sourcePath,null,true); } catch { File.Copy(tmp,_sourcePath,true); try{File.Delete(tmp);}catch{} }
'''
new_source='''                    try { File.Replace(tmp,_sourcePath,null,true); }
                    catch
                    {
                        string rollback = _sourcePath + ".restore.rollback";
                        if (File.Exists(rollback)) File.Delete(rollback);
                        if (File.Exists(_sourcePath)) File.Move(_sourcePath,rollback);
                        try
                        {
                            File.Move(tmp,_sourcePath);
                            if (File.Exists(rollback)) File.Delete(rollback);
                        }
                        catch
                        {
                            if (File.Exists(_sourcePath)) File.Delete(_sourcePath);
                            if (File.Exists(rollback)) File.Move(rollback,_sourcePath);
                            throw;
                        }
                    }
'''
if old_source not in s: raise SystemExit('v270 restore-safe physical source marker missing')
s=s.replace(old_source,new_source,1)

old_work_restore='''                CloseActiveRuntimeForSwitch(); File.Copy(immutableOriginal,_workPath,true); ReopenRuntimeAfterWorkFileChange();
'''
new_work_restore='''                CloseActiveRuntimeForSwitch();
                string workRestoreTemp = Path.Combine(_sessionDir,"work-restore-"+Guid.NewGuid().ToString("N")+".pdf");
                File.Copy(immutableOriginal,workRestoreTemp,true);
                ReplaceWorkFileSafely(workRestoreTemp,_workPath);
                ReopenRuntimeAfterWorkFileChange();
'''
if old_work_restore not in s: raise SystemExit('v270 restore-safe work restore marker missing')
s=s.replace(old_work_restore,new_work_restore,1)

old_catch='''            catch(Exception ex) { AppDiagnostics.LogException("RESTORE_ORIGINAL_FAIL",ex); MessageBox.Show(this,"Chưa khôi phục được PDF gốc.\\r\\n\\r\\n"+ex.Message,"Khôi phục PDF gốc",MessageBoxButtons.OK,MessageBoxIcon.Error); }
'''
new_catch='''            catch(Exception ex)
            {
                AppDiagnostics.LogException("RESTORE_ORIGINAL_FAIL",ex);
                try { if (_pdf == null && !string.IsNullOrEmpty(_workPath) && File.Exists(_workPath)) ReopenRuntimeAfterWorkFileChange(); } catch(Exception reopenEx) { AppDiagnostics.LogException("RESTORE_RUNTIME_REOPEN_FAIL",reopenEx); }
                MessageBox.Show(this,"Chưa khôi phục được PDF gốc.\\r\\n\\r\\n"+ex.Message,"Khôi phục PDF gốc",MessageBoxButtons.OK,MessageBoxIcon.Error);
            }
'''
if old_catch not in s: raise SystemExit('v270 restore-safe catch marker missing')
s=s.replace(old_catch,new_catch,1)

if '.restore.rollback' not in s: raise SystemExit('v270 restore rollback marker still missing')
if '.replace.rollback' not in s: raise SystemExit('v270 work replace rollback marker still missing')
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_RESTORE_SAFE_OK')
