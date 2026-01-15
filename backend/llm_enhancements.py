"""
LLM-Enhanced Recommendations
Uses local Ollama or free Groq API for semantic understanding
"""

import os
from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)

# Try to import LLM clients
OLLAMA_AVAILABLE = False
GROQ_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
    logger.info("✅ Ollama available (local LLM)")
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY')) if os.getenv('GROQ_API_KEY') else None
    if groq_client:
        logger.info("✅ Groq available (cloud LLM)")
except ImportError:
    pass


class LLMEnhancer:
    """Enhance recommendations using LLM semantic understanding"""
    
    def __init__(self):
        self.use_ollama = OLLAMA_AVAILABLE
        self.use_groq = GROQ_AVAILABLE and groq_client
        
        if not self.use_ollama and not self.use_groq:
            logger.warning("No LLM available. Install: ollama or groq")
    
    def _call_llm(self, prompt: str, max_tokens: int = 100) -> Optional[str]:
        """Call LLM (tries Ollama first, then Groq)"""
        try:
            # Try Ollama (local, fast, free!)
            if self.use_ollama:
                response = ollama.generate(
                    model='llama3.2',  # Small, fast model
                    prompt=prompt,
                    options={'num_predict': max_tokens}
                )
                return response['response'].strip()
            
            # Fallback to Groq (cloud, fast, free tier)
            elif self.use_groq:
                response = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",  # Fast, free
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
        
        return None
    
    def semantic_tag_similarity(self, tags_a: List[str], tags_b: List[str]) -> float:
        """
        Calculate semantic similarity between tag sets
        e.g., "synthwave" and "synth-pop" are semantically similar even if not exact match
        """
        if not self.use_ollama and not self.use_groq:
            return 0.0
        
        if not tags_a or not tags_b:
            return 0.0
        
        prompt = f"""Compare these music tags semantically. Rate similarity 0.0-1.0.

Tags A: {', '.join(tags_a[:10])}
Tags B: {', '.join(tags_b[:10])}

Consider: Similar genres, moods, eras, styles.
Respond with ONLY a number between 0.0 and 1.0.

Similarity score:"""
        
        try:
            response = self._call_llm(prompt, max_tokens=10)
            if response:
                # Extract number from response
                import re
                match = re.search(r'0\.\d+|1\.0|0\.0', response)
                if match:
                    return float(match.group())
        except:
            pass
        
        return 0.0
    
    def analyze_user_vibe(self, vibe_description: str) -> List[str]:
        """
        Understand natural language vibe and return relevant tags
        e.g., "sad rainy day music" → ["melancholy", "rainy", "acoustic", "slow"]
        """
        if not self.use_ollama and not self.use_groq:
            return []
        
        prompt = f"""A user wants music for this vibe: "{vibe_description}"

What music tags/genres match this vibe?
List 5-10 relevant tags (genres, moods, styles, eras).

Respond with ONLY a comma-separated list of tags.

Tags:"""
        
        try:
            response = self._call_llm(prompt, max_tokens=50)
            if response:
                # Parse tags
                tags = [tag.strip().lower() for tag in response.split(',')]
                return [tag for tag in tags if tag and len(tag) > 2][:10]
        except:
            pass
        
        return []
    
    def expand_genre_preferences(self, liked_genres: List[str]) -> List[str]:
        """
        Given genres user likes, suggest related genres they might enjoy
        e.g., ["synthwave", "80s pop"] → ["new wave", "synth-pop", "outrun", "vaporwave"]
        """
        if not self.use_ollama and not self.use_groq:
            return liked_genres
        
        if not liked_genres:
            return []
        
        prompt = f"""User likes these music genres: {', '.join(liked_genres[:5])}

Suggest 5-8 similar/related genres they would probably enjoy.

Respond with ONLY a comma-separated list.

Related genres:"""
        
        try:
            response = self._call_llm(prompt, max_tokens=50)
            if response:
                expanded = [g.strip().lower() for g in response.split(',')]
                # Combine original + expanded
                all_genres = list(set(liked_genres + expanded))
                return all_genres[:15]
        except:
            pass
        
        return liked_genres
    
    def explain_match(self, song_a: str, song_b: str, score: float, tags_a: List[str], tags_b: List[str]) -> str:
        """
        Generate human-readable explanation of why songs match
        """
        if not self.use_ollama and not self.use_groq:
            return f"Match score: {score*100:.0f}%"
        
        prompt = f"""Explain why these songs are similar (1 sentence):

Song A: {song_a}
Tags: {', '.join(tags_a[:5])}

Song B: {song_b}
Tags: {', '.join(tags_b[:5])}

Match: {score*100:.0f}%

Explanation:"""
        
        try:
            response = self._call_llm(prompt, max_tokens=50)
            if response:
                return response
        except:
            pass
        
        return f"{score*100:.0f}% match based on genres and community data"


# Global instance
llm_enhancer = LLMEnhancer()












