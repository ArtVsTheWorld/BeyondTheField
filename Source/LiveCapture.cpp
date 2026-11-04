#include "LiveTables.h"
#include <tlhelp32.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <thread>
int wmain(int argc,wchar_t** argv){
    const bool probe=argc==5&&std::wstring(argv[3])==L"--probe";
    if(argc!=3&&argc!=4&&!probe){std::cerr<<"Usage: LiveCapture.exe PID output.json [--schema | --probe verified-hint.json]\n";return 2;}
    const bool inspect=argc==4;if(inspect&&std::wstring(argv[3])!=L"--schema")return 2;
    const DWORD pid=std::stoul(argv[1]);HANDLE process=OpenProcess(PROCESS_VM_READ|PROCESS_QUERY_LIMITED_INFORMATION,FALSE,pid);if(!process)return 3;
    try{
        wchar_t exe[32768]{};DWORD size=32768;if(!QueryFullProcessImageNameW(process,0,exe,&size)||_wcsicmp(std::filesystem::path(exe).filename().c_str(),L"CollegeFB27.exe"))throw std::runtime_error("Expected CollegeFB27.exe");
        HANDLE snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pid);MODULEENTRY32W entry{};entry.dwSize=sizeof(entry);uintptr_t base=0;
        if(snapshot!=INVALID_HANDLE_VALUE){if(Module32FirstW(snapshot,&entry))base=reinterpret_cast<uintptr_t>(entry.modBaseAddr);CloseHandle(snapshot);}if(!base)throw std::runtime_error("Game module unavailable");
        if(probe){
            std::ifstream hintFile(std::filesystem::path(argv[4]),std::ios::binary);dynasty::live::Json hint;hintFile>>hint;
            dynasty::live::sessionContextHint()={hint.at("career"),hint.at("database"),hint.at("context")};
            dynasty::live::PackedChangeWatch watch;const auto began=GetTickCount64();auto data=dynasty::live::Capture(base,process).run(&watch);
            dynasty::live::Json report={{"status",data.at("status")},{"records",data.at("records").size()},{"captureMs",GetTickCount64()-began},{"retainedBytes",watch.bytes()},{"ranges",watch.rangeCount()},{"samples",dynasty::live::Json::array()}};
            for(int i=0;i<12;++i){const auto start=GetTickCount64();size_t bytes=0,calls=0;const bool same=watch.unchanged([&](uintptr_t at,void* out,size_t n){SIZE_T got=0;++calls;bytes+=n;return ReadProcessMemory(process,reinterpret_cast<void*>(at),out,n,&got)&&got==n;});report["samples"].push_back({{"unchanged",same},{"probeMs",GetTickCount64()-start},{"bytes",bytes},{"calls",calls}});std::this_thread::sleep_for(std::chrono::milliseconds(1000));}
            std::ofstream out(std::filesystem::path(argv[2]),std::ios::binary);out<<report.dump(2);if(!out)throw std::runtime_error("Cannot write probe report");std::cout<<report.dump()<<'\n';CloseHandle(process);return 0;
        }
        dynasty::live::Capture capture(base,process);auto data=inspect?capture.inspectSchemas():capture.run();std::ofstream out(std::filesystem::path(argv[2]),std::ios::binary);out<<data.dump();if(!out)throw std::runtime_error("Cannot write snapshot");std::cout<<"Captured "<<data.at(inspect?"tables":"records").size()<<(inspect?" schema descriptions":" live records")<<", read only\n";CloseHandle(process);return 0;
    }catch(const std::exception& e){CloseHandle(process);std::cerr<<e.what()<<"\n";return 1;}
}
