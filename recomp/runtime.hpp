#pragma once
#include <cstdint>
#include <vector>
#include <stdexcept>
namespace tmrecomp {
struct Cpu { uint64_t r[32]{}; uint64_t lr{}; bool ca{}; };
struct Memory {
  uint64_t base;
  std::vector<uint8_t> bytes;
  Memory(uint64_t base_, size_t size):base(base_),bytes(size){}
  size_t index(uint64_t addr, size_t count) const {
    if (addr < base || addr - base > bytes.size() || count > bytes.size() - (addr-base)) throw std::out_of_range("PPU memory address");
    return static_cast<size_t>(addr-base);
  }
  uint32_t load32(uint64_t addr) const {
    auto n=index(addr,4);return uint32_t(bytes[n])<<24 | uint32_t(bytes[n+1])<<16 | uint32_t(bytes[n+2])<<8 | bytes[n+3];
  }
  uint64_t load64(uint64_t addr) const {
    auto n=index(addr,8);uint64_t v=0;for(int i=0;i<8;++i)v=(v<<8)|bytes[n+i];return v;
  }
  void store64(uint64_t addr,uint64_t v) {
    auto n=index(addr,8);for(int i=0;i<8;++i)bytes[n+i]=static_cast<uint8_t>(v>>(56-8*i));
  }
  void store32(uint64_t addr,uint32_t v) {
    auto n=index(addr,4);for(int i=0;i<4;++i)bytes[n+i]=static_cast<uint8_t>(v>>(24-8*i));
  }
  void store8(uint64_t addr,uint8_t v) {bytes[index(addr,1)]=v;}
};
uint64_t entry_00354c80(Cpu&,Memory&);
uint64_t startup_00354d88(Cpu&,Memory&);
uint64_t startup_00354de0(Cpu&,Memory&);
void fn_009946c0(Cpu&,Memory&);
void fn_009946e0(Cpu&,Memory&);
void fn_00994838(Cpu&,Memory&);
}
