# Launch checklist — envlens

Order matters. Each stage gates the next. Do not skip to reddit with a repo that has no releases.

## T-14 → T-7: make the repo survivable

- [ ] README has a one-line tagline above the fold, install, use, real output
- [ ] `LICENSE` present (MIT/Apache-2.0 — pick one, no license = nobody uses it)
- [ ] At least one tagged release with a downloadable artifact or package
- [ ] CI green on `main`
- [ ] `examples/` with a case that runs in under 30 seconds
- [ ] Issues enabled, Discussions enabled, security advisory enabled
- [ ] Profile README on the owner account links the repo
- [ ] Social preview image uploaded (Settings → General → Social preview, 1280×640)
- [ ] Repo description filled, 10 topics set (`gh repo edit --add-topic`)
- [ ] Branch protection on `main`: require CI, require one review

## T-7 → T-1: seed the ground

- [ ] 8–12 `good first issue` tickets written, each with a file pointer and acceptance line
- [ ] 3 "help wanted" tickets on real gaps
- [ ] CONTRIBUTING.md merged
- [ ] One demo GIF or asciinema in the README (a static screenshot loses 40% of clicks)
- [ ] Draft launch post in `docs/launch/hackernews.md`, read out loud once
- [ ] Draft reddit variants per sub — each written for that sub, not copy-pasted
- [ ] 5 awesome-list PRs opened (`docs/launch/awesome-lists.md`)
- [ ] Personal network: 10 people who actually use the thing, told privately first

## T-0: launch day

- [ ] Post to Hacker News, 06:00–08:00 US Eastern, Tuesday–Thursday
- [ ] Stay in the thread for 6 hours. Every critical comment answered within 20 min
- [ ] Reddit posts 2h after HN, staggered — never simultaneous
- [ ] X thread posted, link in bio, pinned
- [ ] Reply to every issue opened that day within 2h
- [ ] Do not edit the HN title after 30 minutes

## T+1 → T+7: hold the gains

- [ ] Thank-you comment in the HN thread with what changed because of feedback
- [ ] Ship a patch release addressing the top 3 complaints from day one
- [ ] Write a "what we learned" post, link it from the README
- [ ] Convert 3 drive-by commenters into issue authors
- [ ] Review traffic sources, kill the channel that sent nothing

## T+30: compound

- [ ] Second launch on a different channel (Lobsters, dev.to, a Discord, a newsletter)
- [ ] Publish a tutorial that targets the search keyword: "how to the-task"
- [ ] Submit to a newsletter (Console.dev, TLDR, Bytes, Python Weekly — pick the one for your stack)
- [ ] Cut a release with a headline feature; tag it, post the notes

## Numbers that mean something

| Signal | Weak | Working |
| --- | --- | --- |
| HN front page | — | 100+ points in 3h |
| Day-1 stars | <50 | 200–800 |
| Star → clone | <2% | 8–15% |
| Clone → issue | <0.5% | 2–5% |
| Week-1 external PRs | 0 | 2+ |

Stars without clones are a vanity metric. Clone rate is the only one that predicts a project surviving.
