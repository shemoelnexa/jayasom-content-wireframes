import fitz
import re
import os

PDF = r"C:\Users\Shemoel\Downloads\Jayasom_Iconography.pdf"
OUT = os.path.join(os.path.dirname(__file__), "..", "icons", "iconography")
os.makedirs(OUT, exist_ok=True)

doc = fitz.open(PDF)
page = doc[0]
words = page.get_text("words")  # x0,y0,x1,y1,text,block,line,word

# Group words by (block, line) to reconstruct full labels
lines = {}
for w in words:
    x0, y0, x1, y1, text, block, line, wno = w
    key = (block, line)
    lines.setdefault(key, []).append((x0, y0, x1, y1, text))

label_boxes = []  # (name, xcenter, y0, y1)
for key, ws in lines.items():
    ws.sort(key=lambda t: t[0])
    text = "".join(t[4] for t in ws)
    x0 = min(t[0] for t in ws)
    x1 = max(t[2] for t in ws)
    y0 = min(t[1] for t in ws)
    y1 = max(t[3] for t in ws)
    label_boxes.append((text, (x0 + x1) / 2, y0, y1, x0, x1))

# Keep only icon-sheet labels (skip the big title "JAYASOMICONOGRAPHY")
skip = {"JAYASOMICONOGRAPHY"}
label_boxes = [l for l in label_boxes if l[0] not in skip]

name_map = {
    "SPA": "spa",
    "FITNESS": "fitness",
    "HOLISTICHEALTH": "holistic-health",
    "PHYSIOTHERAPY": "physiotherapy",
    "AESTHETICBEAUTY": "aesthetic-beauty",
    "NUTRITION": "nutrition",
    "EXPERIENCES": "experiences",
    "INFANTS": "infants",
    "TODDLERS": "toddlers",
    "TWEENS": "tweens",
    "TEENS": "teens",
    "FAMILY": "family",
    "INDIVIDUALSESSION": "individual-session",
    "GROUPSESSION": "group-session",
    "NOMOBILEPHONE": "no-mobile-phone",
    "NOSMOKING": "no-smoking",
    "KEEPSILENT": "keep-silent",
    "SOUND": "sound",
}

icons = []
for text, xc, y0, y1, x0, x1 in label_boxes:
    key = text.replace(" ", "")
    if key not in name_map:
        print("UNMATCHED LABEL:", repr(text))
        continue
    icons.append({"name": name_map[key], "label_x0": x0, "label_x1": x1, "label_xc": xc, "label_y0": y0, "label_y1": y1})

print(f"Found {len(icons)} icon labels")

drawings = page.get_drawings()
# Drop the two full-page background fills (page border rects)
drawings = [d for d in drawings if not (d["rect"].width > 1000 and d["rect"].height > 900)]
print(f"{len(drawings)} candidate icon drawings")

# Assign each drawing to nearest label: same row band (icon sits below label, within ~200pt),
# and closest x-center.
def assign(dr):
    r = dr["rect"]
    cx = (r.x0 + r.x1) / 2
    cy = (r.y0 + r.y1) / 2
    best = None
    best_dist = None
    for ic in icons:
        # icon must be below the label, within 260pt vertically
        if cy < ic["label_y1"] - 5 or cy > ic["label_y1"] + 260:
            continue
        dx = abs(cx - ic["label_xc"])
        if dx > 140:
            continue
        dist = dx
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = ic
    return best

groups = {ic["name"]: [] for ic in icons}
unassigned = 0
for dr in drawings:
    ic = assign(dr)
    if ic is None:
        unassigned += 1
        continue
    groups[ic["name"]].append(dr)

print("unassigned drawings:", unassigned)
for name, ds in groups.items():
    print(name, len(ds))


def item_to_path(item, ox, oy, scale):
    op = item[0]
    def pt(p):
        return ((p.x - ox) * scale, (p.y - oy) * scale)
    if op == "l":
        p1, p2 = item[1], item[2]
        x1, y1 = pt(p1); x2, y2 = pt(p2)
        return f"M {x1:.2f} {y1:.2f} L {x2:.2f} {y2:.2f}"
    elif op == "c":
        p1, p2, p3, p4 = item[1], item[2], item[3], item[4]
        x1, y1 = pt(p1); x2, y2 = pt(p2); x3, y3 = pt(p3); x4, y4 = pt(p4)
        return f"M {x1:.2f} {y1:.2f} C {x2:.2f} {y2:.2f} {x3:.2f} {y3:.2f} {x4:.2f} {y4:.2f}"
    elif op == "re":
        rect = item[1]
        x0, y0 = pt((rect.x0, rect.y0)) if not hasattr(rect, "x0") else pt(fitz.Point(rect.x0, rect.y0))
        x1, y1 = pt(fitz.Point(rect.x1, rect.y1))
        return f"M {x0:.2f} {y0:.2f} L {x1:.2f} {y0:.2f} L {x1:.2f} {y1:.2f} L {x0:.2f} {y1:.2f} Z"
    elif op == "qu":
        quad = item[1]
        pts = [pt(quad.ul), pt(quad.ur), pt(quad.lr), pt(quad.ll)]
        d = f"M {pts[0][0]:.2f} {pts[0][1]:.2f} "
        for p in pts[1:]:
            d += f"L {p[0]:.2f} {p[1]:.2f} "
        return d + "Z"
    else:
        return ""


for name, ds in groups.items():
    if not ds:
        print("NO DRAWINGS FOR", name)
        continue
    x0 = min(d["rect"].x0 for d in ds)
    y0 = min(d["rect"].y0 for d in ds)
    x1 = max(d["rect"].x1 for d in ds)
    y1 = max(d["rect"].y1 for d in ds)
    w = x1 - x0
    h = y1 - y0
    pad = max(w, h) * 0.08
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad
    w = x1 - x0; h = y1 - y0
    size = max(w, h)
    scale = 24.0 / size
    ox, oy = x0, y0

    path_ds = []
    for d in ds:
        for item in d["items"]:
            pd = item_to_path(item, ox, oy, scale)
            if pd:
                path_ds.append(pd)

    vb_w = w * scale
    vb_h = h * scale
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}" '
        f'fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">'
        + "".join(f'<path d="{p}"/>' for p in path_ds)
        + "</svg>"
    )
    with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name, f"{vb_w:.1f}x{vb_h:.1f}", len(path_ds), "subpaths")
