#include "runtime.hpp"
#include <iostream>
#include <stdexcept>
using namespace tmrecomp;
static void check(bool b, const char* message) {if(!b) throw std::runtime_error(message);}
static Memory make_memory(){
  Memory m(0,0x2100000);
  m.store32(0xf31ac0+0x551c,0x01a69fc0);
  m.store32(0xf31ac0+0x5520,0x00f9fef4);
  m.store32(0x00f9fef4,0x00100000);
  m.map_region(0x40000000,0x00f00000);
  return m;
}
int main(){
try {
  auto mem=make_memory(); Cpu cpu;
  cpu.r[1]=0x1fffe80;cpu.r[2]=0xf31ac0;cpu.r[3]=0x40000000;cpu.r[4]=0xf00000;cpu.lr=0x4ec92c;
  for(int i=25;i<=31;++i)cpu.r[i]=0x12340000+i;
  auto next=heap_start_0098c8c0(cpu,mem);
  check(next==0x988b78 && cpu.lr==0x98c8f4 && cpu.r[1]==0x1fffdd0,"prologue/call");
  check(cpu.r[30]==0xf00000 && cpu.r[31]==0x40000000 && mem.load64(cpu.r[1]+192)==0x4ec92c,"stack saved");
  next=heap_helper_00988b78(cpu,mem);
  check(next==0x98c8f4 && cpu.r[1]==0x1fffdd0,"helper returned");
  check(mem.load32(0x1a69fc0)==0x58585858,"descriptor signature");
  check(mem.load32(0x1a69fc0+4)==0x100000 && mem.load32(0x1a69fc0+8)==0x100000,"descriptor size");
  check(mem.load32(0x1a69fc0+12)==0x100000 && mem.load32(0x1a69fc0+16)==0xfffff && mem.load32(0x1a69fc0+20)==7,"descriptor fields");
  next=heap_after_00988b78(cpu,mem);
  check(next==0x98769c && cpu.lr==0x98c954,"next helper boundary");
  check(cpu.r[3]==0x40000010 && cpu.r[4]==0 && cpu.r[5]==496,"next helper ABI");
  check(cpu.r[25]==0x40000010 && cpu.r[28]==0x40000008 && cpu.r[29]==0x400001d0,"heap address arithmetic");
  check(heap_memset_0098769c(cpu,mem)==0x98c954,"memset return");
  check(mem.load32(0x40000010)==0 && mem.load32(0x400001fc)==0,"memset 496 bytes");
  next=heap_after_0098769c(cpu,mem);
  check(next==0x988b0c && cpu.lr==0x98c990,"list head boundary");
  check(mem.load32(0x40000008+4)==499 && mem.load32(0x40000010+432)==0xf00000,"heap header fields");
  check(mem.load32(0x40000010+444)==7 && mem.load32(0x40000010+32)==0x58585858,"allocator signature and flags");
  check(heap_list_heads_00988b0c(cpu,mem)==0x98c990,"list head return");
  for(int i=0;i<32;i++) {
    auto head=0x40000010+36+i*8;
    check(mem.load32(head+8)==static_cast<unsigned>(head) && mem.load32(head+12)==static_cast<unsigned>(head),"list head self-link");
  }
  next=heap_after_00988b0c(cpu,mem);
  check(next==0x988aa8 && cpu.lr==0x98c9c8,"next memory helper boundary");
  check(cpu.r[3]==0x40000010 && cpu.r[4]==0x400001f8 && cpu.r[5]==0xeffdd8,"next helper ABI");
  // Verify the helper's preinitialised global is left untouched on later calls.
  cpu.lr=0xdeadbeef;cpu.r[1]=0x1fffe80;
  mem.store32(0x1a69fc0+4,0x222000);
  next=heap_helper_00988b78(cpu,mem);
  check(next==0xdeadbeef && mem.load32(0x1a69fc0+4)==0x222000,"already initialised helper");
  // Failure length branch: no call to the next helper, saved stack restored.
  auto m2=make_memory();Cpu small;
  small.r[1]=0x1fffe80;small.r[2]=0xf31ac0;small.r[3]=0x40000000;small.r[4]=400;small.lr=0x4ec92c;
  next=heap_start_0098c8c0(small,m2);check(next==0x988b78,"short frame");
  check(heap_helper_00988b78(small,m2)==0x98c8f4,"short helper");
  check(heap_after_00988b78(small,m2)==0x98c9f8,"short arena rejected");
  check(heap_failed_return_0098c9f8(small,m2)==0x4ec92c && small.r[1]==0x1fffe80 && small.r[3]==0,"failure epilogue");
  // Invalid global config: stops at assert/error branch instead of returning success.
  auto m3=make_memory();m3.store32(0x00f9fef4,0x100003);
  Cpu bad;bad.r[1]=0x1fffe80;bad.r[2]=0xf31ac0;bad.lr=0x98c8f4;
  check(heap_helper_00988b78(bad,m3)==0x95fa3c && bad.lr==0x988be4,"invalid allocator config");
  std::cout<<"PASS: heap prologue, global init, ABI, 2 error branches, epilogue, second-call path\n";
} catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}
}
