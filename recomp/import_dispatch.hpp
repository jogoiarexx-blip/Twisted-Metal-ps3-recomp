#pragma once
#include "import_table.hpp"
#include "tls_hle.hpp"
#include "spurs_hle.hpp"
#include <stdexcept>
#include <string>
namespace tmrecomp {
// Address-to-NID resolution is derived from the RPCS3 session for BCUS98106 v1.06.
// This skips the unresolved PS3 import stub, as a native host import dispatcher would.
inline uint64_t dispatch_import(uint64_t address, Cpu &cpu, Memory &mem) {
  const Import* entry=find_import(address);
  if(!entry) throw std::runtime_error("unmapped PPU import at " + std::to_string(address));
  if(entry->nid==0x744680a2 && std::string(entry->module)=="sysPrxForUser") {
    const uint64_t resume=cpu.lr;
    sys_initialize_tls_main(cpu,mem);
    return resume;
  }
  if(std::string(entry->module)=="cellSpurs") {
    if(entry->nid==0x7fdf4fefu) return spurs_barrier_initialize(cpu,mem);
    if(entry->nid==0x9fcb567bu) return spurs_get_taskset_info(cpu,mem);
  }
  throw std::runtime_error(std::string("unimplemented HLE: ")+entry->module+"::"+entry->name);
}
}
