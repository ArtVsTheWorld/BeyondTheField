#pragma once
#include <array>
#include <atomic>
#include <cstdint>

namespace recruitingfog::playerperf {
#if defined(PLAYER_FOG_PERF)
// Development-only, bounded UI callback sampling. No game/process discovery,
// file writes, allocation or log formatting occurs in a sampled callback.
struct Counter {
    std::atomic<unsigned> attempts{0},samples{0};
    std::atomic<uint64_t> ticks{0},maximum{0};
    std::array<std::atomic<unsigned>,8> buckets{};
};
inline Counter rows,nativeRows,scriptAdapters,columns;
inline uint64_t frequency(){static const uint64_t value=[](){LARGE_INTEGER f{};QueryPerformanceFrequency(&f);return uint64_t(f.QuadPart);}();return value;}
inline uint64_t now(){LARGE_INTEGER t{};QueryPerformanceCounter(&t);return uint64_t(t.QuadPart);}
struct Sample {
    Counter& counter;uint64_t started=0;
    explicit Sample(Counter& selected):counter(selected){if(counter.attempts.fetch_add(1,std::memory_order_relaxed)<8192)started=now();}
    ~Sample(){if(!started)return;const auto elapsed=now()-started;counter.samples.fetch_add(1,std::memory_order_relaxed);counter.ticks.fetch_add(elapsed,std::memory_order_relaxed);
        auto old=counter.maximum.load(std::memory_order_relaxed);while(elapsed>old&&!counter.maximum.compare_exchange_weak(old,elapsed,std::memory_order_relaxed)){}
        const auto us=double(elapsed)*1000000./frequency();unsigned bucket=0;for(const auto boundary:{1.,5.,10.,50.,100.,500.,1000.}){if(us<boundary)break;++bucket;}counter.buckets[bucket].fetch_add(1,std::memory_order_relaxed);
    }
};
template<class Json>Json report(const Counter& counter){Json buckets=Json::array();for(const auto& bucket:counter.buckets)buckets.push_back(bucket.load());const auto n=counter.samples.load();
    return {{"samples",n},{"totalUs",double(counter.ticks.load())*1000000./frequency()},{"meanUs",n?double(counter.ticks.load())*1000000./frequency()/n:0.},{"maximumUs",double(counter.maximum.load())*1000000./frequency()},{"bucketsLtUs",{1,5,10,50,100,500,1000}},{"bucketCounts",buckets}};
}
#else
struct Counter{};inline Counter rows,nativeRows,scriptAdapters,columns;
struct Sample {explicit Sample(Counter&) {}};
#endif
}
