from pathlib import Path

root = Path('tach-xep-pdf-v2.3.2')
p = root / 'TachXepTrangPDF.cs'
s = p.read_text(encoding='utf-8-sig')

# Make the header responsive and centered instead of using fixed X coordinates.
old_header = '''            Label title = new Label();
            title.Text = "TÁCH & XẾP TRANG PDF";
            title.Font = new Font("Segoe UI", 18f, FontStyle.Bold);
            title.AutoSize = true;
            title.Location = new Point(20, 12);
            header.Controls.Add(title);

            Label author = new Label();
            author.Text = "Phần mềm được thiết kế bởi Nguyễn Huy Toàn - Văn phòng Đảng ủy xã Thanh Lâm - 0979928450";
            author.Font = new Font("Segoe UI", 9.5f, FontStyle.Bold);
            author.ForeColor = Color.FromArgb(40, 85, 155);
            author.AutoSize = true;
            author.Location = new Point(22, 50);
            header.Controls.Add(author);

            _fileLabel = new Label();
            _fileLabel.Text = "File đang xử lý: Chưa mở tài liệu";
            _fileLabel.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            _fileLabel.ForeColor = Color.FromArgb(35, 35, 35);
            _fileLabel.AutoEllipsis = true;
            _fileLabel.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            _fileLabel.Location = new Point(690, 20);
            _fileLabel.Size = new Size(730, 28);
            header.Controls.Add(_fileLabel);

            _selectionLabel = new Label();
            _selectionLabel.Text = "Đang chọn: -";
            _selectionLabel.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            _selectionLabel.TextAlign = ContentAlignment.MiddleRight;
            _selectionLabel.Location = new Point(1060, 50);
            _selectionLabel.Size = new Size(360, 26);
            header.Controls.Add(_selectionLabel);'''

new_header = '''            TableLayoutPanel headerGrid = new TableLayoutPanel();
            headerGrid.Dock = DockStyle.Fill;
            headerGrid.ColumnCount = 3;
            headerGrid.RowCount = 3;
            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));
            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 52));
            headerGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 24));
            headerGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));
            headerGrid.RowStyles.Add(new RowStyle(SizeType.Absolute, 26));
            headerGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            header.Controls.Add(headerGrid);

            Label title = new Label();
            title.Text = "TÁCH & XẾP TRANG PDF";
            title.Font = new Font("Segoe UI", 18f, FontStyle.Bold);
            title.Dock = DockStyle.Fill;
            title.TextAlign = ContentAlignment.MiddleCenter;
            headerGrid.Controls.Add(title, 0, 0);
            headerGrid.SetColumnSpan(title, 3);

            Label author = new Label();
            author.Text = "Phần mềm được thiết kế bởi Nguyễn Huy Toàn - Văn phòng Đảng ủy xã Thanh Lâm - 0979928450";
            author.Font = new Font("Segoe UI", 9.5f, FontStyle.Bold);
            author.ForeColor = Color.FromArgb(40, 85, 155);
            author.Dock = DockStyle.Fill;
            author.TextAlign = ContentAlignment.MiddleCenter;
            author.AutoEllipsis = true;
            headerGrid.Controls.Add(author, 0, 1);
            headerGrid.SetColumnSpan(author, 3);

            _fileLabel = new Label();
            _fileLabel.Text = "File đang xử lý: Chưa mở tài liệu";
            _fileLabel.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            _fileLabel.ForeColor = Color.FromArgb(35, 35, 35);
            _fileLabel.AutoEllipsis = true;
            _fileLabel.Dock = DockStyle.Fill;
            _fileLabel.TextAlign = ContentAlignment.MiddleCenter;
            headerGrid.Controls.Add(_fileLabel, 1, 2);

            _selectionLabel = new Label();
            _selectionLabel.Text = "Đang chọn: -";
            _selectionLabel.Dock = DockStyle.Fill;
            _selectionLabel.TextAlign = ContentAlignment.MiddleRight;
            _selectionLabel.Padding = new Padding(0, 0, 12, 0);
            headerGrid.Controls.Add(_selectionLabel, 2, 2);'''

if old_header not in s:
    raise SystemExit('Expected fixed header block not found')
s = s.replace(old_header, new_header, 1)

# Add reusable UI visibility assertions for the CI smoke test.
program_marker = '''    internal static class Program
    {
        [STAThread]'''
program_helper = '''    internal static class Program
    {
        private static Control FindControlByText(Control root, string text)
        {
            if (root == null) return null;
            if (string.Equals(root.Text, text, StringComparison.Ordinal)) return root;
            foreach (Control child in root.Controls)
            {
                Control found = FindControlByText(child, text);
                if (found != null) return found;
            }
            return null;
        }

        private static void AssertUiControlVisible(Form form, string text)
        {
            Control c = FindControlByText(form, text);
            if (c == null) throw new InvalidOperationException("UI control missing: " + text);
            if (!c.Visible || c.Width <= 2 || c.Height <= 2) throw new InvalidOperationException("UI control hidden/zero size: " + text);
            Rectangle fr = form.RectangleToScreen(form.ClientRectangle);
            Rectangle cr = c.RectangleToScreen(c.ClientRectangle);
            if (!fr.IntersectsWith(cr)) throw new InvalidOperationException("UI control outside form: " + text);
        }

        [STAThread]'''
if program_marker not in s:
    raise SystemExit('Program marker not found')
s = s.replace(program_marker, program_helper, 1)

old_smoke_body = '''                        form.Show();
                        Application.DoEvents();
                        form.PerformLayout();
                        form.Width += 1;
                        Application.DoEvents();
                        form.Width -= 1;
                        Application.DoEvents();
                        form.Hide();'''
new_smoke_body = '''                        form.Show();
                        Application.DoEvents();
                        Size[] smokeSizes = new Size[]
                        {
                            new Size(1280, 720),
                            new Size(1440, 900),
                            new Size(1660, 900),
                            new Size(1920, 1080)
                        };
                        string[] required = new string[]
                        {
                            "TÁCH & XẾP TRANG PDF",
                            "Mở PDF",
                            "TỰ XOAY THÔNG MINH",
                            "TỰ CHIA & SẮP XẾP",
                            "Xuất PDF",
                            "Lưu vào file gốc",
                            "THỨ TỰ TRANG",
                            "XEM TRƯỚC",
                            "THÔNG TIN & HƯỚNG DẪN"
                        };
                        foreach (Size size in smokeSizes)
                        {
                            form.Size = size;
                            form.PerformLayout();
                            Application.DoEvents();
                            foreach (string text in required) AssertUiControlVisible(form, text);
                        }
                        form.Hide();'''
if old_smoke_body not in s:
    raise SystemExit('Expected UI smoke body not found')
s = s.replace(old_smoke_body, new_smoke_body, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V234_HEADER_AND_MULTI_SIZE_UI_SMOKE_OK')
