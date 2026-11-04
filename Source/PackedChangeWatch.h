#pragma once
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <map>
#include <stdexcept>
#include <vector>

namespace dynasty::live {
// Records only bytes actually consumed by a successful capture. Overlapping
// reads must agree. Probe reads can coalesce holes within the same memory page,
// but never compare those unconsumed bytes (e.g. unrelated UI timers).
class PackedChangeWatch {
    struct Range {uintptr_t address;std::vector<unsigned char> bytes;};
    std::map<uintptr_t,std::vector<unsigned char>> ranges;
    size_t retained=0;bool usable=true;
public:
    static constexpr size_t maximumBytes=128u*1024*1024,chunkBytes=1024*1024;
    bool available()const{return usable&&!ranges.empty();}
    size_t bytes()const{return retained;}
    size_t rangeCount()const{return ranges.size();}
    void record(uintptr_t address,const std::vector<unsigned char>& bytes){
        if(!usable||bytes.empty())return;
        if(address+bytes.size()<address)throw std::runtime_error("Capture observation address overflow");
        auto end=address+bytes.size(),cursor=address;
        auto it=ranges.upper_bound(address);if(it!=ranges.begin())--it;
        while(it!=ranges.end()&&it->first+it->second.size()<=cursor)++it;
        while(cursor<end){
            if(it==ranges.end()||it->first>cursor){
                const auto high=it==ranges.end()?end:(std::min)(end,it->first);
                const auto count=high-cursor;
                if(count>maximumBytes-retained){ranges.clear();retained=0;usable=false;return;}
                ranges.emplace(cursor,std::vector<unsigned char>(bytes.begin()+(cursor-address),bytes.begin()+(high-address)));retained+=count;cursor=high;
            }else{
                const auto high=(std::min)(end,it->first+it->second.size());
                if(memcmp(bytes.data()+(cursor-address),it->second.data()+(cursor-it->first),high-cursor))throw std::runtime_error("Dynasty changed during observed reads; retry");
                cursor=high;++it;
            }
        }
    }
    // An unreadable, cancelled, moved or changed span is never "unchanged".
    // Read takes (address, buffer, size), and owns its own time/read budget.
    template<class Read>bool unchanged(Read read)const{
        if(!available())return false;
        std::vector<unsigned char> buffer(chunkBytes);
        auto it=ranges.begin();
        while(it!=ranges.end()){
            const auto first=it;uintptr_t low=it->first,high=low+it->second.size();++it;
            while(it!=ranges.end()&&it->first<=((high-1)|uintptr_t(0xfff))&&it->first+it->second.size()-low<=chunkBytes){high=(std::max)(high,it->first+it->second.size());++it;}
            for(auto at=low;at<high;){
                const auto count=static_cast<size_t>((std::min)(uintptr_t(chunkBytes),high-at));
                if(!read(at,buffer.data(),count))return false;
                for(auto range=first;range!=it;++range){
                    const auto a=(std::max)(at,range->first),b=(std::min)(at+count,range->first+range->second.size());
                    if(a<b&&memcmp(buffer.data()+(a-at),range->second.data()+(a-range->first),b-a))return false;
                }
                at+=count;
            }
        }
        return true;
    }
};
}
