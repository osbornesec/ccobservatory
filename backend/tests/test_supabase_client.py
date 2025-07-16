"""
Test suite for Supabase Client following Canon TDD approach.
Tests written one at a time, with minimal implementation to pass each test.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.database.supabase_client import SupabaseConfig, SupabaseClientManager


class TestSupabaseConfig:
    """Test SupabaseConfig functionality following Canon TDD approach."""
    
    def test_supabase_config_initialization_sets_attributes_from_environment(self):
        """First test: SupabaseConfig initializes attributes from environment variables."""
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
        }):
            config = SupabaseConfig()
            
            assert config.url == 'https://test.supabase.co'
            assert config.key == 'test-key'
            assert config.service_role_key == 'test-service-key'
    
    def test_supabase_config_validate_returns_false_for_missing_url(self):
        """Second test: validate() returns False when SUPABASE_URL is missing."""
        with patch.dict('os.environ', {
            'SUPABASE_KEY': 'test-key'
        }, clear=True):
            config = SupabaseConfig()
            
            with patch('app.database.supabase_client.logger') as mock_logger:
                result = config.validate()
                
                assert result is False
                mock_logger.error.assert_called_once_with("SUPABASE_URL environment variable is required")
    
    def test_supabase_config_validate_returns_false_for_missing_key(self):
        """Third test: validate() returns False when SUPABASE_KEY is missing."""
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co'
        }, clear=True):
            config = SupabaseConfig()
            
            with patch('app.database.supabase_client.logger') as mock_logger:
                result = config.validate()
                
                assert result is False
                mock_logger.error.assert_called_once_with("SUPABASE_KEY environment variable is required")
    
    def test_supabase_config_validate_returns_true_for_valid_config(self):
        """Fourth test: validate() returns True when all required config is present."""
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key'
        }):
            config = SupabaseConfig()
            
            result = config.validate()
            
            assert result is True


class TestSupabaseClientManager:
    """Test SupabaseClientManager functionality following Canon TDD approach."""
    
    def test_supabase_client_manager_initialization(self):
        """Fifth test: SupabaseClientManager initializes with None clients and config."""
        manager = SupabaseClientManager()
        
        assert manager._client is None
        assert manager._service_client is None
        assert isinstance(manager.config, SupabaseConfig)
    
    def test_get_client_raises_error_for_invalid_configuration(self):
        """Sixth test: get_client raises ValueError for invalid configuration."""
        manager = SupabaseClientManager()
        
        # Mock config to be invalid
        with patch.object(manager.config, 'validate', return_value=False):
            with pytest.raises(ValueError, match="Invalid Supabase configuration"):
                manager.get_client()
    
    def test_get_client_creates_and_returns_client_for_valid_config(self):
        """Seventh test: get_client creates and returns client for valid configuration."""
        manager = SupabaseClientManager()
        
        # Mock config to be valid
        with patch.object(manager.config, 'validate', return_value=True):
            with patch('app.database.supabase_client.create_client') as mock_create:
                with patch('app.database.supabase_client.logger') as mock_logger:
                    manager.config.url = 'https://test.supabase.co'
                    manager.config.key = 'test-key'
                    
                    mock_client = MagicMock()
                    mock_create.return_value = mock_client
                    
                    result = manager.get_client()
                    
                    # Verify client was created with correct parameters
                    mock_create.assert_called_once_with('https://test.supabase.co', 'test-key')
                    mock_logger.info.assert_called_once_with("Initializing Supabase client")
                    
                    # Verify client is cached
                    assert manager._client is mock_client
                    assert result is mock_client
    
    def test_get_client_returns_cached_client_on_subsequent_calls(self):
        """Eighth test: get_client returns cached client on subsequent calls."""
        manager = SupabaseClientManager()
        
        # Mock config to be valid
        with patch.object(manager.config, 'validate', return_value=True):
            with patch('app.database.supabase_client.create_client') as mock_create:
                with patch('app.database.supabase_client.logger') as mock_logger:
                    manager.config.url = 'https://test.supabase.co'
                    manager.config.key = 'test-key'
                    
                    mock_client = MagicMock()
                    mock_create.return_value = mock_client
                    
                    # First call
                    result1 = manager.get_client()
                    # Second call
                    result2 = manager.get_client()
                    
                    # Verify create_client was called only once
                    mock_create.assert_called_once()
                    
                    # Verify same client instance is returned
                    assert result1 is result2
                    assert result1 is mock_client