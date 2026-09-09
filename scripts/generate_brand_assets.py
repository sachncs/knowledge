"""Generate the knowledge brand assets: logo, favicon, OG image.

Usage:
    python scripts/generate_brand_assets.py

Run from the repository root. Writes PNGs into docs/assets/.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS = REPO_ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

INDIGO = (63, 81, 181)
INDIGO_DARK = (40, 53, 130)
WHITE = (255, 255, 255)
SLATE_900 = (15, 23, 42)
SLATE_50 = (248, 250, 252)


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Locate a system sans-serif font, falling back to PIL's default."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            font = ImageFont.truetype(candidate, size)
            assert isinstance(font, ImageFont.FreeTypeFont)
            return font
    fallback = ImageFont.load_default()
    assert isinstance(fallback, ImageFont.FreeTypeFont)
    return fallback


def draw_logo(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = int(size * 0.18)
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=INDIGO)
    # Subtle gradient by drawing a darker overlay in the bottom-right.
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        (int(size * 0.55), int(size * 0.55), size, size), radius=radius, fill=INDIGO_DARK
    )
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)
    font = find_font(int(size * 0.55), bold=True)
    text = "K"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((size - text_w) / 2 - bbox[0], (size - text_h) / 2 - bbox[1] - int(size * 0.02)),
        text,
        font=font,
        fill=WHITE,
    )
    return img


def draw_og_image() -> Image.Image:
    """Generate the 1200x630 Open Graph social preview image."""
    width, height = 1200, 630
    img = Image.new("RGB", (width, height), INDIGO)
    draw = ImageDraw.Draw(img)
    # Diagonal accent block in the bottom-right.
    draw.polygon(
        [(width * 0.45, height), (width, height), (width, height * 0.45)],
        fill=INDIGO_DARK,
    )
    # Three-node knowledge-graph motif on the left, matching the wordmark.
    motif_radius = 28
    motif_color_a = INDIGO_DARK
    motif_color_b = (40, 53, 130)
    motif_color_c = (30, 40, 110)
    # Connector lines
    draw.line([(110, 280), (60, 410)], fill=motif_color_c, width=6)
    draw.line([(110, 280), (190, 420)], fill=motif_color_c, width=6)
    draw.line([(110, 280), (130, 440)], fill=motif_color_c, width=6)
    # Nodes
    draw.ellipse(
        [(60 - motif_radius, 410 - motif_radius), (60 + motif_radius, 410 + motif_radius)],
        fill=motif_color_a,
    )
    draw.ellipse(
        [(110 - 40, 280 - 40), (110 + 40, 280 + 40)],
        fill=motif_color_b,
    )
    draw.ellipse(
        [(130 - 22, 440 - 22), (130 + 22, 440 + 22)],
        fill=motif_color_b,
    )
    draw.ellipse(
        [(190 - motif_radius, 420 - motif_radius), (190 + motif_radius, 420 + motif_radius)],
        fill=motif_color_a,
    )
    # Title.
    title_font = find_font(96, bold=True)
    subtitle_font = find_font(38)
    tagline_font = find_font(28)
    draw.text((280, 180), "knowledge", fill=WHITE, font=title_font)
    draw.text(
        (282, 300),
        "Documentation, structured.",
        fill=(220, 225, 240),
        font=subtitle_font,
    )
    draw.text(
        (282, 350),
        "Turn any URL or file into a versionable, diffable",
        fill=(190, 200, 220),
        font=tagline_font,
    )
    draw.text(
        (282, 388),
        "OKF v0.1 bundle of linked Markdown concepts.",
        fill=(190, 200, 220),
        font=tagline_font,
    )
    # Footer link.
    link_font = find_font(26)
    draw.text(
        (90, height - 70),
        "github.com/sachncs/knowledge  •  MIT License  •  pip install knowledge",
        fill=(220, 225, 240),
        font=link_font,
    )
    return img


def draw_favicon(size: int) -> Image.Image:
    img = draw_logo(size)
    # Favicons also want an opaque background in some browsers.
    opaque = Image.new("RGBA", img.size, INDIGO)
    opaque.paste(img, (0, 0), img)
    return opaque


def main() -> None:
    # Main logo (used as header branding on the docs site).
    draw_logo(512).save(ASSETS / "logo.png")
    # Favicon.
    draw_favicon(64).save(ASSETS / "favicon.png")
    # Apple touch icon.
    draw_favicon(180).save(ASSETS / "apple-touch-icon.png")
    # Social preview image.
    draw_og_image().save(ASSETS / "og-image.png")
    print("Wrote brand assets to", ASSETS)


if __name__ == "__main__":
    main()
