"""
Agent-related API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from app.database import get_db
from app.models.agents import Agent
from app.schemas.agents import AgentCreate, AgentUpdate, AgentResponse, AgentSummary
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[AgentResponse])
async def get_agents(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by agent status"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    department: Optional[str] = Query(None, description="Filter by department"),
    territory: Optional[str] = Query(None, description="Filter by territory"),
    db: Session = Depends(get_db)
):
    """Get paginated agents with optional filters"""
    try:
        query = db.query(Agent)
        
        # Apply filters
        if status:
            query = query.filter(Agent.status == status)
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
        if department:
            query = query.filter(Agent.department == department)
        if territory:
            query = query.filter(Agent.territory == territory)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        agents = query.offset(
            (pagination.page - 1) * pagination.size
        ).limit(pagination.size).all()
        
        return PaginatedResponse(
            items=agents,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agents"
        )

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a specific agent by ID"""
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent"
        )

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent"""
    try:
        # Check if agent ID already exists
        existing = db.query(Agent).filter(Agent.agent_id == agent_data.agent_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with ID {agent_data.agent_id} already exists"
            )
        
        agent = Agent(**agent_data.model_dump())
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Created agent: {agent.agent_id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent"
        )

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str, 
    agent_data: AgentUpdate, 
    db: Session = Depends(get_db)
):
    """Update an agent"""
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        # Update fields
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Updated agent: {agent.agent_id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent"
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent"""
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        db.delete(agent)
        db.commit()
        
        logger.info(f"Deleted agent: {agent_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete agent"
        )

@router.get("/summary/stats", response_model=AgentSummary)
async def get_agent_summary(db: Session = Depends(get_db)):
    """Get agent statistics summary"""
    try:
        total_agents = db.query(func.count(Agent.id)).scalar()
        
        active_agents = db.query(func.count(Agent.id)).filter(
            Agent.status == "active"
        ).scalar()
        
        inactive_agents = db.query(func.count(Agent.id)).filter(
            Agent.status == "inactive"
        ).scalar()
        
        top_performers = db.query(func.count(Agent.id)).filter(
            Agent.is_top_performer == True
        ).scalar()
        
        total_premium_written = db.query(func.sum(Agent.total_premium_written)).scalar() or 0
        total_commission_paid = db.query(func.sum(Agent.total_commission_earned)).scalar() or 0
        
        return AgentSummary(
            total_agents=total_agents,
            active_agents=active_agents,
            inactive_agents=inactive_agents,
            top_performers=top_performers,
            total_premium_written=round(total_premium_written, 2),
            total_commission_paid=round(total_commission_paid, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching agent summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent summary"
        )
