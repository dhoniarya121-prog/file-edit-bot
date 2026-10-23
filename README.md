# Channel Cleaner Bot (Telegram + Render)

Channel ke naye post se faltu text hata kar post ko turant edit kar deta hai.

## Setup
1. @BotFather > `/newbot` > token copy karo.
2. Bot ko apne channel me **Admin** banao, permission: **Post messages + Edit messages of others** (+ Delete messages agar DELETE_IF_EMPTY chahiye).
3. In files ko GitHub repo me push karo (bot.py, requirements.txt, render.yaml).
4. Render > New > Blueprint (ya Web Service) > repo chuno.
5. Environment me `BOT_TOKEN` daalo > Deploy.

## Settings (Environment variables)
| Name | Default | Kaam |
|---|---|---|
| REMOVE_LINKS | true | links + hyperlinks hataye |
| REMOVE_MENTIONS | true | @username hataye |
| REMOVE_HASHTAGS | true | #tags hataye |
| REMOVE_EMOJI_SPAM | false | repeat hone wale emoji/chars kam kare |
| BLOCKED_WORDS | (khali) | comma-separated; ye word wali poori line hat jati hai |
| REMOVE_PHRASES | (khali) | comma-separated; sirf ye phrase hatega |
| ALLOWED_CHANNELS | (khali) | channel IDs (e.g. -100123...); khali = jahan admin ho wahan |
| DELETE_IF_EMPTY | false | cleaning ke baad kuch na bache to post delete |

## Notes
- Render free plan 15 min idle ke baad sleep hota hai; pehle post pe jagne me ~30-50 sec lag sakte hain. Instant chahiye to paid plan lo ya UptimeRobot se service URL ping karo.
- Local test: `BOT_TOKEN=xxx python bot.py` (polling mode).
- Bold/italic formatting preserve hoti hai.
