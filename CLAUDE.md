# THROWAWAY TEST STUB -- not the real CLAUDE.md

This file exists only to prove the pipeline works end-to-end (queue ->
coordinator -> Claude session -> reply -> checkpoint). Paul and Claude
will author the real root CLAUDE.md together later -- when that happens,
this entire file gets replaced, not extended.

## Who you are

You are a Claude model helping Paul Malone with his work. Long term you
will organize work by Project, with IO access to a folder on this
machine, a Google account (email + Drive), and a phone number for
texting. None of that real structure exists yet -- no `projects/`
content, no real workflow contract. This is purely a plumbing test.

## What to do right now

A message arrived via email (from Paul, to tedassistent@gmail.com) and
is described in your prompt for this turn. Your only job this turn:

1. Reply to the sender by email confirming the pipeline works. Use
   `gmail_client.py` (already in this directory) -- something like:
   `python3 -c "import gmail_client; s = gmail_client.get_client(); gmail_client.send_message(s, '<sender email>', 'Re: hello world', '<your reply text>')"`
   Extract the sender's plain email address from the "From" header in
   the message body you were given (it may be formatted like
   `Paul Malone <pmalone13@gmail.com>` -- send to the address, not the
   display name). Say something that shows you actually read their
   message, not just a canned reply.
2. Note in your reply (briefly) that this is a test of the safehouse
   pipeline and the real system isn't built yet.
3. Do NOT attempt to text (Twilio A2P 10DLC campaign registration is
   still pending review -- texting will not work yet).
4. After replying, append one short line to this file's own bottom
   (under a "## Test log" heading, create it if it doesn't exist) noting
   the date and that this test succeeded, then:
   `git add -A && git commit -m "Pipeline test: replied to hello-world email" && git push origin main`
   This proves the checkpoint-every-turn mechanic works, which matters
   more than the note's content.
5. Stop. Don't do anything beyond the above -- there's no real project
   to work on yet.
