# Fight Landlord Game Logic Simulation

## Project Description

This is a local Fight Landlord (Dou Dizhu) game logic algorithm simulation project. The project implements the core logic of the Fight Landlord game, including card creation, shuffling, distribution, player management, and game rule judgment. Through this project, you can simulate the complete process of a Fight Landlord game without actual network connections or user interfaces.

## Key Features

- **Local Simulation**: The project runs locally without network connections, fully simulating Fight Landlord game logic.
- **Algorithm Implementation**: Includes complete Fight Landlord game algorithms, such as card pattern recognition and win/loss determination.
- **Multi-language Support**: The project comes with a Chinese language pack JSON file (lan_ch.json) and supports multi-language extensions.
- **Extensibility**: If network and UI components are integrated, it can become a complete playable Fight Landlord game.

## Installation Requirements

- Python 3.x
- No third-party packages required (all dependencies are Python standard library)

## How to Run

Run the following command from the project root directory:

```bash
python3 server.py
```

## Multi-language Support

The project uses JSON files to store language packs, currently including a Chinese language pack (lan_ch.json). You can support other languages by modifying or adding new JSON files.

## Extensibility

This project is a pure logic simulation. If you want to expand it into a complete game, you can:

- Add network modules for multiplayer online battles
- Integrate graphical user interfaces (GUI)
- Add more language packs