from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/patch_v260.py')
s = p.read_text(encoding='utf-8-sig')
old = "nav_helper = r'''        private void LayoutPageNavigationButtons()\n"
new = r'''nav_helper = r''' + "'''" + r'''        private static Control FindControlByText(Control root, string text)
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

        private void LayoutPageNavigationButtons()
'''
if old not in s:
    raise SystemExit('v260 nav_helper start marker missing')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8-sig')
print('FIX_PATCH_V260_FINDCONTROL_OK')
