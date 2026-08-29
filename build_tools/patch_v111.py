from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Patch target not found: {label}")
    return text.replace(old, new, 1)


def patch(root: Path) -> None:
    core = root / "pdf_scan_organizer" / "core.py"
    s = core.read_text(encoding="utf-8")
    insert = r'''

@dataclass(frozen=True, slots=True)
class BackupCleanupResult:
    deleted_files: int = 0
    deleted_bytes: int = 0
    removed_dirs: int = 0
    failures: tuple[str, ...] = ()


def backup_stats_for_paths(pdf_paths: Iterable[Path | str]) -> tuple[int, int]:
    """Return count and total bytes for backups belonging to the supplied PDFs."""
    count = 0
    total_bytes = 0
    seen: set[str] = set()
    for raw in pdf_paths:
        pdf = Path(raw).resolve()
        backup = backup_path_for(pdf)
        key = os.path.normcase(str(backup))
        if key in seen:
            continue
        seen.add(key)
        try:
            stat = backup.stat()
        except FileNotFoundError:
            continue
        except OSError:
            continue
        if backup.is_file():
            count += 1
            total_bytes += stat.st_size
    return count, total_bytes


def cleanup_backups_for_paths(pdf_paths: Iterable[Path | str]) -> BackupCleanupResult:
    """Delete only app backups for supplied PDFs and remove empty backup directories."""
    deleted_files = 0
    deleted_bytes = 0
    failures: list[str] = []
    candidate_dirs: set[Path] = set()
    seen: set[str] = set()

    for raw in pdf_paths:
        pdf = Path(raw).resolve()
        backup = backup_path_for(pdf)
        candidate_dirs.add(backup.parent)
        key = os.path.normcase(str(backup))
        if key in seen:
            continue
        seen.add(key)
        try:
            if not backup.exists():
                continue
            size = backup.stat().st_size
            backup.unlink()
            deleted_files += 1
            deleted_bytes += size
        except Exception as exc:
            failures.append(f"{backup}: {exc}")

    removed_dirs = 0
    for directory in sorted(candidate_dirs, key=lambda item: len(item.parts), reverse=True):
        try:
            directory.rmdir()
            removed_dirs += 1
        except FileNotFoundError:
            pass
        except OSError:
            pass

    return BackupCleanupResult(
        deleted_files=deleted_files,
        deleted_bytes=deleted_bytes,
        removed_dirs=removed_dirs,
        failures=tuple(failures),
    )
'''
    s = replace_once(
        s,
        "def _validate_pdf(path: Path, expected_pages: int | None = None) -> int:\n",
        insert + "\n\ndef _validate_pdf(path: Path, expected_pages: int | None = None) -> int:\n",
        "core backup cleanup insertion",
    )
    s = s.replace("phiên bản 1.1.0 chưa hỗ trợ file mã hóa.", "phiên bản 1.1.1 chưa hỗ trợ file mã hóa.")
    core.write_text(s, encoding="utf-8")

    app = root / "pdf_scan_organizer" / "app.py"
    s = app.read_text(encoding="utf-8")
    s = replace_once(
        s,
        "from .core import DocumentSession, PdfOrganizerError, find_pdfs",
        "from .core import (\n    DocumentSession,\n    PdfOrganizerError,\n    backup_stats_for_paths,\n    cleanup_backups_for_paths,\n    find_pdfs,\n)",
        "app core imports",
    )
    old_foot = '''        foot = tk.Frame(p, bg=COLORS["panel"], padx=10, pady=9)\n        foot.pack(fill="x")\n        self._action_button(foot, "✓ ĐÁNH DẤU HOÀN THÀNH", self.toggle_completed, COLORS["green"], COLORS["green_hover"], width=23)\n'''
    new_foot = '''        foot = tk.Frame(p, bg=COLORS["panel"], padx=8, pady=9)\n        foot.pack(fill="x")\n        foot.grid_columnconfigure(0, weight=1)\n        foot.grid_columnconfigure(1, weight=1)\n\n        mark_btn = tk.Button(\n            foot, text="✓ ĐÁNH DẤU\\nHOÀN THÀNH", command=self.toggle_completed,\n            bg=COLORS["green"], fg="white", activebackground=COLORS["green_hover"], activeforeground="white",\n            relief="flat", bd=0, padx=5, pady=6, cursor="hand2", font=("Segoe UI Semibold", 8),\n        )\n        mark_btn.grid(row=0, column=0, sticky="ew", padx=(2, 3))\n        self.action_buttons.append(mark_btn)\n\n        finish_btn = tk.Button(\n            foot, text="✓ HOÀN TẤT\\nTHƯ MỤC", command=self.complete_folder,\n            bg=COLORS["gold"], fg="white", activebackground=COLORS["gold_hover"], activeforeground="white",\n            relief="flat", bd=0, padx=5, pady=6, cursor="hand2", font=("Segoe UI Semibold", 8),\n        )\n        finish_btn.grid(row=0, column=1, sticky="ew", padx=(3, 2))\n        self.action_buttons.append(finish_btn)\n'''
    s = replace_once(s, old_foot, new_foot, "file-panel completion buttons")

    methods = r'''    @staticmethod
    def _format_bytes(value: int) -> str:
        size = float(max(value, 0))
        units = ["B", "KB", "MB", "GB", "TB"]
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
            size /= 1024
        return f"{value} B"

    def complete_folder(self):
        """Confirm a fully processed folder, then purge only this folder's PDF backups."""
        if self.busy:
            return
        if not self.current_folder or not self.folder_paths:
            messagebox.showinfo("Hoàn tất thư mục", "Hãy bấm MỞ THƯ MỤC PDF trước khi dùng chức năng này.", parent=self)
            return

        folder_set = set(self.folder_paths)
        dirty = [s.name for path, s in self.sessions.items() if path in folder_set and s.dirty]
        if dirty:
            preview = "\n".join(f"• {name}" for name in dirty[:8])
            suffix = "" if len(dirty) <= 8 else f"\n• … và {len(dirty) - 8} file khác"
            messagebox.showwarning(
                "Còn file chưa lưu",
                f"Chưa thể hoàn tất thư mục vì còn {len(dirty)} file có thay đổi chưa lưu.\n\n"
                f"{preview}{suffix}\n\nHãy lưu các file này trước để không mất chỉnh sửa.",
                parent=self,
            )
            return

        incomplete = [path for path in self.folder_paths if not self.progress_store.get(path).completed]
        if incomplete:
            names = [Path(path).name for path in incomplete[:8]]
            preview = "\n".join(f"• {name}" for name in names)
            suffix = "" if len(incomplete) <= 8 else f"\n• … và {len(incomplete) - 8} file khác"
            messagebox.showwarning(
                "Chưa đủ điều kiện xóa backup",
                f"Còn {len(incomplete)} file chưa được ĐÁNH DẤU HOÀN THÀNH.\n\n"
                f"{preview}{suffix}\n\n"
                "Để bảo vệ dữ liệu, ứng dụng chưa xóa backup. Hãy kiểm tra và hoàn thành các file còn lại trước.",
                parent=self,
            )
            return

        backup_count, backup_bytes = backup_stats_for_paths(self.folder_paths)
        if backup_count == 0:
            self.status_var.set("Thư mục đã hoàn tất và hiện không còn bản sao lưu cần dọn.")
            messagebox.showinfo("Hoàn tất thư mục", "Tất cả PDF đã được đánh dấu hoàn thành và không còn backup cần xóa.", parent=self)
            return

        size_text = self._format_bytes(backup_bytes)
        if not messagebox.askyesno(
            "HOÀN TẤT THƯ MỤC & XÓA BACKUP",
            f"Tất cả {len(self.folder_paths)} PDF đã được đánh dấu hoàn thành và không có thay đổi chưa lưu.\n\n"
            f"Sẽ xóa {backup_count} bản PDF backup, tổng dung lượng khoảng {size_text}.\n\n"
            "Các PDF đã chỉnh vẫn giữ nguyên đúng tên và đúng vị trí file gốc.\n"
            "Sau khi xóa backup, chức năng KHÔI PHỤC PDF GỐC sẽ không còn dùng được cho các file này.\n\n"
            "Bạn xác nhận thư mục đã hoàn tất và muốn xóa backup ngay?",
            parent=self,
        ):
            return

        paths = list(self.folder_paths)
        self._set_busy(True, f"Đang dọn {backup_count} bản sao lưu của thư mục…")
        threading.Thread(target=self._complete_folder_worker, args=(paths,), daemon=True).start()

    def _complete_folder_worker(self, paths: list[str]):
        result = cleanup_backups_for_paths(paths)
        self.ui_queue.put(("folder_cleanup_done", result))

'''
    s = replace_once(s, "    def _open_next_file(self):\n", methods + "    def _open_next_file(self):\n", "complete-folder methods")

    handler = r'''                elif kind == "folder_cleanup_done":
                    _, result = msg
                    self._set_busy(False)
                    self._refresh_file_tree()
                    self._update_folder_progress()
                    if result.failures:
                        self.status_var.set(f"Đã xóa {result.deleted_files} backup nhưng còn {len(result.failures)} lỗi cần kiểm tra.")
                        messagebox.showerror(
                            "Dọn backup chưa hoàn tất",
                            f"Đã xóa {result.deleted_files} backup ({self._format_bytes(result.deleted_bytes)}), "
                            f"nhưng còn {len(result.failures)} lỗi.\n\n" + "\n\n".join(result.failures[:12]),
                            parent=self,
                        )
                    else:
                        self.status_var.set(
                            f"Thư mục đã hoàn tất • Đã xóa {result.deleted_files} backup "
                            f"({self._format_bytes(result.deleted_bytes)})."
                        )
                        messagebox.showinfo(
                            "Thư mục đã hoàn tất",
                            f"Đã xóa an toàn {result.deleted_files} bản sao lưu "
                            f"({self._format_bytes(result.deleted_bytes)}).\n\n"
                            "Các file PDF đã chỉnh vẫn nằm nguyên tại vị trí cũ và không bị đổi tên.\n"
                            "Thư mục backup trống cũng đã được tự động xóa.",
                            parent=self,
                        )
'''
    s = replace_once(s, '                elif kind == "bulk_progress":\n', handler + '                elif kind == "bulk_progress":\n', "cleanup UI queue handler")
    app.write_text(s, encoding="utf-8")

    main = root / "main.py"
    s = main.read_text(encoding="utf-8")
    s = replace_once(s, "from pdf_scan_organizer.core import DocumentSession", "from pdf_scan_organizer.core import DocumentSession, cleanup_backups_for_paths", "self-test import")
    s = replace_once(
        s,
        '''        if not session.has_original_backup:\n            raise RuntimeError("Self-test backup missing")\n''',
        '''        if not session.has_original_backup:\n            raise RuntimeError("Self-test backup missing")\n        cleanup = cleanup_backups_for_paths([path])\n        if cleanup.deleted_files != 1 or cleanup.failures:\n            raise RuntimeError("Self-test backup cleanup failed")\n        if session.has_original_backup:\n            raise RuntimeError("Self-test backup still exists after cleanup")\n        if len(PdfReader(str(path)).pages) != 3:\n            raise RuntimeError("Self-test PDF damaged after backup cleanup")\n''',
        "self-test cleanup assertions",
    )
    main.write_text(s, encoding="utf-8")

    tests = root / "tests" / "test_core.py"
    s = tests.read_text(encoding="utf-8")
    s = replace_once(
        s,
        "from pdf_scan_organizer.core import DocumentSession, backup_path_for, find_pdfs",
        "from pdf_scan_organizer.core import (\n    DocumentSession,\n    backup_path_for,\n    backup_stats_for_paths,\n    cleanup_backups_for_paths,\n    find_pdfs,\n)",
        "test imports",
    )
    new_tests = r'''    def test_cleanup_backups_for_completed_folder(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            first = base / "first.pdf"
            second = base / "second.pdf"
            make_labeled_pdf(first, ["1", "2"])
            make_labeled_pdf(second, ["1", "2", "3"])
            for path in (first, second):
                session = DocumentSession(path)
                session.reverse_all()
                session.save_atomic()
                self.assertTrue(backup_path_for(path).exists())
            count, total_bytes = backup_stats_for_paths([first, second])
            self.assertEqual(count, 2)
            self.assertGreater(total_bytes, 0)
            result = cleanup_backups_for_paths([first, second])
            self.assertEqual(result.deleted_files, 2)
            self.assertGreater(result.deleted_bytes, 0)
            self.assertFalse(result.failures)
            self.assertFalse(backup_path_for(first).exists())
            self.assertFalse(backup_path_for(second).exists())
            self.assertFalse((base / ".PDF-Scan-Organizer-Backup").exists())
            self.assertEqual(width_labels(first), [220, 210])
            self.assertEqual(width_labels(second), [230, 220, 210])

    def test_cleanup_preserves_unrelated_file_in_backup_dir(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            path = base / "book.pdf"
            make_labeled_pdf(path, ["1", "2"])
            session = DocumentSession(path)
            session.reverse_all()
            session.save_atomic()
            backup_dir = backup_path_for(path).parent
            unrelated = backup_dir / "do-not-delete.txt"
            unrelated.write_text("keep", encoding="utf-8")
            result = cleanup_backups_for_paths([path])
            self.assertEqual(result.deleted_files, 1)
            self.assertTrue(unrelated.exists())
            self.assertTrue(backup_dir.exists())

'''
    s = replace_once(s, "    def test_render_png_and_find(self):\n", new_tests + "    def test_render_png_and_find(self):\n", "cleanup regression tests")
    tests.write_text(s, encoding="utf-8")

    init = root / "pdf_scan_organizer" / "__init__.py"
    init.write_text(init.read_text(encoding="utf-8").replace('__version__ = "1.1.0"', '__version__ = "1.1.1"'), encoding="utf-8")

    assets = root / "build_assets.py"
    s = assets.read_text(encoding="utf-8")
    s = s.replace("(1,1,0,0)", "(1,1,1,0)")
    s = s.replace("'1.1.0'", "'1.1.1'")
    s = s.replace("PDF-Scan-Organizer-v1.1.0.exe", "PDF-Scan-Organizer-v1.1.1.exe")
    assets.write_text(s, encoding="utf-8")

    readme = root / "README.md"
    s = readme.read_text(encoding="utf-8")
    s = s.replace("# PDF Scan Organizer v1.1.0", "# PDF Scan Organizer v1.1.1")
    marker = "## An toàn dữ liệu\n"
    addition = '''## Hoàn tất thư mục và dọn backup\n\n- Nút **✓ HOÀN TẤT THƯ MỤC** nằm ngay cạnh **✓ ĐÁNH DẤU HOÀN THÀNH**.\n- Chỉ xóa backup khi không còn thay đổi chưa lưu và tất cả PDF đã được đánh dấu hoàn thành.\n- Hiển thị số backup và dung lượng trước khi xác nhận xóa.\n- Chỉ xóa backup do ứng dụng tạo; file lạ được giữ nguyên.\n- Thư mục backup trống tự xóa sau khi dọn xong.\n\n'''
    s = replace_once(s, marker, addition + marker, "README completion section")
    readme.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_v111.py <source-root>")
    patch(Path(sys.argv[1]).resolve())
    print("PATCH_V111_OK")
