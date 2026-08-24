#!/usr/bin/env python3
"""Compose a faithful photo print beside a deterministic tape-collage paper field."""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import (
    Image,
    ImageChops,
    ImageColor,
    ImageDraw,
    ImageFilter,
    ImageFont,
    ImageOps,
    ImageStat,
)


def parse_aspect(value: str) -> tuple[int, int] | None:
    if value.lower() == "auto":
        return None
    try:
        width_text, height_text = value.split(":", 1)
        width, height = int(width_text), int(height_text)
    except (ValueError, AttributeError) as exc:
        raise argparse.ArgumentTypeError("aspect must be W:H or auto") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("aspect values must be positive")
    divisor = math.gcd(width, height)
    return width // divisor, height // divisor


def unit_fraction(value: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise argparse.ArgumentTypeError("value must be between 0 and 1")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a borderless photo-print and tape-collage paper composition."
    )
    parser.add_argument("--photo", type=Path, required=True)
    parser.add_argument(
        "--motif",
        type=Path,
        help="preferred transparent RGBA tape motif with no page background or text",
    )
    parser.add_argument(
        "--paper-panel",
        type=Path,
        help="legacy RGB paper-panel input; prefer --motif for new work",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--orientation",
        choices=("auto", "top-bottom", "left-right"),
        default="auto",
        help="auto uses left-right for portrait photos and top-bottom otherwise",
    )
    parser.add_argument(
        "--photo-position",
        choices=("auto", "top", "bottom", "left", "right"),
        default="auto",
    )
    parser.add_argument("--photo-fraction", type=unit_fraction, default=0.5)
    parser.add_argument(
        "--final-aspect",
        type=parse_aspect,
        default=(3, 4),
        metavar="W:H|auto",
        help="final canvas aspect; default 3:4 portrait; use auto for source-driven size",
    )
    parser.add_argument(
        "--crop-mode",
        choices=("auto", "none"),
        default="auto",
        help="auto may crop the photo to reduce matte while respecting --max-crop",
    )
    parser.add_argument(
        "--max-crop",
        type=unit_fraction,
        default=0.20,
        help="maximum fraction of original photo area that may be removed",
    )
    parser.add_argument("--crop-anchor-x", type=unit_fraction, default=0.5)
    parser.add_argument("--crop-anchor-y", type=unit_fraction, default=0.5)
    parser.add_argument(
        "--matte-color",
        default="#faf8f3",
        help="clean warm-white journal-paper base; default avoids yellowed aging",
    )
    parser.add_argument(
        "--photo-treatment",
        choices=("print", "flat"),
        default="print",
        help="print keeps source pixels unchanged by default and adds physical placement, torn edges, and shadow",
    )
    parser.add_argument(
        "--photo-border",
        type=unit_fraction,
        default=0.0,
        help="optional paper border as a fraction of retained photo's short edge; default 0",
    )
    parser.add_argument(
        "--photo-shadow",
        type=unit_fraction,
        default=0.010,
        help="dual contact-shadow scale as a fraction of retained photo's short edge",
    )
    parser.add_argument(
        "--photo-texture-strength",
        type=unit_fraction,
        default=0.0,
        help="optional print grain applied to photo pixels; default 0 preserves pixel values",
    )
    parser.add_argument(
        "--photo-rotation",
        type=float,
        default=0.0,
        metavar="DEGREES",
        help="optional user-requested photo rotation; default 0 keeps the print straight",
    )
    parser.add_argument(
        "--photo-edge-style",
        choices=("straight", "torn-seam", "torn-exposed"),
        default="torn-exposed",
        help="torn-exposed tears every edge not coincident with the final canvas",
    )
    parser.add_argument(
        "--paper-texture-strength",
        type=unit_fraction,
        default=1.0,
        help="visibility of deterministic multi-scale warm journal-paper fibers; default remains visible at fitted view",
    )
    parser.add_argument(
        "--motif-position",
        choices=("upper-left", "upper-right", "lower-left", "lower-right"),
        default="lower-right",
        help="deterministic placement inside the paper zone",
    )
    parser.add_argument(
        "--motif-area-fraction",
        type=unit_fraction,
        default=0.17,
        help="target motif bounding-box area as a fraction of the paper zone",
    )
    parser.add_argument(
        "--motif-max-width-fraction",
        type=unit_fraction,
        default=0.52,
        help="maximum motif width as a fraction of the paper zone",
    )
    parser.add_argument(
        "--motif-max-height-fraction",
        type=unit_fraction,
        default=0.48,
        help="maximum motif height as a fraction of the paper zone",
    )
    parser.add_argument(
        "--motif-safe-inset",
        type=unit_fraction,
        default=0.11,
        help="minimum inset from paper edges as a fraction of the panel short side",
    )
    parser.add_argument(
        "--motif-shadow",
        type=unit_fraction,
        default=0.008,
        help="narrow contact-shadow blur as a fraction of the paper short side",
    )
    parser.add_argument("--caption")
    parser.add_argument("--caption-x", type=unit_fraction)
    parser.add_argument("--caption-y", type=unit_fraction)
    parser.add_argument(
        "--caption-align", choices=("left", "center", "right"), default="left"
    )
    parser.add_argument(
        "--caption-size",
        type=float,
        default=28.0,
        metavar="POINTS",
        help="caption size in point-equivalent units; default 28; recommended 26-32",
    )
    parser.add_argument("--caption-color", default="#514b45")
    parser.add_argument("--font", type=Path)
    parser.add_argument(
        "--plan",
        action="store_true",
        help="print resolved layout and crop geometry without composing an image",
    )
    return parser.parse_args()


def resolve_orientation(source: Image.Image, requested: str) -> str:
    if requested != "auto":
        return requested
    return "left-right" if source.height > source.width else "top-bottom"


def resolve_photo_position(orientation: str, requested: str) -> str:
    if requested == "auto":
        return "left" if orientation == "left-right" else "top"
    valid = {
        "top-bottom": {"top", "bottom"},
        "left-right": {"left", "right"},
    }
    if requested not in valid[orientation]:
        raise ValueError(
            f"{orientation} orientation is incompatible with photo-position {requested}"
        )
    return requested


def validate_args(args: argparse.Namespace) -> None:
    if not 0.05 <= args.photo_fraction <= 0.95:
        raise ValueError("--photo-fraction must be between 0.05 and 0.95")
    if args.motif is not None and args.paper_panel is not None:
        raise ValueError("use exactly one of --motif or legacy --paper-panel")
    if not args.plan and args.output is None:
        raise ValueError("--output is required unless --plan is used")
    if not args.plan and args.motif is None and args.paper_panel is None:
        raise ValueError("--motif is required for new work; --paper-panel is legacy")
    if args.motif_area_fraction <= 0:
        raise ValueError("--motif-area-fraction must be greater than zero")
    if args.motif_max_width_fraction <= 0 or args.motif_max_height_fraction <= 0:
        raise ValueError("motif maximum-size fractions must be greater than zero")
    if args.caption_size <= 0:
        raise ValueError("--caption-size must be positive")
    if abs(args.photo_rotation) > 30:
        raise ValueError("--photo-rotation must stay between -30 and 30 degrees")


def target_photo_band_aspect(
    final_aspect: tuple[int, int], photo_fraction: float, orientation: str
) -> float:
    canvas_aspect = final_aspect[0] / final_aspect[1]
    if orientation == "top-bottom":
        return canvas_aspect / photo_fraction
    return canvas_aspect * photo_fraction


def anchored_start(removed: int, anchor: float) -> int:
    return min(removed, max(0, round(removed * anchor)))


def crop_source(
    source: Image.Image,
    args: argparse.Namespace,
    orientation: str,
) -> tuple[Image.Image, tuple[int, int, int, int], float]:
    full_box = (0, 0, source.width, source.height)
    if args.crop_mode == "none" or args.max_crop == 0 or args.final_aspect is None:
        return source.copy(), full_box, 0.0

    target_aspect = target_photo_band_aspect(
        args.final_aspect, args.photo_fraction, orientation
    )
    source_aspect = source.width / source.height
    left, top, right, bottom = full_box

    if source_aspect > target_aspect:
        ideal_width = max(1, round(source.height * target_aspect))
        ideal_removed = max(0, source.width - ideal_width)
        max_removed = math.floor(source.width * args.max_crop)
        removed = min(ideal_removed, max_removed)
        left = anchored_start(removed, args.crop_anchor_x)
        right = source.width - (removed - left)
    elif source_aspect < target_aspect:
        ideal_height = max(1, round(source.width / target_aspect))
        ideal_removed = max(0, source.height - ideal_height)
        max_removed = math.floor(source.height * args.max_crop)
        removed = min(ideal_removed, max_removed)
        top = anchored_start(removed, args.crop_anchor_y)
        bottom = source.height - (removed - top)

    crop_box = (left, top, right, bottom)
    cropped = source.crop(crop_box)
    retained_area = cropped.width * cropped.height
    original_area = source.width * source.height
    crop_fraction = 1.0 - retained_area / original_area
    if crop_fraction > args.max_crop + 1e-12:
        raise RuntimeError("computed crop exceeds --max-crop")
    return cropped, crop_box, crop_fraction


def photo_print_metrics(
    source: Image.Image, args: argparse.Namespace
) -> tuple[int, int, int]:
    if args.photo_treatment == "flat":
        return 0, 0, 0
    short_edge = min(source.width, source.height)
    border = max(1, round(short_edge * args.photo_border)) if args.photo_border else 0
    shadow_blur = max(2, round(short_edge * args.photo_shadow))
    rotation = math.radians(abs(args.photo_rotation))
    rotated_width = abs(source.width * math.cos(rotation)) + abs(
        source.height * math.sin(rotation)
    )
    rotated_height = abs(source.width * math.sin(rotation)) + abs(
        source.height * math.cos(rotation)
    )
    rotation_margin = max(
        0,
        math.ceil((rotated_width - source.width) / 2),
        math.ceil((rotated_height - source.height) / 2),
    )
    decoration_margin = border + rotation_margin + shadow_blur
    return border, shadow_blur, decoration_margin


def exact_aspect_canvas(
    source: Image.Image,
    photo_fraction: float,
    orientation: str,
    aspect: tuple[int, int],
    decoration_margin: int = 0,
) -> tuple[int, int]:
    aspect_width, aspect_height = aspect
    required_width = source.width + 2 * decoration_margin
    required_height = source.height + 2 * decoration_margin
    if orientation == "top-bottom":
        scale = math.ceil(
            max(
                required_width / aspect_width,
                required_height / (photo_fraction * aspect_height),
            )
        )
    else:
        scale = math.ceil(
            max(
                required_height / aspect_height,
                required_width / (photo_fraction * aspect_width),
            )
        )
    return aspect_width * scale, aspect_height * scale


@dataclass(frozen=True)
class Layout:
    orientation: str
    photo_position: str
    output_size: tuple[int, int]
    photo_band_box: tuple[int, int, int, int]
    photo_box: tuple[int, int, int, int]
    photo_print_box: tuple[int, int, int, int]
    paper_box: tuple[int, int, int, int]
    crop_box: tuple[int, int, int, int]
    crop_fraction: float
    photo_border: int
    photo_shadow_blur: int
    cropped_source: Image.Image


def build_layout(source: Image.Image, args: argparse.Namespace) -> Layout:
    orientation = resolve_orientation(source, args.orientation)
    photo_position = resolve_photo_position(orientation, args.photo_position)
    cropped, crop_box, crop_fraction = crop_source(source, args, orientation)
    photo_border, photo_shadow_blur, decoration_margin = photo_print_metrics(
        cropped, args
    )

    if args.final_aspect is None:
        ratio = (1.0 - args.photo_fraction) / args.photo_fraction
        decorated_width = cropped.width + 2 * decoration_margin
        decorated_height = cropped.height + 2 * decoration_margin
        if orientation == "top-bottom":
            output_size = (
                decorated_width,
                decorated_height + max(1, round(decorated_height * ratio)),
            )
        else:
            output_size = (
                decorated_width + max(1, round(decorated_width * ratio)),
                decorated_height,
            )
    else:
        output_size = exact_aspect_canvas(
            cropped,
            args.photo_fraction,
            orientation,
            args.final_aspect,
            decoration_margin,
        )

    output_width, output_height = output_size
    if orientation == "top-bottom":
        photo_band_height = round(output_height * args.photo_fraction)
        if photo_position == "top":
            photo_band_box = (0, 0, output_width, photo_band_height)
            paper_box = (0, photo_band_height, output_width, output_height)
        else:
            paper_box = (0, 0, output_width, output_height - photo_band_height)
            photo_band_box = (
                0,
                output_height - photo_band_height,
                output_width,
                output_height,
            )
    else:
        photo_band_width = round(output_width * args.photo_fraction)
        if photo_position == "left":
            photo_band_box = (0, 0, photo_band_width, output_height)
            paper_box = (photo_band_width, 0, output_width, output_height)
        else:
            paper_box = (0, 0, output_width - photo_band_width, output_height)
            photo_band_box = (
                output_width - photo_band_width,
                0,
                output_width,
                output_height,
            )

    band_left, band_top, band_right, band_bottom = photo_band_box
    band_width = band_right - band_left
    band_height = band_bottom - band_top
    photo_x = band_left + (band_width - cropped.width) // 2
    photo_y = band_top + (band_height - cropped.height) // 2
    # A rotated physical print stays centered inside its own zone so the torn
    # edges and shadow remain separated from the paper-panel motif. Straight
    # flat placement retains the older seam-aligned behavior.
    if args.photo_treatment == "flat" or not args.photo_rotation:
        if orientation == "left-right":
            photo_x = band_right - cropped.width if photo_position == "left" else band_left
        else:
            photo_y = band_bottom - cropped.height if photo_position == "top" else band_top
    photo_box = (
        photo_x,
        photo_y,
        photo_x + cropped.width,
        photo_y + cropped.height,
    )
    photo_print_box = (
        photo_box[0] - photo_border,
        photo_box[1] - photo_border,
        photo_box[2] + photo_border,
        photo_box[3] + photo_border,
    )
    return Layout(
        orientation=orientation,
        photo_position=photo_position,
        output_size=output_size,
        photo_band_box=photo_band_box,
        photo_box=photo_box,
        photo_print_box=photo_print_box,
        paper_box=paper_box,
        crop_box=crop_box,
        crop_fraction=crop_fraction,
        photo_border=photo_border,
        photo_shadow_blur=photo_shadow_blur,
        cropped_source=cropped,
    )


def load_typewriter_font(
    path: Path | None, size: int
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        path,
        Path(r"C:\Windows\Fonts\cour.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_caption(
    output: Image.Image,
    paper_box: tuple[int, int, int, int],
    args: argparse.Namespace,
    motif_box: tuple[int, int, int, int] | None = None,
) -> None:
    if not args.caption:
        return
    caption = " ".join(args.caption.split())
    left, top, right, bottom = paper_box
    paper_width, paper_height = right - left, bottom - top
    size_pixels = max(1, round(args.caption_size * 96 / 72))
    font = load_typewriter_font(args.font, size_pixels)
    draw = ImageDraw.Draw(output)
    bbox = draw.textbbox((0, 0), caption, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    margin = max(4, round(min(paper_width, paper_height) * args.motif_safe_inset))
    gap = max(6, round(min(paper_width, paper_height) * 0.035))

    if args.caption_x is not None:
        anchor_x = left + round(args.caption_x * paper_width)
        if args.caption_align == "center":
            x = anchor_x - text_width // 2
        elif args.caption_align == "right":
            x = anchor_x - text_width
        else:
            x = anchor_x
    elif motif_box is not None:
        x = motif_box[0]
    else:
        x = left + margin

    if args.caption_y is not None:
        y = top + round(args.caption_y * paper_height)
    elif motif_box is not None:
        above = motif_box[1] - gap - text_height
        below = motif_box[3] + gap
        y = above if above >= top + margin else below
    else:
        y = top + margin

    x = min(max(x, left + margin), right - margin - text_width)
    y = min(max(y, top + margin), bottom - margin - text_height)
    draw.text(
        (x - bbox[0], y - bbox[1]),
        caption,
        font=font,
        fill=ImageColor.getrgb(args.caption_color),
    )


def make_paper_texture(
    size: tuple[int, int],
    base_color: str,
    strength: float,
    seed: int,
) -> Image.Image:
    """Create clean warm journal paper with irregular multi-scale fibers."""
    width, height = size
    base = ImageColor.getrgb(base_color)
    paper = Image.new("RGBA", size, (*base, 255))
    if strength <= 0:
        return paper.convert("RGB")

    rng = random.Random(seed)
    short_edge = min(width, height)
    area = width * height

    # Keep broad pulp-density movement extremely quiet. It should stop the
    # page from looking digitally flat without turning into beige clouds,
    # stains, or theatrical aging.
    cell = max(16, short_edge // 36)
    low_size = (max(2, width // cell + 2), max(2, height // cell + 2))
    low = Image.new("L", low_size)
    low.putdata([rng.randint(108, 146) for _ in range(low_size[0] * low_size[1])])
    low = low.resize(size, Image.Resampling.BICUBIC).filter(
        ImageFilter.GaussianBlur(max(1.0, cell * 0.72))
    )
    dark_alpha = low.point(
        lambda value: round(max(0, 127 - value) * strength * 0.10)
    )
    light_alpha = low.point(
        lambda value: round(max(0, value - 127) * strength * 0.07)
    )
    density_dark = Image.new("RGBA", size, (178, 171, 158, 0))
    density_dark.putalpha(dark_alpha)
    density_light = Image.new("RGBA", size, (255, 255, 252, 0))
    density_light.putalpha(light_alpha)
    paper = Image.alpha_composite(paper, density_dark)
    paper = Image.alpha_composite(paper, density_light)

    # A finer irregular pulp field carries most of the tactile variation. Its
    # amplitude is low enough to read as fibers rather than mottled dirt.
    pulp_cell = max(3, short_edge // 220)
    pulp_size = (
        max(2, width // pulp_cell + 2),
        max(2, height // pulp_cell + 2),
    )
    pulp = Image.new("L", pulp_size)
    pulp.putdata([rng.randint(92, 164) for _ in range(pulp_size[0] * pulp_size[1])])
    pulp = pulp.resize(size, Image.Resampling.BICUBIC).filter(
        ImageFilter.GaussianBlur(max(0.7, pulp_cell * 0.34))
    )
    pulp_dark_alpha = pulp.point(
        lambda value: round(max(0, 127 - value) * strength * 0.24)
    )
    pulp_light_alpha = pulp.point(
        lambda value: round(max(0, value - 127) * strength * 0.16)
    )
    pulp_dark = Image.new("RGBA", size, (168, 160, 146, 0))
    pulp_dark.putalpha(pulp_dark_alpha)
    pulp_light = Image.new("RGBA", size, (255, 255, 252, 0))
    pulp_light.putalpha(pulp_light_alpha)
    paper = Image.alpha_composite(paper, pulp_dark)
    paper = Image.alpha_composite(paper, pulp_light)

    # Sparse broken scan residue suggests a real scanned journal sheet. Avoid
    # repeated ruling or dense horizontal bands.
    scan_overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan_overlay)
    scan_count = max(5, min(16, height // 220))
    for _ in range(scan_count):
        y = rng.randrange(height)
        start = rng.randint(0, max(0, width // 6))
        trace_end = rng.randint(max(start + 1, width // 2), width)
        alpha = max(2, round(rng.randint(5, 9) * strength))
        color = (
            (162, 156, 146, alpha)
            if rng.random() < 0.58
            else (255, 255, 252, alpha)
        )
        cursor = start
        while cursor < trace_end:
            segment = rng.randint(max(8, width // 24), max(12, width // 8))
            end = min(trace_end, cursor + segment)
            scan_draw.line(
                (cursor, y, end, y + rng.choice((-1, 0, 0, 1))),
                fill=color,
                width=1,
            )
            cursor = end + rng.randint(max(5, width // 70), max(8, width // 30))
    vertical_count = max(1, min(4, width // 650))
    for _ in range(vertical_count):
        x = rng.randrange(width)
        start = rng.randint(0, max(0, height // 5))
        end = rng.randint(max(start + 1, height // 2), height)
        alpha = max(1, round(rng.randint(2, 4) * strength))
        scan_draw.line((x, start, x, end), fill=(171, 166, 157, alpha), width=1)
    scan_overlay = scan_overlay.filter(ImageFilter.GaussianBlur(0.65))
    paper = Image.alpha_composite(paper, scan_overlay)

    # Soft longer threads sit beneath crisp microfibers and make the sheet
    # feel like uncoated notebook stock rather than a noise filter.
    soft_fibers = Image.new("RGBA", size, (0, 0, 0, 0))
    soft_draw = ImageDraw.Draw(soft_fibers)
    soft_count = max(240, area // 10000)
    for _ in range(soft_count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        length = rng.randint(12, max(14, min(52, max(width, height) // 42)))
        angle = rng.uniform(0, math.pi)
        dx = round(math.cos(angle) * length)
        dy = round(math.sin(angle) * length)
        alpha = max(2, round(rng.randint(5, 11) * strength))
        color = (
            (164, 157, 146, alpha)
            if rng.random() < 0.58
            else (255, 255, 252, alpha)
        )
        soft_draw.line((x, y, x + dx, y + dy), fill=color, width=1)
    soft_fibers = soft_fibers.filter(ImageFilter.GaussianBlur(0.75))
    paper = Image.alpha_composite(paper, soft_fibers)

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Dense, low-contrast microfibers carry visible notebook-paper texture at
    # normal viewing size without darkening the page or forming a pattern.
    fiber_count = max(1800, area // 620)
    fiber_alpha = max(2, round(15 * strength))
    for _ in range(fiber_count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        length = rng.randint(4, max(7, min(28, max(width, height) // 48)))
        color = (
            (166, 159, 147, fiber_alpha)
            if rng.random() < 0.60
            else (255, 255, 252, fiber_alpha)
        )
        angle = rng.uniform(0, math.pi)
        dx = round(math.cos(angle) * length)
        dy = round(math.sin(angle) * length)
        x2 = min(width - 1, max(0, x + dx))
        y2 = min(height - 1, max(0, y + dy))
        draw.line((x, y, x2, y2), fill=color, width=1)

    # Tiny pulp inclusions remain sparse and neutral: tactile, never dirty.
    floc_overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    floc_draw = ImageDraw.Draw(floc_overlay)
    floc_count = max(70, area // 30000)
    for _ in range(floc_count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        radius_x = rng.randint(1, max(2, min(4, width // 420)))
        radius_y = rng.randint(1, max(2, min(4, height // 420)))
        alpha = max(2, round(rng.randint(5, 10) * strength))
        color = (
            (161, 154, 143, alpha)
            if rng.random() < 0.55
            else (255, 255, 252, alpha)
        )
        floc_draw.ellipse(
            (x - radius_x, y - radius_y, x + radius_x, y + radius_y),
            fill=color,
        )
    floc_overlay = floc_overlay.filter(ImageFilter.GaussianBlur(0.55))
    paper = Image.alpha_composite(paper, floc_overlay)

    fleck_count = max(20, area // 140000)
    for _ in range(fleck_count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        radius = rng.choice((1, 1, 1, 2))
        alpha = max(1, round(rng.randint(3, 7) * strength))
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(154, 148, 138, alpha),
        )

    overlay = overlay.filter(ImageFilter.GaussianBlur(0.35))
    return Image.alpha_composite(paper, overlay).convert("RGB")


def make_unified_paper_background(layout: Layout, args: argparse.Namespace) -> Image.Image:
    """Generate the one and only paper sheet used by the preferred workflow."""
    return make_paper_texture(
        layout.output_size,
        args.matte_color,
        args.paper_texture_strength,
        seed=layout.output_size[0] * 7919 + layout.output_size[1] * 104729,
    )


def trim_transparent_motif(motif: Image.Image) -> Image.Image:
    """Validate and trim a genuinely transparent RGBA motif asset."""
    rgba = motif.convert("RGBA")
    alpha = rgba.getchannel("A")
    minimum, maximum = alpha.getextrema()
    if maximum == 0:
        raise ValueError("--motif contains no visible pixels")
    if minimum == 255:
        raise ValueError(
            "--motif must have genuine transparent pixels; do not supply a paper "
            "background, checkerboard preview, or opaque RGB panel"
        )
    visible = alpha.point(lambda value: 255 if value >= 8 else 0)
    bounds = visible.getbbox()
    if bounds is None:
        raise ValueError("--motif has no sufficiently visible alpha content")
    return rgba.crop(bounds)


def place_transparent_motif(
    output: Image.Image,
    motif: Image.Image,
    layout: Layout,
    args: argparse.Namespace,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Scale, inset, shadow, and place an RGBA motif without importing a paper matte."""
    motif = trim_transparent_motif(motif)
    left, top, right, bottom = layout.paper_box
    paper_width, paper_height = right - left, bottom - top
    short_edge = min(paper_width, paper_height)
    inset = max(4, round(short_edge * args.motif_safe_inset))
    available_width = max(1, paper_width - 2 * inset)
    available_height = max(1, paper_height - 2 * inset)
    max_width = max(
        1,
        min(available_width, round(paper_width * args.motif_max_width_fraction)),
    )
    max_height = max(
        1,
        min(available_height, round(paper_height * args.motif_max_height_fraction)),
    )
    target_area = max(
        1.0,
        paper_width * paper_height * args.motif_area_fraction,
    )
    area_scale = math.sqrt(target_area / (motif.width * motif.height))
    scale = min(area_scale, max_width / motif.width, max_height / motif.height)
    motif_size = (
        max(1, round(motif.width * scale)),
        max(1, round(motif.height * scale)),
    )
    motif = motif.resize(motif_size, Image.Resampling.LANCZOS)

    horizontal = "left" if args.motif_position.endswith("left") else "right"
    vertical = "upper" if args.motif_position.startswith("upper") else "lower"
    x = left + inset if horizontal == "left" else right - inset - motif.width
    y = top + inset if vertical == "upper" else bottom - inset - motif.height
    motif_box = (x, y, x + motif.width, y + motif.height)

    paper_mask = Image.new("L", output.size, 0)
    ImageDraw.Draw(paper_mask).rectangle((left, top, right - 1, bottom - 1), fill=255)
    blur = max(1, round(short_edge * args.motif_shadow))
    shadow_alpha = Image.new("L", output.size, 0)
    shadow_alpha.paste(motif.getchannel("A"), (x + max(1, blur // 2), y + max(1, blur // 2)))
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(blur))
    shadow_alpha = shadow_alpha.point(lambda value: round(value * 0.16))
    shadow_alpha = ImageChops.multiply(shadow_alpha, paper_mask)
    shadow = Image.new("RGBA", output.size, (52, 45, 38, 0))
    shadow.putalpha(shadow_alpha)
    composed = Image.alpha_composite(output.convert("RGBA"), shadow)

    motif_canvas = Image.new("RGBA", output.size, (0, 0, 0, 0))
    motif_canvas.alpha_composite(motif, (x, y))
    composed = Image.alpha_composite(composed, motif_canvas)
    return composed.convert("RGB"), motif_box


def make_photo_print_surface(
    source: Image.Image,
    strength: float,
    seed: int,
) -> Image.Image:
    """Add restrained deterministic ink absorption and print grain."""
    if strength <= 0:
        return source.copy()
    rng = random.Random(seed)
    surface = source.convert("RGBA")
    overlay = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = source.size
    scan_alpha = max(1, round(5 * strength))
    y = rng.randint(2, 6)
    while y < height:
        color = (248, 244, 235, scan_alpha) if rng.random() < 0.55 else (44, 38, 32, scan_alpha)
        draw.line((0, y, width, y), fill=color, width=1)
        y += rng.randint(5, 11)
    speckles = max(100, width * height // 5500)
    speck_alpha = max(1, round(12 * strength))
    for _ in range(speckles):
        x = rng.randrange(width)
        y = rng.randrange(height)
        color = (
            (250, 247, 239, speck_alpha)
            if rng.random() < 0.52
            else (48, 42, 36, speck_alpha)
        )
        draw.point((x, y), fill=color)
    return Image.alpha_composite(surface, overlay).convert("RGB")


def make_photo_edge_mask(
    size: tuple[int, int],
    layout: Layout,
    edge_style: str,
    rotation: float,
    seed: int,
) -> Image.Image:
    """Create restrained torn fibers on requested, non-canvas-coincident edges."""
    width, height = size
    mask = Image.new("L", size, 255)
    if edge_style == "straight":
        return mask
    rng = random.Random(seed)
    pixels = mask.load()
    depth = max(4, round(min(width, height) * 0.009))

    if edge_style == "torn-seam":
        sides = {
            "left": {"right"},
            "right": {"left"},
            "top": {"bottom"},
            "bottom": {"top"},
        }[layout.photo_position]
    else:
        if rotation:
            # Once tilted, no complete edge remains coincident with a canvas edge.
            sides = {"left", "top", "right", "bottom"}
        else:
            output_width, output_height = layout.output_size
            left, top, right, bottom = layout.photo_box
            sides = set()
            if left > 0:
                sides.add("left")
            if top > 0:
                sides.add("top")
            if right < output_width:
                sides.add("right")
            if bottom < output_height:
                sides.add("bottom")

    def edge_profile(length: int) -> list[int]:
        """Make a slow torn contour plus restrained one-pixel fiber jitter."""
        step = max(12, min(42, max(1, length // 55)))
        control_count = math.ceil(length / step) + 1
        current = depth * rng.uniform(0.36, 0.64)
        controls: list[float] = []
        for _ in range(control_count):
            current = min(
                depth * 0.86,
                max(depth * 0.10, current + rng.uniform(-0.22, 0.22) * depth),
            )
            controls.append(current)
        values: list[int] = []
        for index in range(length):
            position = index / step
            lower = min(len(controls) - 1, int(position))
            upper = min(len(controls) - 1, lower + 1)
            fraction = position - lower
            value = controls[lower] * (1.0 - fraction) + controls[upper] * fraction
            value += rng.choice((-1, 0, 0, 0, 0, 1))
            values.append(max(1, min(depth, round(value))))
        return values

    for side in sides:
        length = height if side in {"left", "right"} else width
        profile = edge_profile(length)
        if side == "left":
            for y, cut in enumerate(profile):
                for x in range(cut):
                    pixels[x, y] = 0
                if cut > 0 and rng.random() < 0.16:
                    pixels[cut - 1, y] = rng.randint(28, 82)
                if cut < width:
                    pixels[cut, y] = rng.randint(105, 188)
                if cut + 1 < width:
                    pixels[cut + 1, y] = min(pixels[cut + 1, y], rng.randint(220, 248))
        elif side == "right":
            for y, cut in enumerate(profile):
                boundary = width - cut - 1
                for x in range(width - cut, width):
                    pixels[x, y] = 0
                if width - cut < width and rng.random() < 0.16:
                    pixels[width - cut, y] = rng.randint(28, 82)
                if boundary >= 0:
                    pixels[boundary, y] = rng.randint(105, 188)
                if boundary - 1 >= 0:
                    pixels[boundary - 1, y] = min(
                        pixels[boundary - 1, y], rng.randint(220, 248)
                    )
        elif side == "top":
            for x, cut in enumerate(profile):
                for y in range(cut):
                    pixels[x, y] = 0
                if cut > 0 and rng.random() < 0.16:
                    pixels[x, cut - 1] = rng.randint(28, 82)
                if cut < height:
                    pixels[x, cut] = rng.randint(105, 188)
                if cut + 1 < height:
                    pixels[x, cut + 1] = min(
                        pixels[x, cut + 1], rng.randint(220, 248)
                    )
        else:
            for x, cut in enumerate(profile):
                boundary = height - cut - 1
                for y in range(height - cut, height):
                    pixels[x, y] = 0
                if height - cut < height and rng.random() < 0.16:
                    pixels[x, height - cut] = rng.randint(28, 82)
                if boundary >= 0:
                    pixels[x, boundary] = rng.randint(105, 188)
                if boundary - 1 >= 0:
                    pixels[x, boundary - 1] = min(
                        pixels[x, boundary - 1], rng.randint(220, 248)
                    )

    # A very small blur removes digital stair-stepping while preserving the
    # irregular contour and translucent exposed fibers.
    return mask.filter(ImageFilter.GaussianBlur(0.32))


def make_continuous_paper_background(
    fitted_paper: Image.Image,
    layout: Layout,
    args: argparse.Namespace,
) -> Image.Image:
    """Synthesize unique paper filler matched to a motif-free seam sample."""
    sample_fraction = 0.08
    if layout.orientation == "left-right":
        sample_width = max(1, round(fitted_paper.width * sample_fraction))
        if layout.photo_position == "left":
            sample = fitted_paper.crop((0, 0, sample_width, fitted_paper.height))
            seam_side = "left"
        else:
            sample = fitted_paper.crop(
                (
                    fitted_paper.width - sample_width,
                    0,
                    fitted_paper.width,
                    fitted_paper.height,
                )
            )
            seam_side = "right"
    else:
        sample_height = max(1, round(fitted_paper.height * sample_fraction))
        if layout.photo_position == "top":
            sample = fitted_paper.crop((0, 0, fitted_paper.width, sample_height))
            seam_side = "top"
        else:
            sample = fitted_paper.crop(
                (
                    0,
                    fitted_paper.height - sample_height,
                    fitted_paper.width,
                    fitted_paper.height,
                )
            )
            seam_side = "bottom"

    medians: list[int] = []
    for channel in sample.split():
        histogram = channel.histogram()
        midpoint = sum(histogram) // 2
        cumulative = 0
        median = 255
        for value, count in enumerate(histogram):
            cumulative += count
            if cumulative >= midpoint:
                median = value
                break
        medians.append(median)
    matched_color = "#" + "".join(
        f"{min(255, value + 2):02x}" for value in medians
    )
    output = make_paper_texture(
        layout.output_size,
        matched_color,
        args.paper_texture_strength,
        seed=layout.output_size[0] * 7919 + layout.output_size[1] * 104729,
    )

    # Match only neutral luminance statistics from the motif-free seam sample.
    # This brings independently generated paper into the same tonal and fiber-
    # contrast family without copying, stretching, mirroring, or tiling pixels.
    target_stat = ImageStat.Stat(sample.convert("L"))
    current_stat = ImageStat.Stat(output.convert("L"))
    target_mean = target_stat.mean[0]
    target_std = max(0.75, target_stat.stddev[0])
    current_mean = current_stat.mean[0]
    current_std = max(0.75, current_stat.stddev[0])
    contrast_gain = min(1.90, max(0.65, target_std / current_std))
    offset = target_mean - contrast_gain * current_mean
    luminance_lut = [
        min(255, max(0, round(contrast_gain * value + offset)))
        for value in range(256)
    ]
    output = output.point(luminance_lut * len(output.getbands()))

    # Keep one continuous synthesized paper sheet across the entire output.
    # Extract only the non-paper motif and its local soft shadows from the
    # generated panel, so no second paper texture can create a visible seam.
    paper_reference = Image.new("RGB", fitted_paper.size, tuple(medians))
    difference = ImageChops.difference(fitted_paper, paper_reference)
    red_diff, green_diff, blue_diff = difference.split()
    peak_difference = ImageChops.lighter(
        red_diff,
        ImageChops.lighter(green_diff, blue_diff),
    )
    saturation = fitted_paper.convert("HSV").split()[1]
    difference_seed = peak_difference.point(
        lambda value: 255 if value >= 24 else 0
    )
    saturation_seed = saturation.point(lambda value: 255 if value >= 28 else 0)
    content_seed = ImageChops.lighter(difference_seed, saturation_seed).filter(
        ImageFilter.MedianFilter(3)
    )
    short_edge = min(fitted_paper.size)
    growth = max(5, round(short_edge * 0.020))
    content_mask = content_seed.filter(ImageFilter.MaxFilter(growth * 2 + 1))
    content_mask = content_mask.filter(
        ImageFilter.GaussianBlur(max(1.0, short_edge * 0.004))
    )
    output.paste(fitted_paper, layout.paper_box[:2], content_mask)
    return output


def mount_photo(
    output: Image.Image,
    layout: Layout,
    args: argparse.Namespace,
) -> Image.Image:
    if args.photo_treatment == "flat":
        output.paste(layout.cropped_source, layout.photo_box[:2])
        return output

    photo_seed = layout.cropped_source.width * 1009 + layout.cropped_source.height * 9173
    photo_surface = make_photo_print_surface(
        layout.cropped_source,
        args.photo_texture_strength,
        seed=photo_seed,
    )
    edge_mask = make_photo_edge_mask(
        photo_surface.size,
        layout,
        args.photo_edge_style,
        args.photo_rotation,
        seed=photo_seed + 7919,
    )

    photo_layer = photo_surface.convert("RGBA")
    photo_layer.putalpha(edge_mask)
    if args.photo_rotation:
        photo_layer = photo_layer.rotate(
            args.photo_rotation,
            resample=Image.Resampling.NEAREST,
            expand=True,
            fillcolor=(0, 0, 0, 0),
        )
    rotated_mask = photo_layer.getchannel("A")
    photo_center_x = (layout.photo_box[0] + layout.photo_box[2]) // 2
    photo_center_y = (layout.photo_box[1] + layout.photo_box[3]) // 2
    layer_x = photo_center_x - photo_layer.width // 2
    layer_y = photo_center_y - photo_layer.height // 2

    band_mask = Image.new("L", output.size, 0)
    band_draw = ImageDraw.Draw(band_mask)
    band_left, band_top, band_right, band_bottom = layout.photo_band_box
    band_draw.rectangle(
        (band_left, band_top, band_right - 1, band_bottom - 1),
        fill=255,
    )

    def add_shadow_layer(
        base: Image.Image,
        blur: int,
        offset: int,
        opacity: float,
        color: tuple[int, int, int],
    ) -> Image.Image:
        alpha = Image.new("L", output.size, 0)
        alpha.paste(rotated_mask, (layer_x + offset, layer_y + offset))
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
        alpha = alpha.point(lambda value: round(value * opacity))
        alpha = ImageChops.multiply(alpha, band_mask)
        layer = Image.new("RGBA", output.size, (*color, 0))
        layer.putalpha(alpha)
        return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")

    # Two restrained layers feel more physical than one uniform dark halo:
    # a broad, pale ambient lift followed by a narrow contact shadow that
    # follows the torn fibers. Both remain clipped to the photo zone.
    ambient_blur = max(2, round(layout.photo_shadow_blur * 1.25))
    ambient_offset = max(1, round(layout.photo_shadow_blur * 0.45))
    output = add_shadow_layer(
        output,
        ambient_blur,
        ambient_offset,
        0.09,
        (83, 76, 66),
    )
    contact_blur = max(1, round(layout.photo_shadow_blur * 0.22))
    contact_offset = max(1, round(layout.photo_shadow_blur * 0.12))
    output = add_shadow_layer(
        output,
        contact_blur,
        contact_offset,
        0.16,
        (70, 62, 53),
    )

    # A broken, paper-colored outer fringe lets the torn photo stock merge
    # with the journal sheet without becoming a white border. It is derived
    # only from the photo alpha and never changes interior source pixels.
    outer = rotated_mask.filter(ImageFilter.MaxFilter(7))
    fringe_local = ImageChops.subtract(outer, rotated_mask)
    fringe_rng = random.Random(photo_seed + 65537)
    noise_size = (
        max(2, rotated_mask.width // 4),
        max(2, rotated_mask.height // 4),
    )
    fringe_noise = Image.new("L", noise_size)
    fringe_noise.putdata(
        [fringe_rng.randint(72, 255) for _ in range(noise_size[0] * noise_size[1])]
    )
    fringe_noise = fringe_noise.resize(
        rotated_mask.size,
        Image.Resampling.BILINEAR,
    ).filter(ImageFilter.GaussianBlur(0.35))
    fringe_local = ImageChops.multiply(fringe_local, fringe_noise)
    fringe_local = fringe_local.point(lambda value: round(value * 0.42))
    fringe_alpha = Image.new("L", output.size, 0)
    fringe_alpha.paste(fringe_local, (layer_x, layer_y))
    fringe_alpha = ImageChops.multiply(fringe_alpha, band_mask)
    fringe = Image.new("RGBA", output.size, (251, 249, 244, 0))
    fringe.putalpha(fringe_alpha)
    output = Image.alpha_composite(output.convert("RGBA"), fringe).convert("RGB")

    left, top, right, bottom = layout.photo_print_box
    if layout.photo_border:
        print_size = (right - left, bottom - top)
        print_stock = make_paper_texture(
            print_size,
            "#fbfaf5",
            min(1.0, args.paper_texture_strength * 0.70),
            seed=print_size[0] * 1009 + print_size[1] * 9173,
        )
        output.paste(print_stock, (left, top))
    photo_canvas = Image.new("RGBA", output.size, (0, 0, 0, 0))
    photo_canvas.paste(photo_layer, (layer_x, layer_y))
    clipped_alpha = ImageChops.multiply(photo_canvas.getchannel("A"), band_mask)
    photo_canvas.putalpha(clipped_alpha)
    return Image.alpha_composite(output.convert("RGBA"), photo_canvas).convert("RGB")


def compose(
    collage_asset: Image.Image,
    layout: Layout,
    args: argparse.Namespace,
) -> Image.Image:
    motif_box: tuple[int, int, int, int] | None = None
    if args.motif is not None:
        output = make_unified_paper_background(layout, args)
        output, motif_box = place_transparent_motif(
            output,
            collage_asset,
            layout,
            args,
        )
    else:
        paper_left, paper_top, paper_right, paper_bottom = layout.paper_box
        paper_size = (paper_right - paper_left, paper_bottom - paper_top)
        fitted_paper = ImageOps.fit(
            collage_asset.convert("RGB"),
            paper_size,
            method=Image.Resampling.LANCZOS,
        )
        output = make_continuous_paper_background(fitted_paper, layout, args)
    output = mount_photo(output, layout, args)
    draw_caption(output, layout.paper_box, args, motif_box)
    return output


def print_plan(
    args: argparse.Namespace,
    original_size: tuple[int, int],
    layout: Layout,
) -> None:
    paper_width = layout.paper_box[2] - layout.paper_box[0]
    paper_height = layout.paper_box[3] - layout.paper_box[1]
    print(f"ORIENTATION={layout.orientation}")
    print(f"PHOTO_POSITION={layout.photo_position}")
    print(f"ORIGINAL_SIZE={original_size}")
    print(f"RETAINED_SIZE={layout.cropped_source.size}")
    print(f"FINAL_SIZE={layout.output_size}")
    print(f"PHOTO_BAND_BOX={layout.photo_band_box}")
    print(f"PHOTO_CONTENT_BOX={layout.photo_box}")
    print(f"PHOTO_PRINT_BOX={layout.photo_print_box}")
    print(f"PAPER_BOX={layout.paper_box}")
    print(f"PAPER_PANEL_SIZE={(paper_width, paper_height)}")
    print(f"PHOTO_CROP_BOX={layout.crop_box}")
    print(f"PHOTO_CROP_FRACTION={layout.crop_fraction:.6f}")
    print(f"PHOTO_TREATMENT={args.photo_treatment}")
    print(f"PHOTO_BORDER={layout.photo_border}")
    print(f"PHOTO_EDGE_STYLE={args.photo_edge_style if args.photo_treatment == 'print' else 'straight'}")
    print(f"PHOTO_ROTATION={args.photo_rotation if args.photo_treatment == 'print' else 0:g}")
    print(f"PHOTO_ZONE_CLIP={'enabled' if args.photo_treatment == 'print' else 'not-needed'}")
    print(
        "PHOTO_SOURCE_TRANSFORM="
        + (
            "deterministic-print-texture"
            if args.photo_treatment == "print" and args.photo_texture_strength > 0
            else "unchanged"
        )
    )
    print(
        "PHOTO_PIXEL_VALUES="
        + (
            "modified-by-opt-in-texture"
            if args.photo_treatment == "print" and args.photo_texture_strength > 0
            else "unchanged"
        )
    )
    print("PHOTO_MATTE_SOURCE=unified-procedural-journal")
    print(
        "COLLAGE_ASSET_MODE="
        + (
            "transparent-rgba-motif"
            if args.motif is not None or args.paper_panel is None
            else "legacy-rgb-paper-panel"
        )
    )
    print(
        "PAPER_TEXTURE_MATCH="
        + ("not-applicable-single-source" if args.paper_panel is None else "legacy-seam-statistics")
    )
    print("PAPER_BACKGROUND_MODE=unified-procedural")
    print(
        "PAPER_PANEL_CONTENT="
        + (
            "transparent-rgba-motif-only"
            if args.motif is not None or args.paper_panel is None
            else "legacy-difference-extracted-motif"
        )
    )
    print(f"FINAL_ASPECT={args.final_aspect or 'auto'}")


def main() -> None:
    args = parse_args()
    validate_args(args)
    source = Image.open(args.photo).convert("RGB")
    layout = build_layout(source, args)
    print_plan(args, source.size, layout)
    if args.plan:
        return

    if args.motif is not None:
        collage_asset = Image.open(args.motif).convert("RGBA")
    else:
        collage_asset = Image.open(args.paper_panel).convert("RGB")
    output = compose(collage_asset, layout, args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, format="PNG", optimize=True)

    if args.photo_treatment == "flat":
        rendered_photo = output.crop(layout.photo_box)
        difference = ImageChops.difference(layout.cropped_source, rendered_photo).getbbox()
        if difference is not None:
            raise RuntimeError(f"Photo panel differs from retained source crop at {difference}")

    print(f"OUTPUT={args.output}")
    print(f"CAPTION={args.caption!r}")
    print(f"CAPTION_POINT_SIZE={args.caption_size:g}")
    if args.photo_treatment == "flat":
        print("PHOTO_PANEL_PIXEL_DIFF=None")
    else:
        print("PHOTO_PANEL_PIXEL_DIFF=not-applicable-physical-placement-mask")


if __name__ == "__main__":
    main()
