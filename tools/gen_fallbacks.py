import re
from pathlib import Path

hle_cpp = Path(r"d:\upstream\sp00nznet-twistedmetal\src\hle_extra.cpp")
text = hle_cpp.read_text(encoding="utf-8", errors="ignore")

funcs = sorted(set(re.findall(r"\b(func_[0-9A-Fa-f]+_lifted)\b", text)))

lines = [
    "/* lifted_fallbacks.cpp -- Weak fallback definitions for tracing hooks. */",
    '#include "ppu_context.h"',
    "",
    '#define DEFINE_LIFTED_FALLBACK(fn) \\',
    '    void fn(ppu_context* ctx) __attribute__((weak)); \\',
    '    void fn(ppu_context* ctx) { (void)ctx; }',
    ""
]
for fn in funcs:
    lines.append(f"DEFINE_LIFTED_FALLBACK({fn})")

out_file = Path(r"d:\upstream\sp00nznet-twistedmetal\src\gen\lifted_fallbacks.cpp")
out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out_file} with {len(funcs)} definitions.")
