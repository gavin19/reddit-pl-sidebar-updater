#!/usr/bin/python3
import praw
import os
import sys
import html.parser
from time import sleep
from datetime import datetime as time
import lxml.html
from lxml.cssselect import CSSSelector as Css
import requests
import configparser
import OAuth2Util


class SidebarStats:
    """Master class."""

    # Change to cwd
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Config
    cp = configparser.ConfigParser()
    cp.read('oauth.ini')
    TEAM = cp['sidebar']['team']
    TEAMD = cp['sidebar']['display']
    SUB = cp['sidebar']['sub']
    update = ''
    ua = 'Sidebar updater for /r/' + SUB
    r = praw.Reddit(user_agent=ua)
    o = OAuth2Util.OAuth2Util(r, server_mode=True)

    def login(self):
        try:
            self.o.refresh()
            self.fetch_stats()
        except:
            raise

    def fetch_stats(self):
        """Fetch stats."""
        team = 'http://www.bbc.co.uk/sport/football/teams/' + self.TEAM
        with requests.Session() as s:
            pos = s.get(team + '/table')
            sleep(1)
            res = s.get(team + '/results')
            sleep(1)
            fixt = s.get(team + '/fixtures')
            sleep(1)
            top = requests.get(team + '/top-scorers')
            if [i for i in [pos, res, fixt, top] if i.status_code == 200]:
                self.parse_stats(pos, res, fixt, top)
            else:
                pass

    def parse_stats(self, pos, res, fixt, top):
        """Parse stats."""
        self.get_position(pos)
        self.get_results(res)
        self.get_fixtures(fixt)
        self.get_top_scorers(top)
        self.update_sidebar()

    def get_position(self, pos):
        """Get table position."""
        table = lxml.html.fromstring(pos.text)

        # Establish if the team is top or bottom of the league
        tab_top = Css('[id] + .league-table tr:nth-of-type(1) .team-name a')
        tab_bottom = Css('[id] + .league-table tr:nth-of-type(20) .team-name a')
        top = tab_top(table)[0].text == self.TEAMD
        bottom = tab_bottom(table)[0].text == self.TEAMD

        # Otherwise establish what position they're in
        place = Css('[id*="' + self.TEAM + '"] .position .position-number')
        place = int(place(table)[0].text)

        # Get surrounding teams based on position
        base_sel = '[id] + .league-table tr:nth-of-type('
        first = base_sel + str((place - 1)) + ') '
        main = base_sel + str(place) + ') '
        second = base_sel + str((place + 1)) + ') '

        if top:
            main = '[id] + .league-table tr:nth-of-type(1) '
            first = '[id] + .league-table tr:nth-of-type(2) '
            second = '[id] + .league-table tr:nth-of-type(3) '
        if bottom:
            second = '[id] + .league-table tr:nth-of-type(18) '
            first = '[id] + .league-table tr:nth-of-type(19) '
            main = '[id] + .league-table tr:nth-of-type(20) '

        def get_row(row):
            rank = table.cssselect(row + '.position-number')[0].text
            team = table.cssselect(row + '.team-name a')[0].text
            pld = table.cssselect(row + '.played')[0].text
            gd = table.cssselect(row + '.goal-difference')[0].text
            pts = table.cssselect(row + '.points')[0].text
            return [rank, team, pld, gd, pts]

        if top:
            self.make_position_table([get_row(main), get_row(first), get_row(second)], focus='####')
        elif bottom:
            self.make_position_table([get_row(second), get_row(first), get_row(main)])
        elif not top and not bottom:
            self.make_position_table([get_row(first), get_row(main), get_row(second)], focus='######')
        else:
            pass

    def make_position_table(self, places, focus='#####'):
        """Make league table."""
        title = focus + 'League table\n'
        th = 'Pos|Team|Pld|GD|Pts\n:-:|:-:|:-:|:-:|:-:\n'
        tr = '{0}|{1}|{2}|{3}|{4}\n'
        content = title + th

        for p in places:
            content += tr.format(p[0], p[1], p[2], p[3], p[4])

        self.update += content

    def get_results(self, res):
        """Get results."""
        table = lxml.html.fromstring(res.text)

        first = '.table-header:first-child + * tbody tr:nth-child(1) '
        second = '.table-header:first-child + * tbody tr:nth-child(2) '
        third = '.table-header:first-child + * tbody tr:nth-child(3) '
        first_place = table.cssselect(first)
        second_place = table.cssselect(second)
        third_place = table.cssselect(third)

        def get_row(row):
            home = table.cssselect(row + '.team-home a')[0].text
            away = table.cssselect(row + '.team-away a')[0].text
            date = table.cssselect(row + '.match-date')[0].text.strip()
            score = table.cssselect(row + '.score abbr')[0].text.strip()
            comp = table.cssselect(row + '.match-competition')[0]
            compinfo = table.cssselect(row + '.match-competition .round-info')
            if compinfo:
                comp = comp + compinfo[0].text
            return [home, away, date, score, comp]

        if third_place:
            self.make_results_table([get_row(first), get_row(second), get_row(third)])
        elif second_place:
            self.make_results_table([get_row(first), get_row(second)])
        elif first_place:
            self.make_results_table([get_row(first)])
        else:
            pass

    def make_results_table(self, places):
        """Make results table."""
        title = '#####Results\n'
        th = 'Home|Away|Date|Score|Comp\n:-:|:-:|:-:|:-:|:-:\n'
        tr = '{0}|{1}|{2}|{3}|{4}\n'
        content = title + th

        for p in places:
            content += tr.format(p[0], p[1], p[2], p[3], p[4])

        self.update += content

    def get_fixtures(self, fixt):
        """Get fixtures."""
        table = lxml.html.fromstring(fixt.text)

        first = 'table:first-of-type [id*="match-row"]:nth-child(1) '
        second = 'table:first-of-type [id*="match-row"]:nth-child(2) '
        third = 'table:first-of-type [id*="match-row"]:nth-child(3) '
        first_place = table.cssselect(first)
        second_place = table.cssselect(second)
        third_place = table.cssselect(third)

        def get_row(row):
            home = table.cssselect(row + '.team-home a')[0].text
            away = table.cssselect(row + '.team-away a')[0].text
            date = table.cssselect(row + '.match-date')[0].text.strip()
            time = table.cssselect(row + '.kickoff')[0].text
            comp = table.cssselect(row + '.match-competition')[0]
            compinfo = table.cssselect(row + '.match-competition .round-info')
            if compinfo:
                comp = comp + compinfo[0].text
            when = date + time
            return [home, away, when.strip(), comp]

        if third_place:
            self.make_fixtures_table([get_row(first), get_row(second), get_row(third)])
        elif second_place:
            self.make_fixtures_table([get_row(first), get_row(second)])
        elif first_place:
            self.make_fixtures_table([get_row(first)])
        else:
            pass

    def make_fixtures_table(self, places):
        """Make fixtures table."""
        title = '#####Fixtures\n'
        th = 'Home|Away|Date|Comp\n:-:|:-:|:-:|:-:\n'
        tr = '{0}|{1}|{2}|{3}\n'
        content = title + th

        for p in places:
            content += tr.format(p[0], p[1], p[2], p[3])

        self.update += content

    def get_top_scorers(self, top):
        """Get top scorers."""
        table = lxml.html.fromstring(top.text)

        first = '.top-scorers-body .rank-1 '
        second = '.top-scorers-body .rank-2 '
        third = '.top-scorers-body .rank-3 '
        first_place = table.cssselect(first)
        second_place = table.cssselect(second)
        third_place = table.cssselect(third)

        def get_row(row):
            name = table.cssselect(row + '.player-name')[0].text.strip()
            fa = table.cssselect(row + '.player-name+*')[0].text.strip()
            lg = table.cssselect(row + '.player-name+*+*')[0].text.strip()
            lc = table.cssselect(row + '.player-name+*+*+*')[0].text.strip()
            tot = table.cssselect(row + '.goal-count')[0].text.strip()
            return [name, lg, fa, lc, tot]

        if third_place:
            self.make_top_scorers_table([get_row(first), get_row(second), get_row(third)])
        elif second_place:
            self.make_top_scorers_table([get_row(first), get_row(second)])
        elif first_place:
            self.make_top_scorers_table([get_row(first)])
        else:
            pass

    def make_top_scorers_table(self, places):
        """Make scorers table."""
        title = '#####Top scorers\n'
        th = 'Name|League|FA|Lge Cup|Total\n:-:|:-:|:-:|:-:|:-:\n'
        tr = '{0}|{1}|{2}|{3}|{4}\n'
        content = title + th

        for p in places:
            content += tr.format(p[0], p[1], p[2], p[3], p[4])

        self.update += '\n' + content + '\n'

    def update_sidebar(self):
        """Update sidebar."""
        start = '[](#stats_start)'
        end = '[](#stats_end)'
        target_sub = self.r.get_subreddit(self.SUB)
        desc = target_sub.get_settings()['description']
        desc = html.parser.HTMLParser().unescape(desc)
        before = desc.split(start)
        after = desc.split(end)
        desc = before[0] + start + '\n' + self.update + end + after[1]
        target_sub.update_settings(description=desc)
        sys.exit()

SidebarStats().login()
