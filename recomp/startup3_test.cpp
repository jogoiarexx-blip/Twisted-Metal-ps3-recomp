#include "runtime.hpp"
#include <iostream>
#include <stdexcept>
using namespace tmrecomp;
static void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
static void run(uint64_t a,uint64_t b){
 Memory mem(0,0x10000);Cpu cpu;
 cpu.r[2]=0x9000;mem.store32(0x1000,0x8000); // r2 - 32768 = 0x1000
 cpu.r[28]=0x2000;cpu.r[31]=a;cpu.r[26]=0x3000;cpu.r[30]=b;cpu.r[27]=0xabc12345;
 for(uint64_t i=0;i<a+1;i++)mem.store32(0x2004+i*8,0x1000+i);
 for(uint64_t i=0;i<b+1;i++)mem.store32(0x3004+i*8,0x2000+i);
 auto next=startup_00354de0(cpu,mem);
 require(next==0x4ec8d0 && cpu.lr==0x354e58,"call target/LR mismatch");
 for(uint64_t i=0;i<a+1;i++)require(mem.load32(0x2000+i*4)==0x1000+i,"loop1 copy mismatch");
 for(uint64_t i=0;i<b+1;i++)require(mem.load32(0x3000+i*4)==0x2000+i,"loop2 copy mismatch");
 require(mem.load32(0x8000)==a && mem.load32(0x8004)==0xabc12345,"global state mismatch");
 require(cpu.r[8]==b+1 && cpu.r[5]==0x3000+4*(b+1),"register updates mismatch");
}
int main(){try {for(uint64_t a: {0ULL,1ULL,3ULL,9ULL})for(uint64_t b: {0ULL,1ULL,3ULL,9ULL})run(a,b);std::cout<<"PASS: 16 startup3 copy-loop cases, zero and multiple iterations\n";}catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}}
