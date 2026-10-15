#include "lv2_memory.hpp"
#include "runtime.hpp"
#include <iostream>
#include <stdexcept>
#include <cstdint>
using namespace tmrecomp;
static int passed=0;
static void check(bool yes,const char* name) {
  if (!yes)throw std::runtime_error(name);
  ++passed;
}
static uint32_t call(Lv2Memory& lv2, Cpu& cpu, Memory& mem, uint64_t sc,
                     uint64_t a,uint64_t b=0,uint64_t c=0) {
  cpu.r[11]=sc;cpu.r[3]=a;cpu.r[4]=b;cpu.r[5]=c;
  auto rc=lv2.dispatch(cpu,mem);
  check(static_cast<uint32_t>(cpu.r[3])==rc,"r3 error encoding");
  return rc;
}
int main() {
  try {
    Memory mem(0,0x400000);Cpu cpu;Lv2Memory lv2;
    check(call(lv2,cpu,mem,0x160,0x1000)==Lv2Memory::ok,"memory-info syscall");
    check(mem.load32(0x1000)==213u*1024*1024 && mem.load32(0x1004)==lv2.available(),"BE32 total/available");
    check(call(lv2,cpu,mem,0x160,0)==Lv2Memory::efault,"memory-info null pointer");
    check(call(lv2,cpu,mem,0x160,0x101)==Lv2Memory::efault,"memory-info unaligned pointer");
    check(call(lv2,cpu,mem,0x160,0x400000)==Lv2Memory::efault,"memory-info unmapped pointer");
    mem.store32(0x1200,0xdeadbeef);
    check(call(lv2,cpu,mem,0x15c,0,0x400,0x1200)==Lv2Memory::ealign,"zero-sized allocation rejected");
    check(call(lv2,cpu,mem,0x15c,0x100000,0x999,0x1200)==Lv2Memory::einval,"invalid flags rejected");
    check(call(lv2,cpu,mem,0x15c,0x180000,0x400,0x1200)==Lv2Memory::ealign,"unaligned 1MB allocation rejected");
    check(call(lv2,cpu,mem,0x15c,0x100000,0x400,0x1201)==Lv2Memory::efault,"unaligned output address rejected");
    check(call(lv2,cpu,mem,0x15c,0x100000,0x400,0)==Lv2Memory::efault,"null output rejected");
    check(lv2.allocations().empty() && mem.load32(0x1200)==0xdeadbeef,"errors leave memory/allocator unchanged");
    check(call(lv2,cpu,mem,0x15c,0xf00000,0x400,0x1200)==Lv2Memory::ok,"15MB allocation succeeds");
    check(mem.load32(0x1200)==0x40000000 && lv2.allocations()[0].page_size==0x100000,"1MB alignment and BE32 guest output");
    check(mem.load32(0x40000000)==0 && mem.load32(0x40effffc)==0,"new guest region is zeroed");
    mem.store32(0x40001000,0x89abcdef);
    check(mem.load32(0x40001000)==0x89abcdef && mem.address(0x40001000,4)[0]==0x89,"guest allocation is real BE memory");
    bool threw=false;
    try {mem.load32(0x40effffe);} catch(const std::out_of_range&) {threw=true;}
    check(threw,"cross-boundary access rejected");
    check(call(lv2,cpu,mem,0x160,0x1000)==Lv2Memory::ok &&
          mem.load32(0x1004)==(213u-15u)*1024*1024,"memory availability reduced after allocation");
    check(call(lv2,cpu,mem,0x15c,0x10000,0x200,0x1204)==Lv2Memory::ok,"64KB allocation succeeds");
    check(mem.load32(0x1204)==0x40f00000 && lv2.allocations()[1].page_size==0x10000,"64KB follows first region without overlap");
    check(call(lv2,cpu,mem,0x15c,0x100000,0,0x1208)==Lv2Memory::ok,"flags zero means 1MB");
    check(mem.load32(0x1208)==0x41000000 && lv2.allocations()[2].page_size==0x100000,"zero-flag alignment applied");
    check(mem.load32(0x40f00000)==0,"second guest allocation exists");
    check(call(lv2,cpu,mem,0x15c,213u*1024*1024,0x400,0x120c)==Lv2Memory::enomem,"physical quota enforced");
    check(mem.load32(0x120c)==0 && lv2.allocations().size()==3,"out of memory is atomic");
    check(call(lv2,cpu,mem,0x160,0x40000000)==Lv2Memory::ok,"guest mapped memory as output accepted");
    check(mem.load32(0x40000000)==lv2.total() && mem.load32(0x40000004)==lv2.available(),"be writes in mapped memory");
    // Small physical budget, no access to host memory outside the two pools.
    Memory limited_mem(0,0x4000);Lv2Memory small(0x100000);Cpu c2;
    check(call(small,c2,limited_mem,0x15c,0x100000,0x400,0x400)==Lv2Memory::ok,"small pool first allocation");
    check(call(small,c2,limited_mem,0x15c,0x100000,0x400,0x404)==Lv2Memory::enomem,"small pool exhaustion");
    check(limited_mem.regions.size()==1 && small.available()==0,"small pool no phantom guest mapping");
    bool unmapped=false;
    try {limited_mem.store32(0x50000000,7);}catch(const std::out_of_range&){unmapped=true;}
    check(unmapped,"guest window outside mapping rejected");
    std::cout<<"PASS: "<<passed<<" LV2 memory dispatch and guest mapping assertions\n";
  } catch (const std::exception& e) {
    std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;
  }
}
