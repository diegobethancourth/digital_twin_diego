# digital_twin_diego

Digital Twin OKUMA and MAZAK, MFG 598 Industrial IoT (ASU)

This is our digital twin for the CNC assignment. The page connects to the Metalogi demo agent (https://demo.metalogi.io), reads the MTConnect data and moves a 3D machine with the real positions. We did not write any machine names or ids in the code: the page reads them from the probe.

## Files

- `index.html` is the digital twin page
- `serve.py` is a small Python server that sends the agent data to the page
- `start_twin.bat` starts everything on Windows with a double-click

## How to run it

### Option 1: on your computer (Python 3)

1. Download the repo (Code → Download ZIP) and unzip it.
2. Double-click `start_twin.bat`, or open PowerShell in the folder and type:

   ```
   python serve.py
   ```

   (if `python` does not work, try `py serve.py`, or `python3 serve.py` on Mac)
3. Open http://localhost:8000/?device=Mazak in the browser (or `?device=OKUMA`).
4. Leave the window open. To stop it, press Ctrl + C.

### Option 2: from GitHub (Codespaces, nothing to install)

1. In this repo, click Code → Codespaces → Create codespace on main.
2. Wait about a minute. The server starts by itself and the twin opens in a new tab.
3. If the tab does not open, go to the Ports tab and click the globe icon on port 8000.

## Why we need serve.py

The demo agent does not let other websites read its data (no CORS). So the page cannot work alone on GitHub Pages. `serve.py` gets the data from the agent and gives it to the page from the same address, and then the browser accepts it.

## What the page does

1. Reads `/probe` and finds the axes, position data items, units and coordinate systems.
2. Builds the 3D machine. There are two views:
   - solid model: the CAD file that the agent gives in the probe (same as the Metalogi example)
   - simplified: 3 linear axes + 2 rotary axes + spindle, made with simple blocks
3. Reads `/current` and then `/sample` every 200 ms, and moves the axes with the real values.

Axes are found by their direction (`Motion/Axis`) and data type (`POSITION`, `ANGLE`), not by their name. So it should also work with other machines.

## What we found in the demo agent

- Mazak: X, Y, Z move the spindle head, B tilts the table and C2 rotates it.
- OKUMA: X, Y, Z1, Z4, B and C3, plus spindles C1, C2 and C6.
