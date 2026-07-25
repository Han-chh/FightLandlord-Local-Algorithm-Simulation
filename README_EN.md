# Fight the Landlord — Local Algorithm Simulation

A Python simulation of Dou Dizhu rules and round state, focused on dealing, combination recognition, legal-play comparison, and win detection.

[中文说明](README.md)

## Overview

The repository models the game as algorithms rather than a graphical product. It creates a 54-card deck, deals three hands, assigns the landlord, recognizes common combinations, compares a candidate play with the table, and advances play/pass state until a hand is empty.

## Screenshot

![The program after shuffling and dealing, at the landlord-selection prompt](assets/screenshots/fightlandlord-terminal.png)

The screenshot comes directly from a real `server.py` terminal session. The repository does not contain a graphical game interface.

## Capabilities

- 54-card deck and three-player deal
- Single, pair, triple, straight, bomb, rocket, and compound recognition
- Legal-play and rank comparison
- Landlord/farmer roles and round-state management
- Pass reset and winner detection

## Run

```bash
python3 server.py
```

## Current scope

The verified product boundary is a local terminal algorithm simulation. The separate `client.py` network entry is incomplete, so this README does not present the project as a working online game.
