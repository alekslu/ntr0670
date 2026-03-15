# Tehtud Muudatuste Dokumentatsioon

Kuupaev: 2026-03-15

## Mida muudeti
- Kaamera pildi votmine eraldati Windowsi skripti sisse: windows_scripts/camera_win.py.
- WSL skript muudeti orkestreerijaks: wsl_scripts/capture_wsl.py.
- Vahepealne C:\temp kopeerimise voog eemaldati tava-kaivitusest.
- Valjund suunati otse repoga jagatud kausta output/webcam.png.
- Lisaargumendid tehti minimaalseks, et kaivitus oleks lihtne.

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
6. Tulemus tekib kaustas output/webcam.png.

## Mis eemaldati varasemast lahendusest
- Kohustuslikud ajutised failiteed C:\temp all.
- Eraldi "tee pilt C:\temp-i ja siis kopeeri" samm.
- Liigne CLI paindlikkus WSL wrapperis.

## Hetke piirangud
- Windowsi skript on endiselt vajalik, sest kaamera capture toimub Windowsis.
- Kui python.exe ei ole WSL-ist leitav, kaivitus ebaonnestub.
- Kui Windowsi Pythonis puudub OpenCV, tuleb paigaldada opencv-python.

## Kuidas kontrollida, et koik tohib
- Kaivita: python3 wsl_scripts/capture_wsl.py
- Kontrolli, et output/webcam.png tekib/uueneb.
- Kontrolli, et valjundis kuvatakse edu voi veateade.

## Jargmised soovituslikud sammud
- Lisa lihtne testskript, mis kontrollib faili olemasolu parast kaivitust.
- Kui kaameraindeks vajab vahetamist, lisa see tagasi WSL skripti lipuna.
- Kui soovid, voib selle faili hiljem jagada osadeks "arhitektuur", "runbook", "muudatuste logi".
