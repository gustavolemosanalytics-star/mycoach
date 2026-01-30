from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any
from app.database import get_db
from app.models.user import User
from app.models.groups import Group, GroupMember, GroupPost
from app.models.workout import Workout
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available groups."""
    groups = db.query(Group).all()
    # Add member count manually or via hybrid property
    return groups

@router.post("/")
async def create_group(
    name: str,
    description: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group and add creator as admin."""
    group = Group(name=name, description=description, owner_id=current_user.id)
    db.add(group)
    db.commit()
    db.refresh(group)
    
    member = GroupMember(group_id=group.id, user_id=current_user.id, role="admin")
    db.add(member)
    db.commit()
    
    return group

@router.post("/{group_id}/join")
async def join_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing group."""
    # Check if already a member
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if existing:
        return {"message": "Already a member"}
        
    member = GroupMember(group_id=group_id, user_id=current_user.id)
    db.add(member)
    db.commit()
    return {"message": "Joined successfully"}

@router.get("/feed")
async def community_feed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest community activities (workouts and posts)."""
    # For now, let's just return latest workouts from everyone (simplified feed)
    workouts = db.query(Workout).order_by(desc(Workout.start_date)).limit(20).all()
    
    feed = []
    for w in workouts:
        feed.append({
            "type": "workout",
            "user": {"name": w.user.name},
            "workout": {
                "id": w.id,
                "name": w.name,
                "sport_type": w.sport_type,
                "distance_km": w.distance_km,
                "duration": w.duration_formatted,
                "highlights": w.highlights
            },
            "created_at": w.start_date
        })
    return feed
