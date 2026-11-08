Calculates the FTLD-CDR Global from the eight FTLD-CDR boxes (the six CDR domains plus Behavior,
Comportment and Personality, and Language). Works offline, no installation needed.
Score a single case (showing the applied rule), view the scoring rules, or score a whole CSV file
(the output adds `FTLD_CDR_global`, `Rule_applied` and `FTLD_CDR_note`; the original file is never modified).

### Download (see Assets below)

| System | File |
|---|---|
| Windows 10 / 11 | `FTLD_CDR_Global_Calculator_Windows.exe` |
| macOS, Apple Silicon (M1 or later) | `FTLD_CDR_Global_Calculator_macOS_AppleSilicon.zip` |
| macOS, Intel | `FTLD_CDR_Global_Calculator_macOS_Intel.zip` |
| Linux | `FTLD_CDR_Global_Calculator_Linux` (or the `.flatpak` / `.snap` packages) |

### First run

* **Windows:** if "Windows protected your PC" appears (the program is not digitally signed),
  click **More info → Run anyway**.
* **macOS:** unzip and move "FTLD-CDR Global Calculator" to Applications. The first time macOS blocks it
  because it is not signed by Apple: open it once, then go to **System Settings → Privacy & Security**
  and click **Open Anyway** (macOS 14 or older: right-click the app → **Open**).
  **Note:** the macOS version has not been tested on a real Mac (the author does not have one). It is
  built automatically and checked to start without errors. Please report any problem on the
  [Issues page](https://github.com/MMarcelo85/Global_FTLD_cdr_calculator/issues).
* **Linux:** run `chmod +x FTLD_CDR_Global_Calculator_Linux` once (or tick "Allow executing file as program"
  in Properties). Flatpak: `flatpak install --user FTLD_CDR_Global_Calculator.flatpak`.
  Snap: `sudo snap install --dangerous FTLD_CDR_Global_Calculator.snap`.

Web version: https://global-ftld-cdr-calculator.streamlit.app/ · CSV format and rules: see the
[README](https://github.com/MMarcelo85/Global_FTLD_cdr_calculator#readme).
