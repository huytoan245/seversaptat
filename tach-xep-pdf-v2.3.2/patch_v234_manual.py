from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

old_start = '''            Panel manual = new Panel(); manual.Dock = DockStyle.Fill; manual.Margin = new Padding(0); settings.Controls.Add(manual, 2, 0);
            FlowLayoutPanel manualButtons = new FlowLayoutPanel(); manualButtons.Dock = DockStyle.Top; manualButtons.Height = 38; manualButtons.WrapContents = false; manualButtons.AutoScroll = true; manual.Controls.Add(manualButtons);'''
new_start = '''            Panel manual = new Panel(); manual.Dock = DockStyle.Fill; manual.Margin = new Padding(0); settings.Controls.Add(manual, 2, 0);
            TableLayoutPanel manualGrid = new TableLayoutPanel(); manualGrid.Dock = DockStyle.Fill; manualGrid.ColumnCount = 1; manualGrid.RowCount = 2; manualGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 38)); manualGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); manual.Controls.Add(manualGrid);
            FlowLayoutPanel manualButtons = new FlowLayoutPanel(); manualButtons.Dock = DockStyle.Fill; manualButtons.WrapContents = false; manualButtons.AutoScroll = true; manualGrid.Controls.Add(manualButtons, 0, 0);'''
if old_start not in s:
    raise SystemExit('manual panel start block not found')
s = s.replace(old_start, new_start, 1)

old_cut = '''            FlowLayoutPanel cutRow = new FlowLayoutPanel(); cutRow.Dock = DockStyle.Fill; cutRow.WrapContents = false; cutRow.Padding = new Padding(68, 2, 0, 0); manual.Controls.Add(cutRow); cutRow.SendToBack();'''
new_cut = '''            FlowLayoutPanel cutRow = new FlowLayoutPanel(); cutRow.Dock = DockStyle.Fill; cutRow.WrapContents = false; cutRow.AutoScroll = true; cutRow.Padding = new Padding(68, 2, 0, 0); manualGrid.Controls.Add(cutRow, 0, 1);'''
if old_cut not in s:
    raise SystemExit('manual cut row block not found')
s = s.replace(old_cut, new_cut, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V234_MANUAL_GRID_OK')
