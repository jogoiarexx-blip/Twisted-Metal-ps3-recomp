import os
import sys
import time
import subprocess
import threading

def main():
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    elf = r"E:\01 jogos\Emulador ps3\01 roms\twisted\PS3_GAME\USRDIR\EBOOT.elf"
    exe = r"D:\Twisted metal\twistedmetal.exe"
    log_path = r"D:\Twisted metal\runner_live.log"

    env = os.environ.copy()
    env["TM_TRACE"] = "0"
    env["GCM_SUBCH1_3D"] = "1"
    env["TM_GAMELOG"] = "1"
    env["RSX_LIVE_DRAW"] = "1"
    env["PAD_AUTOPRESS"] = "1"
    env["PAD_FORCE_FOCUS"] = "1"
    env["PAD_STICK"] = "128,0,128,128,25,65"
    env["PAD_SCRIPT"] = "26:0x0200,28:0x0200,30:0x0200,32:0x0200,34:0x0400,36:0x0800,38:0x4000"
    env["TM_SKIP_BANKUNLOAD"] = "1"
    env["TM_BRB_SILENT"] = "1"
    env["TM_BRB_PARK"] = "1"
    env["TM_BRB_ACK"] = "1"
    env["TM_JQ_WORKERS"] = "4"
    # TM_LOADDONE (forced load-complete probe) is opt-in: when forced it made ~1/3 of boots diverge.
    if "TM_LOADDONE" in os.environ:
        env["TM_LOADDONE"] = os.environ["TM_LOADDONE"]
    env["TM_VIDEO_MODES"] = "2,1"
    # Do not inherit stale TM_FORCEWORLD or TM_FORCESTATE unless explicitly requested with TM_FORCE_ENABLE=1
    if os.environ.get("TM_FORCE_ENABLE") == "1":
        if "TM_FORCEWORLD" in os.environ: env["TM_FORCEWORLD"] = os.environ["TM_FORCEWORLD"]
        if "TM_FORCESTATE" in os.environ: env["TM_FORCESTATE"] = os.environ["TM_FORCESTATE"]
    else:
        env.pop("TM_FORCEWORLD", None)
        env.pop("TM_FORCESTATE", None)
    env["TM_RSX_W"] = "1280"
    env["TM_RSX_H"] = "720"
    env["TM_LIVE_DUMP"] = "1"
    env["TM_FBDUMP"] = "3"
    env["TM_MAINSTACK"] = "2"
    env["TM_WATCHDOG_SECS"] = "0"  # disable watchdog to avoid any SuspendThread lock contention

    # Clean old dumps
    for p in os.listdir(r"D:\Twisted metal"):
        if (p.startswith("surf_arena_") or p.startswith("surf_menu_")) and p.endswith(".ppm"):
            try: os.remove(os.path.join(r"D:\Twisted metal", p))
            except: pass

    with open(log_path, "w", encoding="utf-8", errors="replace", buffering=1) as log_f:
        p = subprocess.Popen(
            [exe, elf],
            cwd=r"D:\Twisted metal",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        t0 = time.time()
        print(f"Started {exe} (PID {p.pid}) for {duration} seconds...")

        def reader():
            for line in p.stdout:
                log_f.write(line)
                if any(k in line for k in ("[live]", "ARENA", "3D", "WorldLoader", "FATAL", "ERROR", "CRASH", "Ui", "Intro", "state", "Movie", "[ui]", "[states]", "[forceworld]", "[probe]", "CommonBank")):
                    print(line.strip())

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        while time.time() - t0 < duration:
            if p.poll() is not None:
                print(f"Process exited early with code {p.returncode}")
                break
            time.sleep(0.5)

        if p.poll() is None:
            print("Time limit reached. Terminating process cleanly...")
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()

        t.join(timeout=2)
        print("Done. Total run time: %.1fs" % (time.time() - t0))

if __name__ == "__main__":
    main()
