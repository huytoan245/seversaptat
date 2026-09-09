from pathlib import Path

p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

# Add a bounded Win32 message pump for deterministic UI smoke. Application.DoEvents()
# can remain inside the real application, but a test harness must never get trapped
# draining a continuously replenished queue (thumbnail/prefetch/preview callbacks).
needle='''        [DllImport("user32.dll")]\n        internal static extern IntPtr SetFocus(IntPtr hwnd);\n'''
insert='''        [DllImport("user32.dll")]\n        internal static extern IntPtr SetFocus(IntPtr hwnd);\n\n        [StructLayout(LayoutKind.Sequential)]\n        internal struct SmokeMsg\n        {\n            internal IntPtr hwnd;\n            internal uint message;\n            internal UIntPtr wParam;\n            internal IntPtr lParam;\n            internal uint time;\n            internal Point pt;\n        }\n\n        [DllImport("user32.dll")]\n        [return: MarshalAs(UnmanagedType.Bool)]\n        private static extern bool PeekMessage(out SmokeMsg lpMsg, IntPtr hWnd, uint wMsgFilterMin, uint wMsgFilterMax, uint wRemoveMsg);\n\n        [DllImport("user32.dll")]\n        [return: MarshalAs(UnmanagedType.Bool)]\n        private static extern bool TranslateMessage(ref SmokeMsg lpMsg);\n\n        [DllImport("user32.dll")]\n        private static extern IntPtr DispatchMessage(ref SmokeMsg lpMsg);\n\n        internal static void PumpPendingMessages(int maxMessages)\n        {\n            SmokeMsg msg;\n            int processed=0;\n            while(processed<maxMessages && PeekMessage(out msg,IntPtr.Zero,0,0,1))\n            {\n                // WM_QUIT belongs to the outer application loop; do not consume/dispatch it in smoke.\n                if(msg.message==0x0012) break;\n                TranslateMessage(ref msg);\n                DispatchMessage(ref msg);\n                processed++;\n            }\n        }\n'''
if needle not in s: raise SystemExit('v270 smoke pump NativeMethods marker missing')
s=s.replace(needle,insert,1)

start=s.find('        internal int RunWorkflowSmoke()\n')
end=s.find('        private void CleanupSession()\n',start)
if start<0 or end<0: raise SystemExit('v270 workflow smoke boundary missing')
block=s[start:end]
count=block.count('Application.DoEvents();')
if count<10: raise SystemExit('v270 expected workflow DoEvents markers missing: '+str(count))
block=block.replace('Application.DoEvents();','NativeMethods.PumpPendingMessages(128);')
old='''                    while(!task.IsCompleted && Environment.TickCount64-started<15000){NativeMethods.PumpPendingMessages(128);Thread.Sleep(10);}\n                    if(!task.IsCompleted) throw new TimeoutException("Workflow smoke timeout at "+name+" after 15 seconds.");\n                    task.GetAwaiter().GetResult(); AppDiagnostics.Log("WORKFLOW_SMOKE_V270", name+" PASS");'''
new='''                    while(!task.IsCompleted && Environment.TickCount64-started<15000)\n                    {\n                        NativeMethods.PumpPendingMessages(128);\n                        Thread.Sleep(5);\n                    }\n                    if(!task.IsCompleted) throw new TimeoutException("Workflow smoke timeout at "+name+" after 15 seconds.");\n                    task.GetAwaiter().GetResult();\n                    NativeMethods.PumpPendingMessages(128);\n                    AppDiagnostics.Log("WORKFLOW_SMOKE_V270", name+" PASS");'''
if old not in block: raise SystemExit('v270 bounded wait smoke marker missing')
block=block.replace(old,new,1)
s=s[:start]+block+s[end:]

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_BOUNDED_SMOKE_PUMP_OK doevents_replaced='+str(count))
