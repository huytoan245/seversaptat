#define UNICODE
#define _UNICODE
#include <windows.h>
#include <shlobj.h>
#include <shellapi.h>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include "payload_map.h"

namespace fs = std::filesystem;

static std::wstring GetLocalAppData()
{
    wchar_t path[MAX_PATH] = {0};
    HRESULT hr = SHGetFolderPathW(nullptr, CSIDL_LOCAL_APPDATA | CSIDL_FLAG_CREATE, nullptr, SHGFP_TYPE_CURRENT, path);
    if (FAILED(hr) || path[0] == 0) throw std::runtime_error("Cannot resolve LocalAppData");
    return path;
}

static std::string Utf8(const std::wstring& s)
{
    if (s.empty()) return {};
    int n = WideCharToMultiByte(CP_UTF8, 0, s.c_str(), (int)s.size(), nullptr, 0, nullptr, nullptr);
    std::string out((size_t)n, '\0');
    WideCharToMultiByte(CP_UTF8, 0, s.c_str(), (int)s.size(), out.data(), n, nullptr, nullptr);
    return out;
}

static void AppendLog(const std::wstring& msg)
{
    try
    {
        fs::path dir = fs::path(GetLocalAppData()) / L"TachXepTrangPDF" / L"Logs";
        fs::create_directories(dir);
        fs::path file = dir / L"launcher-v2.3.2.log";
        SYSTEMTIME st; GetLocalTime(&st);
        wchar_t stamp[64];
        swprintf_s(stamp, L"%04u-%02u-%02u %02u:%02u:%02u.%03u", st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond, st.wMilliseconds);
        std::ofstream f(file, std::ios::binary | std::ios::app);
        std::string line = Utf8(std::wstring(stamp) + L" " + msg + L"\r\n");
        f.write(line.data(), (std::streamsize)line.size());
    }
    catch (...) {}
}

static std::wstring ReadSmallText(const fs::path& p)
{
    std::ifstream f(p, std::ios::binary);
    if (!f) return L"";
    std::string s((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    return std::wstring(s.begin(), s.end());
}

static void WriteSmallText(const fs::path& p, const std::wstring& text)
{
    std::ofstream f(p, std::ios::binary | std::ios::trunc);
    std::string s(text.begin(), text.end());
    f.write(s.data(), (std::streamsize)s.size());
    f.flush();
    if (!f) throw std::runtime_error("Cannot write sentinel");
}

static void ExtractResourceFile(const PayloadItem& item, const fs::path& root)
{
    HRSRC hrsrc = FindResourceW(nullptr, MAKEINTRESOURCEW(item.id), RT_RCDATA);
    if (!hrsrc) throw std::runtime_error("FindResource failed");
    HGLOBAL hglob = LoadResource(nullptr, hrsrc);
    if (!hglob) throw std::runtime_error("LoadResource failed");
    DWORD size = SizeofResource(nullptr, hrsrc);
    const void* data = LockResource(hglob);
    if (!data && size > 0) throw std::runtime_error("LockResource failed");

    fs::path out = root / fs::path(item.relativePath);
    fs::create_directories(out.parent_path());
    fs::path tmp = out; tmp += L".new";
    {
        std::ofstream f(tmp, std::ios::binary | std::ios::trunc);
        if (!f) throw std::runtime_error("Cannot create payload file");
        if (size) f.write(reinterpret_cast<const char*>(data), size);
        f.flush();
        if (!f) throw std::runtime_error("Cannot write payload file");
    }
    std::error_code ec;
    fs::remove(out, ec);
    ec.clear();
    fs::rename(tmp, out, ec);
    if (ec) throw std::runtime_error("Cannot finalize payload file");
}

static fs::path EnsurePayload()
{
    fs::path root = fs::path(GetLocalAppData()) / L"TachXepTrangPDF" / L"Runtime" / L"v2.3.2";
    fs::path sentinel = root / L".payload.sha256";
    std::wstring existing = ReadSmallText(sentinel);
    if (existing == kPayloadHash)
    {
        AppendLog(L"Payload cache verified: " + root.wstring());
        return root;
    }

    AppendLog(L"Preparing offline payload in " + root.wstring());
    std::error_code ec;
    fs::remove_all(root, ec);
    fs::create_directories(root);
    for (size_t i = 0; i < kPayloadItemCount; ++i)
        ExtractResourceFile(kPayloadItems[i], root);
    WriteSmallText(sentinel, kPayloadHash);
    AppendLog(L"Payload extraction completed. Files=" + std::to_wstring(kPayloadItemCount));
    return root;
}

static std::wstring QuoteArg(const std::wstring& arg)
{
    if (arg.find_first_of(L" \t\n\v\"") == std::wstring::npos) return arg;
    std::wstring out = L"\"";
    size_t slashes = 0;
    for (wchar_t c : arg)
    {
        if (c == L'\\') { ++slashes; continue; }
        if (c == L'\"')
        {
            out.append(slashes * 2 + 1, L'\\'); out.push_back(L'\"'); slashes = 0; continue;
        }
        out.append(slashes, L'\\'); slashes = 0; out.push_back(c);
    }
    out.append(slashes * 2, L'\\'); out.push_back(L'\"');
    return out;
}

static DWORD RunInner(const fs::path& root)
{
    fs::path exe = root / L"Tach_Xep_Trang_PDF_v2.3.2.exe";
    if (!fs::exists(exe)) throw std::runtime_error("Inner executable is missing");

    int argc = 0;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    std::wstring cmd = QuoteArg(exe.wstring());
    if (argv)
    {
        for (int i = 1; i < argc; ++i) { cmd += L" "; cmd += QuoteArg(argv[i]); }
        LocalFree(argv);
    }

    std::vector<wchar_t> buf(cmd.begin(), cmd.end()); buf.push_back(L'\0');
    STARTUPINFOW si{}; si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};
    AppendLog(L"Launching inner application: " + exe.wstring());
    BOOL ok = CreateProcessW(exe.c_str(), buf.data(), nullptr, nullptr, FALSE, 0, nullptr, root.c_str(), &si, &pi);
    if (!ok)
    {
        DWORD e = GetLastError();
        AppendLog(L"CreateProcess failed. Win32=" + std::to_wstring(e));
        throw std::runtime_error("CreateProcess failed");
    }
    CloseHandle(pi.hThread);
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0; GetExitCodeProcess(pi.hProcess, &code); CloseHandle(pi.hProcess);
    AppendLog(L"Inner application exited with code " + std::to_wstring(code));
    return code;
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int)
{
    try
    {
        AppendLog(L"Launcher v2.3.2 start. Offline bootstrap; no network APIs used.");
        fs::path root = EnsurePayload();
        int argc = 0;
        LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
        bool extractOnly = (argv != nullptr && argc >= 2 && std::wstring(argv[1]) == L"--extract-only");
        if (argv) LocalFree(argv);
        if (extractOnly) { AppendLog(L"Extract-only completed successfully."); return 0; }
        return (int)RunInner(root);
    }
    catch (const std::exception& ex)
    {
        std::wstring logPath;
        try { logPath = (fs::path(GetLocalAppData()) / L"TachXepTrangPDF" / L"Logs" / L"launcher-v2.3.2.log").wstring(); } catch (...) { logPath = L"(không xác định)"; }
        std::wstring msg = L"Không thể khởi động Tách & Xếp Trang PDF v2.3.2.\r\n\r\n";
        std::string what = ex.what(); msg.append(what.begin(), what.end());
        msg += L"\r\n\r\nNhật ký: " + logPath;
        AppendLog(L"FATAL: " + msg);
        MessageBoxW(nullptr, msg.c_str(), L"Tách & Xếp Trang PDF v2.3.2", MB_OK | MB_ICONERROR);
        return 60;
    }
    catch (...)
    {
        MessageBoxW(nullptr, L"Không thể khởi động ứng dụng. Hãy kiểm tra launcher-v2.3.2.log trong LocalAppData.", L"Tách & Xếp Trang PDF v2.3.2", MB_OK | MB_ICONERROR);
        return 61;
    }
}
