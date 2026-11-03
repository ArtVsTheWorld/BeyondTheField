#pragma once
#include "HubTab.h"
#include <string_view>
namespace social::embedded {
inline constexpr char panelId[]="CM_DYNASTY_SOCIAL";
inline constexpr char childId[]="CM_DYNASTY_SOCIAL_FEED";
inline constexpr char donorId[]="CM_ACTIONHOME";
inline constexpr char screenKey[]="screen_news";
inline constexpr char linkage[]="panelmenu.component.subscreenpanel.SubScreenPanel";
struct Plan {size_t donor=0,position=0;double priority=0;};
inline std::optional<Plan> plan(const std::vector<nlohmann::json>& rows){
    std::optional<size_t> donor,stats;
    std::set<std::string> ids;
    for(size_t i=0;i<rows.size();++i){const auto key=rows[i].value("id",std::string());if(key.empty()||!ids.insert(key).second||key==panelId)return {};
        if(key==donorId)donor=i;if(key=="CM_LEAGUE")stats=i;
    }
    if(!donor||!stats||!ids.count("DynastyCentral")||rows[*donor].value("linkage",std::string())!=linkage)return {};
    const auto& target=rows[*stats];if(!target.contains("priority")||!target["priority"].is_number())return {};
    const double high=target["priority"].get<double>();if(!std::isfinite(high))return {};
    double low=high-1;for(const auto& row:rows)if(row.contains("priority")&&row["priority"].is_number()){const double p=row["priority"].get<double>();if(std::isfinite(p)&&p<high&&p>low)low=p;}
    return Plan{*donor,*stats,(low+high)/2};
}
inline bool stockPanel(std::string_view id){return id=="CM_ACTIONHOME"||id=="CM_CAREER"||id=="cm_coach"||id=="cm_team"||id=="CM_NEWSTAB"||id=="CM_LEAGUE"||id=="DynastyCentral";}
}
