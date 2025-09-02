"""
Validation tests to ensure the testing infrastructure is properly set up.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSetupValidation:
    """Test class to validate the testing infrastructure setup."""
    
    def test_pytest_is_working(self):
        """Basic test to ensure pytest is functioning."""
        assert True
    
    def test_project_structure_exists(self):
        """Test that required project files exist."""
        project_root = Path(__file__).parent.parent
        
        # Check main project files
        assert (project_root / "mcp_pipe.py").exists()
        assert (project_root / "calculator.py").exists()
        assert (project_root / "requirements.txt").exists()
        assert (project_root / "pyproject.toml").exists()
        
        # Check test structure
        assert (project_root / "tests").exists()
        assert (project_root / "tests" / "__init__.py").exists()
        assert (project_root / "tests" / "conftest.py").exists()
        assert (project_root / "tests" / "unit").exists()
        assert (project_root / "tests" / "integration").exists()
    
    def test_imports_work(self):
        """Test that main project modules can be imported."""
        try:
            import mcp_pipe
            import calculator
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import project modules: {e}")
    
    def test_fixtures_are_available(self, temp_dir, mock_env_vars):
        """Test that custom fixtures are working."""
        assert temp_dir.exists()
        assert isinstance(mock_env_vars, dict)
        assert "MCP_ENDPOINT" in mock_env_vars
    
    @pytest.mark.unit
    def test_unit_marker_works(self):
        """Test that the unit marker is working."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker_works(self):
        """Test that the integration marker is working.""" 
        assert True
    
    @pytest.mark.slow
    def test_slow_marker_works(self):
        """Test that the slow marker is working."""
        assert True
    
    def test_coverage_configuration(self):
        """Test that coverage is configured properly."""
        # This test mainly validates that the configuration exists
        # Actual coverage will be tested when running with --cov
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        assert "[tool.coverage.run]" in content
        assert "[tool.coverage.report]" in content
        assert "fail_under = 80" in content
    
    def test_environment_setup(self, mock_env_vars, mock_config_file):
        """Test environment and configuration setup."""
        assert mock_env_vars["MCP_ENDPOINT"] == "ws://localhost:8765"
        assert mock_config_file.exists()
        
        # Test config file content
        import json
        with open(mock_config_file) as f:
            config = json.load(f)
        
        assert "mcpServers" in config
        assert "test-server" in config["mcpServers"]