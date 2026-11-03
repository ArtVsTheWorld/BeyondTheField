#include "LiveTables.h"
#include <tlhelp32.h>
#include <filesystem>
#include <fstream>
#include <iostream>
int wmain(int argc,wchar_t** argv){
    if(argc!=3&&argc!=4){std::cerr<<"Usage: LiveCapture.exe PID output.json [--schema]\n";return 2;}
    const bool inspect=argc==4;if(inspect&&std::wstring(argv[3])!=L"--schema")return 2;
    const DWORD pid=std::stoul(argv[1]);HANDLE process=OpenProcess(PROCESS_VM_READ|PROCESS_QUERY_LIMITED_INFORMATION,FALSE,pid);if(!process)return 3;
    try{
        wchar_t exe[32768]{};DWORD size=32768;if(!QueryFullProcessImageNameW(process,0,exe,&size)||_wcsicmp(std::filesystem::path(exe).filename().c_str(),L"CollegeFB27.exe"))throw std::runtime_error("Expected CollegeFB27.exe");
        HANDLE snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pid);MODULEENTRY32W entry{};entry.dwSize=sizeof(entry);uintptr_t base=0;
        if(snapshot!=INVALID_HANDLE_VALUE){if(Module32FirstW(snapshot,&entry))base=reinterpret_cast<uintptr_t>(entry.modBaseAddr);CloseHandle(snapshot);}if(!base)throw std::runtime_error("Game module unavailable");
        dynasty::live::Capture capture(base,process);auto data=inspect?capture.inspectSchemas():capture.run();std::ofstream out(std::filesystem::path(argv[2]),std::ios::binary);out<<data.dump();if(!out)throw std::runtime_error("Cannot write snapshot");std::cout<<"Captured "<<data.at(inspect?"tables":"records").size()<<(inspect?" schema descriptions":" live records")<<", read only\n";CloseHandle(process);return 0;
    }catch(const std::exception& e){CloseHandle(process);std::cerr<<e.what()<<"\n";return 1;}
}
