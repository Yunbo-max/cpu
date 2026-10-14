// Diagnostic-only observer: const public getters, no adjacency/state mutation.
#include <fstream>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <algorithm>
namespace cartesian_abstractions {
static void r008_snapshot(const Abstraction &a, const ShortestPaths *sp,
                          const std::vector<int> &costs, const char *kind,
                          int parent=-1, int child1=-1, int child2=-1, int var=-1,
                          const std::vector<int> &modified={}) {
    const char *path=std::getenv("RSI_SPLIT_WITNESS_PATH");
    if (!path || !*path) return;
    const bool initial=std::string(kind)=="initial";
    if (initial) { std::ifstream old(path); if(old.good()) throw std::runtime_error("Witness exists"); }
    std::ofstream f(path, initial ? std::ios::out : std::ios::out|std::ios::app);
    if(!f) throw std::runtime_error("Witness open failed");
    const auto &ts=a.get_transition_system();
    const auto &out=ts.get_outgoing_transitions();
    const auto &in=ts.get_incoming_transitions();
    const auto &loops=ts.get_loops();
    const int n=a.get_num_states();
    if(static_cast<int>(out.size())!=n || static_cast<int>(in.size())!=n || static_cast<int>(loops.size())!=n)
        throw std::runtime_error("Witness state/adjacency size mismatch");
    f << "BEGIN " << kind << ' ' << n << ' ' << parent << ' ' << child1 << ' ' << child2 << ' ' << var << '\n';
    f << "META " << n << ' ' << a.get_initial_state().get_id() << ' ' << ts.get_num_non_loops() << ' ' << ts.get_num_loops() << ' ' << INF_COSTS << '\n';
    for(unsigned op=0;op<costs.size();++op) f << "C " << op << ' ' << costs[op] << '\n';
    f << "M";for(int v:modified) f << ' ' << v;f << '\n';
    std::vector<int> goals(a.get_goals().begin(),a.get_goals().end());std::sort(goals.begin(),goals.end());
    for(int g:goals) f << "G " << g << '\n';
    for(int s=0;s<n;++s) {
        const auto &st=a.get_state(s);f << "E " << s << ' ' << st.is_spurious() << '\n';
        if(sp) f << "D " << s << ' ' << sp->get_64bit_init_distance(s) << ' ' << sp->get_64bit_goal_distance(s) << '\n';
        const auto &d=st.get_cartesian_set();
        for(int v=0;v<d.get_n_vars();++v) {
            f << "V " << s << ' ' << v << ' ' << d.var_size(v);
            for(int x=0;x<d.var_size(v);++x) if(d.test(v,x)) f << ' ' << x;
            f << '\n';
        }
        unsigned pos=0;for(const auto &t:out[s]) f << "O " << s << ' ' << t.op_id << ' ' << t.target_id << ' ' << pos++ << '\n';
        pos=0;for(const auto &t:in[s]) f << "I " << s << ' ' << t.op_id << ' ' << t.target_id << ' ' << pos++ << '\n';
        pos=0;for(int op:loops[s]) f << "L " << s << ' ' << op << ' ' << pos++ << '\n';
    }
    f << "END " << kind << ' ' << n << '\n';f.flush();
    if(!f || f.tellp()>static_cast<std::streamoff>(2000000000LL)) throw std::runtime_error("Witness incomplete/2GB diagnostic bound exceeded");
}
}
