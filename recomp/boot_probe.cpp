#include <algorithm>
#include "runtime.hpp"
#include "import_dispatch.hpp"
#include "lv2_memory.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
using namespace tmrecomp;
static uint64_t be64(const std::vector<uint8_t>&v,size_t at) {
  if(at+8>v.size())throw std::runtime_error("ELF header truncated");
  uint64_t x=0;for(int i=0;i<8;++i)x=(x<<8)|v[at+i];return x;
}
static uint32_t be32(const std::vector<uint8_t>&v,size_t at) {
  if(at+4>v.size())throw std::runtime_error("ELF header truncated");
  uint32_t x=0;for(int i=0;i<4;++i)x=(x<<8)|v[at+i];return x;
}
int main(int argc,char**argv) {
 try {
  if(argc!=2){std::cerr<<"Usage: boot_probe EBOOT-update.elf\n";return 2;}
  std::ifstream in(argv[1],std::ios::binary);
  if(!in)throw std::runtime_error("Cannot open ELF");
  std::vector<uint8_t> elf((std::istreambuf_iterator<char>(in)),{});
  if(elf.size()<64 || elf[0]!=0x7f || elf[1]!='E' || elf[2]!='L' || elf[3]!='F' || elf[4]!=2 || elf[5]!=2 || elf[18]!=0 || elf[19]!=21 || be64(elf,24)!=0xf13170)throw std::runtime_error("Not the expected PPU ELF entry");
  Memory mem(0,0x4000000);
  auto phoff=be64(elf,32);auto phsize=(elf.at(54)<<8)|elf.at(55);auto count=(elf.at(56)<<8)|elf.at(57);
  if(phsize<56 || phoff>elf.size() || size_t(count)> (elf.size()-phoff)/phsize)throw std::runtime_error("Invalid program headers");
  for(int i=0;i<count;++i) {
    auto p=phoff+i*phsize;
    if(be32(elf,p)!=1)continue;
    auto offset=be64(elf,p+8),vaddr=be64(elf,p+16),filesz=be64(elf,p+32),memsz=be64(elf,p+40);
    if(offset>elf.size() || filesz>elf.size()-offset || memsz<filesz || vaddr>mem.bytes.size() || memsz>mem.bytes.size()-vaddr)throw std::runtime_error("Invalid LOAD segment");
    std::copy_n(elf.begin()+offset,filesz,mem.bytes.begin()+vaddr);
  }
  Cpu cpu;cpu.r[1]=0x2000000;
  // Boot harness inputs: the PS3 loader supplies these before the entry function.
  // Use this ELF's PT_TLS fields and a representative main thread ID.
  uint64_t tls_addr=0,tls_file=0,tls_size=0;
  for(int i=0;i<count;++i) { auto p=phoff+i*phsize; if(be32(elf,p)==7) { tls_addr=be64(elf,p+16);tls_file=be64(elf,p+32);tls_size=be64(elf,p+40); } }
  if(!tls_addr || !tls_size) throw std::runtime_error("Missing PT_TLS");
  cpu.r[7]=0x01000000;cpu.r[8]=tls_addr;cpu.r[9]=tls_file;cpu.r[10]=tls_size;
  auto toc_expected=mem.load32(0xf13174);
  auto next=entry_00354c80(cpu,mem);
  if(cpu.r[2]!=toc_expected || cpu.r[1]!=0x1ffff90 || mem.load64(cpu.r[1])!=0 || cpu.lr!=0x354ca0 || next!=0x354d88)throw std::runtime_error("Entry state mismatch");
  std::cout<<std::hex<<"ELF entry 0x354c80 -> first call 0x"<<next<<"; TOC 0x"<<cpu.r[2]<<"; SP 0x"<<cpu.r[1]<<"; LR 0x"<<cpu.lr<<"\n";
  next=startup_00354d88(cpu,mem);
  if(cpu.r[1]!=0x1fffef0 || mem.load64(cpu.r[1])!=0x1ffff90 || mem.load64(cpu.r[1]+0xb0)!=0x354ca0 || cpu.r[11]!=0xf9fef8 || mem.load32(cpu.r[11])!=0 || cpu.lr!=0x354de0 || next!=0xc8d094) throw std::runtime_error("Second block state mismatch");
  std::cout<<"Second block 0x354d88 -> call 0x"<<next<<"; SP 0x"<<cpu.r[1]<<"; LR 0x"<<cpu.lr<<"\n";
  if(cpu.r[4]!=tls_addr || cpu.r[5]!=tls_file || cpu.r[6]!=tls_size) throw std::runtime_error("TLS ABI arguments mismatch");
  uint64_t resume=dispatch_import(next,cpu,mem);
  if(resume!=0x354de0) throw std::runtime_error("Import return address mismatch");
  for(uint64_t i=0;i<tls_file;i++) if(mem.bytes[mem.index(0x03000060+i,1)]!=mem.bytes[mem.index(tls_addr+i,1)]) throw std::runtime_error("TLS image mismatch");
  if(cpu.r[13]!=0x03007060) throw std::runtime_error("TLS register mismatch");
  std::cout<<"HLE sys_initialize_tls: r13 0x"<<cpu.r[13]<<"; copied 0x"<<tls_file<<" bytes at 0x3000060\n";
  std::cout<<"HLE return PC 0x"<<resume<<"; import table entries "<<std::dec<<(sizeof(imports)/sizeof(imports[0]))<<std::hex<<"\n";
  next=startup_00354de0(cpu,mem);
  if(next!=0x4ec8d0 || cpu.lr!=0x354e58)throw std::runtime_error("Third block state mismatch");
  std::cout<<"Third block 0x354de0 -> call 0x"<<next<<"; LR 0x"<<cpu.lr<<"\n";
  auto sc=startup_004ec8d0(cpu,mem);
  if(sc!=0x4ec8ec || cpu.r[11]!=0x160 || cpu.r[3]!=0x17dfc48 || cpu.r[1]!=0x1fffe80 || mem.load64(cpu.r[1])!=0x1fffef0 || mem.load64(cpu.r[1]+128)!=0x354e58) throw std::runtime_error("Fourth block state mismatch");
  std::cout<<"Memory setup 0x4ec8d0 -> LV2 syscall 0x"<<cpu.r[11]<<" at PC 0x"<<sc<<"; arg 0x"<<cpu.r[3]<<"\n";
  Lv2Memory lv2;
  if (lv2.dispatch(cpu,mem)!=Lv2Memory::ok || mem.load32(0x17dfc48)!=lv2.total() ||
      mem.load32(0x17dfc4c)!=lv2.available())
    throw std::runtime_error("LV2 0x160 failed to fill guest memory-info");
  std::cout<<"LV2 0x160: total 0x"<<mem.load32(0x17dfc48)<<" available 0x"<<mem.load32(0x17dfc4c)<<"\n";
  sc=startup_after_004ec8ec(cpu,mem);
  if (sc!=0x4ec908 || cpu.r[11]!=0x15c)throw std::runtime_error("LV2 allocation call state mismatch");
  if (lv2.dispatch(cpu,mem)!=Lv2Memory::ok || mem.load32(0x17dfc40)!=Lv2Memory::alloc_base)
    throw std::runtime_error("LV2 0x15c allocation failed");
  if(lv2.available()!=lv2.total()-0x00f00000)
    throw std::runtime_error("LV2 memory quota mismatch");
  std::cout<<"LV2 0x15c: allocated guest 0x"<<mem.load32(0x17dfc40)<<" (0xF00000 bytes, 1MB pages)\n";
  next=startup_after_004ec908(cpu,mem);
  if (next!=0x98c8c0 || cpu.r[3]!=Lv2Memory::alloc_base || cpu.r[4]!=0xf00000 || cpu.lr!=0x4ec92c)
    throw std::runtime_error("Helper 0x98c8c0 call state mismatch");
  std::cout<<"Heap allocation 0x"<<next<<" -> ";
  next=heap_start_0098c8c0(cpu,mem);
  if (next!=0x988b78 || cpu.lr!=0x98c8f4) throw std::runtime_error("Heap prologue mismatch");
  std::cout<<"init helper 0x"<<next<<"\n";
  next=heap_helper_00988b78(cpu,mem);
  if (next!=0x98c8f4) throw std::runtime_error("Allocator init helper did not return");
  next=heap_after_00988b78(cpu,mem);
  if (next!=0x98769c || cpu.lr!=0x98c954)throw std::runtime_error("Heap size/alignment checks failed");
  std::cout<<"Allocator descriptor initialized; memset at 0x"<<next<<"\n";
  next=heap_memset_0098769c(cpu,mem);
  if (next!=0x98c954)throw std::runtime_error("Guest memset returned unexpectedly");
  next=heap_after_0098769c(cpu,mem);
  if (next!=0x988b0c)throw std::runtime_error("Heap header initialization failed");
  std::cout<<"Heap header ready; list-head helper at 0x"<<next<<"\n";
  next=heap_list_heads_00988b0c(cpu,mem);
  if (next!=0x98c990)throw std::runtime_error("List-head initialization failed");
  next=heap_after_00988b0c(cpu,mem);
  if (next!=0x988aa8 || cpu.lr!=0x98c9c8)throw std::runtime_error("Heap continuation mismatch");
  std::cout<<"NEXT: helper 0x"<<next<<" (NOT recompiled). No menu or gameplay yet.\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}
