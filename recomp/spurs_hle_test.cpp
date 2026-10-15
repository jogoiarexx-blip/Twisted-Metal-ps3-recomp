#include "runtime.hpp"
#include "import_dispatch.hpp"
#include <iostream>
#include <stdexcept>
using namespace tmrecomp;
static void require(bool value, const char* why) { if(!value) throw std::runtime_error(why); }
static void run(){
  Memory mem(0,0x10000); Cpu cpu; cpu.lr=0x12345678;
  const uint64_t bar_import=0x00c8c02c, info_import=0x00c8c144;
  const uint32_t taskset=0x4000, barrier=0x8000, info=0xa000;
  cpu.r[3]=taskset;cpu.r[4]=barrier;cpu.r[5]=6;
  for(int i=0;i<128;i+=4)mem.store32(barrier+i,0xFEEDFACE);
  require(dispatch_import(bar_import,cpu,mem)==cpu.lr,"barrier return PC");
  require(cpu.r[3]==0 && mem.load32(barrier+4)==6 && mem.load32(barrier+0x34)==taskset,"barrier values");
  require(mem.load32(barrier)==0 && mem.load32(barrier+124)==0,"barrier memory cleared");
  cpu.r[3]=taskset;cpu.r[4]=barrier;cpu.r[5]=0;
  dispatch_import(bar_import,cpu,mem);require(cpu.r[3]==spurs_status(spurs_err_inval),"zero count rejected");
  require(mem.load32(barrier+4)==6,"invalid count must not mutate");
  cpu.r[3]=taskset;cpu.r[4]=barrier;cpu.r[5]=129;
  dispatch_import(bar_import,cpu,mem);require(cpu.r[3]==spurs_status(spurs_err_inval),"count 129 rejected");
  cpu.r[3]=taskset;cpu.r[4]=barrier+4;cpu.r[5]=6;
  dispatch_import(bar_import,cpu,mem);require(cpu.r[3]==spurs_status(spurs_err_align),"barrier alignment rejected");
  cpu.r[3]=0;cpu.r[4]=barrier;cpu.r[5]=6;
  dispatch_import(bar_import,cpu,mem);require(cpu.r[3]==spurs_status(spurs_err_null),"null taskset rejected");
  mem.store64(taskset+0x68,0x123456789ABCDEF0ULL);
  mem.store32(taskset+0x74,5);
  mem.store32(taskset+0x1890,0x2900);
  for(uint32_t i=0;i<0x2420;i+=4)mem.store32(info+i,0xFEEDFACE);
  cpu.r[3]=taskset;cpu.r[4]=info;
  require(dispatch_import(info_import,cpu,mem)==cpu.lr,"info return PC");
  require(cpu.r[3]==0,"info success");
  require(mem.load64(info+0x2400)==0x123456789ABCDEF0ULL,"info args");
  require(mem.load32(info+0x2408)==5 && mem.load32(info+0x241C)==0x2900,"info WID/size");
  require(mem.load32(info)==0 && mem.load32(info+0x2410)==0,"info zeroed");
  cpu.r[3]=taskset+4;cpu.r[4]=info;
  dispatch_import(info_import,cpu,mem);
  require(cpu.r[3]==spurs_status(spurs_err_align),"taskset alignment rejected");
  cpu.r[3]=taskset;cpu.r[4]=0;
  dispatch_import(info_import,cpu,mem);
  require(cpu.r[3]==spurs_status(spurs_err_null),"null out buffer rejected");
  cpu.r[3]=taskset;cpu.r[4]=0x10000;cpu.r[5]=6;
  bool rejected=false;
  try{dispatch_import(bar_import,cpu,mem);}catch(const std::out_of_range&){rejected=true;}
  require(rejected,"out of range barrier rejected");
  std::cout<<"PASS: 16 SPURS ABI, memory and import-dispatch checks\n";
}
int main(){try{run();}catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}}
