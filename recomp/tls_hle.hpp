#pragma once
#include "runtime.hpp"
#include <stdexcept>
namespace tmrecomp {
// Incomplete model of sysPrxForUser::sys_initialize_tls (NID 0x744680a2).
// Allocates the main thread TLS image; process-wide mutex/atexit setup remains pending.
inline void sys_initialize_tls_main(Cpu& cpu, Memory& mem) {
  if (cpu.r[13]) return;
  const uint64_t image=cpu.r[4], file_size=cpu.r[5], mem_size=cpu.r[6];
  if (mem_size<file_size || mem_size+0x30>0x40000 || image>0xffffffffULL) throw std::runtime_error("invalid TLS arguments");
  constexpr uint64_t block=0x03000000;
  // s_tls_area = block+0x30, ppu_alloc_tls() returns it, then gpr13 = area+0x7030.
  constexpr uint64_t area=block+0x30;
  for(uint64_t i=0;i<0x30;i++)mem.store8(area+i,0);
  for(uint64_t i=0;i<file_size;i++)mem.store8(area+0x30+i,mem.bytes[mem.index(image+i,1)]);
  for(uint64_t i=file_size;i<mem_size;i++)mem.store8(area+0x30+i,0);
  cpu.r[13]=area+0x7030;
}
}
