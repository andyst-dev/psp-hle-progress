#!/usr/bin/env python3
"""HLE coverage treemap for a recompiled module (tile area = firmware imports).

Input : JSON produced by crossing the module's imports (locoroco_imports.c) with
        the toolkit's HLE entries (psp_hle_entries()).
Output: a standalone SVG for the repo, or an SVG bound to the theme for a widget.

    python3 hle_treemap.py hle_cov.json docs/progress/hle-coverage.svg
    python3 hle_treemap.py hle_cov.json out.html --widget

The rendered text is ENGLISH: the picture is meant to sit in a repository next to
a README, like pokeheartgold's docs/progress/treemap.svg.

Readability rule: a label is written only when its ESTIMATED width fits its tile
(CHAR_W x size x length plus margins). Otherwise the size steps down, then the
label goes vertical, and only then does the tile carry a number whose name the
legend at the bottom supplies. A tile marked as reached-by-the-run reserves a
band on the right for the ring, so the marker never lands on a word.
"""
import json, os, sys
import xml.etree.ElementTree as ET

VERT, ROUGE, MARQUE = "#1f9d55", "#b3402f", "#111827"

# short, unique library labels: long names cannot fit a small tile
NOMS = {
    "ThreadManForUser": "ThreadMan", "SysMemUserForUser": "SysMem", "Kernel_Library": "KernelLib",
    "UtilsForUser": "Utils", "InterruptManager": "Interrupt", "ModuleMgrForUser": "ModuleMgr",
    "LoadExecForUser": "LoadExec", "sceSuspendForUser": "Suspend", "StdioForUser": "Stdio",
    "sceSasCore": "SasCore", "sceAudio": "Audio", "sceAtrac3plus": "ATRAC3+",
    "scePsmfPlayer": "PsmfPlayer", "sceMpeg": "Mpeg", "sceUmdUser": "UmdUser",
    "sceLibFont": "LibFont", "sceUtility": "Utility", "sceNetAdhoc": "NetAdhoc",
    "sceNetAdhocMatching": "AdhocMatch", "sceNetAdhocctl": "AdhocCtl", "sceNet": "Net",
    "sceWlanDrv": "WlanDrv", "sceGe_user": "Ge", "sceDisplay": "Display", "sceCtrl": "Ctrl",
    "IoFileMgrForUser": "IoFileMgr", "sceRtc": "Rtc", "scePower": "Power", "sceImpose": "Impose",
}
# family names, English, plus the shorter forms a narrow tile can carry
FAM_EN = {"Noyau systeme": "System core", "Audio": "Audio", "Video / UMD": "Video / UMD",
          "Police (font)": "Font", "Sauvegarde / utilitaire": "Save / utility", "Reseau": "Network",
          "Entrees / affichage / GE": "Input / display / GE", "Fichiers": "Files",
          "Divers systeme": "Misc"}
FAM_COURT = {"Input / display / GE": "Input / GE", "Save / utility": "Save / utility",
             "System core": "System core", "Font": "Font", "Misc": "Misc"}
CHAR_W = 0.56          # mean glyph width as a fraction of the size (uppercase-heavy, pessimistic)
PAD = 6                # inner margin of a tile
RING = 13              # band reserved on the right of a tile that carries the ring

def squarify(sizes, x, y, w, h, out):
    """Squarified treemap (Bruls et al.): keep taking into the current band while
    the worst tile ratio improves."""
    sizes = list(sizes)
    if not sizes: return
    if len(sizes) == 1:
        out.append((x, y, w, h)); return
    total = sum(sizes)
    if total <= 0:
        for _ in sizes: out.append((x, y, w, h))
        return
    vertical = w >= h

    def worst(k):
        s = sum(sizes[:k])
        if s <= 0: return float("inf")
        band, along = (w * s / total, h) if vertical else (h * s / total, w)
        r = 0.0
        for sz in sizes[:k]:
            side = along * sz / s if s else 0
            if side <= 0: return float("inf")
            r = max(r, max(band / side, side / band))
        return r

    k, best = 1, worst(1)
    for i in range(2, len(sizes) + 1):
        r = worst(i)
        if r <= best: k, best = i, r
        else: break
    s = sum(sizes[:k])
    if vertical:
        bw = w * s / total
        squarify(sizes[:k], x, y, bw, h, out)
        squarify(sizes[k:], x + bw, y, w - bw, h, out)
    else:
        bh = h * s / total
        squarify(sizes[:k], x, y, w, bh, out)
        squarify(sizes[k:], x, y + bh, w, h - bh, out)

def build(d, w, h, fs=1.0, theme="light"):
    fam, cov, atteints = d["familles"], d["cov"], d["atteints"]
    tot_c = sum(v[0] for v in cov.values()); tot = sum(sum(v) for v in cov.values())
    pct = 100.0 * tot_c / tot
    if theme == "light":
        BG, FG, SUB, TUILE, bord, vide, sep = "#ffffff", "#0f172a", "#64748b", "#f6f8fa", "#dbe1e8", "#ecf0f4", "#e6eaf0"
        txt_dark, txt_light = "#0f172a", "#ffffff"
    else:
        BG, FG, SUB = "none", "var(--foreground)", "var(--muted-foreground)"
        TUILE, bord, vide, sep = "var(--card)", "var(--border)", "var(--accent)", "var(--border)"
        txt_dark, txt_light = "var(--foreground)", "#ffffff"
    M = 26 * fs; TOP = 118 * fs; LEG = 150 * fs
    F = lambda n: n * fs
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" '
         f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Inter,Helvetica,sans-serif">']
    if BG != "none": o.append(f'<rect width="{w:.0f}" height="{h:.0f}" fill="{BG}"/>')
    # header
    o.append(f'<text x="{M:.0f}" y="{46*fs:.0f}" font-size="{F(23):.1f}" font-weight="700" fill="{FG}" '
             f'letter-spacing="-0.4">LocoRoco firmware HLE coverage</text>')
    o.append(f'<text x="{M:.0f}" y="{68*fs:.0f}" font-size="{F(12.5):.1f}" fill="{SUB}">'
             f'UCES00304 &#183; {tot} imported firmware functions &#183; tile area = number of imports</text>')
    o.append(f'<text x="{w-M:.0f}" y="{52*fs:.0f}" font-size="{F(34):.1f}" font-weight="700" fill="{FG}" '
             f'text-anchor="end" letter-spacing="-1">{tot_c}<tspan font-size="{F(20):.1f}" fill="{SUB}">/{tot}</tspan></text>')
    o.append(f'<text x="{w-M:.0f}" y="{72*fs:.0f}" font-size="{F(12.5):.1f}" fill="{SUB}" '
             f'text-anchor="end">{pct:.1f}% implemented &#183; {tot-tot_c} functions to write</text>')
    o.append(f'<line x1="{M:.0f}" y1="{88*fs:.0f}" x2="{w-M:.0f}" y2="{88*fs:.0f}" stroke="{sep}" stroke-width="1"/>')
    o.append(f'<text x="{M:.0f}" y="{106*fs:.0f}" font-size="{F(11.5):.1f}" fill="{SUB}">'
             f'green = implemented &#160;|&#160; red = missing &#160;|&#160; '
             f'<tspan font-weight="600">ring</tspan> = reached by the bring-up run with no implementation '
             f'(sceUmdUser x4, sceRtc x1)</text>')
    # treemap
    fams = [(FAM_EN.get(n, n), [l for l in ls if l in cov]) for n, ls in fam]
    fams = [(n, ls) for n, ls in fams if ls]
    rects = []; squarify([sum(sum(cov[l]) for l in ls) for _, ls in fams],
                         M, TOP, w - 2 * M, h - TOP - LEG, rects)
    at_libs = {l for l, _ in atteints}
    bad, legend = [], []
    numeros = {}
    n = 0
    for (name, ls), (x, y, tw, th) in zip(fams, rects):
        o.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{tw:.2f}" height="{th:.2f}" fill="{TUILE}" '
                 f'stroke="{bord}" stroke-width="1.2" rx="7"/>')
        cc = sum(cov[l][0] for l in ls); tt = sum(sum(cov[l]) for l in ls)
        ratio = f"{cc}/{tt}"
        rw = len(ratio) * CHAR_W * F(12) + 10
        base = FAM_COURT.get(name, name)
        label, lfs = base, F(12.5)
        for cand, cfs in ((name, F(12.5)), (base, F(12.5)), (base, F(11)), (base, F(10))):
            if len(cand) * CHAR_W * cfs <= tw - rw - 22:
                label, lfs = cand, cfs
                break
        else:
            label = ""
        vertical_titre = False
        if not label and tw < 62 and th >= 84:
            # narrow and tall: the family name reads better rotated than truncated
            if len(base) * CHAR_W * F(10) <= th - 2 * PAD:
                label, lfs, vertical_titre = base, F(10), True
        if vertical_titre:
            cx, cy = x + tw / 2 + 3.6, y + th / 2
            o.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="{lfs:.1f}" font-weight="650" fill="{FG}" '
                     f'text-anchor="middle" transform="rotate(-90 {cx:.1f} {cy:.1f})">{label}</text>')
            o.append(f'<text x="{x+tw/2:.1f}" y="{y+th-7:.1f}" font-size="{F(11):.1f}" fill="{SUB}" text-anchor="middle">{ratio}</text>')
        else:
            if label:
                o.append(f'<text x="{x+11:.1f}" y="{y+19*fs+6:.1f}" font-size="{lfs:.1f}" font-weight="650" fill="{FG}">{label}</text>')
            o.append(f'<text x="{x+tw-11:.1f}" y="{y+19*fs+6:.1f}" font-size="{F(12):.1f}" fill="{SUB}" text-anchor="end">{ratio}</text>')
        sr = []; squarify([sum(cov[l]) for l in ls], x + 5, y + 24 * fs + 6, tw - 10, th - (28 * fs + 6), sr)
        for lib, (lx, ly, lw, lh) in zip(ls, sr):
            c2, m2 = cov[lib]
            frac = c2 / (c2 + m2) if c2 + m2 else 0
            o.append(f'<rect x="{lx:.2f}" y="{ly:.2f}" width="{lw:.2f}" height="{lh:.2f}" fill="{vide}" '
                     f'stroke="{bord}" stroke-width="0.7" rx="4"/>')
            vh = lh * frac
            if c2: o.append(f'<rect x="{lx:.2f}" y="{ly:.2f}" width="{lw:.2f}" height="{vh:.2f}" fill="{VERT}" rx="4"/>')
            if m2: o.append(f'<rect x="{lx:.2f}" y="{ly+vh:.2f}" width="{lw:.2f}" height="{lh-vh:.2f}" fill="{ROUGE}" rx="4"/>')
            marked = lib in at_libs
            # the ring owns the right-hand band, so the band is taken out of the
            # width a label may use -- otherwise the marker lands on a word
            avail = lw - 2 * PAD - (RING if marked else 0)
            col = txt_light if (m2 == 0 or c2 == 0 or frac > 0.55) else txt_dark
            short = NOMS.get(lib, lib)
            n += 1
            legend.append((n, lib, short, c2, c2 + m2, name))
            placed = False
            for cand, cfs in ((f"{short}  {c2}/{c2+m2}", F(11.5)), (short, F(12)), (short, F(10.5)),
                              (short, F(9.8)), (short[:8], F(9.2)), (short[:6], F(9))):
                if len(cand) * CHAR_W * cfs <= avail and cfs * 1.4 <= lh - 4:
                    ly_t = ly + (lh / 2 + cfs * 0.36 if cfs < F(11) else 15 * fs + 2)
                    o.append(f'<text x="{lx+PAD-2:.1f}" y="{ly_t:.1f}" font-size="{cfs:.1f}" '
                             f'font-weight="620" fill="{col}">{cand}</text>')
                    placed = True
                    break
            if not placed and lh > 46 and lw > 15 and len(short) * CHAR_W * F(9.8) <= lh - 2 * PAD:
                cx, cy = lx + lw / 2 + 3.4, ly + lh / 2
                o.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="{F(9.8):.1f}" font-weight="620" fill="{col}" '
                         f'text-anchor="middle" transform="rotate(-90 {cx:.1f} {cy:.1f})">{short}</text>')
                placed = True
            if not placed:
                bad.append((short, round(lw, 1), round(lh, 1)))
                numeros[lib] = n
                cen = lx + (lw - (RING if marked else 0)) / 2
                o.append(f'<text x="{cen:.1f}" y="{ly+lh/2+4:.1f}" font-size="{F(10):.1f}" font-weight="700" fill="{col}" '
                         f'text-anchor="middle">{n}</text>')
            if marked:
                o.append(f'<circle cx="{lx+lw-RING/2-2:.1f}" cy="{ly+lh/2:.1f}" r="4.2" fill="#ffffff" '
                         f'stroke="{MARQUE}" stroke-width="1.5"/>')
    # legend: every library, including those whose tile could not carry its name
    ly0 = h - LEG + 12 * fs
    o.append(f'<line x1="{M:.0f}" y1="{ly0-14*fs:.0f}" x2="{w-M:.0f}" y2="{ly0-14*fs:.0f}" stroke="{sep}" stroke-width="1"/>')
    o.append(f'<text x="{M:.0f}" y="{ly0:.0f}" font-size="{F(11):.1f}" font-weight="650" fill="{SUB}" '
             f'letter-spacing="0.4">LIBRARIES - COVERED / IMPORTED</text>')
    cols = 4 if w > 1000 else 3
    cw = (w - 2 * M) / cols
    rows = (len(legend) + cols - 1) // cols
    for i, (num, lib, short, c2, t2, fam_name) in enumerate(sorted(legend, key=lambda r: (r[5], -r[4], r[1]))):
        cx = M + (i // rows) * cw
        cy = ly0 + 20 * fs + (i % rows) * 17 * fs
        dot = VERT if c2 == t2 else (ROUGE if c2 == 0 else "#c9a227")
        o.append(f'<circle cx="{cx+4:.1f}" cy="{cy-4:.1f}" r="4" fill="{dot}"/>')
        idx = f"{numeros[lib]} " if lib in numeros else ""
        o.append(f'<text x="{cx+15:.1f}" y="{cy:.1f}" font-size="{F(10.5):.1f}" fill="{FG}">'
                 f'<tspan fill="{SUB}">{idx}</tspan>{short}'
                 f'<tspan fill="{SUB}">  {c2}/{t2}</tspan></text>')
    o.append('</svg>')
    texte = "\n".join(o)
    # Un SVG est du XML : une entite HTML (`&nbsp;`, `&middot;`) le rend
    # invalide, et un SVG invalide n'est affiche par personne -- ni GitHub, ni
    # un rasteriseur. Mesure : c'est ce qui a fait qu'une image poussee
    # n'apparaissait pas du tout dans un README.
    ET.fromstring(texte)
    return texte, bad

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    widget = "--widget" in sys.argv
    svg, bad = build(d, 940 if widget else 1200, 800 if widget else 820, 1.28 if widget else 1.0,
                     "dark" if widget else "light")
    if len(sys.argv) > 2 and not widget:
        os.makedirs(os.path.dirname(sys.argv[2]), exist_ok=True)
        open(sys.argv[2], "w").write(svg); print("wrote", sys.argv[2], len(svg), "bytes")
    print("tiles whose label had to fall back to a number:", bad)
