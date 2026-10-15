// Generated from ELF 41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d
#include "runtime.hpp"
namespace tmrecomp {
uint64_t startup_00354d88(Cpu &cpu, Memory &mem) {
  // 0x00354d88: f821ff61
  uint64_t old_sp=cpu.r[1]; cpu.r[1]-=0xa0; mem.store64(cpu.r[1],old_sp);
  // 0x00354d8c: 7c0802a6
  cpu.r[0] = cpu.lr;
  // 0x00354d90: fb410070
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(112)), cpu.r[26]);
  // 0x00354d94: fb810080
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(128)), cpu.r[28]);
  // 0x00354d98: fbc10090
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(144)), cpu.r[30]);
  // 0x00354d9c: fbe10098
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(152)), cpu.r[31]);
  // 0x00354da0: fb610078
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(120)), cpu.r[27]);
  // 0x00354da4: fba10088
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(136)), cpu.r[29]);
  // 0x00354da8: f80100b0
  mem.store64(cpu.r[1] + static_cast<uint64_t>(static_cast<int64_t>(176)), cpu.r[0]);
  // 0x00354dac: 7c7f1b78
  cpu.r[31] = cpu.r[3];
  // 0x00354db0: 7c9c2378
  cpu.r[28] = cpu.r[4];
  // 0x00354db4: 7cba2b78
  cpu.r[26] = cpu.r[5];
  // 0x00354db8: 7cde3378
  cpu.r[30] = cpu.r[6];
  // 0x00354dbc: 7d9d6378
  cpu.r[29] = cpu.r[12];
  // 0x00354dc0: 81628004
  cpu.r[11] = mem.load32(cpu.r[2] + static_cast<uint64_t>(static_cast<int64_t>(-32764)));
  // 0x00354dc4: 79040020
  cpu.r[4] = cpu.r[8] & 0xffffffffULL;
  // 0x00354dc8: 79460020
  cpu.r[6] = cpu.r[10] & 0xffffffffULL;
  // 0x00354dcc: 7ce33b78
  cpu.r[3] = cpu.r[7];
  // 0x00354dd0: 79250020
  cpu.r[5] = cpu.r[9] & 0xffffffffULL;
  // 0x00354dd4: 7f9be378
  cpu.r[27] = cpu.r[28];
  // 0x00354dd8: 93ab0000
  mem.store32(cpu.r[11] + static_cast<uint64_t>(static_cast<int64_t>(0)), static_cast<uint32_t>(cpu.r[29]));
  // 0x00354ddc: 489382b9
  cpu.lr = 0x354de0; return 0xc8d094;
}
}
