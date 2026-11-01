#pragma once
#include <array>
namespace social {
// Library/asset pairs verified in the installed native image reference tables.
// These are illustrative sample avatars, not live Dynasty player bindings.
struct Post { const char* author; const char* handle; const char* body; int imageLibrary; int imageValue; };
inline constexpr std::array<Post,3> samplePosts{{
    {"Campus Football Wire", "@CampusFBWire", "A new week. A new chance to make a statement. Who is ready for Saturday? #CollegeFootball",79,598},
    {"QB Room", "@QBRoom12", "Extra reps after practice. Staying ready for my opportunity. #KeepWorking",1,1},
    {"Saturday Spotlight", "@SatSpotlight", "Rankings bring the attention. Rivalries bring the noise. This weekend cannot get here soon enough.",0,76}
}};
}
