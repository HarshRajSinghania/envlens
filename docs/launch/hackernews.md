# Hacker News submission — envlens

## Title

The title is 80% of the outcome. Rules: no clickbait, no "Show HN" unless it is
something people can try. Show HN gets a different audience and a lower ceiling.

Pick one:

```
Show HN: envlens – Find missing env vars before your deploy does
```

```
envlens: the-task in 40ms, no daemon
```

```
I built envlens because {{PROBLEM}} took 40 lines of boilerplate
```

Do not use: "blazing fast", "revolutionary", "game-changer", "yet another". HN reads those as a downvote signal.

## Text body (Show HN)

```
Hi HN,

I kept writing the same {{PROBLEM}} code in every project, so I extracted it.

envlens does {{ONE THING}} in one command:

    $ envlens ./input
    ✓ 1,284 records in 340ms

What is different: {{DIFFERENTIATOR}}. No account, no telemetry, single binary.

It is at v0.1 and the API will move. The parts I am least sure about:
- {{OPEN QUESTION 1}}
- {{OPEN QUESTION 2}}

Would rather hear it is wrong now than after 1.0.

Repo: https://github.com/n5za/envlens
```

Naming your own weak points is the single highest-leverage move on HN. It converts
attackers into advisors.

## Timing

- Tuesday, Wednesday, or Thursday
- 06:00–08:00 US Eastern (10:00–12:00 UTC)
- Never Friday, never a US holiday, never the day a major model ships

## The first 60 minutes decide everything

- 5 points in 10 min → it will surface
- Reply to the first 3 comments within 10 minutes; comment velocity feeds ranking
- Do not ask anyone to upvote. Vote rings get detected and the post gets buried
- Do not edit the title after 30 min — it resets ranking

## Comment armour

| Comment | Response shape |
| --- | --- |
| "Why not just use X?" | Name the one concrete difference. Concede the rest. |
| "This is trivial" | "It is 400 lines. The value is not difficulty, it is that you don't write them." |
| "Security?" | Link SECURITY.md, name the threat model boundary. |
| "Doesn't work on Windows" | "Correct, and now tracked: #issue. Fixed this week." Never argue. |
| Hostile, no content | Ignore. Not one reply. |

Every acknowledged bug gets an issue number in the reply and a fix inside 7 days.
HN remembers the follow-through more than the launch.

## After

Post one comment at +24h: what shipped because of the thread. That comment is what
gets the repo its second wave.

## Realistic outcome

- Front page 3h+ → 300–2000 stars, 10–40 issues, 3–8 real contributors
- Page 2 → 20–80 stars, still worth it
- Dead → the post was not the problem, the README was. Fix the README and try again in 3 months with a new angle.
