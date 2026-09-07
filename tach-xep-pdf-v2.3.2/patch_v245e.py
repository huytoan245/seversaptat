from pathlib import Path
import hashlib

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
raw = p.read_bytes()
expected = 'ea3b16c54c2437f480194b2eb97147e662138b2f09cfafcdef01c3f047a6a452'
if hashlib.sha256(raw).hexdigest() != expected:
    raise SystemExit('unexpected source before v2.4.5e preview smoke patch')
s = raw.decode('utf-8-sig')

old = '''                SelectAdjacent(1);
                Application.DoEvents();
                if (SelectedIndex != 1) throw new InvalidOperationException("Workflow smoke: cannot select page 2.");
                if (_list.TopItem == null || _list.TopItem.Index != 0) throw new InvalidOperationException("Workflow smoke: page 1 is not kept visible when page 2 is selected.");
                if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank after selecting page 2.");
                Bitmap beforeRapid = _previewMaster;
                SelectAdjacent(1); Application.DoEvents(); if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank during rapid page-down.");
                SelectAdjacent(-1); Application.DoEvents(); if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank during rapid page-up.");
                if (_thumbs.ImageSize.Width == _previewMaster.Width && _thumbs.ImageSize.Height == _previewMaster.Height) throw new InvalidOperationException("Workflow smoke: tiny thumbnail leaked into Preview.");
                string selectedKey = ModelKey(_list.Items[SelectedIndex].Tag);
                if (_previewModelKey != selectedKey) throw new InvalidOperationException("Workflow smoke: preview did not switch immediately to selected page.");
'''
new = '''                SelectAdjacent(1);
                Application.DoEvents();
                if (SelectedIndex != 1) throw new InvalidOperationException("Workflow smoke: cannot select page 2.");
                if (_list.TopItem == null || _list.TopItem.Index != 0) throw new InvalidOperationException("Workflow smoke: page 1 is not kept visible when page 2 is selected.");
                if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank after selecting page 2.");

                // An uncached real page is intentionally rendered in the background. The product contract is
                // to keep the previous real page visible until the new real-aspect bitmap is ready, not to
                // stretch a thumbnail just to make this assertion synchronous. Wait only for the initial
                // uncached page, then verify that revisiting the now-cached page is immediate.
                string page2Key = ModelKey(_list.Items[SelectedIndex].Tag);
                long previewWaitStarted = Environment.TickCount64;
                while (_previewModelKey != page2Key && Environment.TickCount64 - previewWaitStarted < 5000)
                {
                    Application.DoEvents();
                    Thread.Sleep(15);
                }
                if (_previewModelKey != page2Key) throw new InvalidOperationException("Workflow smoke: uncached real preview did not settle within 5 seconds.");
                Bitmap cacheProbe;
                if (!TryGetCachedPreview(PreviewCacheKey(_list.Items[SelectedIndex].Tag), out cacheProbe))
                    throw new InvalidOperationException("Workflow smoke: settled preview was not stored in the real-page cache.");
                cacheProbe.Dispose();

                Bitmap beforeRapid = _previewMaster;
                SelectAdjacent(1); Application.DoEvents(); if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank during rapid page-down.");
                SelectAdjacent(-1); Application.DoEvents(); if (_preview.Image == null) throw new InvalidOperationException("Workflow smoke: preview flashed blank during rapid page-up.");
                if (_thumbs.ImageSize.Width == _previewMaster.Width && _thumbs.ImageSize.Height == _previewMaster.Height) throw new InvalidOperationException("Workflow smoke: tiny thumbnail leaked into Preview.");
                string selectedKey = ModelKey(_list.Items[SelectedIndex].Tag);
                if (_previewModelKey != selectedKey || selectedKey != page2Key)
                    throw new InvalidOperationException("Workflow smoke: cached real preview did not switch immediately when revisiting the selected page.");
                if (_previewMaster == null || beforeRapid == null) throw new InvalidOperationException("Workflow smoke: real preview disappeared during rapid navigation.");
'''
if old not in s:
    raise SystemExit('workflow preview smoke block missing')
s = s.replace(old, new, 1)

out = s.encode('utf-8-sig')
actual = hashlib.sha256(out).hexdigest()
expected_final = '4d52d10b20d345ff99406755de27fc5b769e6aedb5bbfecc0848dce1c28004aa'
if actual != expected_final:
    raise SystemExit('v2.4.5e checksum mismatch: ' + actual)
p.write_bytes(out)
print('PATCH_V245E_ASYNC_REAL_PREVIEW_SMOKE_OK source_sha256=' + actual)
