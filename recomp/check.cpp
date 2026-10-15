#include "runtime.hpp"
#include <cstdlib>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv) {
  if(argc!=4) return 2;
  auto addr=std::stoull(argv[1],nullptr,0), r3=std::stoull(argv[2],nullptr,0), word=std::stoull(argv[3],nullptr,0);
  tmrecomp::Cpu cpu;tmrecomp::Memory mem(0x100000,0x1000);
  cpu.r[3]=r3;cpu.r[4]=0x12345678;
  mem.store32(0x100048,static_cast<uint32_t>(word));
  mem.store32(0x1001ac,static_cast<uint32_t>(word));
  if(addr==0x994838) tmrecomp::fn_00994838(cpu,mem);
  else if(addr==0x9946e0) tmrecomp::fn_009946e0(cpu,mem);
  else if(addr==0x9946c0) tmrecomp::fn_009946c0(cpu,mem);
  else return 3;
  std::cout<<std::hex<<cpu.r[3]<<" "<<cpu.r[4]<<" "<<mem.load32(0x100040)<<" "<<mem.load32(0x100044)<<" "<<mem.load32(0x100048)<<" "<<mem.load32(0x10004c)<<" "<<mem.load32(0x10015c)<<" "<<mem.load32(0x1001ac)<<"\n";
}
