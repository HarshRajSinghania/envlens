# Reddit plan — envlens

Rules differ per sub and moderators enforce them. Read the sidebar of each before posting.
One post per sub, staggered 2–24h apart, each rewritten for the room. Copy-paste gets removed.

## Target order

| # | Sub | Angle | Format | Self-promo tolerance |
| --- | --- | --- | --- | --- |
| 1 | r/programming | the engineering tradeoff | text post, no link in title | low — needs substance |
| 2 | r/en_US.UTF-8 | idiom fit, "how I solved X" | text + link in body | medium |
| 3 | r/opensource | maintainer story, roadmap | text | high |
| 4 | r/commandline | the CLI surface | asciinema + text | medium |
| 5 | r/devops | pipeline integration | text | low–medium |
| 6 | r/SideProject | build story | image + text | high |
| 7 | r/coolgithubprojects | plain link | link post | high |
| 8 | r/selfhosted | if it replaces a service | text | medium |

Do not post to more than 3 subs in one day. The same domain hitting the front page 6 times
in a day reads as spam and gets domain-banned.

## r/programming post shape

```
Title: envlens – the-task without the daemon
```

```
I have been writing the same {{PROBLEM}} block in every project for two years.
This is the extraction.

The interesting part was not the parsing, it was {{TECHNICAL DETAIL}}.
{{ONE PARAGRAPH ON THE HARD PART — this is why the post survives}}

Benchmark on 1.2M records, M1:
  envlens        340 ms
  {{ALT1}}       2.1 s
  {{ALT2}}       890 ms

Method: {{BENCH_METHOD}}, script in the repo under bench/.

Happy to answer on the design. The main thing I got wrong first was {{MISTAKE}},
which is why the API looks the way it does now.

https://github.com/n5za/envlens
```

## r/en_US.UTF-8 post shape

Lead with the idiom, not the product.

```
Title: Cleanest way I have found to {{TASK}} in en_US.UTF-8
```

Show 15 lines of before/after code in the post body. Link at the bottom. Code gets upvotes,
links get removed.

## r/SideProject post shape

```
Title: I built envlens because {{PROBLEM}} annoyed me for 3 years
```

Screenshot or GIF first. 3 bullets on what it does. 1 bullet on what it does not do.
Link. Ask one specific question to seed comments: "would you use this for {{USE CASE}}?"

## Rules that get posts removed

- Link post with a bare URL and no context → removed in r/programming
- Posting the same text to 5 subs in an hour → shadowban
- Any title containing "I made", "my", "free" → filtered in several subs
- Asking for stars → removed everywhere, and rightly
- Posting from an account under 30 days old → auto-filtered in the big subs

## Follow-up

Reply to every top-level comment in the first 3 hours. Convert feature requests to issues
and link them. Post a follow-up in the same sub 3–4 weeks later only if there is a real
release — not to farm a second wave.
