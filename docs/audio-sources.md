# Real Melbourne ambience recordings

Two CC0 field-recording excerpts are bundled in `public/audio/`. These are real recorded environments, not speech synthesis, cloned voices, fabricated current service announcements or dynamically matched PA messages.

| Asset | Actual location | Creator and primary source | License |
|---|---|---|---|
| `southern-cross-ambience.mp3` | Southern Cross station | [Train Station ambience — eaglechopper](https://freesound.org/people/eaglechopper/sounds/237999/) (2014) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `flinders-exterior-ambience.mp3` | Flinders Street / Swanston Street intersection, outside the station | [Melbourne City Intersection Trams & Cars Traffic Afternoon — melbourne.atmospheres](https://freesound.org/people/melbourne.atmospheres/sounds/582919/) (2021) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |

The Southern Cross author describes arriving/departing trains and muffled announcer sound. The Flinders/Swanston author describes road traffic, trams, bells, pedestrian crossing, footsteps, chatter and bicycles. Both primary sound pages explicitly display Creative Commons 0 and permission to copy, modify and distribute, including commercial use. These source descriptions do not establish the exact speech content of the selected excerpts. Do not present either as an accurate current timetable or a player-triggered station announcement.

Original downloads on Freesound require login; these assets instead use the site's openly served public MP3 previews, without logging in, authenticated downloads or bypassing access controls. The Freesound HTML/embed request returned HTTP502 in the environment; its public CDN served the previews normally. [Openverse's public audio index](https://api.openverse.org/v1/audio/?q=Flinders&license=cc0&page_size=20) provided the Flinders/Swanston preview URL. The Southern Cross creator ID was resolved from the author's other indexed recordings and the public preview URL was successfully verified against the source's duration. Exact preview URLs, hashes, creators, license links and transformations are in `public/audio/sources.json`.

## Preparation and verification

Rebuild: `python3 scripts/prepare-audio.py /path/to/southern-cross-source.mp3 /path/to/flinders-intersection-source.mp3` (Python standard library and FFmpeg).

Each output is a 60-second stereo loop encoded at 128 kbit/s. Southern Cross uses source seconds 20–82; Flinders/Swanston uses 30–92. Preparation applies a 65 Hz high-pass filter, loudness normalization targeting −24 LUFS, then joins the tail and head with a 2-second equal-power crossfade. This preserves ambience and keeps file sizes below 1 MB each. Attribution is retained voluntarily despite CC0 not requiring it.

FFmpeg successfully decodes both files; duration, integrated loudness and true peak are checked. No human listening review has been performed in this subtask. Final playback mixing, perceived loop seam, selected-excerpt suitability and intelligibility of any PA require listening in the integrated game. No announcement transcript is asserted.

## Leads not bundled

- [TrainStationAmbience_V1 — phuonglamb, Freesound 844030](https://freesound.org/people/phuonglamb/sounds/844030/) is explicitly CC0 and described as Flinders Street station recordings. Its public preview URL could not be established through accessible public metadata; no login was attempted. This remains a better future interior-specific recording once publicly accessible or supplied by the user.
- [Kyle Evans / Squeakyfish Guide Dogs soundscapes](https://www.squeakyfish.com.au/guidedogs/) include a 14-minute Flinders station soundscape, but the creator explicitly excludes commercial use and licenses it **CC BY-NC-SA 4.0**. It is not bundled or treated as unrestricted free game audio.
- Royal Park and generic train recordings were not substituted for City Loop station interiors.

Measured output: Southern Cross **−24.4 LUFS, −10.2 dBFS true peak**; Flinders exterior **−27.3 LUFS, −8.3 dBFS true peak**. Both decode to exactly 60 seconds and are 960,932 bytes. Neither clips.

## Parliament departure recording

`parliament-departure.mp3` is derived from [Xtrap depart.mp3 by Tanoseki](https://freesound.org/people/Tanoseki/sounds/69560/), published 23 March 2009. The creator explicitly identifies Parliament station, Melbourne, and an Xtrapolis train departing. Source and derivative are **[CC BY 3.0 Unported](https://creativecommons.org/licenses/by/3.0/)**, not CC0. Commercial redistribution is permitted with attribution. Preserve this credit in the game's accessible credits/attribution:

> Xtrap depart.mp3 by Tanoseki, via Freesound, CC BY 3.0. Modified: high-pass filter, loudness normalization, edge fades and MP3 re-encoding.

Link the title to the source and the license to its URL. This is a historic Xtrapolis field recording, not HCMT engine audio, verified current PA, or a recording of any other City Loop station. Treat it as a **one-shot departure sound**, not a continuous background loop; repeated departures would be misleading. No intelligible PA transcript has been verified.

Rebuild all three assets by adding `--parliament /path/to/parliament-departure-source.mp3` to the preparation command. The public preview URL was obtained from Openverse and downloaded from Freesound's CDN. The original source/derivative hashes and attribution are retained in `sources.json`.

The bounded search did not locate a suitable unrestricted Flagstaff platform recording or Melbourne Central platform recording. The CC0 Central result was a toilet ventilation fan; the Flagstaff results were Arizona recordings or a Melbourne outdoor cycling soundscape. None was relabelled as platform ambience. Whisper, faster-whisper and transcription CLI tools were absent, and no general audio-transcription tool was exposed in this session, so no automatic speech transcription or human listening review was claimed.

Parliament output validation: 45.741474 seconds, 733,144 bytes, −21.8 LUFS integrated and −5.6 dBFS true peak; no clipping.
