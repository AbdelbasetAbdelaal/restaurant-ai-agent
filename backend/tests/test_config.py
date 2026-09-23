from app.core.config import Settings


def test_default_config():
    """Verify default configuration values."""
    settings = Settings()
    assert settings.APP_NAME == "Restaurant AI Agent"
    assert isinstance(settings.DEBUG, bool)
    assert "postgresql" in settings.DATABASE_URL
    assert "redis" in settings.REDIS_URL
    assert settings.SECRET_KEY != ""
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) >= 1


def test_cors_origins_parsing_comma_separated():
    """Verify CORS origins string parsing into list."""
    s = Settings(CORS_ORIGINS="http://localhost:3000,http://example.com")
    assert s.CORS_ORIGINS == ["http://localhost:3000", "http://example.com"]


def test_cors_origins_parsing_json_string():
    """Verify CORS origins JSON array string parsing."""
    s = Settings(CORS_ORIGINS='["http://localhost:3000", "https://app.restaurant.com"]')
    assert s.CORS_ORIGINS == ["http://localhost:3000", "https://app.restaurant.com"]


def test_environment_helpers():
    """Verify environment helper properties."""
    prod_settings = Settings(APP_ENV="production")
    assert prod_settings.is_production is True
    assert prod_settings.is_testing is False

    test_settings = Settings(APP_ENV="test")
    assert test_settings.is_testing is True
    assert test_settings.is_production is False
