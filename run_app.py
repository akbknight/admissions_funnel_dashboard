import asyncio
import sys
from streamlit.web import cli as stcli

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "app.py", "--server.headless=true", "--server.port=8503"]
    sys.exit(stcli.main())
