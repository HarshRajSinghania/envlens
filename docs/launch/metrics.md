# Metrics — envlens

Track weekly, one row. Fifteen minutes. The point is to kill channels that do not work
and double the one that does.

## Pull the numbers

```bash
# traffic, last 14 days
gh api repos/n5za/envlens/traffic/views

# clones — the only star-adjacent number that means anything
gh api repos/n5za/envlens/traffic/clones

# referrers — where the traffic actually came from
gh api repos/n5za/envlens/traffic/popular/referrers

# stars, forks, watchers
gh api repos/n5za/envlens --jq '{stars:.stargazers_count,forks:.forks_count,watchers:.subscribers_count,issues:.open_issues_count}'
```

Note: traffic API needs push access and only returns 14 days.

## Log

| Week | Views | Uniques | Clones | Stars | Forks | Issues opened | External PRs | Merged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W1 | | | | | | | | |
| W2 | | | | | | | | |

## Read the ratios, not the totals

| Ratio | Healthy | Diagnosis if low |
| --- | --- | --- |
| clones / views | 10–25% | README does not convince — the install path is unclear |
| stars / views | 1–4% | Wrong audience, or no social proof in the README |
| issues / clones | 1–3% | People install, it works, they leave — no reason to stay |
| external PRs / stars | 1–5% | No good-first-issue funnel, CONTRIBUTING too heavy |
| returning views / uniques | >1.3 | Nobody comes back — no changelog cadence |

## Channel attribution

Every launch link gets a UTM parameter, every README badge links through the repo only.
For the referrers endpoint, the source names are enough to see which channel converted.

Kill rule: a channel that sends >200 views and <2% clone rate gets one retry with different
copy, then it is dead. Stop posting there.

## Monthly review, 4 questions

1. Which channel sent the most clones, not the most views?
2. Which issue got the most 👍? That is the next release.
3. How many issues closed vs opened? A project that only accrues issues reads as abandoned.
4. What did the last release change for a user who never reads the changelog?
