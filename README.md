# pl-sidebar-updater
Adds a league/results/fixtures/top scorers table (all 3 deep) to the sidebar of your subreddit.

The info is pulled from the BBC Sport website, so it may be subject to change in the future.

To run, it requires [Python 3](https://www.python.org/downloads/). It also requires you to then install [pip](https://pip.pypa.io/en/stable/installing/). With pip installed, you need to install [PRAW](https://github.com/praw-dev/praw) and [OAuth2Util](https://github.com/SmBe19/praw-OAuth2Util), like so

    pip install praw
    pip install praw-OAuth2Util

from a terminal/command prompt. Finally, you need to install [lxml](http://lxml.de/installation.html).

You will also need to make a [script app](https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example) (the **First Steps** section) on reddit so you can approve the script on first use.

In the `oauth.ini` file, you'll need to copy/paste in the `app_key` and `app_secret` values that you got when creating the app.

In that same ini file, you'll need to change the `team`/`display` and `sub` fields to match the target subreddit. The `team` value needs to exactly match that which is used on the BBC website. For example, Leicester would be `leicester-city`, as found in the URL for that team

http://www.bbc.co.uk/sport/football/teams/leicester-city

The `display` value is the one used in the [league table](http://www.bbc.co.uk/sport/football/premier-league/table), which would be *Leicester* in this case. The `sub` value is the name of the subreddit. For Lecicester, it'd be `lcfc`.

In the sidebar of the subreddit, add `[](#stats_start)[](#stats_end)`, where you want the tables to be injected.

With those in place, you can run the script from a terminal/prompt with

    python sidebar_stats.py

On first run your default browser will open with a page asking if you want to allow the script access, which you need to agree to. See the [OAuth guide](https://github.com/SmBe19/praw-OAuth2Util/blob/master/OAuth2Util/README.md) if you run into any issues.

That should give you something like [this](https://dl.dropboxusercontent.com/u/2552046/img/stats.png), which you can style with subreddit CSS.

Ideally you'd automate it with cron/Task Scheduler so it auto-updates the info without needing to do so manually after every fixture.
