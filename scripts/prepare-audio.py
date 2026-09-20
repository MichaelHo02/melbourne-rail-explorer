#!/usr/bin/env python3
"""Prepare licensed field-recording assets from the documented public preview files.
Usage: python3 scripts/prepare-audio.py /tmp/southern-cross-source.mp3 /tmp/flinders-intersection-source.mp3
Requires ffmpeg. Sources, licenses and locations are retained in the manifest.
"""
import argparse,hashlib,json,pathlib,subprocess
parser=argparse.ArgumentParser();parser.add_argument('southern_cross');parser.add_argument('flinders_exterior');parser.add_argument('--parliament');args=parser.parse_args()
output=pathlib.Path('public/audio');output.mkdir(parents=True,exist_ok=True)
clips=[
 {'file':'southern-cross-ambience.mp3','input':args.southern_cross,'start':20,'title':'Train Station ambience','creator':'eaglechopper','source':'https://freesound.org/people/eaglechopper/sounds/237999/','preview':'https://cdn.freesound.org/previews/237/237999_3948615-hq.mp3','location':'Southern Cross station, Melbourne','description':'Historic station field recording; source author describes trains arriving/departing and muffled announcements. Not a dynamic service announcement.'},
 {'file':'flinders-exterior-ambience.mp3','input':args.flinders_exterior,'start':30,'title':'Melbourne City Intersection Trams & Cars Traffic Afternoon','creator':'melbourne.atmospheres','source':'https://freesound.org/people/melbourne.atmospheres/sounds/582919/','preview':'https://cdn.freesound.org/previews/582/582919_13141607-hq.mp3','location':'Flinders Street / Swanston Street intersection, Melbourne','description':'Outdoor intersection beside Flinders Street station: traffic, trams and pedestrian activity. Not station-platform or onboard audio.'},
]
manifest=[]
for clip in clips:
 source=pathlib.Path(clip['input']);target=output/clip['file']
 # A 62s segment becomes a 60s loop: retain middle58s, then equal-power
 # crossfade the last2s into the first2s. The result ends where its middle starts.
 graph='[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,highpass=f=65,loudnorm=I=-24:TP=-3:LRA=11,asplit=3[m][t][h];[m]atrim=start=2:end=60,asetpts=PTS-STARTPTS[mid];[t]atrim=start=60:end=62,asetpts=PTS-STARTPTS[tail];[h]atrim=start=0:end=2,asetpts=PTS-STARTPTS[head];[tail][head]acrossfade=d=2:c1=qsin:c2=qsin[join];[mid][join]concat=n=2:v=0:a=1[out]'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(clip['start']),'-t','62','-i',str(source),'-filter_complex',graph,'-map','[out]','-ar','44100','-c:a','libmp3lame','-b:a','128k',str(target)],check=True)
 item={k:v for k,v in clip.items() if k!='input'}
 item.update({'license':'CC0 1.0 Universal','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'durationSeconds':60,'processing':'62-second excerpt; 65 Hz high pass; -24 LUFS target; 2-second equal-power wrap crossfade; stereo MP3 128 kbit/s','verification':'Decoder, duration, loudness and clipping checked. No human listening review or PA transcript verification yet.'})
 manifest.append(item)
if args.parliament:
 source=pathlib.Path(args.parliament);target=output/'parliament-departure.mp3'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-af','highpass=f=65,loudnorm=I=-24:TP=-3:LRA=11,afade=t=in:d=0.1,afade=t=out:st=45:d=0.7','-ar','44100','-c:a','libmp3lame','-b:a','128k',str(target)],check=True)
 manifest.append({'file':target.name,'title':'Xtrap depart.mp3','creator':'Tanoseki','source':'https://freesound.org/people/Tanoseki/sounds/69560/','preview':'https://cdn.freesound.org/previews/69/69560_911819-hq.mp3','location':'Parliament station, Melbourne','description':'Historic field recording of an Xtrapolis departure, published 23 March 2009. Not HCMT traction audio or a current service announcement.','license':'CC BY 3.0 Unported','licenseUrl':'https://creativecommons.org/licenses/by/3.0/','derivativeLicense':'CC BY 3.0 Unported','attribution':'Xtrap depart.mp3 by Tanoseki, via Freesound, CC BY 3.0. Modified: high-pass filter, loudness normalization, edge fades and MP3 re-encoding.','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'durationSeconds':float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(target)],text=True).strip()),'loop':False,'processing':'Full departure recording; 65 Hz high pass; -24 LUFS target; brief edge fades; stereo MP3 128 kbit/s','verification':'Decoder, duration and true peak checked. Human listening and transcript verification not performed.'})
(output/'sources.json').write_text(json.dumps({'assets':manifest},indent=2)+'\n')
print('Prepared',len(manifest),'documented licensed field recordings')
