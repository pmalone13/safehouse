# Paris, September 2026

Trip planning/logistics for Paul and Christine's Paris trip. Not a
sub-project of anything else — flat under `projects/paris-september-2026/`
per Paul's own naming in the message that created it (queue id 29,
2026-09-07 ~21:53Z, voice message).

## Trip facts as of creation

- **Travelers:** Paul and Christine.
- **Outbound:** September 13, 2026, JetBlue, to Paris. (Note: Paul's
  first words on the voice message said "Paris October 2026" then
  immediately self-corrected to "Paris September 2026" — the project
  name and all dates here use the correction, not the false start.)
- **Lodging:** none booked yet. Plan is to "wing it" and rent something
  (Airbnb-style, unspecified) for about a week in Paris itself.
- **Side trip:** Normandy, by train, dates not yet specified — after
  the Paris week, before the return leg.
- **Return — Paul:** ~September 25, 2026, timed to make a party back
  home on the 26th.
- **Return — Christine:** uncertain — "26th, 27th, or maybe 28th,"
  i.e. she may stay 1-3 days longer than Paul.

## Open items (his to resolve, not mine to guess)

- Paris lodging — nothing booked as of this writing.
- Normandy leg — no dates, no specific itinerary (which sites, how
  many nights) yet.
- Christine's actual return date/flight.
- Return flight(s) for Paul — only the target date (25th) is known,
  not a booked flight.

## Capability note

Same standing limitation as `alliecar`: this VM has no reliable
persistent web access for booking or live-availability lookups (though
`WebFetch`/`WebSearch` have worked ad hoc for specific URLs — see the
alliecar project's Session 4 correction). Treat lodging/flight
research here as "try it live and say what worked," not "assumed
blocked" or "assumed will definitely work."

## Log

- **2026-09-07 ~21:53Z — queue id 29, Paul, voice message, project
  created.** Full transcript: "Perfect. Add a new project called Paris
  October 2026. Actually Paris September 2026. Christine and I are
  going to go to Paris the 13th of this month on JetBlue. We're going
  to find a Paris. We don't have a place to stay. We're going to wing
  it and rent something for like a week there. Then we're going to do
  a trip up to Normandy by train. I'm going to fly back. I think the
  25th so I can make it to a party here of the 26th and Christine's
  probably going to come back like the 26th or 27th or maybe the 28th."
  * Used the self-corrected name ("Paris September 2026") rather than
    the false start, since the correction came immediately and
    explicitly ("Actually...").
  * "We're going to find a Paris" almost certainly a transcription
    artifact (likely "find a place") — the very next sentence, "We
    don't have a place to stay," makes the same point cleanly, so
    treated the garbled clause as redundant rather than a separate
    fact to chase.
  * Extracted the concrete facts (dates, travelers, airline, general
    shape of the trip: Paris week + Normandy by train) and logged the
    explicit unknowns as open items above rather than inventing
    lodging or a Normandy itinerary that wasn't said.
  * This is the second project created directly from a voice message
    (after `alliecar` was created by email); no code involved, so
    outside the hard boundary entirely — just folder + `CLAUDE.md`
    creation, the normal step-3 checkpoint action.
  * Replied by SMS confirming the project was created and read the key
    facts back, so Paul can correct anything transcription mangled.
  * Updated the root `CLAUDE.md` "Current project" pointer to this
    file. `alliecar` and `safehouse/general` remain live threads —
    same three-projects-at-once situation as when alliecar and general
    were both active on 09-07; don't drop either.
