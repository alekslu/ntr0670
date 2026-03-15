# Rakenduse Dokumentatsioon

Kuupaev: 2026-03-15

## Mis rakendus teeb

Rakendus teeb USB kaameraga pildi ja tuvastab sellelt inimesi, pead ja palle YOLO mudeli abil.

Voog lyyhidalt:
1. Kasutaja kaivitab WSL-ist yle tahes capture_and_detect.py.
2. Windows Python teeb kaameraga pildi ja salvestab selle kausta output/images/ jarjestikuse failinimega.
3. WSL Python laeb output/images kausta pildid YOLO mudelisse ja tuvastab inimesed, head ja pallid.
4. Tulemus tekib output/analysis/detections_all.json faili ja output/analysis/annotated/ kausta.

Kasutusnaide: spordis mängija ja palli asukoha jälgimine ühe käsuga ilma käsitsi faile liigutamata.

## Mida muudeti
- Kaamera pildi votmine eraldati Windowsi skripti sisse: windows_scripts/camera_win.py.
- WSL skript muudeti orkestreerijaks: wsl_scripts/capture_wsl.py.
- Vahepealne C:\temp kopeerimise voog eemaldati tava-kaivitusest.
- Valjund suunati otse repoga jagatud kausta output/webcam.png.
- Lisaargumendid tehti minimaalseks, et kaivitus oleks lihtne.
- Lisati YOLO tuvastus WSL poolele: wsl_scripts/detect_yolo.py.
- Lisati full pipeline skript: wsl_scripts/capture_and_detect.py.

## Miks nii tehti
- USB kaamera avamine tootab stabiilsemalt Windowsi poolel.
- Arenduse juhtimine peab siiski kaima WSL-ist.
- Eesmargiks oli hoida koik failid uhes Git projektis ilma kasitsi tostmiseta.

## Praegune too- ja andmevoog
1. Kasutaja kaivitab WSL-is: python3 wsl_scripts/capture_wsl.py.
2. WSL skript leiab repo juurkausta oma asukoha jargi.
3. WSL skript teisendab vajalikud teed Windowsi formaati (wslpath -w).
4. WSL skript kaivitab Windows Pythoni:
	python.exe windows_scripts/camera_win.py --output <windows_path>.
5. Windows skript avab kaamera, soojendab luhidalt, teeb uhe kaadri ja salvestab faili.
6. Tulemus tekib kaustas output/images/ failina image_ppkkaaaa_tt_mm_ss.png (nt image_15032026_18_42_07.png).

## YOLO tuvastuse voog
1. WSL skript detect_yolo.py loeb vaikimisi koik .png/.jpg/.jpeg pildid kaustast output/images/.
2. YOLO mudel (vaikimisi yolov8l.pt) teeb inferentsi CPU peal.
3. Arvesse voetakse klassid person, sports ball ja frisbee.
   - frisbee lisati, sest pall keha ees tuvastatakse yolov8 poolt tihti frisbee-na.
4. Iga person bbox pealt arvutatakse head_estimate (ulemised 35%).
5. Tulemus salvestatakse koondfaili output/analysis/detections_all.json ning iga pildi margendatud versioon output/analysis/annotated/ kausta.

Tahelepanu: head_estimate ei ole eraldi peamudel, vaid inimese kasti pealt tehtud hinnang.

## YOLO mudelid

Vaikimisi: yolov8l.pt (87 MB, aeglasem, kuid koige tapsem CPU peal).

Saadaval mudelid, mis laaditakse alla automaatselt:
- yolov8n.pt  6 MB   kiireim, testimiseks
- yolov8s.pt  22 MB  soovitatav igapaevane kasutus
- yolov8m.pt  52 MB  parem tapsus, aeglasem
- yolov8l.pt  87 MB  parim tapsus CPU peal

Mudeli vahetamine: --model yolov8s.pt lipuga.

## Laved ja nende muutmine

Vaikimisi laved:
- inimene: --conf-person 0.35
- pall:    --conf-ball   0.03

Lave langetamine aitab kui pall on osaliselt varjatud.
Lave tostmine vahendab valetuvastusel.

## Mis eemaldati varasemast lahendusest
- Kohustuslikud ajutised failiteed C:\temp all.
- Eraldi "tee pilt C:\temp-i ja siis kopeeri" samm.
- Liigne CLI paindlikkus WSL wrapperis.

## Hetke piirangud
- Windowsi skript on endiselt vajalik, sest kaamera capture toimub Windowsis.
- Kui python.exe ei ole WSL-ist leitav, kaivitus ebaonnestub.
- Kui Windowsi Pythonis puudub OpenCV, tuleb paigaldada opencv-python.

## Kuidas kontrollida, et koik tohib
- Kaivita: python wsl_scripts/capture_wsl.py
- Kontrolli, et output/images/ kausta tekib uus ajatempliga fail.
- Kontrolli, et valjundis kuvatakse edu voi veateade.
- Kaivita tuvastus: python wsl_scripts/detect_yolo.py
- Kontrolli, et tekib output/analysis/detections_all.json ja output/analysis/annotated/ kaust.

## Jargmised soovituslikud sammud
- Lisa lihtne testskript, mis kontrollib faili olemasolu parast kaivitust.
- Kui kaameraindeks vajab vahetamist, lisa see tagasi WSL skripti lipuna.
- Kui soovid, voib selle faili hiljem jagada osadeks "arhitektuur", "runbook", "muudatuste logi".
