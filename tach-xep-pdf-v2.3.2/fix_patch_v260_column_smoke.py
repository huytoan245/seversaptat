from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/patch_v260.py')
s = p.read_text(encoding='utf-8-sig')
old = '''required_marker = '                            "TỆP ĐANG XỬ LÝ",\\n'\nif required_marker not in s:\n    raise SystemExit('UI smoke file-header marker missing')\ns = s.replace(required_marker, required_marker + '                            "Trạng thái",\\n', 1)\n'''
new = '''required_marker = '                            "TỆP ĐANG XỬ LÝ",\\n'\nif required_marker not in s:\n    raise SystemExit('UI smoke file-header marker missing')\n# ColumnHeader is not a WinForms Control, so the generic control-tree smoke cannot find it.\n# The status header is validated in RunWorkflowSmoke below and by the release source contract.\n'''
if old not in s:
    raise SystemExit('v260 generic status-header smoke block missing')
s = s.replace(old, new, 1)

# Strengthen the real MainForm workflow smoke with an actual ListView column assertion.
anchor = '                // v2.6.0 workflow-status regression.\n'
if anchor not in s:
    raise SystemExit('v260 workflow status smoke anchor missing')
insert = '''                if (_fileList == null || _fileList.Columns.Count < 2 || _fileList.Columns[1].Text != "Trạng thái") throw new InvalidOperationException("Workflow smoke: Trạng thái ListView column missing.");\n'''
s = s.replace(anchor, anchor + insert, 1)
p.write_text(s, encoding='utf-8-sig')
print('FIX_PATCH_V260_COLUMN_SMOKE_OK')
