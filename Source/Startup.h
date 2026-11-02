#pragma once
#include <functional>
#include <string>
namespace social {
// Empty reason means ready. Transient title/loading states do not consume the
// only load attempt. Verified menu hooks may already be present; asset-dependent
// presentation and Social Media entry remain gated until this probe succeeds.
inline bool awaitStartup(const std::function<bool()>& cancelled,const std::function<std::string()>& probe,const std::function<void(const std::string&)>& report,const std::function<void()>& pause){
    std::string previous;
    while(!cancelled()){
        const auto reason=probe();if(reason.empty())return !cancelled();
        if(reason!=previous){report(reason);previous=reason;}pause();
    }
    return false;
}
}
