#!/usr/bin/env python3
"""Cross a recompiled module's firmware imports with the toolkit's HLE entries.

Inputs
  module_imports.c   the C the toolkit emits for the import thunks; each is
                     annotated `/* <library> :: NID 0xNNNNNNNN */`
  hle.txt            one registered entry per line: `<NID>\t<library>\t<name>`,
                     produced by compiling tools/hle_dump.c against the toolkit
                     and running it
  pspsdk/src/**/*.S  optional; supplies human names for the NIDs that are not
                     implemented (they are not in hle.txt by definition)

Outputs
  data/<module>-hle-cov.json      families, covered/missing per library
  docs/progress/hle-missing.md    the missing functions, named, by family

No game data is read: an import list is the set of firmware entry points a game
calls, which is what the toolkit reports and nothing else.
"""
import argparse, collections, json, os, re, sys

FAMILIES = [
    ("System core", ["ThreadManForUser", "SysMemUserForUser", "Kernel_Library", "UtilsForUser",
                     "InterruptManager", "ModuleMgrForUser", "LoadExecForUser", "sceSuspendForUser",
                     "StdioForUser"]),
    ("Audio", ["sceSasCore", "sceAudio", "sceAtrac3plus"]),
    ("Video / UMD", ["scePsmfPlayer", "sceMpeg", "sceUmdUser"]),
    ("Font", ["sceLibFont"]),
    ("Save / utility", ["sceUtility"]),
    ("Network", ["sceNetAdhoc", "sceNetAdhocMatching", "sceNetAdhocctl", "sceNet", "sceWlanDrv"]),
    ("Input / display / GE", ["sceGe_user", "sceDisplay", "sceCtrl"]),
    ("Files", ["IoFileMgrForUser"]),
    ("Misc", ["sceRtc", "scePower", "sceImpose"]),
]

def parse_imports(path):
    txt = open(path, errors="replace").read()
    return [(lib.strip(), nid) for lib, nid in
            re.findall(r"/\* ([^:\n]+?) :: NID 0x([0-9A-F]{8}) \*/", txt)]

def parse_hle(path):
    out = {}
    for line in open(path, errors="replace"):
        if line.startswith("#"): continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 3: out[parts[0].upper()] = (parts[1], parts[2])
    return out

def parse_pspsdk(root):
    names = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".S"): continue
            txt = open(os.path.join(dirpath, f), errors="replace").read()
            for lib, nid, nom in re.findall(
                    r'IMPORT_FUNC[ \t]+"([^"]+)"[ \t]*,[ \t]*(0x[0-9A-Fa-f]+)[ \t]*,[ \t]*(\w+)', txt):
                names[(lib, nid[2:].upper())] = nom
    return names

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imports", help="the module's *_imports.c")
    ap.add_argument("hle", help="hle.txt from tools/hle_dump.c")
    ap.add_argument("--pspsdk", default=None, help="pspsdk checkout, for naming what is missing")
    ap.add_argument("--module", default="locoroco")
    ap.add_argument("--reached", default="", help="NID hex list seen unimplemented at run time, comma separated")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--source-ref", help="exact Git revision of the measured checkout")
    ap.add_argument("--source-label", default="Measured checkout")
    ap.add_argument("--snapshot", help="output stem; defaults to the module name")
    ap.add_argument("--observed-source", help="exact runtime revision for the supplied sampled log")
    a = ap.parse_args()
    for option, value in [("--source-ref", a.source_ref), ("--observed-source", a.observed_source)]:
        if value is not None and not re.fullmatch(r"[0-9a-fA-F]{40}", value):
            ap.error(option + " must be an exact 40-digit Git revision")
    stem = a.snapshot or a.module

    pairs = parse_imports(a.imports)
    if not pairs or len(pairs) != len(set(pairs)):
        ap.error("the import list must be nonempty and have no duplicate library/NID pairs")
    hle = parse_hle(a.hle)
    names = parse_pspsdk(a.pspsdk) if a.pspsdk else {}
    reached = {n.strip().upper() for n in a.reached.split(",") if n.strip()}

    cov = collections.defaultdict(lambda: [0, 0, []])
    for lib, nid in pairs:
        c = cov[lib]
        if nid in hle: c[0] += 1
        else: c[1] += 1; c[2].append(nid)

    tot = sum(v[0] + v[1] for v in cov.values()); tot_c = sum(v[0] for v in cov.values())
    os.makedirs(f"{a.outdir}/data", exist_ok=True)
    os.makedirs(f"{a.outdir}/docs/progress", exist_ok=True)
    lib2fam = {l: f for f, ls in FAMILIES for l in ls}
    unknown = sorted(set(cov) - set(lib2fam))
    if unknown:
        ap.error("libraries without a family: " + ", ".join(unknown))
    atteints = sorted((lib, nid) for lib, nid in pairs if nid in reached and nid not in hle)
    json.dump({"module": a.module, "imports": tot, "covered": tot_c,
               "metric": "registered_hle_handler_availability",
               "source": {"revision": a.source_ref, "label": a.source_label},
               "observations": {"runtime_revision": a.observed_source, "rate_limited": True},
               "registered": {nid: {"library": lib, "name": hle[nid][1]}
                              for lib, nid in pairs if nid in hle},
               "familles": FAMILIES, "cov": {k: v[:2] for k, v in cov.items()},
               "missing": {k: v[2] for k, v in cov.items()},
               "atteints": atteints},
              open(f"{a.outdir}/data/{stem}-hle-cov.json", "w"), indent=1)

    par_fam = collections.defaultdict(list)
    for lib, nids in cov.items():
        for nid in nids[2]:
            par_fam[lib2fam.get(lib, "Other")].append((lib, nid, names.get((lib, nid), "")))
    out = [f"# Missing firmware functions - {a.module}", "",
           f"**{tot - tot_c} of {tot} imported firmware functions have no registered handler** "
           f"({tot_c} have a registered handler, {100.0*tot_c/tot:.1f}%). Registration is not proof of firmware fidelity. Names come from pspsdk where it "
           f"declares the NID; other entries remain unnamed in this report.", "",
           "`*` marks a missing handler observed in the sampled bring-up log. The log is rate-limited; "
           "this is not a complete reachability report or proof of the current blocker.", "",
           "Regenerate: `tools/hle_coverage.py` (see README).", ""]
    for fam, items in sorted(par_fam.items(), key=lambda x: -len(x[1])):
        out += [f"## {fam} ({len(items)})", "", "| library | NID | function |", "|---|---|---|"]
        for lib, nid, nom in sorted(items, key=lambda x: (x[0], x[2] or "zz")):
            star = " *" if (lib, nid) in atteints else ""
            out.append(f"| {lib} | `0x{nid}` | {nom or '(not named in pspsdk)'}{star} |")
        out.append("")
    open(f"{a.outdir}/docs/progress/{'hle-missing.md' if not a.snapshot else 'hle-missing-' + stem + '.md'}", "w").write("\n".join(out))
    print(f"{a.module}: {tot_c}/{tot} registered ({100.0*tot_c/tot:.1f}%), "
          f"{tot-tot_c} missing, {len(atteints)} reached at run time")

if __name__ == "__main__":
    main()
