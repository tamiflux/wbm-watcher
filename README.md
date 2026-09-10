# WBM Listing Watcher

Checks the WBM Berlin apartment listings page every 5 minutes and sends you
a Telegram message the moment a new listing appears.

## 1. Create a Telegram bot (2 minutes)

1. In Telegram, open a chat with **@BotFather**.
2. Send `/newbot` and follow the prompts (pick any name/username).
3. BotFather will give you a **bot token** — looks like
   `123456789:AAExampleTokenxxxxxxxxxxxxxxxxxxxxx`. Save it.
4. Start a chat with your new bot (search its username, hit Start) and send
   it any message, e.g. "hi".
5. Get your **chat ID**: open this URL in your browser (replace `<TOKEN>`):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
   You'll see JSON containing `"chat":{"id": 123456789, ...}`. That number
   is your chat ID.

## 2. Create a GitHub repo

1. Go to github.com → New repository (can be private).
2. Upload all the files from this project, keeping the folder structure:
   ```
   your-repo/
   ├── .github/workflows/check-listings.yml
   ├── scripts/check_wbm.py
   ├── requirements.txt
   └── README.md
   ```
   (Easiest: `git init`, `git add .`, `git commit`, then push — or use
   GitHub's "Add file → Upload files" in the web UI, which supports
   drag-and-drop of the whole folder.)

## 3. Add your secrets

In your new repo: **Settings → Secrets and variables → Actions → New
repository secret**. Add two secrets:

- `TELEGRAM_BOT_TOKEN` → the token from step 1
- `TELEGRAM_CHAT_ID` → the chat ID from step 1

## 4. Turn it on

- Go to the **Actions** tab of your repo. GitHub sometimes disables
  scheduled workflows on first push — click "I understand my workflows, go
  ahead and enable them" if you see that banner.
- Click into "Check WBM listings" → **Run workflow** to trigger it manually
  once. This first run just saves a baseline snapshot (so you don't get
  spammed with all 11 current listings at once) — you won't get a Telegram
  message yet, that's expected.
- From then on, it runs automatically every 5 minutes. Any listing that
  appears after the baseline run will trigger an instant Telegram message
  with its title and link.

## Notes / things to know

- GitHub's free tier gives you plenty of Action minutes for a job this
  light (runs in a few seconds, every 5 minutes) — this will comfortably
  fit in the free quota for a personal account.
- 5 minutes is roughly GitHub's practical minimum for scheduled workflows;
  it won't reliably run more often than that, and running much more often
  isn't necessary or polite to WBM's servers.
- If WBM changes their page's HTML structure, the scraping logic in
  `check_wbm.py` (the part matching `/wohnungen-berlin/angebote/details/`)
  may need a small update. If it silently stops finding listings, that's
  the first place to check.
- You can adjust the filters (rooms, area, price) by changing the URL in
  `check_wbm.py` to a filtered WBM search URL, if you want to narrow it
  down to specific criteria.

Good luck with the flat hunt! 🍀
