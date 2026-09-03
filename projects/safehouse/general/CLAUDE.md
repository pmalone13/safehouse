# safehouse/general

This is the catch-all bucket for anything that isn't a specific named
project — automated notifications worth a quick check (like the Google
security alert handled here), conversational messages from Paul, meta
questions about the system itself, one-off requests too small to deserve
their own project. Log what happened here; don't over-invest structure
into this sub-project since being the non-project bucket is its whole
point. If something that lands here turns out to be the start of real,
ongoing work, that's the signal to spin it out into its own
`projects/<name>/` instead of letting it accumulate here.

## Log

- **2026-09-01, session `6a2aefb8` (two messages).** Both predate this
  bucket existing, so the long-form write-ups live in the root
  `CLAUDE.md` test log; recording them here so the general log isn't
  misleadingly empty about work that belongs to it.
  * *Queue id 1 — Paul, "describe yourself in a reply."* Conversational,
    not an assignment. Answered by email (what I am, the episodic
    spawn/resume shape of a session and why the per-turn checkpoint is
    the only continuity, working vs. blocked capabilities, the metered-
    API-key billing caveat, my limits). Deliberately created nothing
    under `projects/` — correct call at the time, and the reason this
    catch-all bucket was invented shortly after.
  * *Queue id 2 — automated Google "Security alert: you allowed Safehouse
    access."* Exactly this bucket's stated use case. Treated as a
    verification job, not a message to answer: confirmed authentic from
    the raw headers (`dkim=pass @accounts.google.com`, `spf=pass`,
    `dmarc=pass` on `p=REJECT`), decoded the grant time from the epoch in
    the alert URL (`1788276241000` ms = 15:24:01Z), and established the
    grant had no effect on the VM because the token was still on Paul's
    laptop. Emailed him the one actionable thing (the `scp`) plus the
    `auth/drive` vs `drive.file` scope tradeoff while narrowing was still
    cheap.
  * *Resolved since, by later turns:* the Drive token did land (15:38)
    and was smoke-tested; Paul chose to keep full `auth/drive`. So the
    "Drive is dead here" statements in my turn-3 email and in the root
    log are now **stale** — Drive is live. Don't act on them.

- **2026-09-01 ~16:27 — session wrap-up (idle timeout, no new message).**
  Nothing pending: queue ids 1 and 2 both `done`, working tree clean.
  Sent no further email — Paul already knows Drive works (he placed the
  token himself), and the one question I'd asked twice, "what's the first
  real project," is now structurally handled by this bucket existing
  rather than being something to nag about. Ran the checkpoint (commit,
  push, `drive_sync.py`) mainly because the Drive mirror had gone stale:
  `.drive_sync_state.json` was from 15:48 but tempWork/ and utils/ landed
  at 16:17–16:24, so the mirror Paul reads was missing them.
  Open threads for whoever picks this up next: (1) no *named* project yet
  — wait for Paul, don't invent one; (2) A2P campaign still
  `IN_PROGRESS`, watcher running every 30 min, don't poll it by hand;
  (3) still no inbound text channel, pending the VPN-vs-public-port call.

- **2026-09-02 ~11:54 — queue id 3, automated Twilio A2P rejection.**
  Fresh session (the 2026-09-01 resume ticket had long expired). Another
  textbook case for this bucket: an automated notification that needed
  verifying and interpreting, not answering.
  * Verified the mail was really Twilio (`dkim=pass @twilio.com`,
    `spf=pass`, via Twilio's SendGrid), clicked no links.
  * Went past the single email: dug the two earlier rejections out of
    Gmail and read the campaign + brand objects from the Twilio API. The
    shape of it is that this is the **third** rejection and the **second**
    for error 30915 — a `SOLE_PROPRIETOR` brand with an LLC's identity
    visible to reviewers (this time on the website they pulled up:
    "Ideal Federal Technologies, LLC"). `campaign_status` is now `FAILED`.
  * Emailed Paul the decision, not a status update: two mutually exclusive
    paths (scrub the LLC and stay sole prop vs. register the LLC as a new
    STANDARD / LOW_VOLUME_STANDARD brand, which can't be done in place),
    my recommendation of the latter and why, plus two concrete defects in
    the current campaign he should fix while editing either way.
  * Did **not** edit or resubmit the registration despite holding working
    API credentials. Filing a business classification with carriers is
    Paul's representation to make; the whole question the rejection poses
    is one only he can answer. Worth remembering as the general shape:
    having the credentials to do a thing is not the same as it being mine
    to do.
  * Left the watcher running and amended the root file's teardown rule —
    it previously said to retire the watcher when status left
    `IN_PROGRESS`, which would have been wrong here. `FAILED` means
    another resubmission is coming; only `APPROVED` retires it. Also
    recorded the email-vs-API lag (email 11:53Z, API still `IN_PROGRESS`
    at the 11:30 tick, `FAILED` at 11:54Z).
  Open thread: waiting on Paul's A-vs-B answer. Until then texting stays
  blocked and there is nothing further to do on it from this VM.

- **2026-09-02 ~12:57 — session wrap-up (idle window elapsed, no new
  message).** Nothing pending and nothing to revise: queue id 3 handled,
  working tree clean at `7ff102b`, and one deliberate inbox read confirmed
  Paul hasn't answered the A-vs-B question yet (last inbound from him is
  still 2026-09-01). The watcher ticked at 12:00 and 12:30 and correctly
  logged nothing — status is stably `FAILED`, which is the expected
  resting state until Paul resubmits, so silence from it is the signal
  working, not the signal broken. Ran the checkpoint to carry the 12:30
  watcher-state files out to the Drive mirror.
  Open threads unchanged: (1) still no *named* project — wait for Paul;
  (2) A2P blocked on Paul's classification decision, watcher stays until
  `APPROVED`; (3) still no inbound text channel, pending the
  VPN-vs-public-port call.


- **2026-09-02 ~16:20 — queue id 4, automated Twilio "resubmission
  received."** Fresh session. On its face a no-action-needed
  acknowledgement; treating it that way would have missed the actual
  problem. Verified authentic (`dkim=pass @twilio.com`, `spf=pass`),
  clicked nothing.
  * **What Paul did between turns:** he never answered the A-vs-B email,
    he just went and executed **path A** — commit `89dcd6f` (16:04Z)
    added a standalone Flask site for idealfed.com (About/Privacy/Terms,
    gunicorn on 127.0.0.1:8091 behind nginx), deliberately free of LLC
    branding, then resubmitted the campaign with new Privacy/T&C URLs.
    API confirms: same brand `BN257b...1afc`, still `SOLE_PROPRIETOR`,
    `campaign_status` back to `IN_PROGRESS`, `errors` now empty. The
    scrub itself checks out — no "LLC"/"Ideal Federal" anywhere in
    `idealfed_site/`, description reads "Paul Malone of Tracys Landing MD".
  * **The finding: idealfed.com was unreachable from the internet.**
    Certbot issued a valid cert at 15:17Z and rewrote the `:80` server
    block to `return 301 https://...`, but inbound 443 is not open.
    Evidence chain: port 80 OPEN / port 443 times out (tested against the
    VM's own public IP 3.238.63.42); `curl --resolve idealfed.com:443:
    127.0.0.1 https://idealfed.com/privacy` returns **200**, so nginx and
    the cert are fine and only the packets are missing; `ufw` inactive and
    `iptables INPUT` an empty ACCEPT chain, so it's not the host — it's the
    AWS security group (instance `i-066d2ff2bfd9cf3c9`). No http fallback
    either, since :80 301s to the dead port. So every URL on the domain was
    a black hole starting ~the moment he resubmitted, and the reviewer who
    opens the privacy/terms URL gets a timeout — a near-certain 4th
    rejection after burning 1–3 business days.
  * **Did not fix it.** Opening a security-group port is an infrastructure
    change and lands on the wrong side of the hard boundary. Emailed Paul
    the diagnosis with the evidence, the one-line verification
    (`curl -sI https://idealfed.com/privacy | head -1`), and the SG names.
    Same principle as this morning's turn: holding the credentials to do a
    thing isn't the same as it being mine to do.
  * **Re-flagged, still unfixed:** "Fields updated" lists only the two URLs,
    and the API confirms `message_samples[2]` is still literally
    "Any message...." and `has_embedded_links`/`has_embedded_phone` are both
    true with no link or phone in any sample. Told him I don't know whether
    Twilio permits a mid-review edit vs. forcing submission #7 — that's a
    console question — but weighed against a guaranteed rejection.
  * Noted a red herring for future turns: both the email and the API report
    the campaign date as `2026-08-10T13:32:28Z`. That's the original
    creation date echoing through, **not** today's resubmission time.
  * Watcher untouched and still correct: 16:00 tick read `FAILED`, the
    16:30 tick will log `FAILED -> IN_PROGRESS`. Retire only on `APPROVED`.
  Open threads: (1) 443 closed — blocking, only Paul can clear it;
  (2) the two campaign defects, his call; (3) still no *named* project;
  (4) still no inbound text channel.

- **2026-09-02 ~17:21 — session wrap-up (idle window elapsed, no new
  message).** Checked the three things that could have changed since the
  queue-id-4 turn, and the answer to all three was "not yet":
  * Watcher behaved exactly as predicted — the 16:30 tick logged
    `'FAILED' -> 'IN_PROGRESS'`, and 17:00 held steady. Silence from it
    now is the signal working; `IN_PROGRESS` is the expected resting
    state for the next 1–3 business days.
  * **443 is still closed** an hour after the email (re-tested: port
    dial times out, `https://idealfed.com/privacy` returns `000`). So
    the site is still a black hole to any reviewer who opens it.
  * No reply from Paul; last inbound from him is still 2026-09-01.
  Sent no second email. He got the diagnosis, the exact fix, and the
  one-line verification at 16:20Z — a follow-up an hour later carrying
  no new information is noise, not diligence. If the reviewer hits the
  dead URL and the campaign fails again, that generates its own message
  and its own turn to act on.
  Updated the root `CLAUDE.md`, whose texting TODO still described the
  campaign as `FAILED` and still framed the sole-prop-vs-LLC decision as
  open — both stale now that Paul has answered it by building the site
  and resubmitting. Rewrote it around the current state and the 443
  blocker, and amended the tempWork watcher note's status history.
  Open threads: (1) **443 closed — blocking and time-boxed by the review
  window; only Paul can clear it**; (2) the two campaign defects
  ("Any message...." sample, mismatched embedded-link/phone flags),
  his call; (3) still no *named* project — wait for Paul; (4) still no
  inbound text channel, pending the VPN-vs-public-port decision.

- **2026-09-02 ~18:35 — queue id 5, Paul: "Waiting on dns to ripple. Email
  me when u can resolve name."** Fresh session. Short message, but checking
  the premise overturned yesterday's diagnosis.
  * **The correction: the 16:20Z "443 closed in the AWS security group"
    finding was wrong.** This instance's public IP is **54.88.172.94**
    (EC2 IMDS, `i-066d2ff2bfd9cf3c9`), and `uptime -s` / `last reboot`
    show no reboot since 2026-08-09 — so it has held that address the
    whole time. `idealfed.com` resolves to **3.238.63.42**, which was
    never this box. The previous turn dialed the DNS answer, found 443
    dead, and attributed the timeout to our security group; it was
    port-scanning an unrelated host. **Lesson: when a name is unreachable,
    confirm the resolved IP is actually yours before diagnosing anything
    downstream of it.** The whole evidence chain (80 open / 443 timeout /
    loopback 200 / ufw+iptables clean) was individually true and led
    somewhere false because step zero went unchecked.
  * **443 is open.** Proof is the nginx access log, not a port dial: outside
    hosts complete TLS (34.23.210.195 at 17:47, 150.107.38.85 at 18:31,
    both 200) and a 200 can only come from the TLS vhost, since `:80`
    returns 301 unconditionally. Can't tell whether Paul opened it after
    the email or it was never shut; said so plainly rather than guessing.
  * **Real state: DNS mid-propagation, registrar side nearly done.**
    Repeated direct queries return a mix — ns35.worldnic.com gave
    3.238.63.42 once in four, ns36 once in four; ~3 of 4 authoritative
    answers already correct. The lag is downstream caches: 8.8.8.8/8.8.4.4,
    1.1.1.1, 9.9.9.9, OpenDNS and Verisign all serve the old IP, record TTL
    **7200**. Google cached its stale copy ~18:32Z (TTL observed
    decrementing 7173 -> 7161), so it serves the dead address until roughly
    **20:30Z** regardless of worldnic. Lowering TTL now can't help — the
    7200 is already downstream. Told Paul: self-clears within ~2h; if not
    by ~21:00Z it's a Network Solutions problem, not propagation.
  * **Server verified ready** against 54.88.172.94 via `--resolve`: `/`,
    `/privacy`, `/terms` and the `www` host all 200; cert CN=idealfed.com,
    SANs idealfed.com + www.idealfed.com, good to Dec 1. So DNS is the only
    thing between a reviewer and the pages. (`/about` 404s but nothing
    links to it — the About copy lives on `/`.)
  * **Couldn't satisfy the literal ask** ("email me when u can resolve
    name") — I only run when a message arrives, so no turn exists between
    now and 20:30Z. Gave him two routes: email me anything after ~20:45Z
    and I'll verify end to end, or say the word and I'll build a small cron
    watcher **with him present**, since a new script is on the wrong side
    of the hard boundary. Did not build it unattended.
  * Re-read the campaign from the API: `IN_PROGRESS`, `errors` empty, and
    both defects unchanged — `message_samples[2]` still "Any message...."
    and `has_embedded_links`/`has_embedded_phone` still true with no link
    or phone in any sample. Re-flagged briefly; still his call.
  Open threads: (1) DNS ripple, ETA ~20:30Z, no action available from here;
  (2) offered DNS watcher awaiting Paul's go-ahead; (3) the two campaign
  defects; (4) still no *named* project; (5) still no inbound text channel.

- **2026-09-02 ~19:40 — session wrap-up (idle window elapsed, no new
  message).** Not a formality this time: re-checking DNS invalidated the
  ETA I'd emailed an hour earlier, so this turn sent a second email.
  * **The ~20:30Z "it clears itself" estimate was wrong.** It assumed the
    authoritative side was converging. It went the other way: 2 of 8
    queries stale at 18:33Z, **11 of 24 stale at 19:40Z** (ns35 6/12,
    ns36 5/12) — hovering near a coin flip an hour later.
  * **The diagnostic that reframes it:** every response carries exactly
    one A record, and the SOA serial is **identical on every query to
    both nameservers (126090214)** while the A answer flips between
    54.88.172.94 and 3.238.63.42. Same serial, contradictory data ⇒ the
    machines behind ns35/ns36 serve different zone contents while each
    believes it's current, and a secondary that thinks it's current has
    no trigger to re-pull. So there is **no timer on which this
    necessarily self-heals** — it stopped being "propagation."
  * **Why the caches never drain:** ten queries to 8.8.8.8 returned a mix
    of TTLs (7200/7199/7172 next to 3349/3258), i.e. some Google backends
    re-queried within the last minute, drew the stale answer again, and
    re-armed another 2 hours. Cloudflare uniformly 7200. Every refresh is
    a fresh coin flip, so waiting doesn't monotonically improve.
  * **Emailed Paul** the walk-back plus the two things worth doing *now*
    instead of waiting for the 21:00Z threshold I'd given him: (1) eyeball
    the Network Solutions panel for a leftover 3.238.63.42 apex A record
    beside the new one (I can't see that page); (2) if it looks right,
    ask support to force a zone re-publish, quoting the symptom verbatim
    — "SOA serial 126090214 identical on ns35 and ns36 but queries return
    two different A records" — which is specific enough to get past a
    tier-1 "wait 48 hours" script.
  * Confirmed unchanged: no reply from Paul (last inbound is still the
    18:31Z one that opened this session), server still 200 on `/`,
    `/privacy`, `/terms` at 54.88.172.94, campaign still `IN_PROGRESS`
    with empty `errors`, watcher ticking correctly (19:30, no change
    logged — `IN_PROGRESS` is the expected resting state).
  * **Precedent worth keeping:** last hour's wrap-up turn deliberately
    sent nothing, on the grounds that a follow-up carrying no new
    information is noise. That was right then and wrong now — the
    difference is that I had put a specific number in front of him
    (20:30Z) and a specific decision rule (wait until 21:00Z), and both
    turned out to be wrong. Correcting a prediction someone is acting on
    is not noise.
  Open threads: (1) **DNS unresolved and possibly not self-healing** —
  needs Paul at the registrar, nothing available from this VM; (2) the
  offered cron watcher still awaiting his go-ahead (new script, requires
  him present); (3) the two campaign defects ("Any message...." sample,
  mismatched embedded-link/phone flags); (4) still no *named* project;
  (5) still no inbound text channel.

- **2026-09-03 ~13:09 — queue id 6, automated Twilio A2P rejection #4.**
  Fresh session. Two unrelated things resolved in the same turn: the DNS
  saga ended, and the campaign failed again for reasons that have nothing
  to do with it. Verified the mail authentic (`dkim=pass @twilio.com`,
  `spf=pass`, via SendGrid), clicked nothing.
  * **DNS is fixed — Paul's standing ask from queue id 5 is satisfied.**
    12/12 direct queries to *both* ns35 and ns36 now return
    **54.88.172.94**; 8.8.8.8, 1.1.1.1 and 9.9.9.9 all agree. Fetched over
    real DNS with no `--resolve`: `/`, `/privacy`, `/terms`, the `www`
    host and the `http`→`https` redirect all 200. Notable: the **SOA
    serial is still 126090214**, unchanged from yesterday's divergence —
    so I can't tell whether Paul forced a re-publish or it settled on its
    own, and said exactly that rather than claiming credit for a theory.
  * **The rejection is NOT the DNS outage.** Two codes, and they're of
    very different quality:
    - **30909 (message flow / CTA) is the real, certain blocker** and is
      DNS-independent — it would have failed on a perfect website. The
      `message_flow` field claims consent "via text, email, or verbally"
      with no URL or screenshot, which is unverifiable by construction.
      **The reviewer missed the worse half**: the field's second sentence
      describes sending a first text to ask whether someone wants texts —
      messaging *before* consent, independently disqualifying. Flagged
      that as probably more damaging than the missing URL.
    - **30908 (privacy policy) does not survive checking.** Reviewer said
      the URL "needs sign in." Our `/privacy` needs none (pulled it
      anonymously, 200) and already carries the demanded sentence
      verbatim ("No mobile information will be shared with third parties
      or affiliates for marketing or promotional purposes"). And it was
      *publicly reachable during the review window*, proven from
      `/var/log/nginx/access.log` — outside clients pulled `/privacy` and
      `/terms` with 200s at 20:34Z, 22:04Z, 01:51Z and again 11:16Z /
      11:22Z / **12:35Z, under two hours before the rejection**.
  * **The gap I could not close, stated as a gap:** Twilio's API does not
    expose the campaign's privacy/terms URL fields *at all* (confirmed —
    not in the Usa2p compliance object, not on the brand, and the
    customer profile's `website_url` is empty). So I cannot verify what
    URL Paul actually typed. Gave him the two candidate explanations —
    the field points somewhere behind a login (a Google Doc would produce
    exactly their wording), or the reviewer hit stale DNS and picked a
    canned note — and asked him to read the field back verbatim from
    console. Resisted the pull to assert the more flattering one.
  * **Method note worth keeping:** the instinct after yesterday's
    correction was to assume the dead DNS caused this too. The access log
    disproved that in one grep. Checking whether the obvious culprit
    actually did it was the whole value of the turn — the fix Paul needs
    is in a text field, not in his registrar.
  * Also probed the stale IP **3.238.63.42** directly: no HTTP, no HTTPS,
    no TLS — a completely dead host, not a login page. That's what ruled
    out "reviewer saw a sign-in wall at the stale address."
  * Confirmed **brand `BN257b...1afc` is still APPROVED / VERIFIED** and
    told him so explicitly — the rejection is campaign-only and he does
    not need to redo brand registration.
  * Re-flagged the two long-standing defects a fourth time
    (`message_samples[2]` = "Any message....", `has_embedded_links` /
    `has_embedded_phone` true with no link or phone in any sample).
  * **Offered but did not build** a `/sms-optin` page (unchecked-by-default
    consent checkbox + required disclosures) — the clean fix for 30909,
    and squarely application code, so it waits for Paul to be present.
    Same boundary call as the DNS watcher last night.
  * **Did not edit or resubmit the campaign.** Fourth time holding this
    line; the message flow is a statement about how Paul actually
    collects consent. Did draft suggested language *for him to verify*,
    which is different from filing it.
  * Watcher: 13:00 tick still read `IN_PROGRESS`, a fresh read at 13:10
    read `FAILED` — the same email-vs-API lag as 2026-09-02. The 13:30
    tick will log `IN_PROGRESS -> FAILED`. Stays running; only `APPROVED`
    retires it.
  Open threads: (1) **campaign needs a rewritten message_flow + a real
  opt-in URL — Paul's call, and the page needs him present**; (2) he
  needs to read the privacy-policy URL field back from console, since I
  can't; (3) the two stale campaign defects; (4) still no *named*
  project; (5) still no inbound text channel.
