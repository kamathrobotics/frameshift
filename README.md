# Versor
[![CI](https://github.com/kamathrobotics/versor/actions/workflows/ci.yml/badge.svg)](https://github.com/kamathrobotics/versor/actions/workflows/ci.yml)
![Project Status](https://img.shields.io/badge/Status-Active-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES%20Modules-yellow?style=flat&logo=javascript&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-r162-black?style=flat&logo=threedotjs&logoColor=white)
![License](https://img.shields.io/github/license/kamathrobotics/versor?label=License)

A browser-based 3D rotation converter with real-time visualization. Convert between rotation formats used in robotics, computer graphics, and aerospace — all client-side, no backend.

## Features

- Convert between 5 rotation formats:
  - **Euler angles** — configurable rotation order (XYZ, ZYX, etc.), degrees or radians
  - **Quaternion** — WXYZ convention, with live norm indicator
  - **Rotation matrix** — 3×3, copy-friendly
  - **Axis-angle** — axis vector + angle
  - **Rotation vector** — compact 3-element representation
- Real-time 3D visualization with Three.js (orbit, pan, zoom)
- Live conversion as you type
- Optional translation offset for the 3D view
- Copy-to-clipboard for all output formats

## Usage

Select an input format, enter values, and all other representations update instantly. The 3D viewer shows the rotation applied to a coordinate frame.

- Left-click + drag to orbit
- Right-click + drag to pan
- Scroll to zoom

## Local Development

```sh
npm install
npm run dev
```

Opens at `http://localhost:8787`.

## Project Structure

```
public/
  index.html                 ← Single-file app (HTML + CSS + JS)
  kamath_robotics_favicon.svg
  kamath_robotics_logo_dark.svg
src/
  worker.js                  ← Cloudflare Worker (404 fallback)
wrangler.jsonc               ← Cloudflare Pages config
package.json                 ← Dev scripts (wrangler dev/deploy)
```

## License

Apache-2.0
