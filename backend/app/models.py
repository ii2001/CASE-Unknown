from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class VisualIdentity(BaseModel):
    approximate_age: int
    hairstyle: str
    hair_color: str
    clothing: str
    distinguishing_non_sensitive_visual_features: str
    portrait_description: str


class Suspect(BaseModel):
    id: str
    name: str
    role: str
    public_profile: str
    personality: str
    actual_alibi: str
    claimed_alibi: str
    private_knowledge: list[str] = []
    known_facts: list[str] = []
    lies: list[str] = []
    visual_identity: VisualIdentity


class Location(BaseModel):
    id: str
    name: str
    description: str
    locked: bool = False
    unlock_clue_id: str | None = None


class Clue(BaseModel):
    id: str
    title: str
    category: str
    location_id: str
    target: str
    critical: bool = False
    red_herring: bool = False
    prerequisites: list[str] = []
    player_description: str
    canonical_significance: str
    visual_asset_id: str | None = None


class ImageBrief(BaseModel):
    id: str
    asset_type: Literal["cover", "suspect", "location", "evidence"]
    subject: str
    environment: str
    visual_description: str
    time_of_day: str = "night"
    mood: str = "tense"
    camera_style: str = "cinematic"
    prohibited_details: list[str] = []
    continuity_notes: str = ""


class CanonicalCase(BaseModel):
    id: str
    title: str
    genre: str
    introduction: str
    incident_summary: str
    culprit_id: str
    motive: str
    crime_time: str
    crime_method: str
    canonical_timeline: list[str]
    solution_summary: str
    suspects: list[Suspect]
    locations: list[Location]
    clues: list[Clue]
    image_briefs: list[ImageBrief]


class InterviewRecord(BaseModel):
    suspect_id: str
    question: str
    answer: str


class PlayerState(BaseModel):
    current_location_id: str
    visited_location_ids: list[str] = []
    discovered_clue_ids: list[str] = []
    unlocked_location_ids: list[str] = []
    interviews: list[InterviewRecord] = []
    narratives: list[str] = []
    completed: bool = False
    won: bool | None = None
    accusation_reasoning: str = ""
    processed_request_ids: list[str] = []


class ActionType(StrEnum):
    MOVE = "MOVE"
    INVESTIGATE = "INVESTIGATE"
    INTERVIEW = "INTERVIEW"
    REVIEW = "REVIEW"
    DEDUCE = "DEDUCE"
    ACCUSE = "ACCUSE"
    HELP = "HELP"


class PlayerAction(BaseModel):
    action_type: ActionType
    target: str = ""
    location: str = ""
    suspect_id: str = ""
    question: str = ""
    query: str = ""
    reasoning: str = ""


class ActionRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    request_id: str = Field(default="", max_length=64)


class AccusationRequest(BaseModel):
    suspect_id: str
    reasoning: str = Field(min_length=3, max_length=2000)


class NewCaseRequest(BaseModel):
    genre: str = "AI laboratory sabotage"
    difficulty: Literal["normal"] = "normal"


class CaseValidationResult(BaseModel):
    valid: bool
    solvable: bool
    contradictions: list[str] = []
    unreachable_clues: list[str] = []
    leakage_risks: list[str] = []
    repair_instructions: list[str] = []
