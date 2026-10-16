#!/usr/bin/env python3
"""Download server jars, verify official hashes, and write first-run config."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCH = Path(__file__).resolve().parent
SERVER = ROOT / "server-26.2"
PLUGINS = SERVER / "plugins"
USER_AGENT = "DrOverthrow-eaglercraft-survival/1.0 (server setup)"


def request_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def java_major() -> int | None:
    try:
        output = subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    match = re.search(r'version\s+"?(\d+)', output)
    if not match:
        match = re.search(r"openjdk\s+(\d+)", output, re.IGNORECASE)
    return int(match.group(1)) if match else None


def download(url: str, destination: Path, sha256: str | None = None,
             sha1: str | None = None) -> None:
    if destination.exists():
        print(f"Already downloaded: {destination.name}")
        return
    print(f"Downloading {destination.name} ...")
    data = request_bytes(url)
    if sha256 and hashlib.sha256(data).hexdigest().lower() != sha256.lower():
        raise RuntimeError(f"SHA-256 verification failed for {destination.name}")
    if sha1 and hashlib.sha1(data).hexdigest().lower() != sha1.lower():
        raise RuntimeError(f"SHA-1 verification failed for {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_bytes(data)
    temporary.replace(destination)
    print(f"Saved {destination.relative_to(ROOT)}")


def get_modrinth_plugin(project: str) -> tuple[str, str, str]:
    """Return (version, direct file URL, sha1) for a Paper plugin supporting 26.2."""
    query = urllib.parse.urlencode({
        "game_versions": json.dumps(["26.2"]),
        "loaders": json.dumps(["paper"]),
    })
    url = f"https://api.modrinth.com/v2/project/{project}/version?{query}"
    versions = json.loads(request_bytes(url).decode("utf-8"))
    for version in versions:
        if version.get("version_type") != "release":
            continue
        files = version.get("files", [])
        chosen = next((f for f in files if f.get("primary")), None)
        if chosen is None:
            chosen = next((f for f in files if f.get("filename", "").endswith(".jar")), None)
        if chosen:
            sha1 = chosen.get("hashes", {}).get("sha1")
            if not sha1:
                continue
            return version.get("version_number", "release"), chosen["url"], sha1
    raise RuntimeError(
        f"Modrinth did not return a Paper release for Minecraft 26.2 ({project}). "
        "Try again later or check the plugin's release page."
    )


def write_first_run_files(port: int) -> None:
    SERVER.mkdir(parents=True, exist_ok=True)
    PLUGINS.mkdir(parents=True, exist_ok=True)
    properties = SERVER / "server.properties"
    if not properties.exists():
        properties.write_text(
            "# Eaglercraft Survival SMP\n"
            "motd=Eaglercraft Survival SMP\n"
            f"server-port={port}\n"
            "online-mode=false\n"
            "gamemode=survival\n"
            "difficulty=normal\n"
            "max-players=20\n"
            "view-distance=6\n"
            "simulation-distance=4\n"
            "spawn-protection=0\n"
            "enable-query=false\n"
            "enable-rcon=false\n"
            "white-list=false\n"
            "pvp=true\n",
            encoding="utf-8",
        )
    eula = SERVER / "eula.txt"
    if not eula.exists():
        print("\nBefore accepting, read the Minecraft EULA: https://aka.ms/MinecraftEULA")
        answer = input("Do you agree to the Minecraft EULA? Type y to accept: ").strip().lower()
        if answer not in ("y", "yes"):
            raise RuntimeError("EULA not accepted. Setup stopped before writing eula=true.")
        eula.write_text(
            "# Accepted by the server owner during setup. https://aka.ms/MinecraftEULA\n"
            "eula=true\n",
            encoding="utf-8",
        )


def main() -> int:
    manifest = json.loads((LAUNCH / "manifest.json").read_text(encoding="utf-8"))
    found_java = java_major()
    required_java = manifest["javaMinimumMajor"]
    if found_java is None:
        print("Java was not found. Open this repo in its configured Codespace and try again.")
        return 1
    if found_java < required_java:
        print(f"Java {found_java} found; Paper 26.2 requires Java {required_java}+.")
        return 1
    print(f"Java {found_java} detected.")

    SERVER.mkdir(parents=True, exist_ok=True)
    PLUGINS.mkdir(parents=True, exist_ok=True)
    paper = manifest["paper"]
    download(paper["url"], SERVER / paper["fileName"], sha256=paper["sha256"])
    eagler = manifest["eaglerXPaper"]
    download(eagler["url"], PLUGINS / eagler["fileName"], sha256=eagler["sha256"])

    for project in manifest["modrinthProjects"]:
        destination = PLUGINS / (project + ".jar")
        if destination.exists():
            print(f"Already downloaded: {destination.name}")
            continue
        version, url, sha1 = get_modrinth_plugin(project)
        print(f"{project}: selected stable release {version} for Minecraft 26.2")
        download(url, destination, sha1=sha1)

    write_first_run_files(manifest["serverPort"])
    paper_path = SERVER / paper["fileName"]
    if paper_path.name != "paper.jar":
        shutil.copy2(paper_path, SERVER / "paper.jar")

    print("\nSetup complete.")
    print("Start the server with: bash launch/start-server.sh")
    print("After it finishes starting, use the Codespaces Ports tab to share port 25565.")
    print("\nSecurity: offline mode does not verify ownership of usernames.")
    print("Do not grant operator permissions until you have a compatible authentication solution.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
