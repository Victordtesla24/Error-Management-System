#!/bin/bash

# Start the autonomous agent with tasks
python3 -c "
import asyncio
import os
from src.error_management.autonomous_agent import autonomous_agent

async def main():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY environment variable not set')
        return
        
    await autonomous_agent.initialize(api_key)
    await autonomous_agent.start()

asyncio.run(main())
" 