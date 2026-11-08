# FTLD-CDR Global Calculator

### Simple app to calculate the FTLD-CDR Global for the ReDLat project

The FTLD-CDR has eight domains or boxes: the six CDR domains (Memory, Orientation, Judgment and Problem
Solving, Community Affairs, Home and Hobbies, Personal Care) plus Behavior, Comportment and Personality,
and Language.

Two versions with the same scoring code (`ftld_core.py`):

* **Web app:** [run it on Streamlit](https://global-ftld-cdr-calculator.streamlit.app/) (`main.py`).
* **Desktop app (Windows / Linux / macOS, no installation, works offline):** download
  `FTLD_CDR_Global_Calculator_Windows.exe`, `FTLD_CDR_Global_Calculator_Linux` or the macOS zip from the
  [Releases page](https://github.com/MMarcelo85/Global_FTLD_cdr_calculator/releases/latest) and double-click it.
  * Windows may show "Windows protected your PC" (the program is not digitally signed):
    click **More info → Run anyway**.
  * Linux: the first time, run `chmod +x FTLD_CDR_Global_Calculator_Linux` (or tick "Allow executing file as program" in Properties).
  * macOS: download `FTLD_CDR_Global_Calculator_macOS_AppleSilicon.zip` (M1 or later) or
    `FTLD_CDR_Global_Calculator_macOS_Intel.zip` (older Intel Macs; Apple menu → About This Mac shows which),
    double-click the zip and move "FTLD-CDR Global Calculator" to Applications. The app is not signed by Apple,
    so the first time macOS blocks it: open it once, then go to **System Settings → Privacy & Security**
    and click **Open Anyway** (on macOS 14 or older: right-click the app → **Open**).
    **Note:** the macOS version has not been tested on a real Mac (the author does not have one). It is
    built automatically and checked to start without errors. If you find a problem, please report it
    on the [Issues page](https://github.com/MMarcelo85/Global_FTLD_cdr_calculator/issues).
  * Linux packages (adds the app to the applications menu), also on the Releases page:
    * Flatpak: `flatpak install --user FTLD_CDR_Global_Calculator.flatpak`
    * Snap: `sudo snap install --dangerous FTLD_CDR_Global_Calculator.snap`
      (`--dangerous` is needed because the snap is not published in the Snap Store).

Both versions let you score a single case (showing the applied rule), view all the rules,
and score a whole CSV file.

### CSV files

* Either exactly 8 columns in this order: Memory, Orientation, Judgment, Community, Home, Personal care,
  Behavior, Language (e.g. `Memory, box1, box2, box3, box4, box5, box6, box7`),
* or any number of columns where the eight FTLD-CDR columns are named Memory, Orientation, Judgment,
  Community, Home, PersonalCare, Behavior, Language (Spanish names such as Memoria, Orientación, Juicio,
  Comunidad, Hogar, Cuidado personal, Comportamiento, Lenguaje and NACC names such as MEMORY, ORIENT,
  JUDGMENT, COMMUN, HOMEHOBB, PERSCARE, COMPORT, CDRLANG also work). Other columns, such as IDs, are kept unchanged.
* Comma, semicolon or tab separated; decimal point or decimal comma (`0.5` / `0,5`); UTF-8 or Latin-1.
* The output adds `FTLD_CDR_global`, `Rule_applied` and `FTLD_CDR_note`. Rows with missing or invalid scores
  (e.g. Personal care = 0.5, or a code such as 9) are kept, with the reason in `FTLD_CDR_note`.
  The original file is never modified.

### FTLD-CDR Scoring Instructions

Two scores must be obtained:

1. FTLD-CDR Box Sum (automatically calculated in REDCap): calculate the sum of values for all responses (including the two additional domains) and enter the total score in the provided space.
2. FTLD-CDR Global: derived from the scores in each of the eight categories ("box scores"). This app calculates this score.

The rules for determining the FTLD-CDR global score are as follows (remember, they involve the eight domains or boxes):

1. If all domains are 0, the FTLD-CDR global score is 0.
2. If the maximum domain score is 0.5, the FTLD-CDR global score is 0.5.
3. If the maximum domain score is greater than 0.5 in any domain, the following applies:
   * A. If the maximum domain score is 1 and all other domains are 0, the FTLD-CDR global score is 0.5.
   * B. If the maximum domain score is 2 or 3 and all other domains are 0, the FTLD-CDR global score is 1.
   * C. If the maximum domain score occurs only once, and there is another score other than zero, the FTLD-CDR global score is one level lower than the level corresponding to the maximum impairment (for example, if the maximum = 2, and there is another score other than zero, the FTLD-CDR global score is 1; if the maximum = 1, and there is another score other than zero, the FTLD-CDR global score is 0.5).
   * D. If the maximum domain score occurs more than once (for example, 1 in 2 domains, 2 in 2 domains), then the FTLD-CDR global score is that maximum domain score.

### Development

* Tests: `python -m unittest discover -s tests` (includes all 312,500 possible score combinations,
  `tests/golden_ftld_cdr.csv.gz`).
* Run the web app: `pip install -r requirements.txt` then `streamlit run main.py`.
* Run the desktop app: `python desktop_app.py` (standard library only).
* New version: update `APP_VERSION` in `desktop_app.py` and the `<release>` line in
  `packaging/flatpak/io.github.mmarcelo85.FTLDCDRGlobalCalculator.metainfo.xml`, commit, then push a tag
  (`git tag -a v2.0.1 -m "v2.0.1" && git push origin v2.0.1`). GitHub Actions runs the tests, builds the
  Windows, Linux and macOS executables plus Flatpak and Snap, and attaches them to a Release whose text is
  `packaging/release_notes.md` (`.github/workflows/build-desktop.yml`).
* Local build: `pyinstaller --onefile --windowed --name FTLD_CDR_Global_Calculator desktop_app.py`
  (on macOS: `pyinstaller --windowed --name "FTLD-CDR Global Calculator" desktop_app.py`).
