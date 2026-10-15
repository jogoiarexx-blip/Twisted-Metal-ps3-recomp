// Twisted Metal BCUS98106 v1.06, 0x4EC8D0..0x4EC944.
// Lifts local instructions ONLY. syscalls and helper calls remain explicit boundaries.
// The guest memory allocator and LV2 are NOT simulated by this module.
#include "runtime.hpp"
#include <stdexcept>
namespace tmrecomp {
namespace {
uint64_t signed_offset(uint64_t r, int64_t delta) {
  return r + static_cast<uint64_t>(delta);
}
}
// Calls 0x160 (352): sys_memory_get_user_memory_size(&info).
uint64_t startup_004ec8d0(Cpu& cpu, Memory& mem) {
  const uint64_t caller_stack = cpu.r[1];
  const uint64_t frame = signed_offset(caller_stack, -112);
  // PPC64 stdu r1,-112(r1) updates SP after storing back chain.
  mem.store64(frame, caller_stack);
  cpu.r[1] = frame;
  cpu.r[0] = cpu.lr;  // mflr r0
  mem.store64(frame + 128, cpu.r[0]);
  cpu.r[3] = 0x017dfc48; // lis/addic/clrldi with 32 bit pointer
  cpu.r[11] = 0x160;
  cpu.ca = false; // addic 0x017e0000 + (-952), no 64-bit unsigned carry
  return 0x4ec8ec; // STOP: lv2 syscall; cannot run without real HLE
}
// Resume ONLY after LV2 syscall 0x160 returns. The caller provides guest side effects and r3.
uint64_t startup_after_004ec8ec(Cpu& cpu, Memory&) {
  cpu.r[3] = 0x00f00000; // 15 MiB requested
  cpu.r[4] = 0x400; // SYS_MEMORY_PAGE_SIZE_1M
  cpu.r[5] = 0x017dfc40; // output allocated pointer (be_u32)
  cpu.r[11] = 0x15c; // 348 sys_memory_allocate
  cpu.ca = false;
  return 0x4ec908; // STOP: lv2 memory allocation; do not fake success
}
// Returns the next helper target based on *actual* r3 from syscall 0x15c.
uint64_t startup_after_004ec908(Cpu& cpu, Memory& mem) {
  // 0x4ec90c cmpwi r3,0; 0x4ec910 beq 0x4ec91c.
  if (static_cast<int32_t>(static_cast<uint32_t>(cpu.r[3])) != 0) {
    cpu.lr = 0x4ec918;
    return 0x95fa3c;  // failure path, never pretend allocation succeeded
  }
  cpu.r[3] = mem.load32(0x017dfc40); // previously allocated guest memory address
  cpu.r[4] = 0x00f00000; // size argument to helper 0x98c8c0
  cpu.lr = 0x4ec92c;
  return 0x98c8c0; // STOP: unimplemented helper
}
// Called AFTER the helper at 0x98c8c0 has actually returned with a value in r3.
uint64_t startup_after_004ec928(Cpu& cpu, Memory& mem) {
  mem.store32(0x017dfc44, static_cast<uint32_t>(cpu.r[3]));
  cpu.lr = 0x4ec938;
  return 0x4ed1f0; // STOP: unimplemented helper
}
// Called AFTER helper at 0x4ed1f0 returns. Restore the real caller link register.
uint64_t startup_after_004ec934(Cpu& cpu, Memory& mem) {
  const uint64_t frame = cpu.r[1];
  cpu.r[0] = mem.load64(frame + 128);
  cpu.lr = cpu.r[0];
  cpu.r[1] = frame + 112;
  return cpu.lr; // blr
}
} // namespace tmrecomp
