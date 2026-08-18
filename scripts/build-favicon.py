#!/usr/bin/env python3
"""
Generate the AG Law favicon set from a single serif monogram.

  favicon.ico          16 / 32 / 48 px, what browsers request by default
  apple-touch-icon.png 180 px, iOS home-screen bookmark
  favicon.svg          vector, modern browsers that prefer it

Mark: capital "A" (Alberto E. Guerra P.) in gold on the site background.
Baskerville SemiBold stands in for Cormorant Garamond — same old-style
serif register, and it survives being rasterised down to 16 px, which
Cormorant's thin strokes would not.

Run from the repo root:  python3 scripts/build-favicon.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent

BG = "#0A0A08"       # --bg
GOLD = "#B8936A"     # --gold
FONT = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_INDEX = 4       # SemiBold
LETTER = "A"

SS = 16              # supersample factor, downsampled with LANCZOS


def render(size, fill_ratio, radius_ratio=0.0):
    """Draw the monogram at `size` px, letter cap-height = fill_ratio * size."""
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if radius_ratio:
        draw.rounded_rectangle(
            [0, 0, big - 1, big - 1], radius=int(big * radius_ratio), fill=BG
        )
    else:
        draw.rectangle([0, 0, big - 1, big - 1], fill=BG)

    # Binary-search the point size that lands the cap-height on target.
    target = big * fill_ratio
    lo, hi = 1, big * 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        font = ImageFont.truetype(FONT, mid, index=FONT_INDEX)
        if draw.textbbox((0, 0), LETTER, font=font)[3] - draw.textbbox(
            (0, 0), LETTER, font=font
        )[1] <= target:
            lo = mid
        else:
            hi = mid - 1

    font = ImageFont.truetype(FONT, lo, index=FONT_INDEX)
    x0, y0, x1, y1 = draw.textbbox((0, 0), LETTER, font=font)
    draw.text(
        ((big - (x1 - x0)) / 2 - x0, (big - (y1 - y0)) / 2 - y0),
        LETTER,
        font=font,
        fill=GOLD,
    )

    return img.resize((size, size), Image.LANCZOS)


def main():
    # .ico — tight crop, the letter has to carry a 16 px tab strip
    ico = render(48, 0.56)
    ico.save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )

    # iOS masks the corners itself, so give the letter more air
    render(180, 0.50, radius_ratio=0.0).convert("RGB").save(
        ROOT / "apple-touch-icon.png", format="PNG", optimize=True
    )

    (ROOT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">\n'
        f'  <rect width="48" height="48" fill="{BG}"/>\n'
        f'  <text x="24" y="24" fill="{GOLD}" font-family="Cormorant Garamond,'
        'Baskerville,Garamond,serif" font-size="42" font-weight="600" '
        'text-anchor="middle" dominant-baseline="central">A</text>\n'
        "</svg>\n"
    )

    for name in ("favicon.ico", "apple-touch-icon.png", "favicon.svg"):
        p = ROOT / name
        print(f"{name:22} {p.stat().st_size:>7,} bytes")


if __name__ == "__main__":
    main()
