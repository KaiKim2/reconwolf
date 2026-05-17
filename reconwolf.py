#!/usr/bin/env python3

import requests
import concurrent.futures
from urllib.parse import urljoin
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Fore.RED}
██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗██╗    ██╗ ██████╗ ██╗     ███████╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██║    ██║██╔═══██╗██║     ██╔════╝
██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║██║ █╗ ██║██║   ██║██║     █████╗
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██║███╗██║██║   ██║██║     ██╔══╝
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║╚███╔███╔╝╚██████╔╝███████╗██║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚══╝╚══╝  ╚═════╝ ╚══════╝╚═╝

                Simple Directory & File Discovery Tool
{Style.RESET_ALL}
"""

print(BANNER)

print("Default extensions: .txt, .json, .html, .css, .js")
print("Only scan systems you own or have permission to test.\n")

site = input("Enter target website: ").strip()

if not site.startswith(("http://", "https://")):
    site = "https://" + site

wordlist = input("Enter wordlist path: ").strip()

default_extensions = ["", ".txt", ".json", ".html", ".css", ".js"]

custom = input(
    "Add custom extensions? (example: php, asp, bak) [y/n]: "
).strip().lower()

if custom == "y":
    extra = input("Enter extensions separated by commas: ").strip()

    for ext in extra.split(","):
        ext = ext.strip()

        if ext:
            if not ext.startswith("."):
                ext = "." + ext

            default_extensions.append(ext)

threads = input("Number of threads (default 20): ").strip()

try:
    THREADS = int(threads) if threads else 20
except ValueError:
    THREADS = 20

headers = {
    "User-Agent": "ReconWolf/2.0"
}

session = requests.Session()

found_count = 0


def scan(word):
    global found_count

    word = word.strip()

    for ext in default_extensions:
        target = f"{word}{ext}"
        url = urljoin(site + "/", target)

        try:
            response = session.get(
                url,
                headers=headers,
                timeout=5,
                allow_redirects=False
            )

            status = response.status_code

            if status == 200:
                found_count += 1
                print(
                    f"{Fore.GREEN}[200 FOUND]{Style.RESET_ALL} {url}"
                )

            elif status == 403:
                print(
                    f"{Fore.YELLOW}[403 FORBIDDEN]{Style.RESET_ALL} {url}"
                )

            elif status in [301, 302]:
                redirect = response.headers.get("Location", "Unknown")
                print(
                    f"{Fore.CYAN}[{status} REDIRECT]{Style.RESET_ALL} "
                    f"{url} -> {redirect}"
                )

        except requests.RequestException:
            pass


try:
    with open(wordlist, "r", encoding="utf-8", errors="ignore") as file:
        words = file.readlines()

    print(f"\n{Fore.MAGENTA}[*] Starting scan...{Style.RESET_ALL}\n")

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=THREADS
    ) as executor:
        executor.map(scan, words)

    print(
        f"\n{Fore.GREEN}[✓] Scan completed. "
        f"Found {found_count} valid paths.{Style.RESET_ALL}"
    )

except FileNotFoundError:
    print(f"{Fore.RED}[!] Wordlist file not found.{Style.RESET_ALL}")

except KeyboardInterrupt:
    print(f"\n{Fore.RED}[!] Scan interrupted by user.{Style.RESET_ALL}")
