#pragma once
#include <cstdint>
#include <vector>
#include <stdexcept>
#include <utility>
namespace tmrecomp {
struct Cpu { uint64_t r[32]{}; uint64_t lr{}; bool ca{}; };
struct Memory {
  uint64_t base;
  std::vector<uint8_t> bytes;
  struct Region { uint64_t base; std::vector<uint8_t> bytes; };
  std::vector<Region> regions;
  Memory(uint64_t base_, size_t size):base(base_),bytes(size){}
  // Executable PT_LOAD/stack remain in bytes; LV2 allocations are sparse guest
  // regions and are not host pointers or writable until explicitly mapped.
  static bool within(uint64_t addr, size_t count, uint64_t start, size_t size) {
    return addr >= start && addr - start <= size && count <= size - (addr-start);
  }
  bool valid(uint64_t addr, size_t count) const {
    if (within(addr,count,base,bytes.size())) return true;
    for (const auto& r : regions)
      if (within(addr,count,r.base,r.bytes.size())) return true;
    return false;
  }
  void map_region(uint64_t addr, size_t size) {
    if (!size || addr > UINT64_MAX-size) throw std::out_of_range("invalid guest mapping");
    if (within(addr,1,base,bytes.size()) ||
        (addr < base && base-addr < size) ||
        (addr >= base && addr-base < bytes.size()))
      throw std::out_of_range("guest mapping overlaps main memory");
    for (const auto& r : regions) {
      if (addr < r.base+r.bytes.size() && r.base < addr+size)
        throw std::out_of_range("guest mapping overlaps existing region");
    }
    // Create before insertion: an allocation failure does not register a mapping.
    Region r{addr,std::vector<uint8_t>(size,0)};
    regions.push_back(std::move(r));
  }
  const uint8_t* address(uint64_t addr,size_t count) const {
    if (within(addr,count,base,bytes.size()))return bytes.data()+static_cast<size_t>(addr-base);
    for (const auto& r : regions)
      if (within(addr,count,r.base,r.bytes.size()))return r.bytes.data()+static_cast<size_t>(addr-r.base);
    throw std::out_of_range("unmapped PPU guest memory");
  }
  uint8_t* address(uint64_t addr,size_t count) {
    return const_cast<uint8_t*>(static_cast<const Memory&>(*this).address(addr,count));
  }
  size_t index(uint64_t addr, size_t count) const {
    if (addr < base || addr - base > bytes.size() || count > bytes.size() - (addr-base)) throw std::out_of_range("PPU memory address");
    return static_cast<size_t>(addr-base);
  }
  uint32_t load32(uint64_t addr) const {
    auto p=address(addr,4);return uint32_t(p[0])<<24 | uint32_t(p[1])<<16 | uint32_t(p[2])<<8 | p[3];
  }
  uint64_t load64(uint64_t addr) const {
    auto p=address(addr,8);uint64_t v=0;for(int i=0;i<8;++i)v=(v<<8)|p[i];return v;
  }
  void store64(uint64_t addr,uint64_t v) {
    auto p=address(addr,8);for(int i=0;i<8;++i)p[i]=static_cast<uint8_t>(v>>(56-8*i));
  }
  void store32(uint64_t addr,uint32_t v) {
    auto p=address(addr,4);for(int i=0;i<4;++i)p[i]=static_cast<uint8_t>(v>>(24-8*i));
  }
  void store8(uint64_t addr,uint8_t v) {*address(addr,1)=v;}
};
uint64_t entry_00354c80(Cpu&,Memory&);
uint64_t startup_00354d88(Cpu&,Memory&);
uint64_t startup_00354de0(Cpu&,Memory&);
uint64_t startup_004ec8d0(Cpu&,Memory&);
uint64_t startup_after_004ec8ec(Cpu&,Memory&);
uint64_t startup_after_004ec908(Cpu&,Memory&);
uint64_t startup_after_004ec928(Cpu&,Memory&);
uint64_t startup_after_004ec934(Cpu&,Memory&);
void fn_009946c0(Cpu&,Memory&);
void fn_009946e0(Cpu&,Memory&);
void fn_00994838(Cpu&,Memory&);
}
