# Tape-collage style system

## Core proposition

Translate one subject, scene, or feeling into a sparse physical construction made primarily from washi-tape fragments. Make the finished work feel handmade and tactile while retaining the clarity and restraint of an editorial illustration.

The defining move is **subject-as-tape**, not a conventional photo pasted down with tape at its corners.

## Soft structural scene distillation — preferred default

For photo transformations, preserve one to three identification anchors and rebuild the main subject from approximately 10–18 coherent broad or medium washi-tape planes.

Preserve perceived volume through adjacent light, middle, and dark tape faces, overlap order, and negative-space cuts. The collage itself must remain flat and front-facing; do not create inflated or sculptural paper depth.

When the source contains useful environmental information, add one or two quiet source-derived supporting echoes behind or beneath the subject—for example a ground swatch, window grid, horizon band, shadow block, foliage patch, or wall rhythm. These echoes must improve recognition or mood and must never become generic scrapbook decoration.

Let the complete motif group occupy roughly 40–55% of the canvas width and 32–48% of its height, usually near the center or lower-middle, while retaining approximately 65–80% visually quiet paper.

Use a source-derived low-saturation palette of four to six colors, normally including warm white, one or two gray or neutral tones, one muted natural hue, and at most one restrained warm accent.

Favor fine matte fibers, gentle translucency, mild analog pigment variation, narrow overlap shadows, mostly clean geometric cuts, and a few natural torn edges. Keep obvious wrinkles below about 25% of the motif region.

Avoid dominant horizontal scan lines, coarse pulp texture, excessive wrinkles, tiny fragments, decorative filler, drawn contours, and overly photoreal surface rendering.

## Preserved-photo paper-composition mode

Activate this mode only when the user asks to preserve, retain, keep, or show the original photograph. It is a clean two-zone paper composition, not a mockup, book spread, or before/after board.

- Resolve the default splice from the source orientation, approximately 50/50: portrait photos (`height > width`) use photo-left and paper-right; landscape or square photos (`width >= height`) use photo-above and paper-below.
- Default the complete two-panel canvas to `3:4` width-to-height portrait. Follow an explicit alternate final ratio.
- Follow explicit requests for another orientation, order, or ratio.
- Keep the photograph faithful and real: no redraw, recolor, retouch, extension, object change, generative reconstruction, or non-uniform stretching.
- If needed for fit, crop without resampling and retain at least 80% of the source pixel area. Use a centered crop by default and shift the crop anchor only to protect the subject. If the 20% crop limit cannot fill the photo panel, preserve the retained pixels at their original size on a clean warm-white matte.
- Keep the two layout zones aligned at one perfectly straight horizontal or vertical division. No feather, gradient, dissolve, page turn, diagonal split, tape bridge, or decorative separator.
- Generate one isolated, text-free tape motif on a genuinely transparent RGBA background and combine it with the original photograph through deterministic raster composition. Do not generate journal paper, page texture, captions, borders, broad page shadows, or the complete two-panel image with the image model. Build one continuous synthesized paper surface across the complete output, then scale, place, and shadow the transparent motif locally; no second paper background may enter the composite.
- Present the retained crop as a borderless physical photo print with unchanged source pixels: no white stock edge and no grain, tint, contrast, or print-noise overlay on the image. Keep the print straight and aligned with its photo zone by default; rotate only when explicitly requested. Form every exposed edge from a slowly varying torn contour with fine translucent fiber breakup and soft antialiasing. Avoid regular zigzags, uniformly noisy sawteeth, hard digital cutout edges, or thick white borders. Settle the print onto the page with a broad pale ambient shadow plus a narrow contact shadow that follows the torn fibers; avoid one uniform dark halo or dramatic floating depth. Clip the photo and both shadows to the photo zone so they cannot overlap paper-panel content or the tape motif. Avoid Polaroid proportions, frames, curled paper, or taped corners.
- Use one continuous clean warm-white journal-paper texture across the complete output, including any uncovered photo-zone space. The base must read as warm white rather than beige or yellow. Build the surface primarily from clearly perceptible fine diffuse fibers in varied directions, a smaller number of softer long fibers, localized short thread clusters, subtle mid- and fine-scale pulp-density relief, sparse neutral inclusions, and a few faint discontinuous scan traces. The fibers and pulp relief must survive normal fitted-screen viewing; an almost textureless digital-white field is not acceptable. Keep broad low-frequency tonal variation extremely weak so it cannot resemble stains, clouds, grime, water damage, or uneven aging. Increase tactile visibility through local thread contrast rather than overall darkening or yellowing. The texture stays low contrast, free of dominant horizontal lines, irregular rather than mechanically repeated, and quieter than the image and collage. Because the paper comes from one deterministic synthesis pass, no sampling, stretching, mirroring, tiling, copied panel pixels, color shift, texture discontinuity, or copied collage content is permitted. Avoid heavy yellowing, dirt, cracks, burns, stains, grunge, or theatrical aging.
- Leave about 80% of the paper panel as quiet negative space by default. Place one tape-collage-and-caption group, about 20% of the paper panel, in a visually balancing corner. Never center the group unless explicitly requested. Keep the whole group inset by at least about 9% of the panel's shorter side so no tape edge, wrinkle, shadow, or title touches the paper boundary. The group may grow for expressive clarity but must not exceed 60% of the paper panel.
- For image-based work, default to one concise factual English title of one to three words, set in clear faded 26–32 pt-equivalent typewriter lettering, 28 pt by default, close to—but never over—the tape motif. Use adequate tracking and moderately dark faded-ink contrast for immediate recognition and visual harmony. Exact user wording overrides it; an explicit no-text request removes it. Add the title deterministically after generating the text-free motif.
- Do not introduce tickets, receipts, labels, stamps, seals, stickers, or meaningless pseudo-writing.
- Require genuine transparency around the generated motif. Reject an opaque matte, baked checkerboard, paper-colored rectangle, edge halo, full page, or full-panel background. Retain narrow shadows between overlapping tape pieces inside the motif, but create the motif-to-page contact shadow deterministically from its alpha mask.
- Default to one motif-generation call. Allow at most one targeted generative revision, only for failed subject recognition or failed tape material. Correct layout, scale, safe inset, paper texture, photo mounting, and caption placement in the deterministic compositor rather than regenerating.

## Composition

- Use a white or warm-white journal page as the field.
- For a minimal isolated object, let the motif occupy roughly 15–25% of the canvas. For the preferred structural photo transformation, use the soft structural scene-distillation dimensions above. In preserved-photo mode, keep the motif-and-caption group compact at about 20% of the paper panel.
- Preserve approximately 65–80% visually quiet paper for the preferred structural default, and allow more negative space for deliberately minimal isolated objects.
- Prefer one isolated motif or one compact motif group.
- Outside preserved-photo mode, place the motif near the center or lower-middle with slight asymmetry and breathing room.
- Keep the complete motif and any text at least about 9% of the shorter paper dimension away from every paper edge unless the user explicitly requests an edge crop or bleed.
- Use near-top-down or gently oblique presentation. Keep the page dominant and the surrounding desk nearly absent.
- Show irregular multi-scale journal-paper fibers clearly enough to remain visible when the whole page is fitted on screen: fine diffuse fibers in varied directions, a few softer long fibers, small thread clusters, fine pulp relief, tiny neutral inclusions, and sparse discontinuous scan traces. Keep the warm-white sheet clean and low contrast but unmistakably tactile. If the page reads as flat digital white, strengthen local fiber and fine-pulp contrast without increasing broad mottling. Suppress cloudy stains; avoid beige cast, dominant horizontal lines, mechanically repeated stripes, heavy stains, torn scrapbook backgrounds, and aged-paper theatrics.

## Material language

- Keep the result visually flat and front-facing, like tape assembled directly on a journal page. Avoid sculptural depth, inflated paper volume, or photoreal object rendering.
- Build with approximately 10–18 broad or medium hand-cut pieces of washi tape, adjusted to subject structure. Prefer coherent structural planes over tiny fragments; combine adjacent similar-color areas when subdivision adds no recognition.
- Favor solid-color tape and familiar basic washi patterns: dots, narrow stripes, grid, checks, simple scallops, or restrained small florals. Within each piece, preserve visible paper fiber, soft edge fuzz, and mild analog pigment variation. Avoid digital gradients, glossy vector fills, photographic texture, marbling, and ornate multicolor prints. Natural translucency, gentle mottling, and overlap darkening are desirable.
- Show slight translucency, especially at overlaps and pale tape edges.
- Make overlapping tape edges legible with narrow, soft contact shadows and slight darkening where one strip presses over another. Preserve shallow stacking rather than dramatic depth.
- Include subtle seams, trapped-air irregularity, uneven tears, tiny folds, or one lifted corner. Add restrained wrinkles or creases only when they clarify the source silhouette, surface direction, or volume. The combined visibly wrinkled area must stay below about 25% of the collage-motif region; do not distress every piece uniformly.
- Combine torn edges and clean-cut edges. Avoid making every edge equally distressed.
- Do not add graphite, pencil, pen, or ink contours. When tape alone needs more definition, use a narrower tape strip, a torn negative-space cutout, an overlap seam, or a restrained stripe/grid pattern made from tape.

## Subject construction

- Reduce the subject to its most recognizable silhouette, gesture, or landmark.
- Convert broad masses into tape strips, blocks, and overlapping translucent planes. Avoid confetti-like chips, overly fine color subdivision, and dense mosaics. If small fragmented color patches are necessary for recognition, their combined area must remain below 70% of the collage-motif region.
- Preserve one to three identification anchors, such as a cat's ears and tail, a cake's layered profile, or a landmark's skyline.
- For every image category, add one or two quiet source-derived environmental echoes when they materially improve recognition, mood, scale, or grounding. Keep them behind or beneath the subject and omit them when they would become generic decoration.
- Use adjacent light, middle, and dark tape faces to preserve perspective or perceived volume when useful. Keep the paper construction shallow and front-facing rather than turning it into a realistic three-dimensional object.
- Let small misalignments and imperfect joins reveal the hand-built process.
- Avoid polished vector symmetry, intricate photoreal rendering, dense cut-paper mosaics, and generic scrapbook layouts.

### Transformation modes

1. **Tape-built illustration — default**
   Rebuild the subject almost entirely from tape with sparse narrow-tape details. Preserve recognition but allow substantial abstraction.

2. **Clean photo-fragment hybrid — optional**
   Use one small, modern cropped photo, photocopy, or halftone fragment and integrate it with tape-built shapes. Keep it contemporary and clean; do not add faux aging or archival ephemera.

3. **Mood distillation — optional**
   Discard literal scene reconstruction. Derive a limited palette, spacing rhythm, and one metaphorical tape motif from the source mood.

## Color

- Derive the palette from the source image when one exists.
- Limit the working palette to about 3–6 colors plus paper and neutral ink.
- Use muted or lightly chalky tape colors with one controlled stronger accent when useful.
- Preserve translucent color mixing at overlaps.
- Avoid a rainbow assortment unless the source or user explicitly calls for it.
- For emotional briefs, let palette carry mood: blue-gray and softened violet for rain or solitude; warm cream, coral, and brown for food or domestic warmth; pale botanical greens and yellow for quiet freshness.

## Typography

- For image-based work, default to one factual one-to-three-word English summary title. For description-only work, default to no text.
- Exact supplied wording overrides the automatic summary; explicit no-text instructions override both.
- Use at most one short title plus one compact metadata line when requested.
- Prefer clear faded typewriter lettering at a 26–32 pt equivalent, 28 pt by default, or compact hand lettering only when the user requests it.
- Keep lettering visually subordinate and separated by negative space.
- Render supplied wording exactly; do not invent filler text.

## Exclusions

Do not introduce these elements unless the user asks for them:

- old photographs, Polaroid proportions, or thick decorative photo frames; a narrow clean mounted-print edge is allowed in preserved-photo mode
- tickets, receipts, labels, postage, stamps, seals, or stickers
- newspaper clippings, maps, ribbons, lace, or botanical scrapbook filler
- visible tape rolls, scissors, pens, hands, or craft-table clutter
- dense journaling, long quotes, ornamental calligraphy, or illegible pseudo-type
- strong grunge, browned paper, heavy film grain, dramatic spotlights, or deep cast shadows
