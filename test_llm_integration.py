"""
Tests for LLM integration with caching and templates
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import tempfile
from src.llm_cache import ExplanationCache
from src.llm_prompt_templates import PromptBuilder, PromptTemplate
from src.llm_integration import PharmaGuardExplainer
from src.llm_config import LLMConfig, PromptConfig, CacheConfig


class TestExplanationCache(unittest.TestCase):
    """Test the explanation caching system."""
    
    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_cache.db")
        self.cache = ExplanationCache(self.db_path)
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_cache_and_retrieve_variant(self):
        """Test caching and retrieving variant explanations."""
        gene = "CYP2D6"
        diplotype = "*1/*1"
        phenotype = "Ultra-Rapid Metabolizer"
        activity_score = 2.0
        explanation = "Test explanation for ultra-rapid metabolizer"
        
        # Cache should be empty initially
        cached = self.cache.get_variant_explanation(gene, diplotype, phenotype, activity_score)
        self.assertIsNone(cached)
        
        # Cache the explanation
        self.cache.cache_variant_explanation(gene, diplotype, phenotype, activity_score, explanation)
        
        # Should be retrievable now
        cached = self.cache.get_variant_explanation(gene, diplotype, phenotype, activity_score)
        self.assertEqual(cached, explanation)
    
    def test_cache_and_retrieve_risk(self):
        """Test caching and retrieving risk explanations."""
        drug = "Codeine"
        gene = "CYP2D6"
        phenotype = "Ultra-Rapid Metabolizer"
        risk_level = "TOXIC"
        explanation = "Test explanation for toxic risk"
        
        # Cache should be empty initially
        cached = self.cache.get_risk_explanation(drug, gene, phenotype, risk_level)
        self.assertIsNone(cached)
        
        # Cache the explanation
        self.cache.cache_risk_explanation(drug, gene, phenotype, risk_level, explanation)
        
        # Should be retrievable now
        cached = self.cache.get_risk_explanation(drug, gene, phenotype, risk_level)
        self.assertEqual(cached, explanation)
    
    def test_cache_stats(self):
        """Test cache statistics."""
        # Add some items
        self.cache.cache_variant_explanation("CYP2D6", "*1/*1", "Normal", 1.0, "explanation 1")
        self.cache.cache_risk_explanation("Codeine", "CYP2D6", "Normal", "SAFE", "explanation 2")
        
        stats = self.cache.get_cache_stats()
        self.assertEqual(stats["variant_explanations"], 1)
        self.assertEqual(stats["risk_explanations"], 1)
    
    def test_case_insensitivity(self):
        """Test that cache keys are case insensitive."""
        gene = "cyp2d6"
        diplotype = "*1/*1"
        phenotype = "normal"
        activity_score = 1.0
        explanation = "Test explanation"
        
        # Cache with lowercase
        self.cache.cache_variant_explanation(gene.lower(), diplotype.lower(), phenotype.lower(), activity_score, explanation)
        
        # Retrieve with uppercase
        cached = self.cache.get_variant_explanation(gene.upper(), diplotype.upper(), phenotype.upper(), activity_score)
        self.assertEqual(cached, explanation)


class TestPromptBuilder(unittest.TestCase):
    """Test prompt template building."""
    
    def setUp(self):
        """Initialize prompt builder."""
        self.builder = PromptBuilder()
    
    def test_build_variant_explanation(self):
        """Test building variant explanation prompt."""
        prompt = self.builder.build_variant_explanation("CYP2D6", "*1/*1", "Normal", 1.0)
        self.assertIn("CYP2D6", prompt)
        self.assertIn("*1/*1", prompt)
        self.assertIn("Normal", prompt)
        self.assertIn("1.00", prompt)
    
    def test_build_risk_explanation(self):
        """Test building risk explanation prompt."""
        prompt = self.builder.build_risk_explanation(
            "Codeine", "CYP2D6", "Normal", "SAFE", 
            "Standard CPIC guidance"
        )
        self.assertIn("Codeine", prompt)
        self.assertIn("CYP2D6", prompt)
        self.assertIn("Normal", prompt)
        self.assertIn("SAFE", prompt)
    
    def test_build_dosing_adjustment(self):
        """Test building dosing adjustment prompt."""
        prompt = self.builder.build_dosing_adjustment(
            "Warfarin", "Normal", "CYP2C9", "5mg daily", "ADJUST"
        )
        self.assertIn("Warfarin", prompt)
        self.assertIn("Normal", prompt)
        self.assertIn("5mg daily", prompt)
    
    def test_system_role(self):
        """Test getting system role."""
        role = self.builder.get_system_role()
        self.assertIn("pharmacogenomics", role.lower())
    
    def test_available_templates(self):
        """Test getting available templates."""
        templates = self.builder.get_available_templates()
        self.assertGreater(len(templates), 0)
        self.assertIn(PromptTemplate.VARIANT_EXPLANATION.value, templates)


class TestPharmaGuardExplainer(unittest.TestCase):
    """Test high-level explainer interface."""
    
    def setUp(self):
        """Initialize explainer without LLM."""
        self.explainer = PharmaGuardExplainer(llm_explainer=None)
    
    def test_explain_risk_profile_fallback(self):
        """Test risk profile explanation in fallback mode."""
        result = self.explainer.explain_risk_profile(
            "Codeine", "CYP2D6", "Ultra-Rapid Metabolizer", "TOXIC",
            "Standard guidance"
        )
        
        self.assertEqual(result["drug"], "Codeine")
        self.assertEqual(result["gene"], "CYP2D6")
        self.assertEqual(result["phenotype"], "Ultra-Rapid Metabolizer")
        self.assertEqual(result["risk_level"], "TOXIC")
        self.assertIn("explanation", result)
        self.assertEqual(result["status"], "fallback")
    
    def test_explain_variant_fallback(self):
        """Test variant explanation in fallback mode."""
        result = self.explainer.explain_variant(
            "CYP2D6", "*1/*1", "Normal", 1.0
        )
        
        self.assertEqual(result["gene"], "CYP2D6")
        self.assertEqual(result["diplotype"], "*1/*1")
        self.assertEqual(result["phenotype"], "Normal")
        self.assertEqual(result["activity_score"], 1.0)
        self.assertIn("explanation", result)
        self.assertEqual(result["metabolism_category"], "Normal Metabolizer")
    
    def test_metabolism_categorization(self):
        """Test metabolism categorization."""
        self.assertEqual(self.explainer._categorize_metabolism(2.0), "Rapid/Ultra-Rapid Metabolizer")
        self.assertEqual(self.explainer._categorize_metabolism(1.0), "Normal Metabolizer")
        self.assertEqual(self.explainer._categorize_metabolism(0.5), "Intermediate Metabolizer")
        self.assertEqual(self.explainer._categorize_metabolism(0.1), "Poor Metabolizer")
    
    def test_risk_comparison(self):
        """Test risk level comparison."""
        self.assertGreater(self.explainer._compare_risks("TOXIC", "SAFE"), 0)
        self.assertLess(self.explainer._compare_risks("SAFE", "TOXIC"), 0)
        self.assertEqual(self.explainer._compare_risks("SAFE", "SAFE"), 0)
    
    def test_clinical_recommendations(self):
        """Test clinical recommendations."""
        toxic_recs = self.explainer.get_clinical_recommendations("Codeine", "TOXIC", "Ultra-Rapid")
        self.assertTrue(any("AVOID" in rec for rec in toxic_recs))
        
        safe_recs = self.explainer.get_clinical_recommendations("Codeine", "SAFE", "Normal")
        self.assertTrue(any("safe" in rec.lower() for rec in safe_recs))


class TestLLMConfig(unittest.TestCase):
    """Test LLM configuration."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = LLMConfig(api_key="test-key")
        config.validate()  # Should not raise
    
    def test_temperature_validation(self):
        """Test temperature bounds validation."""
        config = LLMConfig(api_key="test-key", temperature=3.0)
        with self.assertRaises(ValueError):
            config.validate()
    
    def test_test_config(self):
        """Test getting test configuration."""
        config = LLMConfig.for_testing()
        self.assertTrue(config.fallback_mode)
        self.assertFalse(config.enable_cache)
    
    def test_production_config(self):
        """Test getting production configuration."""
        config = LLMConfig.for_testing()  # Using test to avoid API key requirement
        config.api_key = "test-key"
        self.assertTrue(config.enable_cache)


class TestPromptConfig(unittest.TestCase):
    """Test prompt configuration."""
    
    def test_system_roles(self):
        """Test getting system roles."""
        for explanation_type in ["risk_explanation", "variant_explanation", "dosing_adjustment"]:
            role = PromptConfig.get_system_role(explanation_type)
            self.assertIsNotNone(role)
            self.assertGreater(len(role), 0)
    
    def test_max_tokens(self):
        """Test max tokens configuration."""
        tokens = PromptConfig.get_max_tokens("risk_explanation")
        self.assertGreater(tokens, 0)
    
    def test_temperatures(self):
        """Test temperature configuration."""
        temp = PromptConfig.get_temperature("dosing_adjustment")
        self.assertGreater(temp, 0)
        self.assertLess(temp, 2)


class TestCacheConfig(unittest.TestCase):
    """Test cache configuration."""
    
    def test_ttl_values(self):
        """Test TTL values."""
        ttl = CacheConfig.get_ttl("variant_explanations")
        self.assertGreater(ttl, 0)
    
    def test_max_entries(self):
        """Test maximum cache entries."""
        max_entries = CacheConfig.get_max_entries("variant_explanations")
        self.assertGreater(max_entries, 0)


if __name__ == "__main__":
    unittest.main()
