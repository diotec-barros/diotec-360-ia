"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Knowledge Harvesting API - Task 7.1.3

Receives training seeds from VS Code extensions worldwide,
distills them, and stores in the global Knowledge Lattice.

"The Collective Intelligence of the Empire"
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from diotec360.ai.knowledge_store import KnowledgeStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

# Initialize knowledge store
knowledge_store = KnowledgeStore()


class TrainingSeed(BaseModel):
    """Training seed from VS Code extension"""
    prompt: str
    writerOutput: str
    criticReview: str
    finalCode: str
    judgeVerdict: str
    z3Proof: Optional[str] = None
    writerProvider: str
    writerModel: str
    criticProvider: str
    criticModel: str
    category: str
    language: str
    complexity: str


@router.post("/harvest")
async def harvest_knowledge(
    seed: TrainingSeed,
    x_sovereign_key: Optional[str] = Header(None)
):
    """
    Harvest a proven code pattern from a VS Code extension
    
    This endpoint receives training seeds from extensions worldwide,
    sanitizes them, and adds them to the global knowledge base.
    
    Returns Merkle root for integrity verification.
    """
    try:
        # Convert to dict
        seed_dict = seed.dict()
        
        # Distill (sanitize and validate)
        distilled = knowledge_store.distill(seed_dict)
        
        if not distilled:
            raise HTTPException(
                status_code=400,
                detail="Seed failed quality validation"
            )
        
        # Store in knowledge lattice
        merkle_root = knowledge_store.store(distilled)
        
        logger.info(
            f"✅ Knowledge harvested: {distilled['id']} "
            f"({distilled['category']}/{distilled['language']}) "
            f"from {seed.writerModel} + {seed.criticModel}"
        )
        
        return {
            "success": True,
            "seedId": distilled['id'],
            "merkleRoot": merkle_root,
            "message": "Knowledge harvested successfully"
        }
        
    except Exception as e:
        logger.error(f"Harvest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_knowledge_stats():
    """
    Get statistics about the global knowledge base
    
    Returns counts by category, language, and complexity.
    """
    try:
        stats = knowledge_store.get_stats()
        
        return {
            "success": True,
            "stats": stats,
            "message": f"Knowledge base contains {stats['total']} proven patterns"
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_training_data(
    format: str = "jsonl",
    x_sovereign_key: Optional[str] = Header(None)
):
    """
    Export knowledge base for AI training
    
    Formats:
    - jsonl: One JSON per line (standard)
    - alpaca: Alpaca instruction format
    - sharegpt: ShareGPT conversation format
    
    Requires sovereign key for access control.
    """
    try:
        if not x_sovereign_key:
            raise HTTPException(
                status_code=401,
                detail="Sovereign key required for export"
            )
        
        # Export
        output_path = knowledge_store.export_for_training(format=format)
        
        logger.info(f"✅ Training data exported: {output_path}")
        
        return {
            "success": True,
            "outputPath": output_path,
            "format": format,
            "message": "Training data exported successfully"
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def knowledge_health():
    """Health check for knowledge harvesting system"""
    try:
        stats = knowledge_store.get_stats()
        
        return {
            "status": "healthy",
            "totalPatterns": stats['total'],
            "message": "Knowledge harvesting system operational"
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
