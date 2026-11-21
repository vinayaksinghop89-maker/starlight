# AURA: first simulator prototype

This is the first AURA milestone: a small 2D simulation with a manually
controlled robot, walls, a red object that flees at AURA's speed during a tag
mission, a grid-based A* planner, and text commands for finding or tagging the
object. Perception is simulated for now; no camera, YOLO model, or robot
hardware is needed.

## Run on Windows

Install Python 3.11, then open a terminal in this `aura` directory:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The simulator uses Pygame Community Edition, which provides a Windows ARM64
wheel and is imported by the code as `pygame`.

If PowerShell prevents environment activation, use Command Prompt and run
`.venv\Scripts\activate.bat` instead.

## Controls

- **WASD** or **arrow keys**: drive the robot manually.
- **T**: enter a mission.
- Type **`find the red object`** and press **Enter**: plan and follow an A*
  route to the object.
- Type **`tag the red object`** and press **Enter**: chase the object as it
  moves away. AURA has 60 seconds to catch it.
- If time expires, the red object chases AURA; use **WASD** or the **arrow
  keys** to escape.
- **R**: restart after either player wins.
- **Space**: stop the current route.
- **Esc**: cancel command entry or close the simulator.

The room and obstacles are fixed in `main.py`. The planner and command parser
are separate modules so they can be tested without opening the game window.

## Tests

From this directory, run:

```powershell
python -m unittest -v
```

Next steps are to make the world editable, add simulated sensor readings, and
then connect OpenCV before trying webcam or YOLO-based perception.
