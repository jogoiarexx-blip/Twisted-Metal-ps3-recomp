// Twisted Metal BCUS98106 1.06: verified block 0x354de0..0x354e54.
#include "runtime.hpp"
#include <stdexcept>
namespace tmrecomp {
uint64_t startup_00354de0(Cpu &cpu, Memory &mem) {
  // 0x354de0 nop; 0x354de4 addi r10,r28,4; 0x354de8 li r8,0.
  cpu.r[10]=cpu.r[28]+4;
  cpu.r[8]=0;
  // 0x354dec..0x354e0c: unsigned cmpd r31,r8; bf cr7.lt,loop.
  // At least one iteration executes, as in the original PowerPC loop.
  uint64_t iterations=0;
  for (;;) {
    cpu.r[9]=static_cast<uint32_t>(cpu.r[10]);
    cpu.r[11]=static_cast<uint32_t>(cpu.r[28]);
    ++cpu.r[8];
    cpu.r[10]+=8;
    const bool lt=cpu.r[31]<cpu.r[8];
    cpu.r[0]=mem.load32(cpu.r[9]);
    cpu.r[28]+=4;
    mem.store32(cpu.r[11],static_cast<uint32_t>(cpu.r[0]));
    if(lt)break;
    if(++iterations>=0x100000)throw std::runtime_error("startup loop 1 safety bound");
  }
  // 0x354e10..0x354e2c: globals and loop initialization.
  cpu.r[9]=mem.load32(cpu.r[2]+static_cast<uint64_t>(static_cast<int64_t>(-32768)));
  cpu.r[29]=cpu.r[26];
  cpu.r[5]=cpu.r[26];
  cpu.r[28]=cpu.r[31];
  cpu.r[10]=cpu.r[26]+4;
  cpu.r[8]=0;
  mem.store32(cpu.r[9],static_cast<uint32_t>(cpu.r[31]));
  mem.store32(cpu.r[9]+4,static_cast<uint32_t>(cpu.r[27]));
  // 0x354e30..0x354e50: second copy loop.
  iterations=0;
  for (;;) {
    cpu.r[9]=static_cast<uint32_t>(cpu.r[10]);
    cpu.r[11]=static_cast<uint32_t>(cpu.r[5]);
    ++cpu.r[8];
    cpu.r[10]+=8;
    const bool lt=cpu.r[30]<cpu.r[8];
    cpu.r[0]=mem.load32(cpu.r[9]);
    cpu.r[5]+=4;
    mem.store32(cpu.r[11],static_cast<uint32_t>(cpu.r[0]));
    if(lt)break;
    if(++iterations>=0x100000)throw std::runtime_error("startup loop 2 safety bound");
  }
  // 0x354e54 bl 0x4ec8d0.
  cpu.lr=0x354e58;
  return 0x4ec8d0;
}
}
