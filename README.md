# digital_twin_diego

**Reusable three-axis CNC digital twin (OKUMA and MAZAK)**: MFG 598 Industrial IoT, Arizona State University.

A web page that reads live MTConnect data from the [Metalogi demo agent](https://demo.metalogi.io/) and animates a 3D machine. It does not hard-code device names, data-item ids or axis names. Everything comes from the agent's machine description (`/probe`).

## Files

| File | What it does |
|---|---|
| `index.html` | The digital twin: discovery tables, 3D model, live data |
| `serve.py` | Small local server. It shows the page and forwards `/mtc/...` to the agent |
| `start_twin.bat` | Windows shortcut: double-click to start the server and open the browser |

## How to run

You only need **Python 3**, with no extra packages.

**Windows**
1. Download the repo (green **Code** button → *Download ZIP*) and unzip it, or `git clone` it.
2. Double-click `start_twin.bat`.

   Or, in PowerShell inside the folder:
   ```powershell
   python serve.py        # if "python" does not work, use: py serve.py
   ```
3. Open <http://localhost:8000/?device=Mazak> (or `?device=OKUMA`).
4. Keep the window open while you use the twin. Press **Ctrl + C** to stop it.

**Mac / Linux**
```bash
python3 serve.py
# then open http://localhost:8000/?device=Mazak
```

**Options**
```bash
python serve.py --port 8080                      # if port 8000 is busy
python serve.py --agent http://<agent-ip>:5000   # use another MTConnect agent
```

> Why a server? The demo agent does not allow web pages from other sites to read its data (no CORS headers). `serve.py` serves the page and the agent data from the same address, so the browser accepts it.

## Using the page

- **Device list**: every device found in `/probe`.
- **View: solid model from probe**: loads the CAD file that the agent declares, as in the Metalogi demo. Each axis moves its own part.
- **View: simplified 5-axis**: block model with 3 linear axes, 2 rotary axes and a spindle. It works with any agent, even one without a CAD file.
- **Axis mapping**: choose which axis drives each slot of the simplified model.
- **Motion scale**: amplify small movements, or show them at true scale.

## How it meets the assignment

| Requirement | How we did it |
|---|---|
| **Discover the machine** | Reads `/probe`. It lists every Linear and Rotary axis with its position data item, units, coordinate system, direction vector (`Motion/Axis`) and parent axis. |
| **Visualize motion** | Reads `/current`, then `/sample` every 200 ms. Linear axes slide along their direction and rotary axes turn. Each axis rides on its parent axis. |
| **No machine-specific assumptions** | Positions come from the data-item type (`POSITION` / `ANGLE`, subtype `ACTUAL`, MACHINE coordinate system). Axes are matched by their direction vector, not their name, so `Z1` or `W` can fill the "Z" slot. |

## Demo agent: what we found

- **Mazak** (5-axis mill): X, Y, Z carry the spindle head; B tilts the table and C2 turns it.
- **OKUMA** (MULTUS lathe): X, Y, Z1, Z4, B (turret tilt), C3, plus spindles C1, C2, C6.
