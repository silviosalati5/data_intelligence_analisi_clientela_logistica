"""
Grafici di sintesi dei risultati (Executive Summary)

Ricostruisce con pandas e matplotlib i quattro grafici della sezione "Sintesi dei risultati"
del README, a partire da output/dataset_analisi_completa.xlsx (foglio "Dataset Clienti"; file generato
dal notebook e non incluso nel repository, perché contiene dati dei clienti):
  - schede dei risultati principali
  - ricavo mensile sui 36 mesi, con i tre mesi di minimo
  - clienti per trend del ricavo (ciambella)
  - clienti per frequenza d'acquisto (ciambella)

Lo stile imita quello delle visualizzazioni Power BI. Tutti i numeri sono calcolati dai dati.
Uso (dalla cartella principale del progetto):  python scripts/grafici_executive_summary.py
Uscita: dashboard/01_executive_summary_*.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch, Wedge

ROOT = Path(__file__).resolve().parent.parent
PATH_DATI = ROOT / "output" / "dataset_analisi_completa.xlsx"
DIR_USCITA = ROOT / "dashboard"

# Font: Segoe UI (come Power BI) se presente, altrimenti un'alternativa simile
_disponibili = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = next(
    (f for f in ("Segoe UI", "Carlito", "Liberation Sans", "DejaVu Sans") if f in _disponibili), "sans-serif"
)

PX = 0.72  # punti per pixel a 100 dpi: i disegni sono definiti in pixel
TXT, GRY, LGR, GRID, BRD = "#252423", "#605E5C", "#A19F9D", "#EAEAEA", "#E1DFDD"
BLUE, ORG, GRN, RED = "#118DFF", "#E8743B", "#107C10", "#D83B01"


# --------------------------------------------------------------------------- utilità
def it(n, dec=0):
    """Formato italiano: punto per le migliaia, virgola per i decimali."""
    return f"{n:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def con_segno(x):
    return ("+" if x >= 0 else "−") + it(abs(x) * 100, 1) + "%"


def tela(w, h, sfondo="white"):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    fig.patch.set_facecolor(sfondo)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    return fig, ax


def testo(ax, x, y, s, px=11, colore=TXT, peso="normal", ha="left", va="baseline", **kw):
    return ax.text(x, y, s, fontsize=px * PX, color=colore, fontweight=peso, ha=ha, va=va, **kw)


def salva(fig, nome):
    DIR_USCITA.mkdir(exist_ok=True)
    fig.savefig(DIR_USCITA / nome, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("salvato", DIR_USCITA.name + "/" + nome)


# --------------------------------------------------------------------------- dati
df = pd.read_excel(PATH_DATI, sheet_name="Dataset Clienti", keep_default_na=False, na_values=[""])
MESI = [f"M-{i}" for i in range(35, -1, -1)]  # dal più vecchio al più recente
serie = df[MESI].sum() / 1e6  # milioni di euro per mese

n_clienti = len(df)
anni = [df[f"ricavo_anno_{k}"].sum() / 1e6 for k in (1, 2, 3)]
attivi = [int((df[f"ricavo_anno_{k}"] != 0).sum()) for k in (1, 2, 3)]
n_top = int(np.ceil(n_clienti / 100))
quota_top = df.nlargest(n_top, "ricavo_anno_3")["ricavo_anno_3"].sum() / df["ricavo_anno_3"].sum()
persi = int(df["periodo_di_vita"].isin(["Vecchi Persi", "Recenti Persi"]).sum())
trend = df["trend_ricavo"].value_counts()
freq = df["comportamento_frequenza"].value_counts()
assert (df["mesi_attivi"] >= 1).all(), "ci sono clienti senza nessun mese di ricavo"


# --------------------------------------------------------------------------- 1) schede
def schede():
    w, h = 1240, 136
    fig, ax = tela(w, h, "#F4F4F4")
    var_ricavo = anni[2] / anni[1] - 1
    var_attivi = attivi[2] / attivi[1] - 1
    voci = [
        ("Ricavo totale, 36 mesi", f"{it(sum(anni), 1)}Mln€", "Per anno (1 · 2 · 3)",
         " · ".join(it(a, 1) for a in anni) + "Mln€", TXT),
        ("Clienti totali", it(n_clienti), "Con almeno un mese di ricavo", "Tutti i clienti", TXT),
        ("Ricavo ultimo anno", f"{it(anni[2], 1)}Mln€", "Variazione sull'anno precedente",
         con_segno(var_ricavo), GRN if var_ricavo >= 0 else RED),
        ("Clienti attivi, ultimo anno", it(attivi[2]), "Variazione sull'anno precedente",
         con_segno(var_attivi), GRN if var_attivi >= 0 else RED),
        ("Top 1% dei clienti", f"{it(quota_top * 100, 1)}%", "Clienti nel Top 1%", it(n_top), TXT),
        ("Clienti persi", it(persi), "Quota sul totale dei clienti", f"{it(persi / n_clienti * 100, 1)}%", TXT),
    ]
    gap = 12.8
    larg = (w - 5 * gap - 4) / 6
    for i, (etichetta, valore, rif, rif_val, colore) in enumerate(voci):
        x, y = 2 + i * (larg + gap), 3
        ax.add_patch(FancyBboxPatch((x, y), larg, h - 8, boxstyle="round,pad=0,rounding_size=6",
                                    fc="white", ec=BRD, lw=0.9))
        testo(ax, x + 14, y + 28, etichetta, 11.5, GRY)
        testo(ax, x + 14, y + 60, valore, 23, TXT, "bold")
        ax.plot([x + 1, x + larg - 1], [y + 76, y + 76], color=GRID, lw=1)
        testo(ax, x + 14, y + 97, rif, 10, GRY)
        testo(ax, x + 14, y + 117, rif_val, 13, colore, "bold")
    salva(fig, "01_executive_summary_schede.png")


# --------------------------------------------------------------------------- 2) grafico mensile
def ricavo_mensile():
    w, h = 860, 420
    fig, ax = tela(w, h)
    testo(ax, 16, 30, "Ricavo mensile, 36 mesi", 14.5, TXT, "bold")
    sx, dx, alto, basso = 66, w - 24, 64, h - 84
    y0, y1 = 6.0, 13.0
    X = lambda i: sx + (dx - sx) * i / 35
    Y = lambda val: alto + (basso - alto) * (1 - (val - y0) / (y1 - y0))
    v = serie.values
    for g in range(6, 14):
        ax.plot([sx, dx], [Y(g), Y(g)], color=GRID, lw=0.9, zorder=1)
        testo(ax, sx - 10, Y(g) + 4, f"{g}Mln €", 10.5, GRY, ha="right")
    ax.plot([X(i) for i in range(36)], [Y(x) for x in v], color=BLUE, lw=2.2 * PX,
            solid_capstyle="round", solid_joinstyle="round", zorder=3)
    for i in range(36):
        testo(ax, X(i) + 3, basso + 14, f"M-{35 - i}", 9.5, GRY, ha="right", va="top",
              rotation=45, rotation_mode="anchor")
    minimi = sorted(np.argsort(v)[:3])  # i tre mesi con il ricavo più basso
    assert np.all(np.diff(minimi) == 12), "i tre minimi non sono a distanza di 12 mesi"
    for i in minimi:
        ax.add_patch(Circle((X(i), Y(v[i])), 5.6, fc=ORG, ec="white", lw=1.6, zorder=5))
        testo(ax, X(i), Y(v[i]) + 22, f"{it(v[i], 1)}Mln€", 10.5, "#B8501F", "bold", ha="center")
    ax.add_patch(Circle((X(35), Y(v[35])), 4.6, fc=BLUE, ec="white", lw=1.4, zorder=5))
    testo(ax, X(35) - 8, Y(v[35]) - 8, f"{it(v[35], 1)}Mln€", 10.5, "#0B5CAD", "bold", ha="right")
    ax.add_patch(Circle((20, h - 16), 4.5, fc=BLUE))
    testo(ax, 30, h - 12, "Ricavo mensile", 10.5, GRY)
    ax.add_patch(Circle((150, h - 16), 4.5, fc=ORG))
    testo(ax, 160, h - 12, "Mese di minimo ricavo", 10.5, GRY)
    salva(fig, "01_executive_summary_ricavo_mensile.png")


# --------------------------------------------------------------------------- 3) ciambelle
def ciambella(nome, titolo, righe):
    w, h = 560, 236
    fig, ax = tela(w, h)
    testo(ax, 16, 30, titolo, 14.5, TXT, "bold")
    cx, cy, r, ri = 205, 138, 74, 52
    tot = sum(v for _, v, _ in righe)
    a = -90.0
    for etichetta, val, colore in righe:
        sw = 360 * val / tot
        ax.add_patch(Wedge((cx, cy), r, a, a + sw, width=r - ri, fc=colore, ec="white", lw=1.4))
        m = np.deg2rad(a + sw / 2)
        ux, uy = np.cos(m), np.sin(m)
        px_, py_ = cx + (r + 1) * ux, cy + (r + 1) * uy
        ex, ey = cx + (r + 13) * ux, cy + (r + 13) * uy
        destra = ux >= 0
        hx = ex + (14 if destra else -14)
        ax.plot([px_, ex, hx], [py_, ey, ey], color=LGR, lw=0.9)
        testo(ax, hx + (5 if destra else -5), ey + 4, f"{it(val)} ({it(100 * val / tot, 1)}%)", 10.5, GRY,
              ha="left" if destra else "right")
        a += sw
    testo(ax, cx, cy + 3, it(tot), 19, TXT, "bold", ha="center")
    testo(ax, cx, cy + 22, "clienti", 10.5, GRY, ha="center")
    ly = cy - (len(righe) - 1) * 11
    for k, (etichetta, val, colore) in enumerate(righe):
        ax.add_patch(Circle((438, ly + k * 24 - 4), 5, fc=colore))
        testo(ax, 450, ly + k * 24, etichetta, 11.5, TXT)
    salva(fig, nome)


if __name__ == "__main__":
    schede()
    ricavo_mensile()
    ciambella("01_executive_summary_trend.png", "Clienti per trend del ricavo",
              [("Stabile", int(trend["Stabile"]), "#A6ADB8"),
               ("Diminuzione", int(trend["Diminuzione"]), ORG),
               ("Aumento", int(trend["Aumento"]), "#1F5FD0")])
    ciambella("01_executive_summary_frequenza.png", "Clienti per frequenza d'acquisto (36 mesi)",
              [("Continuativi", int(freq["Continuativi"]), "#17206B"),
               ("Scostanti", int(freq["Scostanti"]), "#5B8DEF"),
               ("Occasionali", int(freq["Occasionali"]), "#C9D3E3")])
