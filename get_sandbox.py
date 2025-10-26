import requests
import json
import os

def parse_cookie_string(cookie_string):
    """Parse cookie string into dictionary"""
    cookies = {}
    for cookie in cookie_string.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookies[name] = value
    return cookies

def save_cookies(cookies):
    """Save cookies to file for future use"""
    with open('saved_cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)
    print("✓ Cookies saved to 'saved_cookies.json' for next time!")

def load_saved_cookies():
    """Load cookies from file if exists"""
    if os.path.exists('saved_cookies.json'):
        with open('saved_cookies.json', 'r') as f:
            return json.load(f)
    return None

def get_sandbox_id(session_id, cookies):
    """Get sandboxId from Blackbox AI API"""

    url = "https://build.blackbox.ai/api/create-sandbox-for-session"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.6",
        "content-type": "application/json",
        "referer": "https://build.blackbox.ai/chat-history"
    }

    payload = {
        "sessionId": session_id,
        "ports": [3000],
        "runDevServer": True
    }

    print(f"\nSending request for session: {session_id}")
    print("Please wait...")

    try:
        response = requests.post(url, headers=headers, json=payload, cookies=cookies)

        print(f"Response status: {response.status_code}")

        if response.status_code == 401:
            print("\n❌ ERROR: 401 Unauthorized")
            print("Your cookies have expired. Please enter fresh cookies!")
            return None

        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            print("\n✅ SUCCESS!")
            print("=" * 50)
            print(f"Sandbox ID: {data.get('sandboxId')}")
            print(f"Session ID: {data.get('sessionId')}")
            print(f"Duration: {data.get('duration')}ms")
            print(f"Dev Server Started: {data.get('devServerStarted')}")
            print(f"NPM Install: {data.get('npmInstallCompleted')}")
            print("=" * 50)
            return data.get('sandboxId')
        else:
            print(f"\n❌ Request failed: {data}")
            return None

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

# Main execution
print("=" * 60)
print("Blackbox AI - Get Sandbox ID (Auto-Convert)")
print("=" * 60)
print()

# Check for saved cookies
saved_cookies = load_saved_cookies()
cookies = None

if saved_cookies:
    print("✓ Found saved cookies from previous session!")
    use_saved = input("Use saved cookies? (y/n): ").strip().lower()
    if use_saved == 'y':
        cookies = saved_cookies
        print("✓ Using saved cookies")
    else:
        print("\nPlease paste your fresh cookie string:")

if cookies is None:
    print()
    print("Paste your cookie string here:")
    print("(The long string from Network tab > Cookie header)")
    print()
    cookie_string = input("Cookie: ").strip()

    if not cookie_string:
        print("❌ Error: No cookies provided")
        input("\nPress Enter to exit...")
        exit()

    # Parse cookies
    cookies = parse_cookie_string(cookie_string)
    print(f"\n✓ Parsed {len(cookies)} cookies successfully!")

    # Check for authentication cookies
    has_session_token = '__Secure-next-auth.session-token' in cookies
    has_csrf_token = '__Host-next-auth.csrf-token' in cookies

    if not has_session_token or not has_csrf_token:
        print("\n⚠️  WARNING: Missing authentication cookies!")
        print("Make sure you copied from the Network tab, not JavaScript console!")
        cont = input("\nContinue anyway? (y/n): ").strip().lower()
        if cont != 'y':
            input("\nPress Enter to exit...")
            exit()

    # Ask to save cookies
    save = input("\nSave cookies for next time? (y/n): ").strip().lower()
    if save == 'y':
        save_cookies(cookies)

# Get session ID
print()
session_id = input("Enter Session ID: ").strip()

if session_id:
    sandbox_id = get_sandbox_id(session_id, cookies)
    if sandbox_id:
        print(f"\n💾 Your sandbox ID: {sandbox_id}")

        # Copy to clipboard
        print(f"\n📋 Sandbox ID: {sandbox_id}")
        print("(Copy this for your use)")
else:
    print("❌ Error: No session ID provided")

input("\nPress Enter to exit...")
