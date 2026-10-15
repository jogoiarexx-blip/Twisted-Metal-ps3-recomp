// Generated from verified ELF SHA-256 41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d
#include "runtime.hpp"
namespace tmrecomp {
uint64_t entry_00354c80(Cpu &cpu, Memory &mem) {
  // 0x00354c80: 38400000 li r2, 0
  cpu.r[2] = 0;
  // 0x00354c84: 644200f1 oris r2, r2, 0xf1
  cpu.r[2] |= uint64_t(0xf1) << 16;
  // 0x00354c88: 60423170 ori r2, r2, 0x3170
  cpu.r[2] |= 0x3170;
  // 0x00354c8c: 80420004 lwz r2, 4(r2)
  cpu.r[2] = mem.load32(cpu.r[2] + 4);
  // 0x00354c90: f821ff91 stdu r1, -0x70(r1)
  { uint64_t old_sp=cpu.r[1]; cpu.r[1]-=0x70; mem.store64(cpu.r[1],old_sp); }
  // 0x00354c94: 39c00000 li r14, 0
  cpu.r[14] = 0;
  // 0x00354c98: f9c10000 std r14, 0(r1)
  mem.store64(cpu.r[1],cpu.r[14]);
  // 0x00354c9c: 480000ed bl 0x354d88
  cpu.lr = 0x354ca0; return 0x354d88;
}
}
