from pydantic import BaseModel, Field
from typing import List


class SetRecommendation(BaseModel):
    reps: int = Field(..., ge=1, le=50)
    target_rpe: int = Field(..., ge=1, le=10)
    rest_time_seconds: int = Field(..., ge=0, le=600)


class ExerciseRecommendation(BaseModel):
    exercise_id: int
    name: str
    sets: List[SetRecommendation]
    instructions: str = Field(..., max_length=500)


class WorkoutDay(BaseModel):
    day_name: str = Field(..., max_length=100)
    focus_muscle_groups: List[str]
    exercises: List[ExerciseRecommendation]


class WorkoutPlanSchema(BaseModel):
    plan_title: str = Field(..., max_length=255)
    periodization_type: str = Field(..., max_length=50)
    days: List[WorkoutDay]
