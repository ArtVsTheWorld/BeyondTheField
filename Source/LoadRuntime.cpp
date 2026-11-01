#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <filesystem>
#include <iostream>
#include <string>

uintptr_t moduleBase(DWORD pid,const std::wstring& filename) {
    HANDLE snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE|TH32CS_SNAPMODULE32,pid);
    if(snapshot==INVALID_HANDLE_VALUE)return 0;
    MODULEENTRY32W entry{};entry.dwSize=sizeof(entry);uintptr_t result=0;
    if(Module32FirstW(snapshot,&entry))do {
        if(_wcsicmp(entry.szModule,filename.c_str())==0){result=reinterpret_cast<uintptr_t>(entry.modBaseAddr);break;}
    }while(Module32NextW(snapshot,&entry));
    CloseHandle(snapshot);return result;
}
int wmain(int argc,wchar_t** argv) {
    if(argc!=3&&argc!=4){std::wcerr<<L"Usage: LoadDynastyEnhancer.exe PID runtime.dll [--stop]\n";return 2;}
    DWORD pid=static_cast<DWORD>(std::stoul(argv[1]));
    auto dll=std::filesystem::absolute(argv[2]);
    if(!std::filesystem::is_regular_file(dll)){std::wcerr<<L"Runtime DLL is missing\n";return 2;}
    HANDLE game=OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION|PROCESS_CREATE_THREAD|PROCESS_VM_OPERATION|PROCESS_VM_WRITE|PROCESS_VM_READ,FALSE,pid);
    if(!game){std::cerr<<"OpenProcess failed: "<<GetLastError()<<"\n";return 3;}
    wchar_t gameName[32768]{};DWORD length=32768;
    if(!QueryFullProcessImageNameW(game,0,gameName,&length)||_wcsicmp(std::filesystem::path(gameName).filename().c_str(),L"CollegeFB27.exe")!=0){CloseHandle(game);return 3;}
    void* remote=nullptr;LPTHREAD_START_ROUTINE function=nullptr;
    if(argc==4) {
        if(std::wstring(argv[3])!=L"--stop"){CloseHandle(game);return 2;}
        uintptr_t base=moduleBase(pid,dll.filename().wstring());
        HMODULE local=LoadLibraryExW(dll.c_str(),nullptr,DONT_RESOLVE_DLL_REFERENCES);
        FARPROC stop=local?GetProcAddress(local,"DynastyEnhancerStop"):nullptr;
        if(!base||!stop){if(local)FreeLibrary(local);CloseHandle(game);return 4;}
        function=reinterpret_cast<LPTHREAD_START_ROUTINE>(base+reinterpret_cast<uintptr_t>(stop)-reinterpret_cast<uintptr_t>(local));
        FreeLibrary(local);
    }else {
        if(moduleBase(pid,dll.filename().wstring())){std::cout<<"Runtime already loaded\n";CloseHandle(game);return 0;}
        FARPROC load=GetProcAddress(GetModuleHandleW(L"kernel32.dll"),"LoadLibraryW");
        MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(reinterpret_cast<void*>(load),&mbi,sizeof(mbi));
        wchar_t owner[32768]{};GetModuleFileNameW(static_cast<HMODULE>(mbi.AllocationBase),owner,32768);
        uintptr_t remoteOwner=moduleBase(pid,std::filesystem::path(owner).filename().wstring());
        if(!remoteOwner){CloseHandle(game);return 4;}
        function=reinterpret_cast<LPTHREAD_START_ROUTINE>(remoteOwner+reinterpret_cast<uintptr_t>(load)-reinterpret_cast<uintptr_t>(mbi.AllocationBase));
        size_t bytes=(dll.wstring().size()+1)*sizeof(wchar_t);
        remote=VirtualAllocEx(game,nullptr,bytes,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
        SIZE_T written=0;
        if(!remote||!WriteProcessMemory(game,remote,dll.c_str(),bytes,&written)||written!=bytes){if(remote)VirtualFreeEx(game,remote,0,MEM_RELEASE);CloseHandle(game);return 5;}
    }
    HANDLE thread=CreateRemoteThread(game,nullptr,0,function,remote,0,nullptr);
    if(!thread){if(remote)VirtualFreeEx(game,remote,0,MEM_RELEASE);CloseHandle(game);std::cerr<<"Runtime load denied: "<<GetLastError()<<"\n";return 6;}
    DWORD wait=WaitForSingleObject(thread,15000);
    if(wait!=WAIT_OBJECT_0){CloseHandle(thread);CloseHandle(game);std::cerr<<"Runtime operation still pending; allocated path retained\n";return 7;}
    DWORD result=0;GetExitCodeThread(thread,&result);CloseHandle(thread);
    if(remote)VirtualFreeEx(game,remote,0,MEM_RELEASE);CloseHandle(game);
    if(argc==4){std::cout<<"Stop result: "<<result<<"\n";return result==0?0:8;}
    bool verified=moduleBase(pid,dll.filename().wstring())!=0;
    std::cout<<(verified?"Loaded; inspect social-media.jsonl for activation":"Native DLL did not load")<<"\n";
    return verified?0:8;
}
