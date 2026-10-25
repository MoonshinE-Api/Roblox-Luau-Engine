"""Optional process deadline. A Windows Job owns the VM and its subprocesses.

This is lifecycle containment, not a security sandbox. The worker waits until
job assignment succeeds; no scripts or compilers run before that gate opens.
"""
import ctypes as C
from ctypes import wintypes as W
import multiprocessing as mp
import os
import sys
import tempfile
import time


class BasicLimits(C.Structure):
    _fields_=[('process_time',C.c_int64),('job_time',C.c_int64),('flags',W.DWORD),
        ('min_working_set',C.c_size_t),('max_working_set',C.c_size_t),
        ('active_processes',W.DWORD),('affinity',C.c_size_t),('priority',W.DWORD),('scheduling',W.DWORD)]


class IoCounters(C.Structure):
    _fields_=[(name,C.c_uint64) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]


class ExtendedLimits(C.Structure):
    _fields_=[('basic',BasicLimits),('io',IoCounters),('process_memory',C.c_size_t),
        ('job_memory',C.c_size_t),('peak_process_memory',C.c_size_t),('peak_job_memory',C.c_size_t)]


class Accounting(C.Structure):
    _fields_=[(name,C.c_int64) for name in ('user','kernel','period_user','period_kernel')]+[
        (name,W.DWORD) for name in ('page_faults','processes','active','terminated')]


class WindowsJob:
    def __init__(self):
        self.handle=None
        self.api=C.WinDLL('kernel32',use_last_error=True)
        self.api.CreateJobObjectW.argtypes=[C.c_void_p,W.LPCWSTR];self.api.CreateJobObjectW.restype=W.HANDLE
        self.api.SetInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD];self.api.SetInformationJobObject.restype=W.BOOL
        self.api.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE];self.api.AssignProcessToJobObject.restype=W.BOOL
        self.api.CloseHandle.argtypes=[W.HANDLE];self.api.CloseHandle.restype=W.BOOL
        self.api.TerminateJobObject.argtypes=[W.HANDLE,W.UINT];self.api.TerminateJobObject.restype=W.BOOL
        self.api.QueryInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.c_void_p];self.api.QueryInformationJobObject.restype=W.BOOL
        self.handle=self.api.CreateJobObjectW(None,None)
        if not self.handle:raise C.WinError(C.get_last_error())
        limits=ExtendedLimits();limits.basic.flags=0x2000 # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle,9,C.byref(limits),C.sizeof(limits)):
            error=C.get_last_error();self.close();raise C.WinError(error)

    def assign(self,process):
        if not self.api.AssignProcessToJobObject(self.handle,process.sentinel):raise C.WinError(C.get_last_error())

    def close(self):
        if self.handle:
            handle,self.handle=self.handle,None
            try:
                if not self.api.TerminateJobObject(handle,1):raise C.WinError(C.get_last_error())
                deadline=time.monotonic()+5
                while True:
                    info=Accounting()
                    if not self.api.QueryInformationJobObject(handle,1,C.byref(info),C.sizeof(info),None):raise C.WinError(C.get_last_error())
                    if info.active==0:break
                    if time.monotonic()>=deadline:raise OSError('Worker process tree did not terminate')
                    time.sleep(.01)
            finally:
                if not self.api.CloseHandle(handle):raise C.WinError(C.get_last_error())


def worker_arguments(arguments):
    result=[];index=0
    while index<len(arguments):
        value=arguments[index]
        if value=='--':result.extend(arguments[index:]);break
        elif value=='--wall-timeout':index+=2
        elif value.startswith('--wall-timeout='):index+=1
        else:result.append(value);index+=1
    return result


def _worker(arguments,ready,temporary_root):
    import signal
    # Only the supervising process handles console Ctrl+C. Its job owns this
    # worker and any compiler/decoder children, including during native calls.
    signal.signal(signal.SIGINT,signal.SIG_IGN)
    # The parent owns temporary files even when the VM is forcibly stopped.
    tempfile.tempdir=temporary_root
    if not ready.wait(15):raise SystemExit(125)
    from run import main,ScriptFailure
    try:main(arguments,supervised=True)
    except ScriptFailure as error:
        print(f'Execution failed: {error}',file=sys.stderr,flush=True)
        raise SystemExit(1) from None


def supervise(arguments,seconds):
    if os.name!='nt':raise OSError('The process deadline currently requires Windows')
    context=mp.get_context('spawn');ready=context.Event()
    deadline=None if seconds is None else time.monotonic()+seconds
    job=WindowsJob();process=None
    try:
        with tempfile.TemporaryDirectory(prefix='recovery-worker-') as directory:
            try:
                process=context.Process(target=_worker,args=(worker_arguments(arguments),ready,directory))
                process.start();job.assign(process);ready.set()
                while process.is_alive():
                    remaining=None if deadline is None else deadline-time.monotonic()
                    if remaining is not None and remaining<=0:
                        print(f'Execution stopped: wall-time limit of {seconds:g} seconds exceeded.',file=sys.stderr,flush=True)
                        return 124
                    process.join(.1 if remaining is None else min(.1,remaining))
                return process.exitcode
            finally:
                # Close the job before touching worker files. This also stops
                # any compiler/asset decoder surviving a failed VM process.
                try:job.close()
                finally:
                    if process is not None and process.pid is not None:
                        if process.is_alive():process.kill()
                        process.join(10)
                        if process.is_alive():raise OSError('VM worker did not terminate')
                        process.close()
    finally:job.close()
