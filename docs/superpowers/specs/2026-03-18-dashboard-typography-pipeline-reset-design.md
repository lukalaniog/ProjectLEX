# LexFlow Dashboard UX Improvements

**Date:** 2026-03-18
**Project:** LEX (JL Laniog Law Firm)
**Author:** Claude Code
**Status:** Draft → Approved → Implementation

---

## Overview

Improve readability and user experience of the LexFlow dashboard by:
1. Increasing font sizes and weights for better legibility across all themes
2. Implementing automatic pipeline state reset to prevent stale UI after case completion

---

## 1. Typography & Visibility Enhancements

### Problem

Current dashboard uses very small text in several areas (as small as 0.52rem for labels and 0.76rem for table rows). While contrast ratios are excellent, the low x-height and tight line spacing make reading uncomfortable on modern high-DPI displays. Users requested "more visible, bigger, and more pleasant to read" text.

### Solution

Scale up core typography while maintaining visual hierarchy and design consistency.

**Specific CSS changes in `lexflow_dashboard.html`:**

| Element | Current Size | New Size | Notes |
|---------|--------------|----------|-------|
| Base body font-size | 16px (implied) | 17px | Larger default improves all rem calculations |
| Body text weight | 400 | 500 | Slightly bolder for better readability |
| Body line-height | normal → 1.6 | | More breathing room |
| Form input/select text | 0.79rem | 0.85rem | Easier to read and fill forms |
| Table rows | 0.76rem | 0.86rem | Visible without zooming |
| Analysis card text | 0.79rem | 0.86rem | Matches table readability |
| Section titles | 1.05rem | 1.15rem | Clearer section boundaries |
| Statistics numbers | 2rem | 2.2rem | Bolder impact on dashboard |

**Labels and muted text:** Increase by ~15% across all uses (e.g., `.stat-lbl`, `.ac-section-lbl`, `.field label`, `.nav-section-lbl`, `.pb-lbl`).

**Implementation approach:**
- Modify the global `body` rule: `font-size: 17px; line-height: 1.6; font-weight: 400;` → `font-weight: 500;`
- Update all explicit `font-size` declarations that appear too small (≥0.80rem stays mostly unchanged; <0.80rem gets 15-20% boost)
- Do NOT scale down larger headings (they're already prominent)

**Dark mode:** Colors unchanged; warmth preserved.
**Light mode:** Colors unchanged; readability maintained.

### Rationale

- 17px base provides modern baseline (most OS defaults are 16px; 17px is a non-breaking increment)
- Weight 500 (Medium) improves scan-ability without feeling heavy
- Line-height 1.6 is WCAG-recommended for body text
- Selective scaling focuses on content areas where users read extensively (forms, tables, analysis)
- No layout thrashing; changes are incremental

---

## 2. Pipeline State Reset After Completion

### Problem

When a case finishes (all three lawyers complete analysis), the live pipeline display in the profile view shows all stages as "done" with a "✓ ALL ANALYSES COMPLETE" message. This persists even when the user navigates away and returns, or starts a new case. The UI doesn't automatically reset, leading to confusion about whether a *new* case is still processing.

### Solution

Add a `resetLivePipeline()` function that clears the live pipeline UI to the initial idle state. Call this function at appropriate transitions to ensure a fresh start.

**New function:**

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

**Integration points (call `resetLivePipeline()`):**

1. In `showView()` when switching to `overview`:
   ```
   if(id === 'overview'){
     const liveWrap = document.getElementById('live-pipeline-wrap');
     if(liveWrap && pollTimer === null){
       resetLivePipeline();
       liveWrap.style.display = 'none';
     }
     renderPipelineViews();
   }
   ```

2. In `showView()` when switching to `form` (new case intake):
   ```
   if(id === 'form'){
     resetLivePipeline();
   }
   ```

3. In `resetDashboard()` after closing success modal:
   ```
   function resetDashboard(){
     document.getElementById('success-modal').classList.remove('open');
     // Reset live pipeline before showing profile/overview
     resetLivePipeline();
     if(profileIdx !== null && caseStore[profileIdx]){
       openProfile(profileIdx,'overview');
     } else {
       showView('overview',document.getElementById('nav-overview'));
     }
   }
   ```

**Why not reset on every profile open?**
- When viewing an *existing* completed case, the live pipeline shouldn't appear at all (the UI already hides it in `openProfile()` when case is COMPLETE). So no reset needed there.
- Reset only needed to clear stale state from *previous* active workflow.

---

## Implementation Notes

- **File to modify:** `lexflow_dashboard.html` only
- **No data model changes:** All changes are presentational (CSS + JS UI state)
- **Backward compatible:** Existing cases and polling logic unaffected
- **No server-side deployment needed:** Pure frontend changes

---

## Acceptance Criteria

### Typography
- [ ] Body text rendered at 17px base with line-height 1.6
- [ ] All form inputs show text at ≥0.85rem
- [ ] Case table rows show text at ≥0.86rem
- [ ] Analysis panel text at ≥0.86rem
- [ ] Section headers at ≥1.15rem
- [ ] Stat counters at ≥2.2rem
- [ ] All other small labels increased by ~15%
- [ ] Dark mode and light mode both render clearly

### Pipeline Reset
- [ ] `resetLivePipeline()` function implemented
- [ ] Called when navigating to Overview (if no active poll)
- [ ] Called when navigating to New Case form
- [ ] Called from `resetDashboard()` after success modal
- [ ] Live pipeline resets to idle state after these actions
- [ ] Completion message disappears
- [ ] No flicker or visual glitches during reset
- [ ] Existing case analysis viewing remains unaffected

---

## Testing Checklist

1. **Typography**
   - Open dashboard in dark mode: verify text is larger and easier to read
   - Switch to light mode: verify same improvement
   - Check case table readability
   - Fill out new case form: ensure input text is clear
   - Open a case with completed analysis: verify analysis text size

2. **Pipeline Reset**
   - Submit a new case and wait for completion
   - Observe live pipeline shows "ALL ANALYSES COMPLETE"
   - Close case profile, go to Overview
   - Click "New Case Intake" → live pipeline should not be visible
   - Complete another case, then click "+ Start New Case Intake"
   - Verify pipeline is reset (no remnants of previous completion)
   - Navigate to a completed case profile: live pipeline should remain hidden (no change)

3. **General**
   - Verify no layout breaks at any screen width
   - Check that theme toggle still works
   - Ensure localStorage saves (theme preference) unaffected

---

## Out of Scope

- Changing font families (IBM Plex Sans, Playfair Display are excellent)
- Redesigning color schemes (existing gold/dark palette is appropriate)
- Modifying pipeline stages or workflow logic
- Backend/n8n changes

---
