#include "runtime.hpp"
#include "import_dispatch.hpp"
#include <iostream>
#include <cassert>

using namespace tmrecomp;

int main() {
    std::cout << "Running sysPrx & GCM HLE tests...\n";

    Memory mem(0, 0x100000);
    Cpu cpu;

    // Test 1: sys_ppu_thread_once (NID 0xa3e3be68, addr 0x00c8d28c)
    uint32_t once_ctrl = 0x1000;
    mem.store32(once_ctrl, 0); // Not run yet
    cpu.r[3] = once_ctrl;
    cpu.r[4] = 0x2000; // Mock init OPD
    cpu.lr   = 0x3000;

    uint64_t next_pc = dispatch_import(0x00c8d28c, cpu, mem);
    assert(next_pc == 0x3000);
    assert(cpu.r[3] == 0); // CELL_OK
    assert(mem.load32(once_ctrl) == 1); // Flipped to done

    // Second call: already done
    cpu.r[3] = once_ctrl;
    cpu.r[4] = 0x2000;
    cpu.lr   = 0x4000;
    next_pc = dispatch_import(0x00c8d28c, cpu, mem);
    assert(next_pc == 0x4000);
    assert(cpu.r[3] == 0);
    assert(mem.load32(once_ctrl) == 1);

    // Test 2: sys_prx_register_library (NID 0x42b23552, addr 0x00c8cf44)
    cpu.r[3] = 0x5000; // Lib descriptor
    cpu.lr   = 0x6000;
    next_pc = dispatch_import(0x00c8cf44, cpu, mem);
    assert(next_pc == 0x6000);
    assert(cpu.r[3] == 0); // CELL_OK

    // Test 3: cellGcmMapEaIoAddressWithFlags (NID 0x626e8518, addr 0x00c8a1c4)
    cpu.r[3] = 0x40000000; // EA
    cpu.r[4] = 0x10000000; // IO
    cpu.r[5] = 0x01000000; // Size
    cpu.r[6] = 0;          // Flags
    cpu.lr   = 0x7000;
    next_pc = dispatch_import(0x00c8a1c4, cpu, mem);
    assert(next_pc == 0x7000);
    assert(cpu.r[3] == 0); // CELL_OK

    std::cout << "PASS: sys_ppu_thread_once, sys_prx_register_library, and cellGcmMap HLE tests passed!\n";
    return 0;
}
