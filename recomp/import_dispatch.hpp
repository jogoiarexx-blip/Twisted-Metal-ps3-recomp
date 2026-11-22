#pragma once
#include "import_table.hpp"
#include "tls_hle.hpp"
#include "spurs_hle.hpp"
#include "sysprx_hle.hpp"
#include <stdexcept>
#include <string>
namespace tmrecomp {
// Address-to-NID resolution is derived from the RPCS3 session for BCUS98106 v1.06.
// This skips the unresolved PS3 import stub, as a native host import dispatcher would.
inline uint64_t dispatch_import(uint64_t address, Cpu &cpu, Memory &mem) {
  const Import* entry=find_import(address);
  if(!entry) throw std::runtime_error("unmapped PPU import at " + std::to_string(address));
  if(std::string(entry->module)=="sysPrxForUser") {
    if(entry->nid==0x744680a2u) {
      const uint64_t resume=cpu.lr;
      sys_initialize_tls_main(cpu,mem);
      return resume;
    }
    if(entry->nid==0xa3e3be68u) return sys_ppu_thread_once_hle(cpu,mem);
    if(entry->nid==0x42b23552u) return sys_prx_register_library_hle(cpu);
    if(entry->nid==0x2f85c0efu) return sys_lwmutex_create_hle(cpu,mem);
  }
  if(std::string(entry->module)=="cellSpurs") {
    if(entry->nid==0x7fdf4fefu) return spurs_barrier_initialize(cpu,mem);
    if(entry->nid==0x9fcb567bu) return spurs_get_taskset_info(cpu,mem);
  }
  if(std::string(entry->module)=="cellGcmSys") {
    if(entry->nid==0x626e8518u) return cellGcmMapEaIoAddressWithFlags_hle(cpu);
    if(entry->nid==0x63441cb4u) return cellGcmMapEaIoAddress_hle(cpu);
  }
  throw std::runtime_error(std::string("unimplemented HLE: ")+entry->module+"::"+entry->name);
}
}
