from typing import List
from fastapi import APIRouter
from src.deterministic.source_registry import source_registry, LegalSourceEntry
from src.deterministic.rules_engine import deterministic_rules_engine
from src.domain.compliance import RulePack

router = APIRouter(prefix="/api/rules", tags=["Rules Engine"])

@router.get("/sources", response_model=List[LegalSourceEntry])
async def list_legal_sources():
    return source_registry.get_all_sources()

@router.get("/rulepacks", response_model=List[RulePack])
async def list_rulepacks():
    return [deterministic_rules_engine.create_default_popia_rulepack()]
