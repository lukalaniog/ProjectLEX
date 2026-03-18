# LexFlow Dashboard UX Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Increase font sizes for better readability, add automatic pipeline reset after case completion, and ensure all text uses theme-aware colors (no hard-coded white that breaks light mode).

**Architecture:** Single-page HTML/JS dashboard. Changes are purely presentational (CSS) and UI state management (JS). No backend or data model modifications needed.

**Tech Stack:** HTML, CSS, JavaScript (vanilla, inline in `lexflow_dashboard.html`)

---

## File Structure

- **`lexflow_dashboard.html`** (modify): Main dashboard file containing all styles, structure, and client-side logic.
  - *CSS section* (lines ~8-500): Typography changes + color fixes
  - *JavaScript section* (lines ~1238-2400): Add `resetLivePipeline()` function and integrate into existing functions

---

### Task 1: Add resetLivePipeline function

**Files:**
- Modify: `lexflow_dashboard.html:2040` (insert new function near other pipeline helpers)

- [ ] **Step 1:** Read the file to find the exact insertion point near `setLiveStage()` or `completeLivePipeline()`.

Run: `grep -n "function setLiveStage" lexflow_dashboard.html`

- [ ] **Step 2:** Add the `resetLivePipeline()` function definition (use exact code from spec):

```javascript
function resetLivePipeline(){
  // Reset all stages to 'idle'
  ['intake','advocate','devil','strategist','complete'].forEach(s => setLiveStage(s, 'idle'));

  // Hide the completion message
  const completeMsg = document.getElementById('lp-complete-msg');
  if(completeMsg) completeMsg.classList.remove('show');

  // Reset pulse dot and label
  const dot = document.getElementById('lp-pulse-dot');
  const lbl = document.getElementById('lp-pulse-lbl');
  if(dot){
    dot.classList.remove('stopped');
    dot.style.background = '';
  }
  if(lbl) lbl.textContent = '—';

  // Ensure live pipeline wrapper is hidden (profile view only shows it for in-progress cases)
  const wrap = document.getElementById('live-pipeline-wrap');
  if(wrap) wrap.style.display = 'none';
}
```

- [ ] **Step 3:** Save file and verify syntax: run `npx html-validate lexflow_dashboard.html` (optional) or just check in browser later.

- [ ] **Step 4:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "feat: add resetLivePipeline function to clear pipeline UI state"
```

---

### Task 2: Integrate reset into `showView()` for Overview

**Files:**
- Modify: `lexflow_dashboard.html:1323-1335` (the `showView()` function's overview branch)

- [ ] **Step 1:** Locate the `showView()` function and find the section:

```javascript
if(id === 'overview'){
  const liveWrap = document.getElementById('live-pipeline-wrap');
  if(liveWrap){
    if(pollTimer === null){
      liveWrap.style.display = 'none';
    } else {
      liveWrap.style.display = 'block';
    }
  }
  renderPipelineViews();
}
```

- [ ] **Step 2:** Modify to call `resetLivePipeline()` when `pollTimer === null`:

```javascript
if(id === 'overview'){
  const liveWrap = document.getElementById('live-pipeline-wrap');
  if(liveWrap){
    if(pollTimer === null){
      resetLivePipeline();  // ADD THIS LINE
      liveWrap.style.display = 'none';
    } else {
      liveWrap.style.display = 'block';
    }
  }
  renderPipelineViews();
}
```

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "feat: reset pipeline when navigating to Overview without active poll"
```

---

### Task 3: Integrate reset into `showView()` for Form

**Files:**
- Modify: `lexflow_dashboard.html:1313-1335` (add another branch in `showView()`)

- [ ] **Step 1:** After the `if(id === 'overview')` block, add:

```javascript
if(id === 'form'){
  resetLivePipeline();
}
```

- [ ] **Step 2:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "feat: reset pipeline when opening new case form"
```

---

### Task 4: Integrate reset into `resetDashboard()`

**Files:**
- Modify: `lexflow_dashboard.html:2309-2317`

- [ ] **Step 1:** Locate `function resetDashboard(){`

- [ ] **Step 2:** Add `resetLivePipeline();` right after removing the modal class:

```javascript
function resetDashboard(){
  document.getElementById('success-modal').classList.remove('open');
  resetLivePipeline();  // ADD THIS LINE
  if(profileIdx !== null && caseStore[profileIdx]){
    openProfile(profileIdx,'overview');
  } else {
    showView('overview',document.getElementById('nav-overview'));
  }
}
```

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "feat: reset pipeline after case submission success modal closes"
```

---

### Task 5: Fix hard-coded white colors to theme-aware

**Files:**
- Modify: `lexflow_dashboard.html` (multiple lines)

- [ ] **Step 1:** Find all hard-coded white colors:
```bash
grep -n "color: var(--white)" lexflow_dashboard.html
grep -n "color: #ffffff" lexflow_dashboard.html
grep -n "color: #fff" lexflow_dashboard.html
```

- [ ] **Step 2:** For each occurrence, replace with `color: var(--text)` using Edit tool. Review context to ensure it's text (not decorative). Common targets:
  - `.topbar-left h2` (line ~108): `color:var(--white)` → `color:var(--text)`
  - `.firm-name` (line ~68): `color:var(--white)` → `color:var(--text)`
  - `.stat-num` (line ~141): `color:var(--white)` → `color:var(--text)`
  - `.sec-title` (line ~161): `color:var(--white)` → `color:var(--text)`
  - `.profile-field .val` (line ~227): if it uses white, change to var(--text)
  - Any table cell or analysis card text forcing white

- [ ] **Step 3:** After replacements, verify no `var(--white)`, `#ffffff`, or `#fff` remain in color declarations for text (search again to confirm).

- [ ] **Step 4:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "fix: use theme-aware text color instead of hard-coded white"
```

---

### Task 6: Typography - Base body styles

**Files:**
- Modify: `lexflow_dashboard.html:54` (the `body` rule)

- [ ] **Step 1:** Find current body rule:

```css
body{background:var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif;min-height:100vh;display:flex;overflow-x:hidden;}
```

- [ ] **Step 2:** Change to:

```css
body{background:var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif;font-size:17px;line-height:1.6;font-weight:500;min-height:100vh;display:flex;overflow-x:hidden;}
```

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase base font size to 17px, weight 500, line-height 1.6"
```

---

### Task 7: Typography - Form inputs

**Files:**
- Modify: `lexflow_dashboard.html:294` (the `.field input, .field select, .field textarea` rule)

- [ ] **Step 1:** Find current rule:

```css
.field input,.field select,.field textarea{background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:8px 11px;font-family:'IBM Plex Sans',sans-serif;font-size:0.79rem;color:var(--text);outline:none;transition:all 0.15s;width:100%;}
```

- [ ] **Step 2:** Change `font-size:0.79rem` → `font-size:0.85rem`

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase form input font size to 0.85rem"
```

---

### Task 8: Typography - Case table rows

**Files:**
- Modify: `lexflow_dashboard.html:184` (the `.cases-wrap td` rule)

- [ ] **Step 1:** Find current rule:

```css
.cases-wrap td{padding:10px 14px;font-size:0.76rem;border-bottom:1px solid var(--border);color:var(--text);vertical-align:middle;}
```

- [ ] **Step 2:** Change `font-size:0.76rem` → `font-size:0.86rem`

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase case table font size to 0.86rem"
```

---

### Task 9: Typography - Analysis cards

**Files:**
- Modify: `lexflow_dashboard.html:254` (the `.ac-text` rule)

- [ ] **Step 1:** Find current rule:

```css
.ac-text{font-size:0.79rem;color:var(--text);line-height:1.65;background:var(--surface2);border-radius:7px;padding:12px 14px;border-left:2px solid var(--border2);}
```

- [ ] **Step 2:** Change `font-size:0.79rem` → `font-size:0.86rem`

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase analysis panel text size to 0.86rem"
```

---

### Task 10: Typography - Section titles

**Files:**
- Modify: `lexflow_dashboard.html:161` (the `.sec-title` rule)

- [ ] **Step 1:** Find current rule:

```css
.sec-title{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:var(--white);}
```

- [ ] **Step 2:** Change `font-size:1.05rem` → `font-size:1.15rem`

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase section title font size to 1.15rem"
```

---

### Task 11: Typography - Stat counters

**Files:**
- Modify: `lexflow_dashboard.html:141` (the `.stat-num` rule)

- [ ] **Step 1:** Find current rule:

```css
.stat-num{font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;color:var(--white);line-height:1;}
```

- [ ] **Step 2:** Change `font-size:2rem` → `font-size:2.2rem`

- [ ] **Step 3:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase stat counter font size to 2.2rem"
```

---

### Task 12: Typography - Small labels (multiple classes)

**Files:**
- Modify: Multiple small label CSS rules (batch edit)

- [ ] **Step 1:** Find all small font sizes (<0.80rem) with grep:

```bash
grep -n "font-size:0\.5[0-4]rem" lexflow_dashboard.html
grep -n "font-size:0\.5[5-9]rem" lexflow_dashboard.html
```

- [ ] **Step 2:** Increase each by ~15-20%. Specific changes:
  - `.stat-lbl` (line ~140): `0.52rem` → `0.6rem`
  - `.ac-section-lbl` (line ~253): `0.54rem` → `0.62rem`
  - `.field label` (line ~291): `0.7rem` → `0.8rem`
  - `.nav-section-lbl` (line ~72): `0.5rem` → `0.58rem`
  - `.pt-lbl` (line ~154): `0.5rem` → `0.58rem`
  - `.pb-lbl` (via `.pipe-badge` line ~196): `0.52rem` → `0.6rem`
  - `.tpl-tag`, `.doc-tag`, `.urg`, etc.: check sizes and boost if <0.70rem

- [ ] **Step 3:** For each match, use Edit to replace the font-size value carefully.

- [ ] **Step 4:** Commit

```bash
git add lexflow_dashboard.html
git commit -m "style: increase small label font sizes by ~15% for readability"
```

---

### Task 13: Final verification (non-code)

**Files:**
- Test manually in browser: `lexflow_dashboard.html`

- [ ] **Step 1:** Open `lexflow_dashboard.html` in browser (dark mode)
- [ ] **Step 2:** Verify typography:
  - Body text is noticeably larger (17px base)
  - Form fields have clear, readable input text (0.85rem)
  - Case table rows are easy to read (0.86rem)
  - Analysis panel text is comfortable (0.86rem)
  - Section headings stand out (1.15rem)
  - Statistics numbers are bold and large (2.2rem)
  - Labels are more legible (not tiny)
- [ ] **Step 3:** Verify theme colors:
  - All text in dark mode is light-colored and readable
  - Switch to light mode: verify NO white text on light backgrounds; all text should be dark (`#1c1c1e`)
  - Check topbar title, firm name, table rows, form labels, analysis text for proper contrast in both themes
- [ ] **Step 4:** Verify pipeline reset:
  - Submit/load a case that's fully complete
  - View profile → pipeline should show complete state
  - Click "New Case Intake" → live pipeline should be hidden
  - Go to Overview → live pipeline should be hidden if no active poll
  - Submit a new case, wait for completion
  - Close success modal → pipeline resets automatically (should show all idle or hidden)
- [ ] **Step 5:** If anything looks broken, layout overflow, or colors wrong, fix CSS and re-test
- [ ] **Step 6:** Final commit (if tweaks)

```bash
git add lexflow_dashboard.html
git commit -m "test: verify all UX improvements working correctly"
```

---

## Plan Review

After writing, dispatch plan-document-reviewer with:
- Spec: `docs/superpowers/specs/2026-03-18-dashboard-typography-pipeline-reset-design.md`
- Plan: (this document)

Fix any issues, re-review until approved (max 3 iterations). Then present to user for final approval before execution.

---
