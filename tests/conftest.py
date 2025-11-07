"""
Shared pytest fixtures for the MCP Pipe testing suite.
"""

import pytest
import tempfile
import os
import json
import asyncio
from unittest.mock import Mock, MagicMock
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture  
def mock_config_file(temp_dir):
    """Create a mock MCP configuration file."""
    config = {
        "mcpServers": {
            "test-server": {
                "command": "python",
                "args": ["test_server.py"],
                "type": "stdio",
                "env": {
                    "TEST_VAR": "test_value"
                }
            },
            "disabled-server": {
                "command": "python",
                "args": ["disabled_server.py"], 
                "disabled": True
            },
            "http-server": {
                "type": "http",
                "url": "http://localhost:8080/api",
                "headers": {
                    "Authorization": "Bearer test-token"
                }
            }
        }
    }
    config_file = temp_dir / "mcp_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    test_env = {
        'MCP_ENDPOINT': 'ws://localhost:8765',
        'MCP_CONFIG': '/path/to/test/config.json',
        'TEST_VAR': 'test_value'
    }
    os.environ.update(test_env)
    yield test_env
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    ws = MagicMock()
    ws.recv = Mock(return_value=asyncio.Future())
    ws.recv.return_value.set_result('{"test": "message"}')
    ws.send = Mock(return_value=asyncio.Future())
    ws.send.return_value.set_result(None)
    return ws


@pytest.fixture
def mock_process():
    """Mock subprocess for server process."""
    process = MagicMock()
    process.stdin = MagicMock()
    process.stdout = MagicMock()
    process.stderr = MagicMock()
    process.stdin.write = Mock()
    process.stdin.flush = Mock()
    process.stdin.close = Mock()
    process.stdout.readline = Mock(return_value="test output\n")
    process.stderr.readline = Mock(return_value="test error\n")
    process.terminate = Mock()
    process.wait = Mock()
    process.kill = Mock()
    return process


@pytest.fixture
def sample_server_script(temp_dir):
    """Create a sample server script for testing."""
    script_content = '''#!/usr/bin/env python3
import sys
import json

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            data = json.loads(line.strip())
            response = {"id": data.get("id"), "result": "test response"}
            print(json.dumps(response))
            sys.stdout.flush()
        except (json.JSONDecodeError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
'''
    script_path = temp_dir / "test_server.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)
    return script_path


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = MagicMock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def calculator_test_cases():
    """Test cases for calculator functionality."""
    return [
        {"expression": "2 + 2", "expected": 4},
        {"expression": "10 * 5", "expected": 50},
        {"expression": "math.sqrt(16)", "expected": 4.0},
        {"expression": "math.pi", "expected": 3.141592653589793},
        {"expression": "2 ** 3", "expected": 8},
        {"expression": "(5 + 3) / 2", "expected": 4.0},
    ]


@pytest.fixture
def invalid_calculator_expressions():
    """Invalid expressions for calculator testing."""
    return [
        "import os",  # Should not allow imports
        "open('/etc/passwd')",  # Should not allow file operations
        "__import__('os')",  # Should not allow dynamic imports
        "eval('2+2')",  # Should not allow nested eval
    ]