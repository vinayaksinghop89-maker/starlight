# AURA Robotics Lab

[![Deploy to GitHub Pages](https://github.com/vinayaksinghop89-maker/starlight/actions/workflows/deploy.yml/badge.svg)](https://github.com/vinayaksinghop89-maker/starlight/actions/workflows/deploy.yml)

AURA is a browser-based 3D robot-tag simulation built with Astro and Three.js.
It demonstrates grid-based A* navigation, obstacle avoidance, a fleeing target,
and a timed role reversal.

## Play online

Visit the [AURA 3D Tag Arena](https://vinayaksinghop89-maker.github.io/starlight/aura/).
The site is deployed to GitHub Pages when changes are pushed to `main`. Enable
GitHub Pages with **GitHub Actions** as the source in the repository's
**Settings → Pages**.

## Run the 3D simulation

Install Node.js, then run these commands from the project root:

```sh
npm install
npm run dev
```

Open the local address printed by Astro and select **Play the 3D tag arena**, or
go directly to `/aura/`.

## How to play

1. Select **Start 60-second chase**. AURA automatically plans a route and chases
   the red target while it tries to escape.
2. If AURA hasn't tagged it after 60 seconds, use **WASD** or the **arrow keys**
   to steer AURA away from the target.
3. Drag in the arena to orbit the camera, scroll to zoom, and select **Reset
   arena** at any time to start over.

Two power orbs spawn on opposite sides of the arena every 30 seconds. Touch
the speed orb for double speed or the jump orb to leap over the opponent; each
effect lasts 5 seconds.

The simulation runs entirely in the browser and does not control physical
hardware.

## Desktop prototype

The original Pygame simulator is in [`aura/`](./aura/). See
[`aura/README.md`](./aura/README.md) for its Windows setup and controls.

## Development

```sh
npm test
npm run build
```
