"""Resume data models"""

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class JobExperience(BaseModel):
    """Job experience"""

    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    date: str = Field(description="Date of employment")
    description: list[str] = Field(
        description="List of projects done / responsibilities during the job"
    )


class Certification(BaseModel):
    """Certification"""

    name: str = Field(description="Name of the certification")
    organization: str = Field(description="Certificate provider")
    date: str = Field(description="Date of certification")


class Education(BaseModel):
    """Education"""

    degree: str = Field(description="Degree or qualification")
    institution: str = Field(description="Name of the institution")
    year: str = Field(description="Year of graduation")
    description: str | None = Field(
        default=None, description="Remarks on education"
    )


class ResumeData(BaseModel):
    """Resume data"""

    name: str | None = Field(default=None, description="Name of the resource")
    title: str | None = Field(
        default=None, description="Title of the resource"
    )
    email: str | None = Field(default=None, description="Email address")
    phone: str | None = Field(default=None, description="Phone number")
    linkedin: str | None = Field(
        default=None, description="LinkedIn profile URL"
    )
    github: str | None = Field(default=None, description="GitHub profile URL")
    website: str | None = Field(default=None, description="Website URL")
    summary: str | None = Field(default=None, description="Executive summary")
    experience: list[JobExperience] | None = Field(
        default=None, description="Job experience"
    )
    education: list[Education] | None = Field(
        default=None, description="Education"
    )
    skills: dict[str, list[str]] | None = Field(
        default=None, description="Skills"
    )
    certifications: list[Certification] | None = Field(
        default=None, description="Certifications"
    )


class ResumeState(MessagesState):
    missing_fields: list[str]
    data: ResumeData
