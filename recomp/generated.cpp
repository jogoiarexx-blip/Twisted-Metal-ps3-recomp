// Generated from SHA-256 41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d
#include "runtime.hpp"
namespace tmrecomp {
void fn_009946c0(Cpu &cpu, Memory &mem) {
  // 0x009946c0: 9083011c stw r4, 0x11c(r3)
  mem.store32((cpu.r[3] + static_cast<uint64_t>(static_cast<int64_t>(284))), static_cast<uint32_t>(cpu.r[4]));
  // 0x009946c4: 4e800020 blr 
  return;
}
void fn_009946e0(Cpu &cpu, Memory &mem) {
  // 0x009946e0: 8063016c lwz r3, 0x16c(r3)
  cpu.r[3] = mem.load32((cpu.r[3] + static_cast<uint64_t>(static_cast<int64_t>(364))));
  // 0x009946e4: 4e800020 blr 
  return;
}
void fn_00994838(Cpu &cpu, Memory &mem) {
  // 0x00994838: 38800000 li r4, 0
  cpu.r[4] = static_cast<uint64_t>(static_cast<int64_t>(0));
  // 0x0099483c: 90830000 stw r4, 0(r3)
  mem.store32((cpu.r[3] + static_cast<uint64_t>(static_cast<int64_t>(0))), static_cast<uint32_t>(cpu.r[4]));
  // 0x00994840: 90830004 stw r4, 4(r3)
  mem.store32((cpu.r[3] + static_cast<uint64_t>(static_cast<int64_t>(4))), static_cast<uint32_t>(cpu.r[4]));
  // 0x00994844: 90830008 stw r4, 8(r3)
  mem.store32((cpu.r[3] + static_cast<uint64_t>(static_cast<int64_t>(8))), static_cast<uint32_t>(cpu.r[4]));
  // 0x00994848: 9083000c stw r4, 0xc(r3)
  mem.store32((cpu.r[3] + static_cast<uint64_t>(static_cast<int64_t>(12))), static_cast<uint32_t>(cpu.r[4]));
  // 0x0099484c: 4e800020 blr 
  return;
}
}
