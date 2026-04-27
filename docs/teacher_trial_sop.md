# Teacher Trial SOP

**Purpose**: Structured process for the P1-18 teacher trial — from preparation to Phase 2 backlog update.

---

## Step 18a — Prepare Materials

### Demo video script (< 3 min)

1. **Intro** (0:00–0:20)  
   "UkePack turns any public-domain MusicXML file into a beginner-friendly ukulele practice PDF in under 5 seconds."

2. **Import** (0:20–0:50)  
   Open browser → `http://localhost:8000/new` → upload `twinkle_twinkle_little_star.musicxml` → click **Create**.

3. **Analysis page** (0:50–1:20)  
   Walk through: detected key, BPM, difficulty level, suggested strum pattern.  
   Show the Level switcher (1 / 2 / 3) updating live via HTMX.

4. **Preview & download** (1:20–2:00)  
   Click **Preview PDF** → scroll through 4 pages (overview, strum, chord chart, teacher notes).  
   Click **Download PDF** and open in system PDF viewer.

5. **License gate** (2:00–2:30)  
   Show the license attribution checkbox that must be ticked before exporting.

6. **Close** (2:30–3:00)  
   "We're looking for your honest feedback on 5 specific areas. The form takes about 5 minutes."

---

### Invitation email template

```
Subject: Quick favour — 5-min feedback on a ukulele teaching tool

Hi [Teacher name],

I'm building UkePack, a tool that automatically converts sheet music into
beginner ukulele practice packs (PDF) for classroom use.

Would you be willing to spend ~20 minutes trying it with one of your songs
and answering 5 short questions? Your feedback will directly shape what we
build next.

I can walk you through it live (Zoom / in-person) or send a pre-recorded
demo video — whichever you prefer.

Availability this week: [your slots]

Thank you!
[Your name]
```

---

## Step 18b — Invite

Checklist:
- [ ] Record or screen-capture the demo video (follow script above)
- [ ] Share [`docs/teacher_guide.md`](./teacher_guide.md) with the teacher as a self-serve reference before / during the session
- [ ] Send invitation email to at least 1 ukulele teacher
- [ ] Agree on trial date/time and delivery method (live walkthrough / async video)
- [ ] Share `feedback.md` form (PDF print or editable Google Doc copy)

---

## Step 18c — Run Trial & Collect Feedback

**Before the session**:
- Start the app: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Confirm `/health` returns 200
- Pre-load at least 1 fixture (e.g., Twinkle Twinkle) so the teacher isn't waiting on import

**During the session**:
- Observe without prompting — note anything the teacher hesitates on
- Only intervene if the app crashes
- Record (with consent) if possible

**After the session**:
- Collect completed `feedback.md`
- Copy raw answers into this file under the "Collected Responses" section below
- Note any ad-hoc verbal observations

---

## Step 18d — Write Conclusion & Update Backlog

After collecting at least 1 teacher response:

1. Summarise findings in `feedback.md` under a new `## Conclusion` heading
2. For each Q1–Q5 with "Disagree" or "Strongly disagree": open a Phase 2 BACKLOG item
3. For the open-ended "one thing to change": consider P1 hotfix or P2 planned feature
4. Mark BACKLOG items `P1-18a/b/c/d` all `[x]` once done
5. Commit: `docs(feedback): teacher trial results and phase 2 backlog update`

---

## Acceptance Criteria

| Step | Done when |
|------|-----------|
| 18a | `feedback.md` + this SOP exist; demo video recorded |
| 18b | Invitation sent; trial date confirmed |
| 18c | Completed `feedback.md` received |
| 18d | Conclusion written; BACKLOG updated; committed |
