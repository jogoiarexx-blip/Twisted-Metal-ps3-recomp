#pragma once
/* Crossfeed v0.11: minimal guest-memory models for two SPURS NIDs present in
 * BCUS98106 update 1.06. Semantics/offsets checked against ps3recomp v0.14.0
 * libs/spurs/cellSpurs.c and spurs_taskset.h (MIT). This is NOT a SPU scheduler.
 * Uses the existing big-endian Memory accessor layer; never reports success
 * without writing the output it promises.
 */
#include "runtime.hpp"
#include <cstdint>
namespace tmrecomp {
constexpr uint32_t spurs_err_null = 0x80410731u;
constexpr uint32_t spurs_err_align = 0x80410730u;
constexpr uint32_t spurs_err_inval = 0x80410722u;
inline uint64_t spurs_status(uint32_t status) {
  return static_cast<uint64_t>(static_cast<int64_t>(static_cast<int32_t>(status)));
}
inline uint64_t spurs_barrier_initialize(Cpu& cpu, Memory& mem) {
  uint32_t taskset = static_cast<uint32_t>(cpu.r[3]);
  uint32_t barrier = static_cast<uint32_t>(cpu.r[4]);
  uint32_t total = static_cast<uint32_t>(cpu.r[5]);
  uint32_t rc = 0;
  if (!taskset || !barrier) rc = spurs_err_null;
  else if ((taskset & 127u) || (barrier & 127u)) rc = spurs_err_align;
  else if (!total || total > 128u) rc = spurs_err_inval;
  else {
    // Preflight the complete destination before touching any word.
    mem.index(barrier, 128);
    for (uint32_t off=0; off<128; off+=8) mem.store64(uint64_t(barrier)+off, 0);
    mem.store32(uint64_t(barrier)+4, total);
    mem.store32(uint64_t(barrier)+0x34, taskset);
  }
  cpu.r[3] = spurs_status(rc);
  return cpu.lr;
}
inline uint64_t spurs_get_taskset_info(Cpu& cpu, Memory& mem) {
  uint32_t taskset = static_cast<uint32_t>(cpu.r[3]);
  uint32_t info = static_cast<uint32_t>(cpu.r[4]);
  uint32_t rc = 0;
  if (!taskset || !info) rc = spurs_err_null;
  else if (taskset & 127u) rc = spurs_err_align;
  else {
    // Includes offsets 0x68, 0x74 and 0x1890 in the taskset, plus a
    // 0x2420-byte result buffer. Writes are guest big endian.
    mem.index(taskset + uint64_t(0x1890), 4);
    mem.index(info, 0x2420);
    uint64_t args = mem.load64(uint64_t(taskset)+0x68);
    uint32_t wid = mem.load32(uint64_t(taskset)+0x74);
    uint32_t size = mem.load32(uint64_t(taskset)+0x1890);
    for (uint32_t off=0; off<0x2420; off+=4) mem.store32(uint64_t(info)+off, 0);
    mem.store64(uint64_t(info)+0x2400, args);
    mem.store32(uint64_t(info)+0x2408, wid);
    mem.store32(uint64_t(info)+0x240C, 0);
    mem.store32(uint64_t(info)+0x241C, size);
  }
  cpu.r[3] = spurs_status(rc);
  return cpu.lr;
}
}
