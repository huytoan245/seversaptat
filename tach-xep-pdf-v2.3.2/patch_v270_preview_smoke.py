from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

old = '''                if (_list.Items.Count != 14) throw new InvalidOperationException("Workflow smoke: source list count mismatch.");

                SplitAndArrange();
                Application.DoEvents();
'''
new = '''                if (_list.Items.Count != 14) throw new InvalidOperationException("Workflow smoke: source list count mismatch.");

                // v2.7.0 smoke synchronization: the no-blank transition contract only becomes
                // meaningful after the first real PDF preview exists. Do not mistake startup's
                // intentional asynchronous first render for a page-transition blank frame.
                string initialPreviewKey = ModelKey(_list.Items[0].Tag);
                long initialPreviewStarted = Environment.TickCount64;
                while ((_previewMaster == null || _preview.Image == null || _previewModelKey != initialPreviewKey)
                    && Environment.TickCount64 - initialPreviewStarted < 5000)
                {
                    Application.DoEvents();
                    Thread.Sleep(15);
                }
                if (_previewMaster == null || _preview.Image == null || _previewModelKey != initialPreviewKey)
                    throw new InvalidOperationException("Workflow smoke: initial real preview did not settle within 5 seconds.");

                SplitAndArrange();
                Application.DoEvents();
'''
if old not in s:
    raise SystemExit('v2.7.0 preview smoke synchronization marker missing')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8-sig')
print('PATCH_V270_PREVIEW_SMOKE_SYNC_OK')
