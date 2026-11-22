// ===========================================================================
// sysPrx & System HLE Dispatchers (Twisted Metal BCUS98106)
// ===========================================================================
// Crossfed from sp00nznet/twistedmetal analysis:
// - sys_ppu_thread_once (0xA3E3BE68): Unblocks FIOS file scheduler init
// - sys_prx_register_library (0x42B23552): Static library registration
// - cellGcmMapEaIoAddressWithFlags (0x626E8518): RSX GCM address mapping
// ===========================================================================
#pragma once
#include "runtime.hpp"
#include <cstdint>
#include <cstdio>

namespace tmrecomp {

// sysPrxForUser 0xA3E3BE68: sys_ppu_thread_once(once_ctrl, init_opd)
// Twisted Metal's FIOS file scheduler relies on this to initialize its
// internal synchronization structures (mutexes and condition variables).
inline uint64_t sys_ppu_thread_once_hle(Cpu &cpu, Memory &mem) {
  const uint32_t ctrl_ptr = static_cast<uint32_t>(cpu.r[3]);
  const uint32_t opd_ptr  = static_cast<uint32_t>(cpu.r[4]);

  if (ctrl_ptr) {
    const uint32_t current_val = mem.load32(ctrl_ptr);
    if (current_val == 0) {
      mem.store32(ctrl_ptr, 1);
      // In a full runtime, opd_ptr is invoked here. In harness mode,
      // setting the control word unblocks threads expecting initialization.
      (void)opd_ptr;
    }
  }

  cpu.r[3] = 0; // CELL_OK
  return cpu.lr;
}

// sysPrxForUser 0x42B23552: sys_prx_register_library(lib)
// Acknowledges library export registration.
inline uint64_t sys_prx_register_library_hle(Cpu &cpu) {
  cpu.r[3] = 0; // CELL_OK
  return cpu.lr;
}

// cellGcmSys 0x626E8518: cellGcmMapEaIoAddressWithFlags(ea, io, size, flags)
// Maps guest effective address (EA) to RSX IO address.
inline uint64_t cellGcmMapEaIoAddressWithFlags_hle(Cpu &cpu) {
  // Returns CELL_OK (0) for mock mappings.
  cpu.r[3] = 0; // CELL_OK
  return cpu.lr;
}

// cellGcmSys 0x63441CB4: cellGcmMapEaIoAddress(ea, io, size)
inline uint64_t cellGcmMapEaIoAddress_hle(Cpu &cpu) {
  cpu.r[3] = 0; // CELL_OK
  return cpu.lr;
}

// sysPrxForUser 0x2F85C0EF: sys_lwmutex_create(lwmutex, attr)
// Initializes a light-weight mutex protecting the heap allocator.
inline uint64_t sys_lwmutex_create_hle(Cpu &cpu, Memory &mem) {
  const uint32_t mutex_ptr = static_cast<uint32_t>(cpu.r[3]);
  if (mutex_ptr) {
    // Initialize guest lwmutex structure with clean non-zero handle
    mem.store32(mutex_ptr, 0);     // lock_var
    mem.store32(mutex_ptr + 4, 1); // attribute / valid flag
  }
  cpu.r[3] = 0; // CELL_OK
  return cpu.lr;
}

} // namespace tmrecomp
