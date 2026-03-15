# Camera Project (WSL2 + Windows USB Camera Bridge)

## Mis see rakendus teeb

Rakendus teeb USB kaameraga pildi ja tuvastab sellelt automaatselt:
- **inimesed** (YOLO klass `person`)
- **pead** (hinnanguline — inimese bounding box ülemine 35%)
- **pallid** (YOLO klassid `sports ball` ja `frisbee`)

Pildid salvestatakse kausta `output/images/` ja failinimega `image_ppkkaaaa_tt_mm_ss.png` (nt `image_15032026_18_42_07.png`).
Tuvastuse koondtulemus salvestatakse `output/analysis/detections_all.json` ja margendatud pildid kausta `output/analysis/annotated/`.

Kasutusnäide: spordis liikumise jälgimine, palli ja mängija asukohta logimine ühe käsuga.

## Süsteemi ülesehitus
- WSL juhib kogu töövoogu.
- Windows käsitleb USB kaamera ligipääsu (WSL2-s pole see stabiilne).
- Kõik väljundfailid tekivad otse repo `output/` kausta — faile pole vaja käsitsi liigutada.

## Project layout
- windows_scripts/camera_win.py: Windows-side OpenCV capture script.
- wsl_scripts/capture_wsl.py: WSL launcher and path bridge.
- wsl_scripts/detect_yolo.py: YOLO inference for person, head estimate and ball (batch reziim output kaustale).
- wsl_scripts/capture_and_detect.py: full flow (capture + detect).
- output/images/: kaamerast salvestatud pildid (jarjestikune numeratsioon).
- output/analysis/: skanni analuusi tulemused (JSON + annotated pildid).
- docs/spec.md: eestikeelne ulevaade, mis muudeti ja kuidas voog toole pandi.

## Prerequisites
- WSL2 Ubuntu environment.
- Windows Python available as python.exe from WSL.
- OpenCV installed in Windows Python environment.
- wslpath available in WSL.

## Setup
WSL venv kiire setup:

```bash
cd ~/ntr0670/camera_proj
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-wsl.txt
```

Venv-ist valjumine:

```bash
deactivate
```

Install OpenCV for the Windows interpreter:

```bash
python.exe -m pip install opencv-python
```

Optional check:

```bash
python.exe -c "import cv2; print(cv2.__version__)"
```

Install WSL-side dependencies for YOLO:

```bash
python -m pip install -r requirements-wsl.txt
```

## Run capture
From repository root in WSL:

```bash
python wsl_scripts/capture_wsl.py
```

Expected result:
- uus fail tekib kausta `output/images/` (nt `image_15032026_18_42_07.png`).
- command exits with code 0 on success.

## YOLO mudelid

| Mudel | Failisuurus | Täpsus | CPU kiirus | Kasutus |
|---|---|---|---|---|
| `yolov8n.pt` | 6 MB | madalaim | kiireim | kiireks testimiseks |
| `yolov8s.pt` | 22 MB | parem | hea | soovitatav igapäevaseks kasutuseks |
| `yolov8m.pt` | 52 MB | hea | aeglasem | kui `s` ei anna piisavalt täpsust |
| `yolov8l.pt` | 87 MB | väga hea | aeglane | vaikimisi, parim täpsus CPU peal |

Mudeli fail laaditakse alla automaatselt esimesel kasutuskorral.

**Vaikimisi mudel** on `yolov8l.pt` — määratud `detect_yolo.py` ja `capture_and_detect.py` argumendi `--model` vaikeväärtusena.

## Run YOLO detection (koik output pildid)

Vaikimisi mudeliga:
```bash
python wsl_scripts/detect_yolo.py
```

Suurema mudeliga:
```bash
python wsl_scripts/detect_yolo.py --model yolov8s.pt
```

Result files:
- `output/analysis/detections_all.json` — koondraport koigi toodeldud piltide kohta
- `output/analysis/annotated/` — iga pildi margendatud versioon

Yhe pildi analyys (valikuline):
```bash
python wsl_scripts/detect_yolo.py --image output/images/image_15032026_18_42_07.png
```

Märkused:
- `person` — YOLO klass person
- `ball` — YOLO klassid sports ball või frisbee (pall varjutud keha ees tuvastatakse tihti frisbee-na)
- `head_estimate` — inimese bbox ülemine 35%, mitte eraldi peamudel

## Run full pipeline (capture + detect)

Vaikimisi mudeliga:
```bash
python wsl_scripts/capture_and_detect.py
```

Suurema mudeliga:
```bash
python wsl_scripts/capture_and_detect.py --model yolov8l.pt
```

**NB:** `capture_and_detect.py` tuleb käivitada WSL terminalist, mitte PowerShellist.

## Tuvastuse lävede muutmine

Vaikimisi läviväärtused:
- `--conf-person 0.35` — inimene tuvastatakse kui konfidents ≥ 35%
- `--conf-ball 0.03` — pall tuvastatakse kui konfidents ≥ 3%

Kui pall jääb tuvastamata (kaetud käega), proovi madalama palliläve või suurema mudeliga:
```bash
python wsl_scripts/detect_yolo.py --conf-ball 0.05 --model yolov8s.pt
```

Kui tuvastatakse liiga palju valesid objekte, tõsta läve:
```bash
python wsl_scripts/detect_yolo.py --conf-person 0.5 --conf-ball 0.15
```

Debug vaade kõigi toortuvastustega:
```bash
python wsl_scripts/detect_yolo.py --conf-ball 0.01 --debug
```

## TODO

- Lisa production mode lyliti, mis salvestab ainult JSON tulemused ja ei salvesta annotated pilte.