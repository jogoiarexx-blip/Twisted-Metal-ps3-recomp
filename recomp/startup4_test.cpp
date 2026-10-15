#include "runtime.hpp"
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
using namespace tmrecomp;
static void require(bool yes,const char* label) { if(!yes) throw std::runtime_error(label); }
int main() {
try {
  Memory mem(0,0x2100000);
  Cpu cpu;
  cpu.r[1]=0x2000000; cpu.lr=0x354e58; cpu.r[3]=0xabc;
  uint64_t next=startup_004ec8d0(cpu,mem);
  require(next==0x4ec8ec && cpu.r[11]==0x160 && cpu.r[3]==0x17dfc48,"LV2 352 number/arguments");
  require(cpu.r[1]==0x1ffff90 && cpu.r[0]==0x354e58,"PPU frame/LR state");
  require(mem.load64(cpu.r[1])==0x2000000 && mem.load64(cpu.r[1]+128)==0x354e58,"PPU frame backchain/LR save");
  // Simulate successful memory-info syscall for TEST ONLY; not production HLE.
  mem.store32(cpu.r[3],0x10000000); mem.store32(cpu.r[3]+4,0x0f000000);cpu.r[3]=0;
  next=startup_after_004ec8ec(cpu,mem);
  require(next==0x4ec908 && cpu.r[11]==0x15c && cpu.r[3]==0xf00000 && cpu.r[4]==0x400 && cpu.r[5]==0x17dfc40,"LV2 348 ABI");
  // Failure must STOP on actual error branch without touching output.
  mem.store32(cpu.r[5],0xdeadbeef);
  cpu.r[3]=0x80010004;
  next=startup_after_004ec908(cpu,mem);
  require(next==0x95fa3c && cpu.lr==0x4ec918 && mem.load32(0x17dfc40)==0xdeadbeef,"allocation failure path");
  // Independently test the success path with explicit mocked allocation side effect.
  cpu.lr=0x354e58;
  mem.store32(0x17dfc40,0x2100000);
  cpu.r[3]=0;
  next=startup_after_004ec908(cpu,mem);
  require(next==0x98c8c0 && cpu.r[3]==0x2100000 && cpu.r[4]==0xf00000 && cpu.lr==0x4ec92c,"allocation success helper");
  cpu.r[3]=0x98765432; // mocked return from actual helper
  next=startup_after_004ec928(cpu,mem);
  require(next==0x4ed1f0 && mem.load32(0x17dfc44)==0x98765432 && cpu.lr==0x4ec938,"helper result store and second helper call");
  cpu.r[3]=0; // mocked return from second helper
  next=startup_after_004ec934(cpu,mem);
  require(next==0x354e58 && cpu.lr==0x354e58 && cpu.r[1]==0x2000000,"function epilogue/return");
  // Invalid outputs must throw instead of silently succeeding.
  Cpu bad;bad.r[1]=0x10;bad.lr=0x20;
  bool thrown=false;try{startup_004ec8d0(bad,mem);}catch(const std::out_of_range&){thrown=true;}
  require(thrown,"stack underflow caught by memory bounds");
  std::cout<<"PASS: 7 startup4 ABI/frame/control-flow tests (mock LV2 results only)\n";
  return 0;
} catch(const std::exception&e) {std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}
}
