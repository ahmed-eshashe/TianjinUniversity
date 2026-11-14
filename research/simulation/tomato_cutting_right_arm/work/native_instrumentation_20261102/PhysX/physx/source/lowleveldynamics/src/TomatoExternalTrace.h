// SPDX-License-Identifier: Apache-2.0
// Experimental observation only. Deferred impulse state is NOT physical velocity or certified motor work.
#ifndef TOMATO_EXTERNAL_TRACE_H
#define TOMATO_EXTERNAL_TRACE_H
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <mutex>
#include <new>
namespace tomato_external {
struct Row {
    std::uint64_t pass;
    std::uintptr_t articulation;
    unsigned link, dof, flags;
    double dt, stepDt, elapsed, impulse, before, after, response;
};
class Recorder {
    static const unsigned capacity = 262144;
    Row* rows;
    FILE* file;
    unsigned count;
    std::uint64_t dropped, passes;
    std::mutex lock;
public:
    Recorder(): rows(nullptr), file(nullptr), count(0), dropped(0), passes(0) {
        const char* path = std::getenv("TOMATO_NATIVE_EXTERNAL_TRACE");
        if (!path || path[0] != '/') return;
        file = std::fopen(path, "wx"); // never overwrite evidence
        if (!file) return;
        rows = new(std::nothrow) Row[capacity];
        if (!rows) { std::fputs("ERROR allocation_failed\n", file); std::fclose(file); file=nullptr; }
    }
    std::uint64_t begin() {
        if (!rows) return 0;
        std::lock_guard<std::mutex> guard(lock);
        return ++passes;
    }
    std::uint64_t snapshot() { std::lock_guard<std::mutex> guard(lock); return passes; }
    void append(const Row& row) {
        if (!rows) return;
        std::lock_guard<std::mutex> guard(lock);
        if (count == capacity) { ++dropped; return; }
        rows[count++] = row;
    }
    ~Recorder() {
        if (!file) return;
        std::fputs("TOMATO_EXTERNAL_IMPULSE_TRACE_V1\nevent,articulation,link,dof,flags,dt,step_dt,reserved,actuation_impulse,deferred_before,deferred_after,combined_increment\n",file);
        for (unsigned i=0;i<count;++i) {
            const Row& r=rows[i];
            std::fprintf(file,"%llu,%llu,%u,%u,%u,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
                static_cast<unsigned long long>(r.pass),static_cast<unsigned long long>(r.articulation),r.link,r.dof,r.flags,
                r.dt,r.stepDt,r.elapsed,r.impulse,r.before,r.after,r.response);
        }
        std::fprintf(file,"END count=%u dropped=%llu passes=%llu\n",count,
            static_cast<unsigned long long>(dropped),static_cast<unsigned long long>(passes));
        std::fclose(file);
        delete[] rows;
    }
};
inline Recorder& recorder() { static Recorder r; return r; }
}
#endif
