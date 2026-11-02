# League-Website

A website that recommends a League of Legends build for your specific champion based on the enemy champions instead of U.GG's one build for every champ.

## Problem

U.GG, the main builds website that everyone uses, only shows the most common build for your champion, not one that is tailored towards your specific matchup. Some items become obsolete when going into certain team comps or other items become vastly better and U.GG doesn't reflect that. My website will return a more matchup-focused set of items to build.

## How it works

The user will enter their champion as well as the enemies along with their KDA. It will then

- Fetch the current champion's stats from Riot Data Dragon
- Builds a threat profile of the enemy team based on damage type, burst/tank, and weighted so fed enemies matter more
- Builds a threat profile of your lane matchup based on damage type, who is more ahead, attack range, and burst/tank
- Ranks Legendary Items against both profiles and splits into paths based on who ends up being more fed later on

## Tech Stack

Languages
- Python3, HTML

Libraries
- FastAPI
- uvicorn
- Jinja2

External Tools
- Riot Data Dragon
- VS Code

## Roadmap

Planned Features

- Lane Matchup and Team Matchup combined
- Own damage type consideration
- Build order
- Anti CC/Healing items
- Match Auto-fill

## Author

[Evan Cai](https://github.com/evan-cai7)
