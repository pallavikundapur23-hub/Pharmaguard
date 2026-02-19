"""
LLM Configuration and Settings
Configure API, caching, and prompt behavior
"""
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM integration."""
    
    # OpenAI API settings
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    temperature: float = 0.6  # Lower = more deterministic
    max_tokens: int = 250
    
    # Caching settings
    cache_db_path: str = "llm_cache.db"
    cache_ttl_days: int = 365  # Time to live for cached explanations
    enable_cache: bool = True
    
    # API rate limiting
    rate_limit_calls_per_min: int = 60
    
    # Prompt behavior
    use_templates: bool = True  # Use pre-built templates
    fallback_mode: bool = False  # Use fallback when API fails
    
    # Logging
    log_api_calls: bool = False
    log_cache_hits: bool = True
    
    def validate(self):
        """Validate configuration."""
        if not self.api_key and not self.fallback_mode:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or enable fallback mode.")
        
        if not (0 <= self.temperature <= 2):
            raise ValueError("Temperature must be between 0 and 2")
        
        if self.cache_ttl_days < 0:
            raise ValueError("Cache TTL must be non-negative")
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create config from environment variables."""
        config = cls()
        config.validate()
        return config
    
    @classmethod
    def for_production(cls) -> "LLMConfig":
        """Create production-ready config."""
        config = cls.from_env()
        config.temperature = 0.5  # More deterministic
        config.enable_cache = True
        config.fallback_mode = False
        return config
    
    @classmethod
    def for_testing(cls) -> "LLMConfig":
        """Create test config."""
        config = cls(
            api_key="test-key",
            fallback_mode=True,
            enable_cache=False,
            log_api_calls=True
        )
        return config


class PromptConfig:
    """Configuration for LLM prompts."""
    
    # System roles for different explanation types
    SYSTEM_ROLES = {
        "risk_explanation": "You are an expert pharmacogenomics assistant. Provide clear, accurate, and clinically relevant explanations. Avoid jargon where possible.",
        "variant_explanation": "You are a genetics expert specializing in pharmacogenomics. Explain complex genetic information in patient-friendly terms.",
        "dosing_adjustment": "You are a clinical pharmacist expert in pharmacogenomics. Provide safe, evidence-based dosing recommendations.",
        "drug_summary": "You are a pharmacogenomics specialist. Provide comprehensive drug-gene interaction summaries.",
        "phenotype_interpretation": "You are a pharmacogenomics educator. Explain phenotypes and their clinical significance clearly."
    }
    
    # Output formatting constraints
    MAX_TOKENS = {
        "risk_explanation": 250,
        "variant_explanation": 180,
        "dosing_adjustment": 220,
        "drug_summary": 250,
        "phenotype_interpretation": 160
    }
    
    # Temperature settings (lower = more deterministic)
    TEMPERATURES = {
        "risk_explanation": 0.6,
        "variant_explanation": 0.5,
        "dosing_adjustment": 0.4,  # Most deterministic for safety
        "drug_summary": 0.6,
        "phenotype_interpretation": 0.5
    }
    
    @staticmethod
    def get_system_role(explanation_type: str = "risk_explanation") -> str:
        """Get system role for explanation type."""
        return PromptConfig.SYSTEM_ROLES.get(explanation_type, PromptConfig.SYSTEM_ROLES["risk_explanation"])
    
    @staticmethod
    def get_max_tokens(explanation_type: str = "risk_explanation") -> int:
        """Get max tokens for explanation type."""
        return PromptConfig.MAX_TOKENS.get(explanation_type, 250)
    
    @staticmethod
    def get_temperature(explanation_type: str = "risk_explanation") -> float:
        """Get temperature for explanation type."""
        return PromptConfig.TEMPERATURES.get(explanation_type, 0.6)


class CacheConfig:
    """Configuration for caching behavior."""
    
    # Default TTL in days for different explanation types
    TTL_DAYS = {
        "variant_explanations": 365,  # Genetic variants don't change
        "risk_explanations": 180,     # CPIC guidelines may update
        "clinical_guidance": 90       # Clinical guidance updates more frequently
    }
    
    # Cache size management
    MAX_CACHE_ENTRIES = {
        "variant_explanations": 5000,  # ~5000 common variants
        "risk_explanations": 10000,    # ~10000 drug-gene combinations
        "clinical_guidance": 1000      # ~1000 guidance items
    }
    
    @staticmethod
    def get_ttl(cache_type: str) -> int:
        """Get TTL for cache type."""
        return CacheConfig.TTL_DAYS.get(cache_type, 180)
    
    @staticmethod
    def get_max_entries(cache_type: str) -> int:
        """Get max entries for cache type."""
        return CacheConfig.MAX_CACHE_ENTRIES.get(cache_type, 5000)


# Default configuration instance
DEFAULT_CONFIG = LLMConfig.from_env()
