// Own runner boundary. Never modifies or injects code into the supplier program.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

public sealed class HtkkWindowsJobProcess : IDisposable {
    private IntPtr job = IntPtr.Zero, process = IntPtr.Zero;
    private Process rootProcess;
    private bool assigned, disposed;
    public bool CleanupVerified { get; private set; }
    public uint ProcessId { get; private set; }
    // Borrowed diagnostic object. Its handle/identity is pinned BEFORE resume,
    // never reconstructed from a PID after the supplier starts executing.
    public Process RootProcess { get { RequireLive(); return rootProcess; } }

    public static HtkkWindowsJobProcess Launch(string executable, string directory, string[] arguments, bool noWindow, bool x86) {
        return LaunchCore(executable, directory, arguments, noWindow, x86, IntPtr.Zero);
    }

    // A private invalid-handle override lets the integration test exercise an
    // ACTUAL AssignProcessToJobObject rejection before the child can execute.
    private static HtkkWindowsJobProcess LaunchCore(string executable, string directory, string[] arguments, bool noWindow, bool x86, IntPtr assignmentOverride) {
        HtkkWindowsJobProcess owner = new HtkkWindowsJobProcess();
        IntPtr environment = IntPtr.Zero, thread = IntPtr.Zero, nullStream = IntPtr.Zero, attributeList = IntPtr.Zero, handleList = IntPtr.Zero;
        bool attributesInitialized = false;
        try {
            if (String.IsNullOrEmpty(executable) || !System.IO.Path.IsPathRooted(executable) || String.IsNullOrEmpty(directory) || !System.IO.Path.IsPathRooted(directory)) throw Failure("launch-arguments-invalid");
            owner.job = CreateJobObject(IntPtr.Zero, null);
            if (owner.job == IntPtr.Zero) throw Failure("job-create-failed");
            JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
            limits.BasicLimitInformation.LimitFlags = 0x2000; // KILL_ON_JOB_CLOSE; no BREAKAWAY flags.
            if (!SetInformationJobObject(owner.job, 9, ref limits, (uint)Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION)))) throw Failure("job-limit-failed");
            environment = Marshal.StringToHGlobalUni(OsEnvironment(x86));
            // A real NUL stream keeps Console.WriteLine/compilers usable. The
            // explicit handle allowlist prevents ANY ambient handle inheritance.
            SECURITY_ATTRIBUTES security = new SECURITY_ATTRIBUTES(); security.nLength = Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES)); security.bInheritHandle = true;
            nullStream = CreateFile(@"\\.\NUL", 0xC0000000, 3, ref security, 3, 0x80, IntPtr.Zero);
            if (nullStream == new IntPtr(-1)) { nullStream = IntPtr.Zero; throw Failure("stdio-create-failed"); }
            IntPtr attributeBytes = IntPtr.Zero;
            InitializeProcThreadAttributeList(IntPtr.Zero, 1, 0, ref attributeBytes);
            if (attributeBytes == IntPtr.Zero) throw Failure("handle-list-failed");
            attributeList = Marshal.AllocHGlobal(attributeBytes);
            if (!InitializeProcThreadAttributeList(attributeList, 1, 0, ref attributeBytes)) throw Failure("handle-list-failed");
            attributesInitialized = true;
            handleList = Marshal.AllocHGlobal(IntPtr.Size); Marshal.WriteIntPtr(handleList, nullStream);
            if (!UpdateProcThreadAttribute(attributeList, 0, new IntPtr(0x20002), handleList, new IntPtr(IntPtr.Size), IntPtr.Zero, IntPtr.Zero)) throw Failure("handle-list-failed");
            STARTUPINFOEX startup = new STARTUPINFOEX(); startup.StartupInfo.cb = (uint)Marshal.SizeOf(typeof(STARTUPINFOEX));
            startup.StartupInfo.dwFlags = 0x100;
            startup.StartupInfo.hStdInput = startup.StartupInfo.hStdOutput = startup.StartupInfo.hStdError = nullStream;
            startup.lpAttributeList = attributeList;
            PROCESS_INFORMATION child;
            uint flags = 0x4 | 0x400 | 0x80000 | (noWindow ? 0x08000000u : 0u); // SUSPENDED + UNICODE_ENVIRONMENT + EXTENDED_STARTUPINFO.
            StringBuilder command = new StringBuilder(QuoteArgument(executable));
            if (arguments != null) foreach (string argument in arguments) command.Append(" ").Append(QuoteArgument(argument));
            if (!CreateProcess(executable, command, IntPtr.Zero, IntPtr.Zero, true, flags, environment, directory, ref startup, out child)) throw Failure("process-create-failed");
            owner.process = child.hProcess; thread = child.hThread; owner.ProcessId = child.dwProcessId;
            IntPtr target = assignmentOverride == IntPtr.Zero ? owner.job : assignmentOverride;
            if (!AssignProcessToJobObject(target, owner.process)) throw Failure("job-assignment-failed");
            owner.assigned = true;
            owner.rootProcess = Process.GetProcessById(checked((int)child.dwProcessId));
            IntPtr diagnosticHandle = owner.rootProcess.Handle;
            long nativeCreation, diagnosticCreation, exit, kernel, user;
            if (!GetProcessTimes(owner.process, out nativeCreation, out exit, out kernel, out user) || !GetProcessTimes(diagnosticHandle, out diagnosticCreation, out exit, out kernel, out user) || nativeCreation != diagnosticCreation || WaitForSingleObject(owner.process, 0) != 0x102) throw Failure("process-identity-failed");
            if (ResumeThread(thread) == UInt32.MaxValue) throw Failure("process-resume-failed");
            return owner;
        } catch (Exception error) {
            bool stopped = owner.Stop(5000);
            owner.CloseHandles();
            if (!stopped) throw Failure("job-cleanup-not-verified");
            string category = error.Message;
            if (!(error is InvalidOperationException) || Array.IndexOf(new string[] { "launch-arguments-invalid", "job-create-failed", "job-limit-failed", "environment-invalid", "stdio-create-failed", "handle-list-failed", "process-create-failed", "job-assignment-failed", "process-identity-failed", "process-resume-failed" }, category) < 0) category = "boundary-tool-failure";
            throw Failure(category);
        } finally {
            if (thread != IntPtr.Zero) CloseHandle(thread);
            if (nullStream != IntPtr.Zero) CloseHandle(nullStream);
            if (attributesInitialized) DeleteProcThreadAttributeList(attributeList);
            if (handleList != IntPtr.Zero) Marshal.FreeHGlobal(handleList);
            if (attributeList != IntPtr.Zero) Marshal.FreeHGlobal(attributeList);
            if (environment != IntPtr.Zero) Marshal.FreeHGlobal(environment);
        }
    }

    public bool WaitForRootExit(int milliseconds) {
        RequireLive(); CheckDeadline(milliseconds);
        uint result = WaitForSingleObject(process, (uint)milliseconds);
        if (result == 0) return true;
        if (result == 0x102) return false;
        throw Failure("process-wait-failed");
    }
    public uint RootExitCode {
        get {
            RequireLive();
            if (WaitForSingleObject(process, 0) != 0) throw Failure("process-not-exited");
            uint code; if (!GetExitCodeProcess(process, out code)) throw Failure("process-exit-code-failed");
            return code;
        }
    }
    public uint ActiveProcesses {
        get {
            RequireLive();
            JOBOBJECT_BASIC_ACCOUNTING_INFORMATION accounting;
            if (!QueryInformationJobObject(job, 1, out accounting, (uint)Marshal.SizeOf(typeof(JOBOBJECT_BASIC_ACCOUNTING_INFORMATION)), IntPtr.Zero)) throw Failure("job-query-failed");
            return accounting.ActiveProcesses;
        }
    }
    // Terminates ALL members, including children reparented after root exit.
    // Returns false on any unverified termination/query; caller must block tokens.
    public bool Stop(int milliseconds) {
        CheckDeadline(milliseconds);
        if (disposed) return CleanupVerified;
        CleanupVerified = false;
        try {
            // An unassigned root is suspended OUTSIDE this empty job. Always
            // terminate it independently; terminating an empty job is unnecessary
            // and must never short-circuit cleanup of that root.
            bool terminationVerified = true;
            if (assigned && job != IntPtr.Zero && !TerminateJobObject(job, 1)) terminationVerified = false;
            if (process != IntPtr.Zero && (!assigned || !terminationVerified)) {
                uint rootState = WaitForSingleObject(process, 0);
                if (rootState == 0xFFFFFFFF) terminationVerified = false;
                else if (rootState != 0 && !TerminateProcess(process, 1) && WaitForSingleObject(process, 0) != 0) terminationVerified = false;
            }
            Stopwatch clock = Stopwatch.StartNew();
            do {
                uint rootState = process == IntPtr.Zero ? 0 : WaitForSingleObject(process, 0);
                if (rootState == 0xFFFFFFFF) return false; // WAIT_FAILED is never an exit proof.
                bool rootStopped = rootState == 0;
                uint active = 0;
                if (job != IntPtr.Zero) {
                    JOBOBJECT_BASIC_ACCOUNTING_INFORMATION accounting;
                    if (!QueryInformationJobObject(job, 1, out accounting, (uint)Marshal.SizeOf(typeof(JOBOBJECT_BASIC_ACCOUNTING_INFORMATION)), IntPtr.Zero)) return false;
                    active = accounting.ActiveProcesses;
                }
                if (rootStopped && active == 0) { CleanupVerified = terminationVerified; return CleanupVerified; }
                if (clock.ElapsedMilliseconds >= milliseconds) return false;
                Thread.Sleep((int)Math.Min(10, Math.Max(1, milliseconds - clock.ElapsedMilliseconds)));
            } while (true);
        } catch { return false; }
    }
    public void Dispose() {
        if (disposed) return;
        bool stopped = Stop(5000); CloseHandles();
        if (!stopped) throw Failure("job-cleanup-not-verified");
    }
    ~HtkkWindowsJobProcess() { CloseHandles(); }
    private void CloseHandles() {
        if (rootProcess != null) { try { rootProcess.Dispose(); } catch { } finally { rootProcess = null; } }
        if (process != IntPtr.Zero) { CloseHandle(process); process = IntPtr.Zero; }
        if (job != IntPtr.Zero) { CloseHandle(job); job = IntPtr.Zero; }
        disposed = true;
    }
    private void RequireLive() { if (disposed || process == IntPtr.Zero || job == IntPtr.Zero) throw Failure("job-not-live"); }
    private static void CheckDeadline(int value) { if (value < 0 || value > 300000) throw Failure("deadline-invalid"); }
    private static InvalidOperationException Failure(string category) { return new InvalidOperationException(category); }
    private static string OsEnvironment(bool x86) {
        SortedDictionary<string,string> values = new SortedDictionary<string,string>(StringComparer.OrdinalIgnoreCase);
        foreach (string key in new string[] { "SystemRoot", "WINDIR", "SystemDrive", "TEMP", "TMP", "PATH", "APPDATA", "LOCALAPPDATA", "USERPROFILE", "ProgramData", "COMSPEC", "PROCESSOR_ARCHITECTURE", "PROCESSOR_ARCHITEW6432", "NUMBER_OF_PROCESSORS" }) {
            string value = Environment.GetEnvironmentVariable(key);
            if (value != null) { if (value.IndexOf('\0') >= 0) throw Failure("environment-invalid"); values[key] = value; }
        }
        if (x86) {
            string native = Environment.GetEnvironmentVariable("PROCESSOR_ARCHITECTURE");
            values["PROCESSOR_ARCHITECTURE"] = "x86";
            if (Environment.Is64BitOperatingSystem && !String.IsNullOrEmpty(native)) values["PROCESSOR_ARCHITEW6432"] = native;
        }
        StringBuilder block = new StringBuilder();
        foreach (KeyValuePair<string,string> value in values) block.Append(value.Key).Append('=').Append(value.Value).Append('\0');
        // Explicit two NULs also when no inherited OS variables are present.
        if (block.Length == 0) block.Append('\0');
        return block.Append('\0').ToString();
    }
    public static string QuoteArgument(string value) {
        if (value == null || value.IndexOf('\0') >= 0) throw Failure("launch-arguments-invalid");
        StringBuilder output = new StringBuilder("\""); int slashes = 0;
        foreach (char character in value) {
            if (character == '\\') { slashes++; continue; }
            if (character == '"') { output.Append('\\', slashes * 2 + 1).Append('"'); slashes = 0; continue; }
            output.Append('\\', slashes).Append(character); slashes = 0;
        }
        return output.Append('\\', slashes * 2).Append('"').ToString();
    }

    [StructLayout(LayoutKind.Sequential)] private struct STARTUPINFO {
        public uint cb; public IntPtr lpReserved, lpDesktop, lpTitle;
        public uint dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public ushort wShowWindow, cbReserved2; public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }
    [StructLayout(LayoutKind.Sequential)] private struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public uint dwProcessId, dwThreadId; }
    [StructLayout(LayoutKind.Sequential)] private struct STARTUPINFOEX { public STARTUPINFO StartupInfo; public IntPtr lpAttributeList; }
    [StructLayout(LayoutKind.Sequential)] private struct SECURITY_ATTRIBUTES { public int nLength; public IntPtr lpSecurityDescriptor; [MarshalAs(UnmanagedType.Bool)] public bool bInheritHandle; }
    [StructLayout(LayoutKind.Sequential)] private struct JOBOBJECT_BASIC_LIMIT_INFORMATION {
        public long PerProcessUserTimeLimit, PerJobUserTimeLimit; public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize, MaximumWorkingSetSize; public uint ActiveProcessLimit;
        public UIntPtr Affinity; public uint PriorityClass, SchedulingClass;
    }
    [StructLayout(LayoutKind.Sequential)] private struct IO_COUNTERS { public ulong ReadOperationCount, WriteOperationCount, OtherOperationCount, ReadTransferCount, WriteTransferCount, OtherTransferCount; }
    [StructLayout(LayoutKind.Sequential)] private struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION {
        public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation; public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemoryUsed, PeakJobMemoryUsed;
    }
    [StructLayout(LayoutKind.Sequential)] private struct JOBOBJECT_BASIC_ACCOUNTING_INFORMATION {
        public long TotalUserTime, TotalKernelTime, ThisPeriodTotalUserTime, ThisPeriodTotalKernelTime;
        public uint TotalPageFaultCount, TotalProcesses, ActiveProcesses, TotalTerminatedProcesses;
    }
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern IntPtr CreateJobObject(IntPtr attributes, string name);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetInformationJobObject(IntPtr job, int informationClass, ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION information, uint length);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool QueryInformationJobObject(IntPtr job, int informationClass, out JOBOBJECT_BASIC_ACCOUNTING_INFORMATION information, uint length, IntPtr returnedLength);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool TerminateJobObject(IntPtr job, uint exitCode);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool TerminateProcess(IntPtr process, uint exitCode);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern bool CreateProcess(string application, StringBuilder command, IntPtr processAttributes, IntPtr threadAttributes, bool inheritHandles, uint flags, IntPtr environment, string directory, ref STARTUPINFOEX startup, out PROCESS_INFORMATION process);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern IntPtr CreateFile(string name, uint access, uint share, ref SECURITY_ATTRIBUTES security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool InitializeProcThreadAttributeList(IntPtr list, int count, uint flags, ref IntPtr size);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool UpdateProcThreadAttribute(IntPtr list, uint flags, IntPtr attribute, IntPtr value, IntPtr length, IntPtr previous, IntPtr returned);
    [DllImport("kernel32.dll")] private static extern void DeleteProcThreadAttributeList(IntPtr list);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern uint ResumeThread(IntPtr thread);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern uint WaitForSingleObject(IntPtr handle, uint milliseconds);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetExitCodeProcess(IntPtr process, out uint exitCode);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetProcessTimes(IntPtr process, out long creation, out long exit, out long kernel, out long user);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool CloseHandle(IntPtr handle);
}
