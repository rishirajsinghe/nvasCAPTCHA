from typing import Optional, Union, Dict, Any
from pydantic import BaseModel, Field, model_validator

class ScreenResolution(BaseModel):
    width: int = Field(..., ge=0)
    height: int = Field(..., ge=0)
    
    @model_validator(mode='before')
    @classmethod
    def parse_string(cls, v: Any) -> Any:
        if isinstance(v, str):
            parts = v.lower().split("x")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return {"width": int(parts[0]), "height": int(parts[1])}
        return v

class EnvironmentFeatures(BaseModel):
    userAgent: str
    screenResolution: ScreenResolution
    touchSupport: bool
    language: str
    platform: str
    hardwareConcurrency: Optional[int] = Field(None, ge=1)
    doNotTrack: bool
    timeZoneOffset: int = Field(alias="timezoneOffset", default_factory=lambda: 0)

    @model_validator(mode='before')
    @classmethod
    def handle_timezone_case(cls, values: dict) -> dict:
        if "timeZoneOffset" in values and "timezoneOffset" not in values:
            values["timezoneOffset"] = values["timeZoneOffset"]
        return values

class BehaviorFeatures(BaseModel):
    # Ge=0 prevents negative values, which are physically impossible for these metrics
    avgMouseSpeed: float = Field(0.0, ge=0.0)
    # Acceleration could theoretically be negative, but our aggregator uses abs() or we just accept all floats for acceleration?
    # Actually, acceleration as a magnitude or vector difference could be negative if slowing down. Let's not restrict it.
    avgMouseAcceleration: float = 0.0
    avgMouseAngleChange: float = Field(0.0, ge=0.0)
    clickCount: int = Field(0, ge=0)
    avgClickInterval: float = Field(0.0, ge=0.0)
    mouseDistance: float = Field(0.0, ge=0.0)
    mouseJitter: int = Field(0, ge=0)
    xMovementVariance: float = Field(0.0, ge=0.0)
    yMovementVariance: float = Field(0.0, ge=0.0)

    keyPressCount: int = Field(0, ge=0)
    avgKeyHoldDuration: float = Field(0.0, ge=0.0)
    avgKeystrokeInterval: float = Field(0.0, ge=0.0)
    typingRate: float = Field(0.0, ge=0.0)
    backspaceCount: int = Field(0, ge=0)
    repeatedKeyCount: int = Field(0, ge=0)
    keyHoldStdDev: float = Field(0.0, ge=0.0)

    scrollEventCount: int = Field(0, ge=0)
    totalScrollDistance: float = Field(0.0, ge=0.0)
    avgScrollSpeed: float = Field(0.0, ge=0.0)
    scrollDirectionChanges: int = Field(0, ge=0)

    pageTime: float = Field(0.0, ge=0.0)
    fieldInteractionCount: int = Field(0, ge=0)
    avgFieldInteractionInterval: float = Field(0.0, ge=0.0)

class VerifyRequest(BaseModel):
    environment: EnvironmentFeatures
    behavior: BehaviorFeatures
    timestamp: Optional[int] = None
    label: Optional[str] = None
    source: Optional[str] = None

class VerifyResponse(BaseModel):
    success: bool
    riskScore: float
    action: str
    reason: Optional[str] = None
    session_id: Optional[str] = None
    modelVersion: Optional[str] = None
