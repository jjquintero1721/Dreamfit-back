from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class CoachListItemResponse(BaseModel):
    """Schema para un coach en la lista del sistema"""
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    name: str
    last_name: str = Field(..., alias="lastName")
    has_active_membership: bool = Field(..., alias="hasActiveMembership")
    membership_end_date: Optional[datetime] = Field(None, alias="membershipEndDate")
    plan_id: Optional[str] = Field(None, alias="planId")
    plan_name: Optional[str] = Field(None, alias="planName")
    mentees_count: int = Field(0, alias="menteesCount")

    class Config:
        populate_by_name = True


class CoachDetailResponse(BaseModel):
    """Schema para los detalles completos de un coach"""
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    name: str
    last_name: str = Field(..., alias="lastName")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    has_active_membership: bool = Field(..., alias="hasActiveMembership")
    membership_start_date: Optional[datetime] = Field(None, alias="membershipStartDate")
    membership_end_date: Optional[datetime] = Field(None, alias="membershipEndDate")
    plan_id: Optional[str] = Field(None, alias="planId")
    plan_name: Optional[str] = Field(None, alias="planName")
    daily_meal_plans_count: int = Field(0, alias="dailyMealPlansCount")
    max_daily_meal_plans: Optional[int] = Field(None, alias="maxDailyMealPlans")
    max_mentees: Optional[int] = Field(None, alias="maxMentees")
    mentees_count: int = Field(0, alias="menteesCount")

    class Config:
        populate_by_name = True


class MenteeBasicInfo(BaseModel):
    """Schema para información básica de un mentee"""
    user_id: str = Field(..., alias="userId")
    email: EmailStr
    name: str
    last_name: str = Field(..., alias="lastName")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    class Config:
        populate_by_name = True


class AssignMembershipRequest(BaseModel):
    """Schema para asignar una membresía a un coach"""
    plan_id: str = Field(..., alias="planId")
    duration_months: int = Field(1, ge=1, le=24, alias="durationMonths")

    class Config:
        populate_by_name = True


class UpdateCoachPasswordRequest(BaseModel):
    """Schema para cambiar la contraseña de un coach desde el sistema"""
    new_password: str = Field(..., min_length=8, alias="newPassword")

    class Config:
        populate_by_name = True
