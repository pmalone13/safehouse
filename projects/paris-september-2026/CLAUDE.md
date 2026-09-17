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
- **Lodging:** booked — 41 Rue Lepic, 75018 Paris (Montmartre), an
  Airbnb-style rental. Confirmed by queue id 61 (2026-09-13 ~00:49Z).
- **Side trip:** Normandy, by train, dates not yet specified — after
  the Paris week, before the return leg.
- **Return — Paul:** ~September 25, 2026, timed to make a party back
  home on the 26th.
- **Return — Christine:** uncertain — "26th, 27th, or maybe 28th,"
  i.e. she may stay 1-3 days longer than Paul.

## Open items (his to resolve, not mine to guess)

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

- **2026-09-07 ~21:55Z — queue id 31, Paul: "No that looks good. That's
  that's what we're doing."** Confirmed by message timing (his reply
  arrived 21:55:22Z, 72s after my 21:54:10Z read-back text and *before*
  the next SMS I sent on an unrelated thread went out at 21:55:55Z) —
  this is his answer to the read-back, not to anything later. All the
  facts recorded above (travelers, JetBlue 09-13, no lodging yet,
  Paris week + Normandy by train, Paul back ~25th for a party the
  26th, Christine back 26th-28th) are **confirmed correct as
  transcribed**, not garbled. No reply needed — nothing new to say.

- **2026-09-13 ~00:49Z — queue id 61, Paul, email, "Paris trip."**
  Landed on travel day: "Arriving 10am tomorrow. Taxi to Air BNB, 41
  Rue Lepic, 75018 Paris, France" plus a request for first-day
  recommendations after the red-eye. This resolves the "Paris lodging"
  open item above — booked, in Montmartre, address recorded. Gmail
  tested working first (`get_client()` succeeded) before replying, so
  no repeat of the 2026-09-08/09 OAuth outage.
  Replied by email (same channel) with a Montmartre-scoped, jet-lag-
  aware plan: stay local to the flat rather than crossing the city,
  prioritize outdoor/daylight activity over resting, cap any nap at
  60-90 min, keep dinner early, push bedtime to a normal local hour.
  Named specific nearby spots (Sacre-Coeur, Place du Tertre, Rue des
  Abbesses/Rue Lepic bakeries, Cafe des Deux Moulins on Rue Lepic
  itself, the I Love You Wall at Square Jehan Rictus) and explicitly
  advised against ticketed/far-flung sights (Louvre, Versailles) on
  day one. No web lookup needed — this is general jet-lag/Montmartre
  knowledge, not a live-availability question, so the "try it live"
  capability note above didn't come into play this turn.
  Root `CLAUDE.md` Current-project pointer moved back here from
  `alliecar` (Paul's message was explicitly about this project);
  alliecar folded back into the other-live-projects list, not dropped.

- **2026-09-13 ~12:27Z — queue id 62, text, "Morning claude."** Purely
  conversational check-in, no ask embedded. Replied by SMS with a
  friendly how's-it-going and an offer to help with the two still-open
  items (Normandy dates, Christine's return date) rather than digging
  for a hidden task in a one-line greeting. No project facts changed.

- **2026-09-13 ~12:29Z — queue id 63, text, "Arriving at about 11am
  tomorrow and staying at 41 Rue Lepic... Give me three suggestions for
  things to do this first day while we are tired."** Same address
  already on file, but the arrival framing ("tomorrow," 11am) doesn't
  line up with queue id 61 (email, ~00:49Z same calendar day, "Arriving
  10am tomorrow" — answered as if he'd already landed and asked for
  day-1 plans hours ago). Didn't chase the discrepancy since it doesn't
  change the answer either way — replied by SMS with a condensed
  3-item version of the same jet-lag-friendly Montmartre plan (Sacre-
  Coeur/Place du Tertre, Rue des Abbesses/Rue Lepic cafes, Square Jehan
  Rictus + vineyard), same nap/dinner/bedtime advice as before. If a
  future turn sees yet another "arriving tomorrow" message, worth
  actually asking Paul to confirm the real arrival date rather than
  answering a third time — this is the second ask that assumes he
  hasn't landed yet.

- **2026-09-13 ~17:37Z — queue id 64, text, "let's just have all the
  not I mean just for the next few weeks the project is Paris... We're
  on route now. Flying standby all the way there because our son works
  for JetBlue."** Two things:
  * **Confirms the project stays `paris-september-2026`** as the active
    pointer for the next few weeks — already the case, no change needed
    to the root `CLAUDE.md` pointer.
  * **Solves the arrival-date puzzle flagged at the end of the queue id
    63 entry above.** They're flying standby (son works for JetBlue),
    so "arriving tomorrow" shifting across messages isn't a
    transcription error or confusion — it's genuinely unresolved because
    standby seating means they may not get on the flight(s) they expect
    and the actual arrival keeps moving. Don't chase this as an
    inconsistency in future turns; it's an accurate reflection of real
    uncertainty. Expect possibly more day-to-day schedule flux for the
    same reason (Normandy leg, return flights) since none of it may be
    firmly booked in advance.
  Replied by SMS: project confirmed staying Paris, standby explanation
  acknowledged, safe travels.

- **2026-09-14 ~07:44Z — queue id 65, text, "Just about to land. Flew
  business class, first time in a long time. Can u see this pic?"**
  The photo itself arrived as a **separate** MMS (`MM5b88...`, empty
  body, 1 media item, sent ~20s after the text) rather than attached to
  the text body — `twilio_webhook.py` only transcribes `audio/*` media
  into the enqueued body (see its own docstring), so an image MMS never
  shows up in the queued text at all; had to go find it. Queried the
  Twilio Messages API directly (`From=+12026181308`, most recent) to
  find the sibling MMS sid, then the Media sub-resource
  (`Messages/{sid}/Media.json` → per-media authenticated GET), same
  mechanism used for the `personal` project's SSA-card/passport photos
  on 2026-09-08. Confirmed real: a selfie in a lie-flat business-class
  seat, headphones on, seatback screen showing an NFL game (Giants),
  blanket/jacket over lap. Saved only to `/tmp` (not committed —
  no standing place for trip photos in this project yet, and nothing
  asked for one). Replied by SMS confirming I could see it, named what
  was in it (lie-flat seat, Giants game) so he knows it's not a guess,
  wished him a safe landing.

- **2026-09-14 ~07:45Z — queue id 66, text, "👍."** Acknowledgment of
  the photo reply above, 79s later. No reply needed, no facts changed.

- **2026-09-14 ~08:28Z — queue id 67, text, "Do you have recommendations
  for our 2nd day? Today will be local stuff. Versailles will be later
  in week."** Day 1 (today, landing day) is the local Montmartre plan
  already sent (queue ids 61/63); this is day 2, one step further out
  than staying local but explicitly not Versailles. Replied by SMS with
  a classic central-Paris metro loop: Louvre or Orsay in the morning
  (flagged Orsay as the lighter option if still jet-lagged), Ile de la
  Cite (Notre-Dame exterior + Sainte-Chapelle) plus a Seine walk into
  the Latin Quarter for lunch, then Eiffel Tower/Trocadero in the late
  afternoon for the light. No web lookup needed — general Paris
  itinerary knowledge, not a live-availability question.

- **2026-09-14 ~09:05Z — queue id 68, text, "R there ubers in paris."**
  Quick factual question, no web lookup needed. Replied by SMS: yes,
  Uber operates normally in Paris; also mentioned Bolt/FreeNow as
  alternatives (sometimes cheaper) and G7 as the major taxi company.

- **2026-09-14 ~11:21Z — queue id 69, text, "Could you recommend a good
  3.5 mile run from my apartment."** General local knowledge, no web
  lookup needed. Replied by SMS with a Montmartre loop from 41 Rue
  Lepic: down Lepic to Place Blanche, along Bd de Clichy to Place
  Pigalle, back up via Rue des Martyrs/Rue Yvonne le Tac, climb to
  Sacre-Coeur, past Place du Tertre and the Montmartre vineyard, back
  down Lepic. ~5.6km (close to 3.5mi), hilly with real climbs at
  Sacre-Coeur. Flagged that this VM has no mapping/GPS tool to verify
  exact distance, so suggested he confirm on his phone once running it.

- **2026-09-14 ~12:09Z — queue id 70, text, "What is the age of the
  buildings around monmontree."** General history question, no web
  lookup needed. Replied by SMS: most Montmartre buildings are 19th
  century (village annexed into Paris in 1860, then rapidly built up
  through the 1860s-1900s), with a few older standouts — Saint-Pierre
  de Montmartre church (~12th c.) and the old windmills like Moulin de
  la Galette (17th-18th c.) — and noted Sacre-Coeur itself is newer
  than it looks (built 1875-1914).

- **2026-09-14 ~19:06Z — queue id 71, text, "Can you list and describe
  famous Paris cemeteries."** General knowledge question, no web lookup
  needed. Replied by SMS with four: Pere Lachaise (20th, largest/most
  visited - Morrison, Chopin, Wilde, Piaf, Moliere), Montmartre Cemetery
  (closest to his flat, sits in an old quarry - Degas, Truffaut, Dalida,
  Nijinsky), Montparnasse (14th - Sartre/de Beauvoir, Baudelaire,
  Gainsbourg), Passy (16th, near Trocadero - Debussy, Manet). Also
  mentioned the Catacombs as a related-but-different (ossuary, not a
  cemetery, needs advance tickets) option. Flagged Montmartre Cemetery
  as the practical pick given his location and offered walking
  directions.

- **2026-09-15 ~15:31Z — queue id 72, text, "Can u help me find an
  evening boat cruise for tonight 8pm or later."** Live-availability
  question, so tried web tools per the capability note rather than
  assuming blocked. `WebSearch` plus `WebFetch` on `cometoparis.com`
  (the `bateauxparisiens.com` site itself returned empty/blank content
  to `WebFetch`, likely JS-rendered) confirmed Bateaux Parisiens runs an
  8:30pm dinner cruise **every day**, near the Eiffel Tower, 2h30,
  tiers €115-245 (Star/Discovery/Privilege/Premier). General search
  results also surfaced Bateaux Mouches as a same-slot cheaper
  alternative. Couldn't confirm actual seat availability for tonight
  specifically (no live booking-engine access) — said so rather than
  promising a seat, and pointed him to book directly at
  `bateauxparisiens.com` / `bateaux-mouches.fr` ASAP since dinner
  cruises want advance reservations. Replied by SMS with both options,
  pricing, and a heads-up to arrive 30min early since boats leave on a
  fixed schedule. Offered to help pick a tier if he wants to go
  further.

- **2026-09-15 ~15:33Z — queue id 73, text, "How about no food."**
  Follow-up on queue id 72 — wants a plain sightseeing cruise, not the
  dinner cruise just recommended. Searched further: standard 1-hour
  no-meal sightseeing cruises (Vedettes du Pont Neuf, Bateaux Parisiens'
  own sightseeing option) run frequently through the evening (every
  30-45min) into the 10-10:30pm range in September, cost ~€15-20, and
  don't need advance reservation the way the dinner cruise does. Named
  two walk-up spots: Vedettes du Pont Neuf (Square du Vert Galant, near
  Pont Neuf/Louvre) and the Bateaux Parisiens dock at the foot of the
  Eiffel Tower. Replied by SMS: just show up ~15min before a departure,
  no booking needed.

- **2026-09-15 ~16:45Z — queue id 74, text, "History of louve."** General
  knowledge question (Louvre history), no web lookup needed. Replied by
  SMS: 1190 fortress (Philip II) -> 1360s royal residence (Charles V) ->
  1540s Renaissance rebuild (Francis I) -> expanded over centuries
  (Catherine de Medici's Tuileries wing) -> court moved to Versailles
  1682 (Louis XIV), Louvre left mostly for art/academies -> opened as
  public museum 1793 during the Revolution -> collection greatly
  expanded under Napoleon -> I.M. Pei glass pyramid added 1989 -> now
  world's most-visited museum (Mona Lisa, Venus de Milo).

- **2026-09-16 ~09:19Z — queue id 75, text, "Morning on walking tour
  starting city hall and east."** General itinerary request, no web
  lookup needed. Replied by SMS with a Hotel de Ville -> Marais route:
  Hotel de Ville itself, into the Marais via Rue des Archives/Rue des
  Francs-Bourgeois, Place des Vosges (Victor Hugo's house), Rue des
  Rosiers (Jewish quarter, L'As du Fallafel), an optional indoor stop
  (Musee Carnavalet or Picasso Museum), ending at Place de la Bastille,
  with the Promenade Plantee flagged as an optional extension further
  east. ~2-2.5hr easy walk, flat terrain.

- **2026-09-16 ~09:50Z — queue id 76, text, "What year did young
  Napoleon fire Cannon on Paris rebels."** General history question, no
  web lookup needed. Replied by SMS: 1795 (13 Vendemiaire, Oct 5) —
  26-year-old Napoleon used cannon ("whiff of grapeshot") to crush a
  royalist uprising against the revolutionary government, defending the
  Tuileries area; the event that launched his rapid rise.

- **2026-09-16 ~11:09Z — queue id 77, text, "What kind of light is
  this" with an MMS photo attached.** Unlike queue id 65 (photo arrived
  as a separate MMS from the text), this one had the image attached
  directly to the same message (`MM9be687a0...`, `num_media=1`) — the
  webhook only ever forwards typed text, never media, into the queued
  body (see `_build_body` in `twilio_webhook.py`, audio-only
  transcription), so the photo itself doesn't reach the session
  automatically either way. Fetched it via the Twilio Media sub-resource
  (`Messages/{sid}/Media.json` -> per-media authenticated GET), same
  mechanism as queue id 65. Image: a long tapered cylindrical metal
  lamp housing suspended on cables strung across a narrow street between
  two buildings, shot looking straight up. Identified as a
  catenary-mounted (cable-suspended) street lamp — common in old
  European streets, including Montmartre, where fixtures hang from wires
  between buildings instead of standing on poles. Saved only to `/tmp`
  (not committed, same as queue id 65 — no standing place for trip
  photos in this project). Replied by SMS with the identification.

- **2026-09-16 ~11:15Z — queue id 78, text, "Halogen, neon?"** Follow-up
  on queue id 77, asking about the bulb/lamp technology rather than the
  mounting style just answered. Re-examined the same photo
  (`/tmp/paris_light_q77.jpg`): the housing is a fully enclosed, opaque
  metal tube with no visible glass or light-emitting element. Ruled out
  neon (needs a visible glass tube) and halogen (doesn't come in that
  elongated shape for street lighting) on that basis, and named the
  enclosed-cylindrical-suspended-fixture style as almost always modern
  LED. Replied by SMS with the reasoning and a practical tell (color at
  night: white/blue = LED, orange = older high-pressure sodium) since
  the photo alone can't confirm without seeing it lit.

- **2026-09-16 ~11:15Z — queue id 79, text, "Florescent."** Third
  guess in the same run (arrived 19s after queue id 78, likely typed in
  quick succession rather than after reading that reply). Same
  reasoning applies: fluorescent is also a glass tube, ruled out for the
  same opaque-metal-housing reason. Replied by SMS reiterating the
  sealed-LED-fixture conclusion.

- **2026-09-16 ~13:41Z — queue id 80, text, "Top five Roman ruins
  Paris?"** General history/sightseeing question, no web lookup needed.
  Replied by SMS with five: Arenes de Lutece (amphitheater, 5th arr),
  Thermes de Cluny (Roman baths, Musee de Cluny), Crypte Archeologique
  (Gallo-Roman remains under the Notre-Dame parvis), Musee Carnavalet's
  Lutetia collection (incl. a Roman-era dugout boat from the Seine), and
  Rue Saint-Jacques (traces the Roman cardo through the Latin Quarter).
  Noted the first three cluster in the Latin Quarter/Ile de la Cite and
  pair naturally with a Notre-Dame stop.

- **2026-09-16 ~13:43Z — queue id 81, text, "Can u give me map of first
  3."** Follow-up on queue id 80, wants a map for the three
  Latin-Quarter ruins (Arenes de Lutece, Thermes de Cluny, Crypte
  Archeologique). No live-mapping tool on this VM, but a Google Maps
  multi-stop directions URL is just a constructed link, not a lookup —
  built one (`/maps/dir/?api=1&origin=...&waypoints=...&destination=...
  &travelmode=walking`) in visiting order and sent by SMS, with an
  estimated ~25-30min total walking time between the three.

- **2026-09-16 ~14:15Z — queue id 82, text, "Why 7 floors in Paris
  buildings?"** General history question, no web lookup needed. Replied
  by SMS: Haussmann-era (1850s-70s) building codes capped height
  relative to street width (cornice height roughly = street width, up
  to ~20m on major boulevards) -> ground floor + 5 upper floors + a
  set-back mansard attic floor (the 7th, behind the sloped zinc roof).
  That uniform cornice line + mansard floor is the classic Haussmannian
  look across central Paris.

- **2026-09-16 ~15:02Z — queue id 83, text, "Did u get pic?"** A photo
  MMS (`MMbe6cb...`, empty body, 1 media item) had arrived 12min earlier
  at 14:50Z but never reached the queue — same known gap as queue ids
  65/77 (`twilio_webhook.py` only transcribes `audio/*` media, images
  never get forwarded into the enqueued body). Fetched it directly via
  the Twilio Media sub-resource (same mechanism as those prior turns).
  Image: striped Roman brick-and-stone "opus mixtum" ruin walls with a
  modern museum wing visible behind — consistent with the Thermes de
  Cluny (Roman baths), #2 on the top-5 list sent for queue id 80, and
  right after the walking-route map sent for queue id 81. Saved only to
  `/tmp` (`/tmp/paris_pic_q83.jpg`, not committed — same no-standing-
  place-for-trip-photos situation as queue ids 65/77). Replied by SMS
  confirming receipt, named what's in it, and asked him to confirm it's
  Cluny rather than assuming.

- **2026-09-16 ~15:07Z — queue id 84, text, "Yes. Now here .."**
  Confirms queue id 83's guess: he's at Thermes de Cluny. No new media
  on this message (checked the Twilio Messages API, `num_media=0`).
  Replied by SMS with a quick tip (frigidarium hall is the highlight)
  and pointed him to the next stop on the queue id 81 walking route
  (Crypte Archeologique, ~10min walk east under the Notre-Dame parvis).

- **2026-09-16 ~17:20Z — queue id 85, text, "what is the earliest
  estimate of homo sapien living in the Paris region. Same for any
  other humanoid like neandrethal."** General prehistory question, used
  `WebSearch` (available this session) rather than answering from
  memory alone given the specific-region framing. Findings: no Homo
  sapiens fossils found in Paris itself; earliest sapiens presence in
  France overall is ~54,000ya (Grotte Mandrin, Rhone valley, a
  temporary incursion later reversed by Neanderthals); in the Paris
  Basin specifically the evidence is Chatelperronian-layer tools
  ~40-45,000ya (contested whether Neanderthal or sapiens made them),
  with clear/undisputed sapiens presence by ~38,000ya (Aurignacian).
  Older hominins go back much further: Levallois-Perret (a Paris
  suburb) gave its name to the Levallois stone-tool technique used by
  Neanderthals in the region ~300-200,000ya; earlier still, the Soucy
  site in the Seine/Paris Basin has Acheulean tools dated
  ~340-370,000ya, attributed to Homo heidelbergensis (a Neanderthal
  ancestor) — so archaic humans occupied the Paris region on and off
  for 300,000+ years before sapiens arrived. Replied by SMS with this
  breakdown. No web-access issue this turn (WebSearch worked fine,
  separate from the ongoing Drive-only outage below).

- **2026-09-17 ~08:31Z — queue id 86, text, "Is the Frenchman
  L'enfaunt who met Franklin in Paris circa 1777 the same man who
  designed DC."** Confirmed yes — Pierre Charles L'Enfant. Used
  `WebSearch` rather than answer purely from memory since the specific
  "met Franklin" claim needed checking: the recruitment-in-Paris-1777
  credit in sources found (Wikipedia, Journal of the American
  Revolution, Founders Archives) goes to envoy Silas Deane (who signed
  L'Enfant's contract) and arms-dealer/playwright Beaumarchais, not
  documented as a personal Franklin connection — Franklin was a fellow
  American commissioner in Paris at the same time, so plausible but not
  confirmed as stated. Flagged that distinction rather than just
  confirming the premise outright. Same L'Enfant later designed the
  1791 Washington DC street plan for Washington. Replied by SMS.

- **2026-09-17 ~11:52Z — queue id 87, text, "Give outline of louve
  history."** Same question as queue id 74 (2026-09-15), likely just
  forgotten/wanted again rather than a new ask. Resent the identical
  outline (1190 fortress -> 1360s royal residence -> 1540s Renaissance
  rebuild -> Louis XIV moves to Versailles 1682 -> public museum 1793
  -> Napoleon-era expansion -> 1989 pyramid -> today's most-visited
  museum) by SMS rather than re-researching from scratch.

- **2026-09-17 ~12:04Z — queue id 88, text, "Louve map walking guide to
  hit top ten pieces."** Follow-up to queue id 87. General art/museum-
  layout knowledge, no web lookup needed. Built a practical walking
  route by actual Louvre wing/floor (start at Pyramid, Denon wing first
  then Sully) rather than just listing famous pieces unordered:
  Michelangelo's Slaves -> Winged Victory of Samothrace -> Mona Lisa ->
  Wedding at Cana -> Liberty Leading the People -> Raft of the Medusa
  -> Coronation of Napoleon -> Venus de Milo -> Great Sphinx of Tanis
  -> Code of Hammurabi. Replied by SMS with room/wing locations and a
  tip to book a timed slot given midday Mona Lisa crowds.

- **2026-09-17 ~12:34Z — queue id 89, text, "What year was winged
  victory carved."** Follow-up on #2 from queue id 88's route. Used
  `WebSearch` rather than memory alone for the specific date range:
  ~190 BC (Hellenistic era, Parian marble; sources cite a range of
  roughly 200-175 BC), artist unknown, discovered in fragments on
  Samothrace in 1863, reconstructed in the Louvre. Replied by SMS.

- **2026-09-17 ~13:34Z — queue id 90, text, "Outline charlamain's
  career."** General history question, no web lookup needed. Replied
  by SMS with a career outline: born c.747 -> co-king 768 (with
  Carloman I) -> sole king 771 -> conquers Lombards 774 -> Saxon Wars
  772-804 -> Roncevaux Pass defeat 778 (Song of Roland) -> crushes Avar
  Khaganate by 796 -> crowned Holy Roman Emperor by Pope Leo III,
  Christmas 800 -> Carolingian Renaissance (Alcuin of York, Aachen
  palace school) -> dies 814 at Aachen, empire split among grandsons at
  Verdun 843.

- **2026-09-17 ~14:26Z — queue id 91, text, "What is considered pre-
  history date wise."** General knowledge question, no web lookup
  needed. Replied by SMS: prehistory = before written records, not a
  fixed universal date — starts with earliest stone tools ~3.3mya (or
  Homo genus emergence ~2.5mya); end date varies by region depending on
  when writing appears locally (Sumer/Mesopotamia ~3200 BC earliest,
  Egypt ~3000 BC, Britain not until the Roman conquest AD 43, some
  regions not until European contact centuries later).

- **2026-09-17 ~14:54Z — queue id 92, text, "Are crown jewels or
  Napoleon rooms open now?"** Live-availability question, tried
  `WebSearch` per the capability note rather than answering from stale
  general knowledge. Found something the general-knowledge answer
  would've missed: an **Oct 19, 2025 Louvre heist** — 8 French Crown
  Jewels pieces stolen from the Apollo Gallery, still unrecovered.
  Gallery itself reopened July 22, 2026 but currently **empty** — no
  jewels on display (remaining pieces to eventually go on view
  elsewhere in the museum, not yet done as of the sources found).
  Napoleon III Apartments: open, no current closure (last renovation
  was 2023-24, fully reopened June 2024). Also confirmed via a quick
  `date` check that today (2026-09-17) is a Thursday, so the museum
  itself isn't hit by its standing Tuesday closure. Replied by SMS:
  Napoleon rooms worth doing, crown jewels room is walkable but has
  nothing to actually see right now.
