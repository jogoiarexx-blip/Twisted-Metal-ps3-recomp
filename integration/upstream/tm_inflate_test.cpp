// All fixture bytes are synthetic (no game assets).
#include <cstdint>
#include <cstdio>
#include <cstring>
extern "C" int tm_inflate(uint8_t*, uint32_t, const uint8_t*, uint32_t);
static const uint8_t stored[] = {0x78,0x01,0x01,0x05,0x00,0xfa,0xff,0x48,0x45,0x4c,0x4c,0x4f,0x04,0x4c,0x01,0x75};
static const uint8_t fast[] = {0x78,0x01,0xf3,0x70,0xf5,0xf1,0xf1,0xf7,0xa0,0x2d,0x01,0x00,0xba,0xb3,0x1d,0x11};
static const uint8_t maximum[] = {0x78,0xda,0xf3,0x70,0xf5,0xf1,0xf1,0xf7,0xa0,0x2d,0x01,0x00,0xba,0xb3,0x1d,0x11};
static const uint8_t raw[] = {0xf3,0x70,0xf5,0xf1,0xf1,0xf7,0xa0,0x2d,0x01,0x00};
int main() {
  uint8_t output[100]{};
  int failures = 0;
  if (tm_inflate(output, 5, stored, sizeof(stored)) != 5 || std::memcmp(output, "HELLO", 5)) ++failures;
  struct Fixture { const uint8_t* data; uint32_t length; };
  const Fixture fixtures[]={{fast,sizeof(fast)},{maximum,sizeof(maximum)},{raw,sizeof(raw)}};
  for (auto fixture:fixtures) {
    std::memset(output, 0, sizeof output);
    int count=tm_inflate(output,sizeof output,fixture.data,fixture.length);
    if(count!=100) { ++failures; continue; }
    for(size_t i=0;i<100;i+=5) if(std::memcmp(output+i,"HELLO",5)) { ++failures; break; }
  }
  if (tm_inflate(output,1,maximum,sizeof maximum) != -1) ++failures;
  if (tm_inflate(output,100,nullptr,0) != -1) ++failures;
  std::printf("synthetic inflater: %s\n",failures?"FAIL":"PASS");
  return failures?1:0;
}
