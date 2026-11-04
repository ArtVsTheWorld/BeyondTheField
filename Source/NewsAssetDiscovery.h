#pragma once
#include "NewsDropdowns.h"
#include <array>
namespace social::assets {
template<class Read>bool apt(uintptr_t address,Read read){std::array<char,14> bytes{};return address>=0x10000&&read(address,bytes.data(),bytes.size())&&(!memcmp(bytes.data(),"Apt Data:1:7:8",14)||!memcmp(bytes.data(),"Apt Data:1:8:8",14));}
template<class Read>bool matches(uintptr_t at,const std::vector<unsigned char>& expected,Read read){std::vector<unsigned char> bytes(expected.size());return read(at,bytes.data(),bytes.size())&&bytes==expected;}
template<class Read>uintptr_t screen(uintptr_t body,unsigned size,const std::vector<dropdown::Patch>& patches,Read read){
 if(size!=726||body<0x10000+0x8a0)return 0;const auto assetBase=body-0x8a0;
 if(!apt(assetBase,read)||(!matches(body,patches[0].original,read)&&!matches(body,patches[0].changed,read)))return 0;
 unsigned poolSize=0;uintptr_t pool=0;
 return read(body-16,&poolSize,4)&&poolSize==180&&read(body-8,&pool,8)&&pool>=assetBase&&pool<assetBase+7321?assetBase:0;
}
template<class Read>uintptr_t model(uintptr_t body,unsigned size,const std::vector<dropdown::Patch>& patches,Read read){
 if(size!=91||body<0x10000+0x24970)return 0;const auto assetBase=body-0x24970;
 if(!apt(assetBase,read))return 0;unsigned poolSize=0;uintptr_t pool=0;
 if(!read(body-16,&poolSize,4)||poolSize!=41||!read(body-8,&pool,8)||pool<assetBase||pool>=assetBase+0x1000000)return 0;
 for(const auto& p:patches)if(p.model&&!matches(assetBase+p.offset,p.original,read)&&!matches(assetBase+p.offset,p.changed,read))return 0;
 return assetBase;
}
}
