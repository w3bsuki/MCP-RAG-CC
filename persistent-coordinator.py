#!/usr/bin/env python3
"""
Persistent MCP Coordinator - Keeps running and handles agent connections
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_coordinator.server import mcp, logger

async def main():
    """Run the MCP coordinator with stdio transport"""
    logger.info("Starting Persistent MCP Coordinator...")
    
    try:
        # The coordinator uses stdio transport
        # This will handle incoming connections from Claude agents
        async with mcp.run() as (read_stream, write_stream):
            logger.info("MCP Coordinator is ready for connections")
            
            # Initialize the server
            await mcp.run_server(read_stream, write_stream)
            
    except Exception as e:
        logger.error(f"Coordinator error: {e}")
        raise

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Coordinator stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)