# Eaglercraft Survival SMP

A beginner-friendly setup for a **Survival** Eaglercraft server. The first target is a Paper **26.2** server with EaglerXPaper for browser WebSocket connections and ViaVersion/ViaBackwards for older protocol clients.

> **Please read:** this repository contains setup automation; it does not keep a server running by itself. GitHub Codespaces is suitable for a temporary test, not reliable 24/7 game hosting. Compatibility across every client build still needs real in-game testing.

## Chromebook: start a temporary test server

1. Open the green **Code** button near the top of this repository.
2. Choose **Codespaces** → **Create codespace on main**. Wait for the browser workspace to finish loading.
3. Open **Terminal → New Terminal** in the Codespaces window.
4. Run:

   ```bash
   python3 launch/setup.py
   ```

   The setup downloads Paper 26.2, EaglerXPaper, ViaVersion and ViaBackwards. It asks you to accept the Minecraft EULA before it writes `eula=true`. Answer `y` only if you agree to the EULA.

   After setup finishes, run:

   ```bash
   bash launch/start-server.sh
   ```

5. Wait for Paper to finish starting and say that the server is ready. **Leave that terminal running.**
6. In Codespaces, open the **Ports** tab at the bottom. Find port **25565**. Set its protocol to **HTTP** because EaglerXPaper accepts ordinary WebSocket (HTTP upgrade) connections on the server port. The outside Codespaces address still uses HTTPS/WSS.
7. Set the port visibility to **Public**. Recheck visibility after changing the protocol, because GitHub may reset a port to private after a protocol change.
8. Use the forwarded hostname shown in the Ports tab. In Eaglercraft, open Multiplayer → Direct Connect and enter:

   ```
   wss://YOUR-CODESPACE-25565.app.github.dev/
   ```

   Replace the example hostname with the actual one shown in your Ports tab. Do not include `https://`.

If it cannot connect, check the terminal for a startup error and confirm port 25565 is Public. Some managed or school accounts restrict Codespaces, public ports, or the compute quota.

## Server settings

- Game mode: Survival
- Difficulty: Normal
- View distance: 6 chunks (lower load)
- Simulation distance: 4 chunks
- Maximum players: 20
- Server port: 25565

The generated server data goes into `server-26.2/`, which is excluded from Git so the world and downloaded server jars are not uploaded to this repository.

## Version compatibility

- **26.2:** the native target for this setup.
- **1.12.2 and other older clients:** ViaVersion and ViaBackwards are installed for protocol translation, and EaglerXPaper provides the Eaglercraft WebSocket layer. This combination is a best-effort starting point, **not a guarantee that every Eaglercraft build from 1.12.2 through 26.2 will work**. Different community clients may behave differently; test with the exact client builds you intend to support.
- Paper 26.2 requires Java 25 or newer. The included Codespaces configuration requests Java 25.

## Important security note

Eaglercraft browser connections generally use offline-mode server authentication. In offline mode, a username alone does **not** prove that the player owns that name. The setup does not grant anyone operator permissions automatically. Do not use `/op` or add operator names until you have installed and verified a compatible authentication solution. Public players can also grief the world, so make backups before experimenting.

## Keeping it online

A Codespace can stop because of idle time, usage limits, or account policies, and the forwarded address is temporary. Treat this as a test server. For a server that should stay online for friends, the next step is moving the same setup to a Minecraft-compatible host or VPS with a persistent disk and secure `wss://` endpoint.

## Useful documentation

- [EaglerXPaper](https://github.com/PlanetDogeCodes/EaglerXPaper)
- [ViaVersion](https://modrinth.com/plugin/viaversion)
- [ViaBackwards](https://modrinth.com/plugin/viabackwards)
- [GitHub Codespaces port forwarding](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace)
- [Minecraft EULA](https://aka.ms/MinecraftEULA)

## Local server commands

After setup, from the repository root:

```bash
bash launch/start-server.sh
```

Stop it with **Ctrl+C** in the terminal running the server.
