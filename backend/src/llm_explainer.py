import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm_cache import ExplanationCache
from src.llm_prompt_templates import PromptBuilder

# Load environment variables from .env file
load_dotenv()

class LLMExplainer:
    """
    Integrates with OpenAI or Groq to provide natural language explanations for pharmacogenomic risks.
    Uses pre-built prompt templates and persistent caching for efficiency.
    Automatically detects available API and uses Groq if available, otherwise OpenAI.
    """
    def __init__(self, api_key: str = None, model: str = None, cache_db: str = "llm_cache.db", provider: str = None):
        # Load environment variables
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        
        # Detect provider
        if provider is None:
            # Auto-detect: prefer Groq if available
            if groq_key:
                provider = "groq"
            elif openai_key:
                provider = "openai"
            else:
                raise ValueError("No API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in .env file.")
        
        self.provider = provider.lower()
        self.cache = ExplanationCache(cache_db)
        self.prompt_builder = PromptBuilder()
        
        # Initialize appropriate client
        if self.provider == "groq":
            try:
                from groq import Groq
                self.client = Groq(api_key=groq_key)
                self.model = model if model else "llama-3.3-70b-versatile"  # High-quality versatile model
                self.api_key = groq_key
                print(f"✓ Using Groq API (Model: {self.model})")
            except ImportError:
                raise ImportError("Groq package not installed. Please run: pip install groq")
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
                self.model = model if model else "gpt-3.5-turbo"
                self.api_key = openai_key
                print(f"✓ Using OpenAI API (Model: {self.model})")
            except ImportError:
                raise ImportError("OpenAI package not installed. Please run: pip install openai")
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'groq'.")

    def get_risk_explanation(self, drug: str, gene: str, phenotype: str, risk_level: str, clinical_guidance: str) -> Dict[str, str]:
        """
        Generates a natural language explanation for a drug-gene-phenotype risk.
        Checks cache first to avoid redundant API calls.
        
        Args:
            drug: Drug name
            gene: Gene name
            phenotype: Phenotype (e.g., "Ultra-Rapid Metabolizer")
            risk_level: Risk level (e.g., "TOXIC", "SAFE")
            clinical_guidance: Clinical context/guidance
        
        Returns:
            Dict with "summary" and "status" keys
        """
        # Check cache first
        cached = self.cache.get_risk_explanation(drug, gene, phenotype, risk_level)
        if cached:
            return {"summary": cached, "status": "success", "from_cache": True}
        
        # Build prompt using template
        prompt = self.prompt_builder.build_risk_explanation(drug, gene, phenotype, risk_level, clinical_guidance)
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=250
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=250,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            
            explanation = response.choices[0].message.content.strip()
            
            # Cache the result
            self.cache.cache_risk_explanation(drug, gene, phenotype, risk_level, explanation)
            
            return {"summary": explanation, "status": "success", "from_cache": False}
        except Exception as e:
            return {"summary": f"Could not generate LLM explanation: {e}", "status": "error", "from_cache": False}


    def get_variant_explanation(self, gene: str, diplotype: str, phenotype: str, activity_score: float) -> Dict[str, str]:
        """
        Generates a natural language explanation for a gene's diplotype and resulting phenotype.
        Checks cache first to avoid redundant API calls.
        
        Args:
            gene: Gene name (e.g., "CYP2D6")
            diplotype: Diplotype (e.g., "*1/*1")
            phenotype: Resulting phenotype (e.g., "Ultra-Rapid Metabolizer")
            activity_score: Activity score (e.g., 2.0)
        
        Returns:
            Dict with "summary" and "status" keys
        """
        # Check cache first
        cached = self.cache.get_variant_explanation(gene, diplotype, phenotype, activity_score)
        if cached:
            return {"summary": cached, "status": "success", "from_cache": True}
        
        # Build prompt using template
        prompt = self.prompt_builder.build_variant_explanation(gene, diplotype, phenotype, activity_score)

        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=180
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=180,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            explanation = response.choices[0].message.content.strip()
            
            # Cache the result
            self.cache.cache_variant_explanation(gene, diplotype, phenotype, activity_score, explanation)
            
            return {"summary": explanation, "status": "success", "from_cache": False}
        except Exception as e:
            return {"summary": f"Could not generate LLM variant explanation: {e}", "status": "error", "from_cache": False}

    def get_dosing_adjustment(self, drug: str, phenotype: str, gene: str, 
                             standard_dose: str, risk_level: str) -> Dict[str, str]:
        """
        Generates dosing adjustment recommendations based on pharmacogenomics.
        
        Args:
            drug: Drug name
            phenotype: Patient's phenotype
            gene: Associated gene
            standard_dose: Standard dose information
            risk_level: Risk level
        
        Returns:
            Dict with "summary" and "status" keys
        """
        prompt = self.prompt_builder.build_dosing_adjustment(drug, phenotype, gene, standard_dose, risk_level)
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=220
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=220,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            explanation = response.choices[0].message.content.strip()
            return {"summary": explanation, "status": "success"}
        except Exception as e:
            return {"summary": f"Could not generate dosing adjustment: {e}", "status": "error"}

    def get_drug_summary(self, drug: str, genes: list, phenotypes: list, 
                        overall_risk: str) -> Dict[str, str]:
        """
        Generates a comprehensive drug summary based on patient's genetic profile.
        
        Args:
            drug: Drug name
            genes: List of relevant genes
            phenotypes: List of patient's phenotypes for those genes
            overall_risk: Overall risk level
        
        Returns:
            Dict with "summary" and "status" keys
        """
        prompt = self.prompt_builder.build_drug_summary(drug, genes, phenotypes, overall_risk)
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=250
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=250,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            explanation = response.choices[0].message.content.strip()
            return {"summary": explanation, "status": "success"}
        except Exception as e:
            return {"summary": f"Could not generate drug summary: {e}", "status": "error"}

    def get_phenotype_interpretation(self, gene: str, phenotype: str, 
                                    activity_score: float) -> Dict[str, str]:
        """
        Generates an interpretation of a pharmacogenomic phenotype.
        
        Args:
            gene: Gene name
            phenotype: Phenotype
            activity_score: Activity score
        
        Returns:
            Dict with "summary" and "status" keys
        """
        prompt = self.prompt_builder.build_phenotype_interpretation(gene, phenotype, activity_score)
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=160
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_builder.get_system_role()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=160,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            explanation = response.choices[0].message.content.strip()
            return {"summary": explanation, "status": "success"}
        except Exception as e:
            return {"summary": f"Could not generate phenotype interpretation: {e}", "status": "error"}

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache hit counts
        """
        return self.cache.get_cache_stats()

if __name__ == "__main__":
    # This block will only run if you execute llm_explainer.py directly
    # For testing purposes - replace with your actual API key or set it in .env
    # Ensure OPENAI_API_KEY is set in your .env file or passed as an argument
    try:
        explainer = LLMExplainer()
        
        # Example 1: Drug risk explanation
        drug_exp = explainer.get_risk_explanation(
            "Codeine", "CYP2D6", "Ultra-Rapid Metabolizer", "TOXIC", 
            "Ultra-rapid metabolizers produce excessively high morphine levels due to enhanced CYP2D6 activity, leading to overdose risk."
        )
        print("\n--- Drug Risk Explanation ---")
        print(drug_exp["summary"])

        # Example 2: Variant explanation
        variant_exp = explainer.get_variant_explanation(
            "CYP2D6", "*1/*1", "Ultra-Rapid Metabolizer", 2.0
        )
        print("\n--- Variant Explanation ---")
        print(variant_exp["summary"])

        # Example 3: Cached call for drug risk explanation (should be fast)
        drug_exp_cached = explainer.get_risk_explanation(
            "Codeine", "CYP2D6", "Ultra-Rapid Metabolizer", "TOXIC", 
            "Ultra-rapid metabolizers produce excessively high morphine levels due to enhanced CYP2D6 activity, leading to overdose risk."
        )
        print("\n--- Cached Drug Risk Explanation ---")
        print(drug_exp_cached["summary"])

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
