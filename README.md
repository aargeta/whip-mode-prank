# Whip Mode — Windows Desktop Prank

Press **Ctrl+Alt+W** and your mouse cursor turns into a whip, a whip-crack sound
plays, and a robotic voice yells **"Get back to work, Claude!"** — cursor snaps
back to normal after ~4 seconds. Fires instantly, no window pops up, totally silent
otherwise.

Runs on Windows via [AutoHotkey v2](https://www.autohotkey.com/) — free, tiny, safe.

## Install (~2 minutes)

1. Install AutoHotkey v2:
   ```
   winget install --id AutoHotkey.AutoHotkey
   ```
   (or download from autohotkey.com if you don't have winget)

2. Grab these 4 files and put them in one folder together:
   - `whip.ahk` — the script
   - `make_assets.py` — regenerates the sound + cursor files (needs Python)
   - `whipcrack.wav` — the crack sound effect
   - `whip.cur` — the whip cursor

   If you only have `whip.ahk` and `make_assets.py`, run:
   ```
   python make_assets.py
   ```
   to generate `whipcrack.wav` and `whip.cur` in the same folder.

3. Double-click `whip.ahk` to run it (or right-click → Run Script).

4. Press **Ctrl+Alt+W**. Enjoy.

## Run it automatically on login (optional)

Drop a shortcut to `whip.ahk` in your Startup folder:
```
Win+R → shell:startup → paste a shortcut to whip.ahk there
```
Now it's armed every time you log in.

## How it works (for the curious)

- `whip.ahk` registers the `Ctrl+Alt+W` hotkey, swaps every system cursor
  (`SetSystemCursor`) to `whip.cur`, plays `whipcrack.wav`, and speaks the line
  through Windows' built-in SAPI text-to-speech (pitched down for the robot
  voice), then restores the default cursors after 4 seconds.
- `make_assets.py` synthesizes the crack sound (a noise burst with a sharp
  decay envelope, no royalty-free-audio-hunting required) and hand-draws the
  whip cursor as a coiled spiral, then packages it as a real `.cur` file.
- Nothing here touches any other app, requires admin rights, or persists
  beyond restoring the cursor — it's a clean, reversible prank.
