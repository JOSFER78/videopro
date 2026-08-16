# Omni Flash Video Syntax & Freeze-Camera Technique (verified)

Source of truth: official Google docs `ai.google.dev/gemini-api/docs/omni`
(last updated 2026-07-30). Model id: `gemini-omni-flash-preview`.
Use ONLY this syntax — do not invent tags (a subagent once produced fake
`@IMAGE_REF_PATH` / `#[Sources]` which Omni does not understand).

## Image-role tags
- `<FIRST_FRAME>` — starting frame of the video (frame 0 = this image).
- `<IMAGE_REF_0>` … `<IMAGE_REF_N>` — reference images (style / subject /
  camera-path guide). References start at 0.
- Simple inline form: `<FIRST_FRAME> a woman is walking` or
  `in the style of <IMAGE_REF_0> a woman <IMAGE_REF_1> is walking`.

## Explicit multi-image form (best for many refs)
```
[# Sources <FIRST_FRAME>@Image1]
[# References <IMAGE_REF_0>@Image2 <IMAGE_REF_1>@Image3]

a woman <IMAGE_REF_0> is walking.
Use Image1 as the starting frame.
Use Image2 and Image3 as references for the video generation.
The images should not be used as literal initial frames.
```

## Camera-path guide = drawing that must NOT appear in output
Official example: upload a hand-drawn fish sketch + text
`"turn this into realistic footage, using the drawing only as a guide for
movement, do not show the drawing in the final video"`.
→ For the red-line technique: upload photo+red curve as an `IMAGE_REF` and
say `use only as a camera path guide, do not show the red line`.

## task parameter (video-config)
`text_to_video` | `image_to_video` | `reference_to_video` | `edit`.
Force `image_to_video` when starting from an image.

## Audio
- Omini GENERATES audio from the text prompt (ambient, SFX, even quoted
  dialogue `"..."` for lip-sync).
- Reference audio upload (supplying a .wav/.mp3) is NOT supported yet per
  docs — do not try to feed multiple ambient tracks.

## Freeze-frame / time-stop
No literal parameter. Achieved by prompt:
`time freezes, everything locks mid-motion like a sculpture, the only
moving thing is <X>`. Less deterministic than Seedance 2.5's explicit
control — expect 2–3 generations + conversational edit refinement.

## Conversational editing
Flow supports natural-language refinement (Interactions API): describe the
change, Omni applies it preserving the rest. Prefer this over full
regeneration.

---

# Dobrodziej / Seedance 2.5 → Omni Flash adaptation (Google Flow only)
Technique (tweet @M_Dobrodziej 2087425842313933171; prompt in Notion
"Seedance 2.5 Prompts vol 3"): one photo + hand-drawn camera path (1=start,
2=end) + total scene freeze except ONE moving element (a dog/pug).

### Image prep
- Image1: source photo clean → `<FIRST_FRAME>`.
- Image2: SAME photo + red curved line (1→2) → `IMAGE_REF_0` (camera guide).
- Optional Image3–5: extra views of the SAME place (other angles, wet
  facades, cobblestones) → `IMAGE_REF_1..N` for 3D consistency.
  Rule: only the camera-guide image carries annotations; reference views
  stay clean so Omni doesn't confuse architecture with instruction.

### Copy-paste prompt (Flow text box; replace ImageN by upload order)
```
[# Sources <FIRST_FRAME>@Image1]
[# References <IMAGE_REF_0>@Image2 <IMAGE_REF_1>@Image3 <IMAGE_REF_2>@Image4 <IMAGE_REF_3>@Image5]

Image1 is the EXACT starting frame: a 1968 black-and-white photograph
by Zbigniew Siemaszko — a young woman running in pouring rain on
Puławska street, Warsaw. Wet dress clinging, reflections on wet asphalt,
nostalgic Eastern-European atmosphere, 35mm film grain, slight sepia,
documentary cinematic composition. INCLUDING a red hand-drawn curved
line with "1" at start and "2" at end.

Image2 is a CAMERA PATH GUIDE: the same photograph with a red trajectory
line drawn on it. Use Image2 ONLY as a guide for camera movement.
The red line represents the CAMERA POSITION over time, NOT an object.
DO NOT reproduce the red line, the numbers, or any drawing in the
final video. The line must never appear.

Images3-5 are additional observations of the SAME physical location
(different angles of the street, wet facades, reflective cobblestones).
Use them only to understand architecture, depth, scale and geometry.
They are NOT separate places. Do not cut between them.

Reconstruct one coherent 3D frozen world from all references.

Then perform ONE continuous camera shot, no cuts:
The camera starts exactly from Image1, low and behind the woman,
glides forward past her shoulder (her red dress frozen mid-swish,
hair suspended, raindrops stopped in the air), then orbits once
around her at chest height holding on her face in tight close-up,
then follows her eyeline down the rain-slicked street toward marker 2.

TIME FREEZES COMPLETELY: every person, raindrop, pigeon and strand
of hair locks mid-motion like a sculpture for the entire shot.

ONE exception — the only living thing: a small DOG in the background
walking slowly left-to-right, wet fur, completely unbothered, the
only moving element in the frozen world. The dog obeys real physics.

The camera moves. The world stays frozen. Smooth gliding camera with
weight, no whip pans, no shake, no speed ramps, no zoom, no 2D slide.
Genuine spatial parallax: near architecture moves faster than far.

Photorealistic documentary footage, natural overcast daylight,
soft diffused light, rain falling visibly but suspended mid-air,
wet pavement reflections, shallow depth of field. No CGI, no plastic
surfaces, no excessive HDR, no bloom.

AUDIO: the frozen world is muffled — a low dreamlike drone, soft
airy whooshes as the camera passes objects, distant rain on stone.
The dog carries his own sound: paws on wet pavement, a light
melancholic piano motif that grows as the camera finds him.
No other music. Final frame: footsteps fade into distance.

One continuous 10-second shot. No cuts. No teleportation.
```

If Flow accepts only one reference at a time: drop Image3–5 lines, keep
FIRST_FRAME + the camera-guide IMAGE_REF_0. If it has no first-frame
slot, prepend `<FIRST_FRAME>` to the photo description in the text.
