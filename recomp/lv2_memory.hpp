#pragma once
// Focused LV2 0x160/0x15c guest-memory HLE for the BCUS98106 1.06 boot probe.
// Semantics cross-checked with RPCS3 0.0.43 sys_memory.cpp / sys_memory.h.
// Address window follows ps3recomp 0.14.0 sys_memory.c; not a complete LV2 VM.
#include "runtime.hpp"
#include <cstddef>
#include <cstdint>
#include <new>
#include <stdexcept>
#include <vector>

namespace tmrecomp {
class Lv2Memory {
public:
  static constexpr uint32_t user_total_default = 213u * 1024 * 1024;
  static constexpr uint64_t alloc_base = 0x40000000ull;
  static constexpr uint64_t alloc_end  = 0x50000000ull;
  static constexpr uint64_t page_64k = 0x10000ull;
  static constexpr uint64_t page_1m  = 0x100000ull;
  static constexpr uint32_t ok = 0;
  static constexpr uint32_t einval = 0x80010002u;
  static constexpr uint32_t enomem = 0x80010004u;
  static constexpr uint32_t efault = 0x8001000du;
  static constexpr uint32_t ealign = 0x80010010u;
  struct Allocation { uint32_t address, size, page_size; };
private:
  uint32_t total_;
  uint32_t allocated_ = 0;
  uint64_t bump_ = alloc_base;
  std::vector<Allocation> allocations_;

  static bool align_up(uint64_t v, uint64_t alignment, uint64_t& result) {
    if (v > UINT64_MAX - (alignment-1))return false;
    result=(v+alignment-1) & ~(alignment-1);
    return true;
  }
  static void set_result(Cpu& cpu,uint32_t error) {
    // PPC64 system call error codes are 32-bit signed values in r3.
    cpu.r[3] = static_cast<uint64_t>(static_cast<int64_t>(static_cast<int32_t>(error)));
  }
  uint32_t get_user_memory_size(uint64_t out, Memory& mem) {
    // PS3 sys_memory_info_t = { be_u32 total_user_memory, available_user_memory }.
    if (out == 0 || (out & 3) != 0 || !mem.valid(out,8))return efault;
    mem.store32(out,total_);
    mem.store32(out+4,total_-allocated_);
    return ok;
  }
  uint32_t allocate(uint64_t size,uint64_t flags,uint64_t out,Memory& mem) {
    // RPCS3 checks zero size first, then exact flags, then size alignment.
    if (size == 0)return ealign;
    const uint64_t alignment = (flags == 0x400 || flags == 0) ? page_1m :
                               (flags == 0x200 ? page_64k : 0);
    if (!alignment)return einval;
    if (size % alignment)return ealign;
    if (out == 0 || (out & 3) != 0 || !mem.valid(out,4))return efault;
    if (size > total_ - allocated_)return enomem;
    uint64_t addr=0;
    if (!align_up(bump_,alignment,addr) || addr > alloc_end || size > alloc_end - addr)
      return enomem;
    // Never expose a host pointer; only add a mapped guest range on success.
    try {
      allocations_.reserve(allocations_.size()+1);
      mem.map_region(addr,static_cast<size_t>(size));
    } catch(const std::bad_alloc&) {return enomem;}
      catch(const std::length_error&) {return enomem;}
      catch(const std::out_of_range&) {return enomem;}
    const auto a=static_cast<uint32_t>(addr);
    allocations_.push_back({a,static_cast<uint32_t>(size),static_cast<uint32_t>(alignment)});
    bump_=addr+size;
    allocated_+=static_cast<uint32_t>(size);
    mem.store32(out,a);
    return ok;
  }
public:
  explicit Lv2Memory(uint32_t total=user_total_default):total_(total){}
  uint32_t total()const{return total_;}
  uint32_t available()const{return total_-allocated_;}
  const std::vector<Allocation>& allocations()const{return allocations_;}
  uint32_t dispatch(Cpu& cpu,Memory& mem) {
    uint32_t result=einval;
    if (cpu.r[11]==0x160)result=get_user_memory_size(cpu.r[3],mem);
    else if (cpu.r[11]==0x15c)result=allocate(cpu.r[3],cpu.r[4],cpu.r[5],mem);
    else throw std::runtime_error("unsupported LV2 memory syscall");
    set_result(cpu,result);
    return result;
  }
};
} // namespace tmrecomp
