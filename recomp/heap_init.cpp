// Twisted Metal BCUS98106 v1.06; powerpc64 big endian ELF SHA-256
// 41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d.
// Interpret only verified PPC64 instructions. Unknown callees remain explicit exits.
#include "runtime.hpp"
#include <cstdint>
#include <stdexcept>
namespace tmrecomp {
namespace {
uint64_t at_toc(const Cpu& cpu, uint16_t offset) { return cpu.r[2] + offset; }
void push(Cpu& cpu, Memory& mem, uint64_t bytes) {
  if (cpu.r[1] < bytes) throw std::out_of_range("PPU stack underflow");
  const uint64_t next = cpu.r[1] - bytes;
  mem.store64(next, cpu.r[1]);
  cpu.r[1] = next;
}
void pop(Cpu& cpu, Memory& mem, uint64_t bytes) {
  const auto previous = mem.load64(cpu.r[1]);
  if (previous != cpu.r[1] + bytes) throw std::runtime_error("PPU backchain mismatch");
  cpu.r[1] = previous;
}
}
// At 0x98c8c0: save r25..r31, r30=size, r31=base, then BL 0x988b78.
uint64_t heap_start_0098c8c0(Cpu& cpu, Memory& mem) {
  push(cpu, mem, 176);
  cpu.r[0] = cpu.lr;
  mem.store64(cpu.r[1] + 160, cpu.r[30]);
  cpu.r[30] = cpu.r[4];
  mem.store64(cpu.r[1] + 168, cpu.r[31]);
  for (int i = 25; i <= 29; ++i) mem.store64(cpu.r[1] + 120 + (i-25)*8, cpu.r[i]);
  mem.store64(cpu.r[1] + 192, cpu.r[0]);
  cpu.r[31] = cpu.r[3];
  cpu.lr = 0x98c8f4;
  return 0x988b78;
}
// Entire helper 0x988b78..0x988be4. Initialises a global allocator descriptor.
uint64_t heap_helper_00988b78(Cpu& cpu, Memory& mem) {
  const auto global = static_cast<uint64_t>(mem.load32(at_toc(cpu, 0x551c)));
  cpu.r[8] = global;
  cpu.r[0] = cpu.lr;
  push(cpu, mem, 112);
  mem.store64(cpu.r[1] + 128, cpu.r[0]);
  const auto current = mem.load32(global + 4);
  cpu.r[0] = current;
  if (current == 0) {
    const auto config = static_cast<uint64_t>(mem.load32(at_toc(cpu, 0x5520)));
    cpu.r[10] = config;
    cpu.r[0] = 7;
    cpu.r[9] = 0x58585858u;
    mem.store32(global + 20, 7);
    const uint32_t limit = mem.load32(config);
    cpu.r[11] = limit;
    mem.store32(global, 0x58585858u);
    const uint32_t mask = limit - 1u;
    cpu.r[0] = mask;
    mem.store32(global+8, limit);
    cpu.r[9] = (limit & mask);
    mem.store32(global+12, limit);
    mem.store32(global+16, mask);
    mem.store32(global+4, limit);
    if (cpu.r[9] != 0) {
      cpu.lr = 0x988be4;
      return 0x95fa3c; // Error handler: not silently skipped.
    }
  }
  cpu.r[0] = mem.load64(cpu.r[1] + 128);
  cpu.lr = cpu.r[0];
  pop(cpu, mem, 112);
  return cpu.lr; // Expected 0x98c8f4.
}
// Executed ONLY when helper 0x988b78 returns to 0x98c8f4.
// Validate minimum arena and its capacity before calling the next memory helper.
uint64_t heap_after_00988b78(Cpu& cpu, Memory& mem) {
  if (cpu.lr != 0x98c8f4) throw std::runtime_error("Unexpected heap helper return");
  const uint32_t size = static_cast<uint32_t>(cpu.r[30]);
  if (size <= 544) { cpu.r[31] = 0; return 0x98c9f8; }
  const uint64_t global = static_cast<uint64_t>(mem.load32(at_toc(cpu, 0x551c)));
  cpu.r[26] = global;
  const uint32_t remaining = static_cast<uint32_t>(0u - 544u - mem.load32(global+4));
  cpu.r[0] = static_cast<uint64_t>(static_cast<int64_t>(-544) - mem.load32(global+4));
  if (remaining <= size) { cpu.r[31] = 0; return 0x98c9f8; }
  cpu.r[0] = cpu.r[31]+8;
  cpu.r[27] = cpu.r[31];
  const uint32_t low = static_cast<uint32_t>(cpu.r[0]) & 0xf;
  cpu.r[0] = low;
  cpu.r[29] = low ? ((16-low)&0xf) : 0;
  if (low) cpu.r[0] = 16-low;
  cpu.r[29] += cpu.r[27];
  cpu.r[4] = 0;
  cpu.r[25] = cpu.r[29]+8;
  cpu.r[28] = static_cast<uint32_t>(cpu.r[29]);
  cpu.r[31] = static_cast<uint32_t>(cpu.r[25]);
  cpu.r[5] = 496;
  cpu.r[3] = cpu.r[31];
  cpu.r[29] += 456;
  cpu.lr = 0x98c954;
  return 0x98769c; // STOP: next helper; don't fake a memset/allocator result.
}
// 0x98c9f8..0x98ca24 is the early failure epilogue; no skipped calls.
uint64_t heap_failed_return_0098c9f8(Cpu& cpu, Memory& mem) {
  const uint64_t frame = cpu.r[1];
  cpu.r[0] = mem.load64(frame+192);
  cpu.r[3] = cpu.r[31];
  for (int i=25;i<=31;++i) cpu.r[i] = mem.load64(frame+120+(i-25)*8);
  cpu.lr = cpu.r[0];
  pop(cpu,mem,176);
  return cpu.lr;
}
}
namespace tmrecomp {
// HLE of the verified inline PowerPC memset at 0x98769c.
// It fills exactly [r3, r3+r5) with low 8 bits of r4; does not grant memory.
uint64_t heap_memset_0098769c(Cpu& cpu, Memory& mem) {
  const auto length = cpu.r[5];
  const auto dst = cpu.r[3];
  if (length > UINT32_MAX || dst > UINT64_MAX - length)
    throw std::out_of_range("guest memset size/overflow");
  if (length) {
    auto* ptr = mem.address(dst, static_cast<size_t>(length));
    const auto byte = static_cast<uint8_t>(cpu.r[4]);
    for (size_t i = 0; i < static_cast<size_t>(length); ++i)ptr[i] = byte;
  }
  cpu.r[4] &= 0xff;
  cpu.r[5] = dst + length;
  return cpu.lr;
}
// Resume after 0x98769c returns to 0x98c954; sets up allocator header.
uint64_t heap_after_0098769c(Cpu& cpu, Memory& mem) {
  if (cpu.lr != 0x98c954) throw std::runtime_error("Unexpected memset return");
  mem.store32(cpu.r[28]+4,499);
  mem.store32(cpu.r[31]+432,static_cast<uint32_t>(cpu.r[30]));
  mem.store32(cpu.r[31]+428,static_cast<uint32_t>(cpu.r[30]));
  mem.store32(cpu.r[31]+476,static_cast<uint32_t>(cpu.r[30]));
  cpu.r[9] = mem.load32(cpu.r[26]);
  cpu.r[3] = cpu.r[31];
  mem.store32(cpu.r[31]+16,static_cast<uint32_t>(cpu.r[27]));
  mem.store32(cpu.r[31]+32,static_cast<uint32_t>(cpu.r[9]));
  cpu.r[0] = mem.load32(cpu.r[26]+20);
  mem.store32(cpu.r[31]+472,static_cast<uint32_t>(cpu.r[27]));
  cpu.r[0] |= 4;
  mem.store32(cpu.r[31]+444,static_cast<uint32_t>(cpu.r[0]));
  cpu.lr=0x98c990;
  return 0x988b0c;
}
// 0x988b0c: a fixed 32-entry circular free-list head initializer.
uint64_t heap_list_heads_00988b0c(Cpu& cpu,Memory& mem) {
  cpu.r[0] = 32;
  cpu.r[3] += 36;
  cpu.r[11] = 0;
  for (uint32_t i=0; i<32; ++i) {
    cpu.r[0] = static_cast<uint32_t>(cpu.r[11]<<3);
    cpu.r[11]++;
    cpu.r[0] = cpu.r[3]+cpu.r[0];
    cpu.r[9] = static_cast<uint32_t>(cpu.r[0]);
    mem.store32(cpu.r[9]+8,static_cast<uint32_t>(cpu.r[0]));
    mem.store32(cpu.r[9]+12,static_cast<uint32_t>(cpu.r[0]));
  }
  return cpu.lr;
}
// Resume after the list-head helper. 0x988aa8 is the next unresolved helper.
uint64_t heap_after_00988b0c(Cpu& cpu, Memory& mem) {
  if (cpu.lr != 0x98c990) throw std::runtime_error("Unexpected list-head helper return");
  cpu.r[0]=560;
  cpu.r[5]=cpu.r[27]+cpu.r[30];
  mem.store32(cpu.r[31]+440,560);
  mem.store32(cpu.r[31]+436,560);
  cpu.r[4]=mem.load32(cpu.r[28]+4);
  cpu.r[3]=cpu.r[31];
  cpu.r[4]=static_cast<uint32_t>(cpu.r[4]) & ~uint64_t(3);
  cpu.r[4]=cpu.r[25]+cpu.r[4]-8;
  cpu.r[5]=cpu.r[5]-cpu.r[4];
  cpu.r[4]=static_cast<uint32_t>(cpu.r[4]);
  cpu.r[5]=static_cast<uint32_t>(cpu.r[5]-48);
  cpu.lr=0x98c9c8;
  return 0x988aa8;
}
}
