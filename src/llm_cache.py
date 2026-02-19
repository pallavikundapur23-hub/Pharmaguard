"""
Database-backed cache for LLM explanations
Provides persistent caching to avoid redundant API calls
"""
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class ExplanationCache:
    """
    SQLite-based persistent cache for LLM explanations.
    Caches variant and drug risk explanations to reduce API calls.
    """
    
    def __init__(self, db_path: str = "llm_cache.db"):
        """Initialize the cache database."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create cache tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS variant_explanations (
                    cache_key TEXT PRIMARY KEY,
                    gene TEXT,
                    diplotype TEXT,
                    phenotype TEXT,
                    activity_score REAL,
                    explanation TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS risk_explanations (
                    cache_key TEXT PRIMARY KEY,
                    drug TEXT,
                    gene TEXT,
                    phenotype TEXT,
                    risk_level TEXT,
                    explanation TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clinical_guidance (
                    cache_key TEXT PRIMARY KEY,
                    drug TEXT,
                    gene TEXT,
                    phenotype TEXT,
                    guidance TEXT,
                    created_at TIMESTAMP
                )
            ''')
            conn.commit()
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a hash key for cache lookup."""
        key_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def get_variant_explanation(self, gene: str, diplotype: str, phenotype: str, activity_score: float) -> Optional[str]:
        """Retrieve cached variant explanation."""
        cache_data = {
            "gene": gene.upper(),
            "diplotype": diplotype.upper(),
            "phenotype": phenotype.lower(),
            "activity_score": round(activity_score, 2)
        }
        cache_key = self._generate_cache_key(cache_data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT explanation FROM variant_explanations
                WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
            ''', (cache_key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def cache_variant_explanation(self, gene: str, diplotype: str, phenotype: str, 
                                 activity_score: float, explanation: str, ttl_days: int = 365):
        """Cache a variant explanation."""
        cache_data = {
            "gene": gene.upper(),
            "diplotype": diplotype.upper(),
            "phenotype": phenotype.lower(),
            "activity_score": round(activity_score, 2)
        }
        cache_key = self._generate_cache_key(cache_data)
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO variant_explanations
                (cache_key, gene, diplotype, phenotype, activity_score, explanation, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
            ''', (cache_key, gene, diplotype, phenotype, activity_score, explanation, expires_at))
            conn.commit()
    
    def get_risk_explanation(self, drug: str, gene: str, phenotype: str, risk_level: str) -> Optional[str]:
        """Retrieve cached risk explanation."""
        cache_data = {
            "drug": drug.lower(),
            "gene": gene.upper(),
            "phenotype": phenotype.lower(),
            "risk_level": risk_level.lower()
        }
        cache_key = self._generate_cache_key(cache_data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT explanation FROM risk_explanations
                WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
            ''', (cache_key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def cache_risk_explanation(self, drug: str, gene: str, phenotype: str, 
                              risk_level: str, explanation: str, ttl_days: int = 365):
        """Cache a risk explanation."""
        cache_data = {
            "drug": drug.lower(),
            "gene": gene.upper(),
            "phenotype": phenotype.lower(),
            "risk_level": risk_level.lower()
        }
        cache_key = self._generate_cache_key(cache_data)
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO risk_explanations
                (cache_key, drug, gene, phenotype, risk_level, explanation, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
            ''', (cache_key, drug, gene, phenotype, risk_level, explanation, expires_at))
            conn.commit()
    
    def get_clinical_guidance(self, drug: str, gene: str, phenotype: str) -> Optional[str]:
        """Retrieve cached clinical guidance."""
        cache_data = {
            "drug": drug.lower(),
            "gene": gene.upper(),
            "phenotype": phenotype.lower()
        }
        cache_key = self._generate_cache_key(cache_data)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT guidance FROM clinical_guidance
                WHERE cache_key = ?
            ''', (cache_key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def cache_clinical_guidance(self, drug: str, gene: str, phenotype: str, guidance: str):
        """Cache clinical guidance."""
        cache_data = {
            "drug": drug.lower(),
            "gene": gene.upper(),
            "phenotype": phenotype.lower()
        }
        cache_key = self._generate_cache_key(cache_data)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO clinical_guidance
                (cache_key, drug, gene, phenotype, guidance, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (cache_key, drug, gene, phenotype, guidance))
            conn.commit()
    
    def clear_expired(self):
        """Remove expired cache entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM variant_explanations WHERE expires_at <= datetime("now")')
            conn.execute('DELETE FROM risk_explanations WHERE expires_at <= datetime("now")')
            conn.commit()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            variant_count = conn.execute(
                'SELECT COUNT(*) FROM variant_explanations WHERE expires_at IS NULL OR expires_at > datetime("now")'
            ).fetchone()[0]
            risk_count = conn.execute(
                'SELECT COUNT(*) FROM risk_explanations WHERE expires_at IS NULL OR expires_at > datetime("now")'
            ).fetchone()[0]
            guidance_count = conn.execute(
                'SELECT COUNT(*) FROM clinical_guidance'
            ).fetchone()[0]
        
        return {
            "variant_explanations": variant_count,
            "risk_explanations": risk_count,
            "clinical_guidance": guidance_count
        }
