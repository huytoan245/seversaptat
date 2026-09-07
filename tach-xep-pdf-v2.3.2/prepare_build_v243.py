from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')

# Advance release identity after the complete v2.4.2 preparation chain.
s=s.replace('release-v2.4.2','release-v2.4.3').replace('v2.4.2','v2.4.3').replace('2.4.2','2.4.3')

# Apply the verified v2.4.3 source diff after v2.4.2 is reconstructed.
old="& python (Join-Path $Project 'patch_v242.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v242.py failed' } }"
new="& python (Join-Path $Project 'patch_v242.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v242.py failed' }; & python (Join-Path $Project 'patch_v243.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v243.py failed' } }"
if old not in s: raise SystemExit('v242 patch-chain marker missing')
s=s.replace(old,new,1)

# Replace the obsolete collapsed-third-pane audit with the protected v2.1-style interactions.
old="'Panel2Collapsed = true',"
new="'EnsureListSelectionVisible','ShowImmediatePreviewFromThumbnail','SemaphoreSlim _previewRenderGate','PdfSession _previewPdf','CHỈNH ĐƯỜNG CẮT','TrackBar _manualCutSlider','Áp dụng đường cắt','ApplyManualCut','GetSelectedSourceFace','Lên 1','Xuống 1','Lên đầu','Xuống cuối','RunWorkflowSmoke',"
if old not in s: raise SystemExit('obsolete collapsed-pane audit marker missing')
s=s.replace(old,new,1)

# Keep the delivered source snapshot reproducible.
old="(Join-Path $Project 'prepare_build_v242.py'), (Join-Path $Project 'regression_test.py'),"
if old in s:
    s=s.replace(old,"(Join-Path $Project 'prepare_build_v242.py'), (Join-Path $Project 'patch_v243.py'), (Join-Path $Project 'prepare_build_v243.py'), (Join-Path $Project 'regression_test.py'),",1)

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V243_DIRECT_OK')
