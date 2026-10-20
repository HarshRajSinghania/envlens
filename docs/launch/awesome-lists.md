# Awesome-list submissions — envlens

These are permanent, free, and send traffic for years. Each list has its own PR format —
follow the existing entries exactly or the PR gets closed.

## How to submit

```bash
gh repo fork sindresorhus/awesome-nodejs --clone
cd awesome-nodejs
# add ONE line to the correct section, alphabetical, matching the local style
git checkout -b add-envlens
git commit -am "Add envlens"
gh pr create --title "Add envlens" --body "envlens — Find missing env vars before your deploy does. MIT licensed, actively maintained."
```

PR body must be three sentences max: what it is, why it belongs in that section, license.

## Target lists by stack

| Stack | List | Section |
| --- | --- | --- |
| Node / JS | sindresorhus/awesome-nodejs | Packages → the matching category |
| JS general | sorrycc/awesome-javascript | Utilities |
| TypeScript | dzharii/awesome-typescript | Libraries |
| Python | vinta/awesome-python | the exact category |
| Go | avelino/awesome-go | the matching sub-list file |
| Rust | rust-unofficial/awesome-rust | Applications / Libraries |
| CLI tools | agarrharr/awesome-cli-apps | the matching section |
| Self-hosted | awesome-selfhosted/awesome-selfhosted | Software → category (has strict rules) |
| DevOps | wsargent/docker-cheat-sheet — no; use awesome-devops lists |  |
| Terminals | k4m4/terminals-are-sexy | Tools |
| macOS | jaywcjlove/awesome-mac | Developer Tools |
| Windows | awesome-windows/awesome-windows |  |
| Linux | inputsh/awesome-linux |  |
| Security | sbilly/awesome-security |  |
| Data | oxnr/awesome-bigdata |  |
| Learning | practical-tutorials/project-based-learning |  |

Also: `awesome-<framework>` lists maintained by framework orgs — smaller but higher intent.

## What gets a PR rejected

- Entry added out of alphabetical order (instant close, no comment)
- Description longer than the neighbours
- Repo under ~100 stars on a list that screens by stars — wait, don't argue
- No license
- Archived repo, or last commit older than 12 months
- Adding to more than one section in one PR

## Realistic return

A merged entry in a 40k-star list sends 5–40 stars/month indefinitely, plus a steady trickle
of the exact users who search that category. It is the highest ROI-per-minute action in the kit.

Open 5 PRs. Expect 2 merges. Do not open 30 in a day — that pattern gets the account flagged
by maintainers who talk to each other.

## After merge

Add the list to your README as a badge or a line in a "Featured in" block. Social proof compounds.
