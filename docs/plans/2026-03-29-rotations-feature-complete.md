# Rotations — Feature Complete Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the rotations converter the definitive tool for roboticists — adding rotvec format, RPY preset, auto-normalize, matrix labels, precision control, rich copy options, viewer polish, gimbal-lock warning, and shareable URLs.

**Architecture:** All input/output lives in `templates/index.html` (one large HTML+CSS+JS file). The Flask backend `app.py` already handles rotvec output; we only need to add `rotvec` as an accepted input format. All other changes are pure frontend.

**Tech Stack:** Flask/Python, scipy Rotation, Three.js r0.162.0, vanilla JS/CSS, no build step.

---

## Task 1: Logo — max brightness + orange glow on hover

**Files:**
- Modify: `templates/index.html` lines 95–105

**Step 1: Locate and replace the logo CSS block**

Find:
```css
.app-footer .logo-link img {
    height: 20px;
    width: auto;
    display: block;
    opacity: 1;
    transition: filter var(--tr);
}

.app-footer .logo-link:hover img {
    filter: drop-shadow(0 0 6px rgba(255,140,0,0.7)) drop-shadow(0 0 12px rgba(255,140,0,0.35));
}
```

Replace with:
```css
.app-footer .logo-link img {
    height: 20px;
    width: auto;
    display: block;
    opacity: 1;
    filter: brightness(1.15) contrast(1.05);
    transition: filter 0.25s ease;
}

.app-footer .logo-link:hover img {
    filter: brightness(1.4) contrast(1.1)
            drop-shadow(0 0 8px rgba(255,140,0,0.9))
            drop-shadow(0 0 20px rgba(255,140,0,0.5))
            drop-shadow(0 0 40px rgba(255,180,0,0.25));
}
```

**Step 2: Verify visually** — refresh browser, logo should be crisp white/orange; hover should produce vivid orange glow.

**Step 3: Commit**
```bash
cd /Users/adityakamath/Documents/Vibes/rotation-converter
git add templates/index.html
git commit -m "feat: logo max brightness + vivid orange glow on hover"
```

---

## Task 2: Backend — add rotvec as accepted input format

**Files:**
- Modify: `app.py` lines 30–47

**Step 1: Add rotvec branch in the input parser**

In `app.py`, after the `axis-angle` block and before the final `else`:
```python
elif input_format == 'rotvec':
    # UI provides [x, y, z] rotation vector (Rodrigues)
    # magnitude = angle in radians; direction = axis
    if input_degrees:
        angle = np.linalg.norm(values)
        axis  = np.array([0.0, 0.0, 1.0]) if angle < 1e-10 else values / angle
        values = axis * np.deg2rad(angle)
    r = Rotation.from_rotvec(values)
```

**Step 2: Add rotvec to the response**

The response JSON already includes `rotvec` derived from `r.as_rotvec()`. But add `rotvec` explicitly as a named key (it already exists via the `axisAngle` logic but we want a clean vector). After line 52 (`rotvec = r.as_rotvec()`), the value is available — no backend changes needed for output.

Actually confirm the full try block already outputs `axisAngle` which covers rotvec display. The frontend will render a new "Rotation Vector" result block. We also need the API to return `rotvec` as a flat array:

In the return jsonify, add after `'axisAngle': {...}`:
```python
'rotvec': [r8(v) for v in rotvec],
```

**Step 3: Test with curl**
```bash
curl -s -X POST http://localhost:5000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"format":"rotvec","values":[1.5708,0,0],"inputDegrees":false,"outputDegrees":true,"inputRotationOrder":"xyz","outputRotationOrder":"xyz","intrinsic":true}'
```
Expected: euler ≈ [90, 0, 0], quaternion ≈ [0.7071, 0.7071, 0, 0]

**Step 4: Commit**
```bash
git add app.py
git commit -m "feat: add rotvec as accepted input format + rotvec in API response"
```

---

## Task 3: Frontend — add Rotation Vector format (input + output)

**Files:**
- Modify: `templates/index.html`
  - Format selector: add `<option value="rotvec">Rotation Vector (Rodrigues)</option>`
  - Add rotvec input group HTML
  - Update `ALL_INPUT_GROUPS` array
  - Update `onFormatChange` to show/hide units for rotvec
  - Update `getValues()` for rotvec
  - Update `renderResults()` to show rotvec result block
  - Update copy handler for rotvec
  - Add rotvec result block HTML

**Step 1: Add option to format selector** (after axis-angle option)
```html
<option value="rotvec">Rotation Vector (Rodrigues)</option>
```

**Step 2: Add rotvec input group HTML** (after axis-angle-inputs div, before reset button)
```html
<!-- Rotation Vector Inputs -->
<div id="rotvec-inputs" class="inputs-group hidden">
    <div class="input-row">
        <span class="axis-label x">X</span>
        <input type="number" step="any" class="num-input" id="rv-x" placeholder="0">
    </div>
    <div class="input-row">
        <span class="axis-label y">Y</span>
        <input type="number" step="any" class="num-input" id="rv-y" placeholder="0">
    </div>
    <div class="input-row">
        <span class="axis-label z">Z</span>
        <input type="number" step="any" class="num-input" id="rv-z" placeholder="0">
    </div>
    <div class="norm-indicator" id="rv-hint">magnitude = angle in radians</div>
</div>
```

**Step 3: Add rotvec result block HTML** (after axis-angle result block, before `/div#results-content`)
```html
<div class="result-block">
    <div class="result-header">
        <span class="result-title">Rotation Vector</span>
        <span class="result-meta">Rodrigues · rad</span>
        <span class="conv-badge">rotvec</span>
        <button class="copy-btn" data-copy="rotvec">copy</button>
    </div>
    <div class="result-values" id="res-rotvec"></div>
</div>
```

**Step 4: Update JS — ALL_INPUT_GROUPS**
```js
const ALL_INPUT_GROUPS = ['euler-inputs', 'quaternion-inputs', 'matrix-inputs', 'axis-angle-inputs', 'rotvec-inputs'];
```

**Step 5: Update JS — onFormatChange**
```js
const showUnits = fmt === 'euler' || fmt === 'axis-angle' || fmt === 'rotvec';
```

**Step 6: Update JS — getValues()**
After the axis-angle block, add:
```js
if (fmt === 'rotvec') {
    return ['rv-x', 'rv-y', 'rv-z'].map(id => {
        const v = parseField(id);
        return isNaN(v) ? 0 : v;
    });
}
```

**Step 7: Update JS — renderResults()** — add rotvec rendering after axis-angle block:
```js
// Rotation Vector
if (data.rotvec) {
    document.getElementById('res-rotvec').innerHTML =
        ['x','y','z'].map((lbl, i) =>
            `<div class="result-row">
                <span class="val-label">${lbl}</span>
                <span class="val-number">${f6(data.rotvec[i])}</span>
                <span class="val-unit"> rad</span>
            </div>`
        ).join('');
}
```

**Step 8: Update JS — copy handler** — add rotvec case:
```js
case 'rotvec':
    text = 'Rotation Vector (rad): [' + d.rotvec.map(f8).join(', ') + ']';
    break;
```

**Step 9: Update JS — reset** — add rotvec reset:
```js
['rv-x', 'rv-y', 'rv-z'].forEach(id => document.getElementById(id).value = '0');
```

**Step 10: Verify** — switch format to Rotation Vector, enter [1.5708, 0, 0], check euler ≈ 90°.

**Step 11: Commit**
```bash
git add templates/index.html
git commit -m "feat: rotation vector (Rodrigues) format — input and output"
```

---

## Task 4: RPY preset — ZYX intrinsic shortcut

**Files:**
- Modify: `templates/index.html` — input rotation order selector

**Step 1: Add RPY option to input rotation order selector**

Find the input rotation order select and add a separator + RPY option at the top:
```html
<select id="input-rotation-order" class="select">
    <option value="zyx" data-rpy="true">ZYX — Roll · Pitch · Yaw (RPY)</option>
    <option value="xyz">XYZ</option>
    <option value="xzy">XZY</option>
    <option value="yxz">YXZ</option>
    <option value="yzx">YZX</option>
    <option value="zxy">ZXY</option>
    <option value="zyx">ZYX</option>
</select>
```

Wait — having two `zyx` entries is confusing. Better approach: rename options to be cleaner and add RPY as a labelled first option:

```html
<select id="input-rotation-order" class="select">
    <option value="zyx">ZYX — RPY (ROS / URDF)</option>
    <option value="xyz">XYZ</option>
    <option value="xzy">XZY</option>
    <option value="yxz">YXZ</option>
    <option value="yzx">YZX</option>
    <option value="zxy">ZXY</option>
</select>
```

Do the same for the output Euler order selector:
```html
<select id="output-euler-order" class="select">
    <option value="zyx">ZYX — RPY (ROS / URDF)</option>
    <option value="xyz">XYZ</option>
    <option value="xzy">XZY</option>
    <option value="yxz">YXZ</option>
    <option value="yzx">YZX</option>
    <option value="zxy">ZXY</option>
</select>
```

**Step 2: Update euler label display** — the ZYX order labels should show Z/Y/X correctly. `syncEulerLabels()` already handles this generically — no change needed.

**Step 3: Verify** — select ZYX, intrinsic, enter [45, 30, 10] — result should be a valid rotation, euler meta shows "ZYX".

**Step 4: Commit**
```bash
git add templates/index.html
git commit -m "feat: RPY (ZYX intrinsic) as first-listed option in Euler order selectors"
```

---

## Task 5: Auto-normalize quaternion button

**Files:**
- Modify: `templates/index.html` — quaternion inputs section

**Step 1: Add normalize button after norm indicator**

After `<div class="norm-indicator" id="quat-norm">|q| = —</div>`, add:
```html
<button class="normalize-btn hidden" id="quat-normalize-btn">normalize</button>
```

**Step 2: Add CSS for normalize button**
```css
.normalize-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    color: var(--accent);
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.08em;
    padding: 4px 10px;
    margin-top: 6px;
    width: 100%;
    transition: background var(--tr), color var(--tr);
}
.normalize-btn:hover { background: var(--accent-dim); }
```

**Step 3: Update `updateQuatNorm()` to show/hide button**

```js
function updateQuatNorm() {
    const ids = ['quat-w', 'quat-x', 'quat-y', 'quat-z'];
    const vals = ids.map(id => parseFloat(document.getElementById(id).value) || 0);
    const norm = Math.sqrt(vals.reduce((s, v) => s + v * v, 0));
    const el = document.getElementById('quat-norm');
    const btn = document.getElementById('quat-normalize-btn');
    if (norm === 0) {
        el.textContent = '|q| = —';
        el.className = 'norm-indicator';
        btn.classList.add('hidden');
    } else {
        const ok = Math.abs(norm - 1) < 0.001;
        el.textContent = '|q| = ' + norm.toFixed(6);
        el.className = 'norm-indicator ' + (ok ? 'ok' : 'bad');
        btn.classList.toggle('hidden', ok);
    }
}
```

**Step 4: Add normalize click handler** (near reset handler)
```js
document.getElementById('quat-normalize-btn').addEventListener('click', () => {
    const ids = ['quat-w', 'quat-x', 'quat-y', 'quat-z'];
    const vals = ids.map(id => parseFloat(document.getElementById(id).value) || 0);
    const norm = Math.sqrt(vals.reduce((s, v) => s + v * v, 0));
    if (norm < 1e-10) return;
    ids.forEach((id, i) => {
        document.getElementById(id).value = (vals[i] / norm).toFixed(8);
    });
    updateQuatNorm();
    convert();
});
```

**Step 5: Verify** — enter quat [2, 0, 0, 0], norm indicator shows "bad", normalize button appears. Click → values become [1, 0, 0, 0], norm shows "ok".

**Step 6: Commit**
```bash
git add templates/index.html
git commit -m "feat: auto-normalize button for quaternion input"
```

---

## Task 6: Matrix input labels (row/column headers)

**Files:**
- Modify: `templates/index.html` — matrix-inputs div

**Step 1: Replace the flat matrix grid with a labeled version**

Find the `<div id="matrix-inputs" class="hidden">` block and replace with:
```html
<div id="matrix-inputs" class="hidden">
    <div class="matrix-labeled">
        <div class="matrix-col-headers">
            <span></span><!-- corner -->
            <span class="mat-header">C₁</span>
            <span class="mat-header">C₂</span>
            <span class="mat-header">C₃</span>
        </div>
        <div class="matrix-row">
            <span class="mat-header row">R₁</span>
            <input type="number" step="any" class="num-input" placeholder="1" data-mi="0">
            <input type="number" step="any" class="num-input" placeholder="0" data-mi="1">
            <input type="number" step="any" class="num-input" placeholder="0" data-mi="2">
        </div>
        <div class="matrix-row">
            <span class="mat-header row">R₂</span>
            <input type="number" step="any" class="num-input" placeholder="0" data-mi="3">
            <input type="number" step="any" class="num-input" placeholder="1" data-mi="4">
            <input type="number" step="any" class="num-input" placeholder="0" data-mi="5">
        </div>
        <div class="matrix-row">
            <span class="mat-header row">R₃</span>
            <input type="number" step="any" class="num-input" placeholder="0" data-mi="6">
            <input type="number" step="any" class="num-input" placeholder="0" data-mi="7">
            <input type="number" step="any" class="num-input" placeholder="1" data-mi="8">
        </div>
    </div>
</div>
```

**Step 2: Add CSS**
```css
.matrix-labeled { margin-top: 10px; }

.matrix-col-headers {
    display: grid;
    grid-template-columns: 22px repeat(3, 1fr);
    gap: 4px;
    margin-bottom: 2px;
}

.matrix-row {
    display: grid;
    grid-template-columns: 22px repeat(3, 1fr);
    gap: 4px;
    margin-bottom: 4px;
}

.mat-header {
    font-family: var(--mono);
    font-size: 9px;
    color: var(--text-lo);
    letter-spacing: 0.06em;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mat-header.row { justify-content: flex-end; padding-right: 4px; }

.matrix-row .num-input {
    text-align: center;
    padding: 6px 4px;
    font-size: 11px;
}
```

**Step 3: Remove old `.matrix-grid` CSS** (no longer used after this change).

**Step 4: Verify** — switch to Matrix input format, should see R₁/R₂/R₃ row labels and C₁/C₂/C₃ column headers.

**Step 5: Commit**
```bash
git add templates/index.html
git commit -m "feat: row/column labels on matrix input (R1-R3, C1-C3)"
```

---

## Task 7: Matrix output labels

**Files:**
- Modify: `templates/index.html` — renderResults matrix section

**Step 1: Update `renderResults()` matrix block**

Replace:
```js
document.getElementById('res-matrix').innerHTML =
    `<div class="res-matrix-grid">
        ${data.matrix.flat().map(v => `<span>${f6(v)}</span>`).join('')}
    </div>`;
```

With:
```js
const rows = data.matrix;
document.getElementById('res-matrix').innerHTML =
    `<div class="res-matrix-output">
        <div class="res-mat-col-hdr"><span></span><span>C₁</span><span>C₂</span><span>C₃</span></div>
        ${rows.map((row, ri) =>
            `<div class="res-mat-row">
                <span class="res-mat-lbl">R${ri+1}</span>
                ${row.map(v => `<span class="res-mat-val">${f6(v)}</span>`).join('')}
            </div>`
        ).join('')}
    </div>`;
```

**Step 2: Add CSS**
```css
.res-matrix-output { margin-top: 2px; }

.res-mat-col-hdr {
    display: grid;
    grid-template-columns: 20px repeat(3, 1fr);
    gap: 2px 4px;
    margin-bottom: 2px;
}

.res-mat-col-hdr span {
    font-family: var(--mono);
    font-size: 9px;
    color: var(--text-lo);
    text-align: right;
    padding-right: 2px;
}

.res-mat-row {
    display: grid;
    grid-template-columns: 20px repeat(3, 1fr);
    gap: 2px 4px;
    margin-bottom: 2px;
}

.res-mat-lbl {
    font-family: var(--mono);
    font-size: 9px;
    color: var(--text-lo);
    text-align: right;
    padding-right: 4px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

.res-mat-val {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--green);
    text-align: right;
    padding: 1px 0;
}
```

**Step 3: Remove old `.res-matrix-grid span` CSS rule.**

**Step 4: Verify** — convert any rotation, matrix result shows R1/R2/R3 row labels and C1/C2/C3 column headers.

**Step 5: Commit**
```bash
git add templates/index.html
git commit -m "feat: row/column labels on matrix output"
```

---

## Task 8: Precision control (decimal places selector)

**Files:**
- Modify: `templates/index.html` — output section + renderResults/copy

**Step 1: Add precision selector to Output section** (after units toggle)
```html
<div class="field">
    <label class="field-label">Precision</label>
    <select id="precision-select" class="select">
        <option value="4">4 decimal places</option>
        <option value="6" selected>6 decimal places</option>
        <option value="8">8 decimal places</option>
        <option value="10">10 decimal places</option>
    </select>
</div>
```

**Step 2: Update JS — replace hard-coded `f6` with dynamic precision function**

Replace:
```js
function f6(v) { return v.toFixed(6); }
```

With:
```js
function fPrec(v) {
    const p = parseInt(document.getElementById('precision-select').value, 10) || 6;
    return v.toFixed(p);
}
```

**Step 3: Replace all `f6(` calls in `renderResults()` with `fPrec(`** — there are ~10 occurrences.

**Step 4: Update copy handler** — replace `f8` with dynamic precision:
```js
const fCopy = v => v.toFixed(parseInt(document.getElementById('precision-select').value, 10) || 6);
```
Replace all `f8` calls in copy handler with `fCopy`.

**Step 5: Wire up precision change** — add to the change event listener:
```js
if (e.target.id === 'precision-select') {
    if (lastResult) renderResults(lastResult);
}
```

**Step 6: Verify** — after conversion, change precision to 4, all result values update to 4 decimal places.

**Step 7: Commit**
```bash
git add templates/index.html
git commit -m "feat: precision control (4/6/8/10 decimal places) on output"
```

---

## Task 9: Rich copy format options + Copy All button

**Files:**
- Modify: `templates/index.html` — result block headers + copy handler + new "Copy All" button

**Step 1: Replace each single `copy` button with a copy-format dropdown menu**

For each result block, change the copy button to a split button with format options. Add CSS for a copy dropdown:

```css
.copy-wrap {
    margin-left: auto;
    position: relative;
    display: flex;
    align-items: center;
    gap: 2px;
}

.copy-btn {
    background: none;
    border: 1px solid var(--border);
    border-right: none;
    border-radius: 3px 0 0 3px;
    color: var(--text-lo);
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.08em;
    padding: 2px 7px;
    transition: border-color var(--tr), color var(--tr);
}

.copy-fmt-btn {
    background: none;
    border: 1px solid var(--border);
    border-radius: 0 3px 3px 0;
    color: var(--text-lo);
    font-family: var(--mono);
    font-size: 8px;
    padding: 2px 5px;
    cursor: pointer;
    transition: border-color var(--tr), color var(--tr);
    position: relative;
}

.copy-fmt-btn:hover { border-color: var(--accent); color: var(--accent); }
.copy-btn:hover { border-color: var(--accent); color: var(--accent); }
.copy-btn.copied { border-color: var(--green); color: var(--green); }

.copy-menu {
    display: none;
    position: absolute;
    right: 0;
    top: 100%;
    margin-top: 2px;
    background: var(--surface-hi);
    border: 1px solid var(--border-hi);
    border-radius: var(--radius);
    z-index: 50;
    min-width: 120px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
}

.copy-menu.open { display: block; }

.copy-menu-item {
    display: block;
    width: 100%;
    background: none;
    border: none;
    color: var(--text);
    font-family: var(--mono);
    font-size: 10px;
    padding: 6px 10px;
    text-align: left;
    cursor: pointer;
    letter-spacing: 0.05em;
    transition: background var(--tr);
}

.copy-menu-item:hover { background: var(--surface); color: var(--accent); }
```

**Step 2: Update each result block to use copy-wrap + copy-menu**

For the Euler result block:
```html
<div class="copy-wrap">
    <button class="copy-btn" data-copy="euler" data-fmt="plain">copy</button>
    <button class="copy-fmt-btn" data-menu="euler">▾</button>
    <div class="copy-menu" id="copy-menu-euler">
        <button class="copy-menu-item" data-copy="euler" data-fmt="plain">Plain text</button>
        <button class="copy-menu-item" data-copy="euler" data-fmt="python">Python list</button>
        <button class="copy-menu-item" data-copy="euler" data-fmt="json">JSON</button>
    </div>
</div>
```

For Quaternion: plain / python / json / ros-urdf
For Matrix: plain / python / json / matlab
For Axis-Angle: plain / python / json
For Rotation Vector: plain / python / json / ros-tf2

**Step 3: Update copy handler** — expand `switch(type)` with `fmt` sub-cases:

```js
document.addEventListener('click', async e => {
    // Close any open menus when clicking outside
    if (!e.target.closest('.copy-wrap')) {
        document.querySelectorAll('.copy-menu.open').forEach(m => m.classList.remove('open'));
    }

    // Toggle menu
    const menuBtn = e.target.closest('.copy-fmt-btn');
    if (menuBtn) {
        e.stopPropagation();
        const menuId = 'copy-menu-' + menuBtn.dataset.menu;
        const menu = document.getElementById(menuId);
        document.querySelectorAll('.copy-menu.open').forEach(m => { if (m !== menu) m.classList.remove('open'); });
        menu.classList.toggle('open');
        return;
    }

    const btn = e.target.closest('.copy-btn, .copy-menu-item');
    if (!btn || !lastResult) return;
    const type = btn.dataset.copy;
    const fmt  = btn.dataset.fmt || 'plain';
    const d    = lastResult;
    const fCopy = v => v.toFixed(parseInt(document.getElementById('precision-select').value, 10) || 6);
    let text = '';

    const fmtEuler = () => {
        switch(fmt) {
            case 'python': return `[${d.euler.map(fCopy).join(', ')}]  # ${d.outputRotationOrder.toUpperCase()} ${d.units}`;
            case 'json':   return JSON.stringify({euler: d.euler.map(v => parseFloat(fCopy(v))), order: d.outputRotationOrder, units: d.units});
            default:       return `Euler (${d.outputRotationOrder.toUpperCase()}, ${d.units}): ${d.euler.map(fCopy).join('  ')}`;
        }
    };

    const fmtQuat = () => {
        switch(fmt) {
            case 'python':   return `[${d.quaternion.map(fCopy).join(', ')}]  # w x y z`;
            case 'json':     return JSON.stringify({w: parseFloat(fCopy(d.quaternion[0])), x: parseFloat(fCopy(d.quaternion[1])), y: parseFloat(fCopy(d.quaternion[2])), z: parseFloat(fCopy(d.quaternion[3]))});
            case 'ros-urdf': return `<origin rpy="0 0 0"/>\n<!-- Use rpy for Euler; quaternion in tf:\n  w=${fCopy(d.quaternion[0])} x=${fCopy(d.quaternion[1])} y=${fCopy(d.quaternion[2])} z=${fCopy(d.quaternion[3])} -->`;
            default:         return `Quaternion (w x y z): ${d.quaternion.map(fCopy).join('  ')}`;
        }
    };

    const fmtMatrix = () => {
        switch(fmt) {
            case 'python': return `np.array([\n  [${d.matrix[0].map(fCopy).join(', ')}],\n  [${d.matrix[1].map(fCopy).join(', ')}],\n  [${d.matrix[2].map(fCopy).join(', ')}]\n])`;
            case 'json':   return JSON.stringify({matrix: d.matrix.map(row => row.map(v => parseFloat(fCopy(v))))});
            case 'matlab': return `[${d.matrix[0].map(fCopy).join(', ')}; ${d.matrix[1].map(fCopy).join(', ')}; ${d.matrix[2].map(fCopy).join(', ')}]`;
            default:       return 'Rotation Matrix:\n' + d.matrix.map(row => row.map(v => fCopy(v).padStart(14)).join('')).join('\n');
        }
    };

    const fmtAA = () => {
        switch(fmt) {
            case 'python': return `angle=${fCopy(d.axisAngle.angle)}, axis=[${d.axisAngle.axis.map(fCopy).join(', ')}]  # ${d.units}`;
            case 'json':   return JSON.stringify({angle: parseFloat(fCopy(d.axisAngle.angle)), axis: d.axisAngle.axis.map(v => parseFloat(fCopy(v))), units: d.units});
            default:       return `Axis-Angle (${d.units}): angle=${fCopy(d.axisAngle.angle)}  axis=[${d.axisAngle.axis.map(fCopy).join(', ')}]`;
        }
    };

    const fmtRV = () => {
        if (!d.rotvec) return '';
        switch(fmt) {
            case 'python':  return `[${d.rotvec.map(fCopy).join(', ')}]  # rotvec rad`;
            case 'json':    return JSON.stringify({rotvec: d.rotvec.map(v => parseFloat(fCopy(v)))});
            case 'ros-tf2': return `# geometry_msgs/Vector3\nx: ${fCopy(d.rotvec[0])}\ny: ${fCopy(d.rotvec[1])}\nz: ${fCopy(d.rotvec[2])}`;
            default:        return `Rotation Vector (rad): [${d.rotvec.map(fCopy).join(', ')}]`;
        }
    };

    switch(type) {
        case 'euler':      text = fmtEuler(); break;
        case 'quaternion': text = fmtQuat();  break;
        case 'matrix':     text = fmtMatrix(); break;
        case 'axis-angle': text = fmtAA();    break;
        case 'rotvec':     text = fmtRV();    break;
    }

    if (!text) return;
    try {
        await navigator.clipboard.writeText(text);
        const mainBtn = document.querySelector(`.copy-btn[data-copy="${type}"]`);
        if (mainBtn) {
            mainBtn.textContent = 'copied!';
            mainBtn.classList.add('copied');
            setTimeout(() => { mainBtn.textContent = 'copy'; mainBtn.classList.remove('copied'); }, 1500);
        }
        // Close any open menu
        document.querySelectorAll('.copy-menu.open').forEach(m => m.classList.remove('open'));
    } catch (_) {}
});
```

**Step 4: Add "Copy All" button** — after the results-content div closing tag add:
```html
<button class="copy-all-btn hidden" id="copy-all-btn">copy all formats</button>
```

CSS:
```css
.copy-all-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-lo);
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.08em;
    padding: 6px 12px;
    margin-top: 8px;
    width: 100%;
    transition: border-color var(--tr), color var(--tr);
}
.copy-all-btn:hover { border-color: var(--border-hi); color: var(--text); }
.copy-all-btn.copied { border-color: var(--green); color: var(--green); }
```

**Step 5: Show/hide copy-all in renderResults** — add `document.getElementById('copy-all-btn').classList.remove('hidden');` in `renderResults()`.

**Step 6: Wire up copy-all**
```js
document.getElementById('copy-all-btn').addEventListener('click', async () => {
    if (!lastResult) return;
    const d = lastResult;
    const fCopy = v => v.toFixed(parseInt(document.getElementById('precision-select').value, 10) || 6);
    const lines = [
        `Euler (${d.outputRotationOrder.toUpperCase()}, ${d.units}): ${d.euler.map(fCopy).join('  ')}`,
        `Quaternion (w x y z): ${d.quaternion.map(fCopy).join('  ')}`,
        `Rotation Matrix:\n` + d.matrix.map(row => row.map(v => fCopy(v).padStart(14)).join('')).join('\n'),
        `Axis-Angle (${d.units}): angle=${fCopy(d.axisAngle.angle)}  axis=[${d.axisAngle.axis.map(fCopy).join(', ')}]`,
    ];
    if (d.rotvec) lines.push(`Rotation Vector (rad): [${d.rotvec.map(fCopy).join(', ')}]`);
    try {
        await navigator.clipboard.writeText(lines.join('\n\n'));
        const btn = document.getElementById('copy-all-btn');
        btn.textContent = 'copied all!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'copy all formats'; btn.classList.remove('copied'); }, 1500);
    } catch (_) {}
});
```

**Step 7: Verify** — convert a rotation, check copy menu dropdown opens, python format copies correctly, "copy all" copies all 5 formats.

**Step 8: Commit**
```bash
git add templates/index.html
git commit -m "feat: rich copy formats (plain/python/json/matlab/ros) + copy-all button"
```

---

## Task 10: Viewer — legend annotation + home button + controls hint

**Files:**
- Modify: `templates/index.html` — viewer-wrap HTML + CSS + Three.js init

**Step 1: Update legend HTML** — replace existing legend with annotated version
```html
<div class="axis-legend">
    <div class="legend-section-label">World frame</div>
    <div class="legend-item"><span class="legend-line dashed x"></span>X</div>
    <div class="legend-item"><span class="legend-line dashed y"></span>Y</div>
    <div class="legend-item"><span class="legend-line dashed z"></span>Z</div>
    <div class="legend-section-label" style="margin-top:6px">Body frame</div>
    <div class="legend-item"><span class="legend-line solid x"></span>X</div>
    <div class="legend-item"><span class="legend-line solid y"></span>Y</div>
    <div class="legend-item"><span class="legend-line solid z"></span>Z</div>
</div>
```

**Step 2: Update legend CSS**
```css
.legend-section-label {
    font-family: var(--mono);
    font-size: 8px;
    color: var(--text-lo);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 3px;
}

.legend-line {
    width: 16px;
    height: 2px;
    flex-shrink: 0;
    border-radius: 1px;
}

.legend-line.solid.x  { background: #ff4444; }
.legend-line.solid.y  { background: #44dd44; }
.legend-line.solid.z  { background: #4488ff; }
.legend-line.dashed.x { background: repeating-linear-gradient(90deg, #ff4444 0 5px, transparent 5px 8px); }
.legend-line.dashed.y { background: repeating-linear-gradient(90deg, #44dd44 0 5px, transparent 5px 8px); }
.legend-line.dashed.z { background: repeating-linear-gradient(90deg, #4488ff 0 5px, transparent 5px 8px); }
```

Remove old `.legend-dot` rules.

**Step 3: Add camera home button HTML** (inside viewer-wrap, after viewer-overlay)
```html
<button class="viewer-home-btn" id="viewer-home-btn" title="Reset camera view">⌂</button>
```

CSS:
```css
.viewer-home-btn {
    position: absolute;
    top: 14px;
    left: 16px;
    z-index: 3;
    background: rgba(9,13,20,0.7);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-lo);
    font-size: 14px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: border-color var(--tr), color var(--tr), background var(--tr);
    backdrop-filter: blur(4px);
}

.viewer-home-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
```

**Step 4: Wire up home button** — in the module script, after `init()`:
```js
document.getElementById('viewer-home-btn').addEventListener('click', () => {
    camera.position.set(6, -6, 4);
    camera.up.set(0, 0, 1);
    controls.target.set(0, 0, 0);
    controls.update();
});
```

**Step 5: Add controls hint overlay HTML** (inside viewer-wrap)
```html
<div class="controls-hint" id="controls-hint">
    <span>drag to orbit · scroll to zoom · right-drag to pan</span>
</div>
```

CSS:
```css
.controls-hint {
    position: absolute;
    bottom: 52px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 3;
    background: rgba(9,13,20,0.75);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 14px;
    font-family: var(--mono);
    font-size: 9px;
    color: var(--text-lo);
    letter-spacing: 0.08em;
    pointer-events: none;
    opacity: 1;
    transition: opacity 0.8s ease;
    backdrop-filter: blur(4px);
    white-space: nowrap;
}

.controls-hint.fade { opacity: 0; }
```

**Step 6: Auto-fade hint** — in module script after `init()`:
```js
setTimeout(() => {
    const hint = document.getElementById('controls-hint');
    if (hint) hint.classList.add('fade');
}, 3000);
```

**Step 7: Update viewer-label** to include Z-up notation — find existing `.viewer-label` and change its text:
```html
<div class="viewer-label">Z-up · 3D Preview</div>
```

**Step 8: Verify** — legend shows dashed/solid sections, home button resets camera, hint fades after 3s.

**Step 9: Commit**
```bash
git add templates/index.html
git commit -m "feat: viewer legend dashed/solid, camera home button, controls hint, Z-up label"
```

---

## Task 11: Axis color CSS variable consistency

**Files:**
- Modify: `templates/index.html` — CSS variables + Three.js axis colors

**Step 1: Update `--ax`, `--ay`, `--az` CSS variables to match Three.js colors exactly**

Three.js uses: `0xff4444` (X), `0x44dd44` (Y), `0x4488ff` (Z)

Current CSS vars: `--ax: #e05252`, `--ay: #52c052`, `--az: #5280e0` — these are slightly different.

Replace in `:root`:
```css
--ax: #ff4444;
--ay: #44dd44;
--az: #4488ff;
```

**Step 2: Verify** — axis labels in inputs (X/Y/Z colored labels), legend dots, and Three.js arrows should now all match exactly.

**Step 3: Commit**
```bash
git add templates/index.html
git commit -m "fix: axis colors now consistent between CSS vars and Three.js (#ff4444 #44dd44 #4488ff)"
```

---

## Task 12: Gimbal lock proximity warning

**Files:**
- Modify: `templates/index.html` — renderResults + CSS

**Step 1: Add gimbal lock detector function**

Gimbal lock for Euler angles occurs when the middle rotation is ±90° (for XYZ/ZYX) or ±90°/0° depending on order. The reliable way: compute `det(J)` numerically — but a simpler heuristic is checking if any component is within 2° of ±90°.

More robust: scipy returns `as_euler` values that wrap. Check if the pitch (middle value for XYZ/ZYX) is near ±90°:

```js
function checkGimbalLock(eulerDeg, order) {
    // Middle rotation is index 1 (second character of order)
    const midIdx = 1;
    const mid = Math.abs(eulerDeg[midIdx]);
    // Check within 3° of ±90° for ZYX/XYZ type orders, within 3° of 0/±90/±180 for others
    const nearSingularity = Math.abs(mid - 90) < 3 || Math.abs(mid + 90) < 3;
    return nearSingularity;
}
```

**Step 2: Add gimbal warning HTML** — inside the euler result-block, after the result-values div:
```html
<div class="gimbal-warning hidden" id="gimbal-warning">
    ⚠ Near gimbal lock — middle rotation ≈ ±90°, one DOF lost
</div>
```

CSS:
```css
.gimbal-warning {
    font-family: var(--mono);
    font-size: 9px;
    color: #ffaa00;
    background: rgba(255,170,0,0.08);
    border: 1px solid rgba(255,170,0,0.25);
    border-radius: var(--radius);
    padding: 4px 8px;
    margin-top: 6px;
    letter-spacing: 0.04em;
    line-height: 1.4;
}
```

**Step 3: Wire up in renderResults()**

After rendering Euler values, add:
```js
const gimbalEl = document.getElementById('gimbal-warning');
const eulerDeg = data.units === 'degrees' ? data.euler : data.euler.map(v => v * 180 / Math.PI);
if (checkGimbalLock(eulerDeg, data.outputRotationOrder)) {
    gimbalEl.classList.remove('hidden');
} else {
    gimbalEl.classList.add('hidden');
}
```

**Step 4: Verify** — enter Euler XYZ with Y=90°, warning should appear. With Y=45°, no warning.

**Step 5: Commit**
```bash
git add templates/index.html
git commit -m "feat: gimbal lock proximity warning when middle Euler angle ≈ ±90°"
```

---

## Task 13: Shareable URL — encode state in hash

**Files:**
- Modify: `templates/index.html` — JS section

**Step 1: Add `encodeState()` function**

```js
function encodeState() {
    const fmt = document.getElementById('format').value;
    const vals = getValues();
    const state = {
        f: fmt,
        v: vals,
        iu: document.getElementById('input-units-toggle').checked ? 1 : 0,
        ou: document.getElementById('output-units-toggle').checked ? 1 : 0,
        io: document.getElementById('input-rotation-order').value,
        oo: document.getElementById('output-euler-order').value,
        ix: document.getElementById('intrinsic-toggle').checked ? 1 : 0,
        p: document.getElementById('precision-select').value,
    };
    return btoa(JSON.stringify(state));
}
```

**Step 2: Add `decodeState()` function**

```js
function decodeState(hash) {
    try {
        const state = JSON.parse(atob(hash.replace(/^#/, '')));
        if (!state.f) return false;

        // Set format
        document.getElementById('format').value = state.f;
        onFormatChange();

        // Set values
        const setById = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = val;
        };

        if (state.f === 'euler') {
            [0,1,2].forEach(i => setById('euler-' + i, state.v[i]));
        } else if (state.f === 'quaternion') {
            ['quat-w','quat-x','quat-y','quat-z'].forEach((id,i) => setById(id, state.v[i]));
        } else if (state.f === 'matrix') {
            document.querySelectorAll('#matrix-inputs .num-input')
                .forEach((el, i) => el.value = state.v[i]);
        } else if (state.f === 'axis-angle') {
            ['aa-angle','aa-x','aa-y','aa-z'].forEach((id,i) => setById(id, state.v[i]));
        } else if (state.f === 'rotvec') {
            ['rv-x','rv-y','rv-z'].forEach((id,i) => setById(id, state.v[i]));
        }

        // Set toggles and selects
        document.getElementById('input-units-toggle').checked = !!state.iu;
        document.getElementById('output-units-toggle').checked = !!state.ou;
        document.getElementById('input-rotation-order').value = state.io || 'xyz';
        document.getElementById('output-euler-order').value = state.oo || 'xyz';
        document.getElementById('intrinsic-toggle').checked = state.ix !== 0;
        document.getElementById('precision-select').value = state.p || '6';
        syncEulerLabels();
        return true;
    } catch (e) {
        return false;
    }
}
```

**Step 3: Add share button to the header**

In `<header class="app-header">`, after the subtitle span:
```html
<button class="share-btn" id="share-btn" title="Copy shareable link">share</button>
```

CSS:
```css
.share-btn {
    margin-left: auto;
    background: none;
    border: 1px solid var(--border);
    border-radius: 3px;
    color: var(--text-lo);
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.1em;
    padding: 3px 9px;
    cursor: pointer;
    transition: border-color var(--tr), color var(--tr);
}
.share-btn:hover { border-color: var(--accent); color: var(--accent); }
.share-btn.copied { border-color: var(--green); color: var(--green); }
```

**Step 4: Wire up share button**
```js
document.getElementById('share-btn').addEventListener('click', async () => {
    const hash = encodeState();
    const url = window.location.origin + window.location.pathname + '#' + hash;
    try {
        await navigator.clipboard.writeText(url);
        const btn = document.getElementById('share-btn');
        btn.textContent = 'copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'share'; btn.classList.remove('copied'); }, 2000);
    } catch (_) {}
});
```

**Step 5: Load state from URL hash on init**

Replace the final `// ── Init` block:
```js
// ── Init ──────────────────────────────────────────────────────
onFormatChange();
syncEulerLabels();
if (window.location.hash) {
    const loaded = decodeState(window.location.hash);
    if (!loaded) convert();
    else convert();
} else {
    convert();
}
```

**Step 6: Update hash on convert** — at the end of `convert()`, after calling `renderResults`:
```js
// Update URL hash silently (no page reload)
history.replaceState(null, '', '#' + encodeState());
```

**Step 7: Verify** — set some values, click share, paste URL in new tab — values should restore. URL should update as you change inputs.

**Step 8: Commit**
```bash
git add templates/index.html
git commit -m "feat: shareable URL — state encoded in URL hash, share button in header"
```

---

## Final: Commit plan doc

```bash
cd /Users/adityakamath/Documents/Vibes/rotation-converter
git add docs/plans/2026-03-29-rotations-feature-complete.md
git commit -m "docs: add feature-complete implementation plan"
```
