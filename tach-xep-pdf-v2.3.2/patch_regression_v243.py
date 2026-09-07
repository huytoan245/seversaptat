from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
required=[
    'private const string AppVersion = "2.4.3";',
    'PreviewZoomSlider',
    '_zoom.Minimum = 50; _zoom.Maximum = 250;',
    'PreviewToolbar',
    'PreviewViewport',
    'ManualCutSlider',
    'Áp dụng đường cắt',
    'GetSelectedCutSource()',
    'ApplyManualCut()',
    'inner.Panel2Collapsed = false',
    'EnsureListSelectionVisible',
    'ShowImmediatePreviewFromThumbnail',
    'SemaphoreSlim _previewRenderGate',
    'Lên 1',
    'Xuống 1',
    'Lên đầu',
    'Xuống cuối',
    '--workflow-smoke',
    'RunWorkflowSmoke',
    'WORKFLOW_SMOKE'
]
for x in required:
    if x not in s: raise SystemExit('missing v2.4.3 regression marker: '+x)
forbidden=[
    'inner.Panel2Collapsed = true',
    '_cut.Enabled = !busy && !_isSplit && SelectedIndex >= 0;'
]
for x in forbidden:
    if x in s: raise SystemExit('forbidden v2.4.2 regression remains: '+x)
print('PATCH_REGRESSION_V243_OK')
