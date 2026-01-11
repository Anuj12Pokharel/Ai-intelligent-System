from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Clause(BaseModel):
    """
    Represents the smallest unit of a legal text (e.g., '(1)', '(a)').
    """
    clause_id: str = Field(description="Unique identifier for the clause within the section")
    content: str = Field(description="The text content of the clause")
    language: Literal["nepali", "english"] = "nepali"

class SubSection(BaseModel):
    """
    Represents a subsection within a section (e.g., Sub-section 1 of Section 3).
    """
    number: str = Field(description="Subsection number")
    content: str = Field(description="Content of the subsection")
    clauses: List[Clause] = Field(default_factory=list)

class Section(BaseModel):
    """
    Represents a specific legal provision or 'Dapha'.
    """
    section_number: str = Field(description="The section number (e.g., '1', '22')")
    title: Optional[str] = Field(None, description="Title of the section if available")
    content: str = Field(description="Main text of the section")
    sub_sections: List[SubSection] = Field(default_factory=list)
    clauses: List[Clause] = Field(default_factory=list, description="Individual clauses within the section")
    page_number: Optional[int] = Field(None, description="Page number in the source PDF")

class Chapter(BaseModel):
    """
    Represents a Chapter or 'Parichhed'.
    """
    chapter_number: str = Field(description="Chapter number")
    title: str = Field(description="Chapter title")
    sections: List[Section] = Field(default_factory=list)

class Part(BaseModel):
    """
    Represents a Part or 'Bhag' (optional high-level grouping).
    """
    part_number: str = Field(description="Part number")
    title: str = Field(description="Part title")
    chapters: List[Chapter] = Field(default_factory=list)

class Act(BaseModel):
    """
    The top-level document representing an Act/Law.
    """
    title: str = Field(description="Full title of the Act")
    act_year: Optional[str] = Field(None, description="Year of enactment")
    source_url: str = Field(description="URL source of the document")
    publication_date: Optional[str] = Field(None, description="Date of publication")
    parts: List[Part] = Field(default_factory=list)
    chapters: List[Chapter] = Field(default_factory=list, description="Chapters directly under Act if no Parts exist")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Muluki Civil Code, 2074",
                "source_url": "https://lawcommission.gov.np/...",
                "parts": [
                    {
                        "part_number": "1",
                        "title": "Preliminary",
                        "chapters": [
                            {
                                "chapter_number": "1",
                                "title": "General Provisions",
                                "sections": [
                                    {
                                        "section_number": "1",
                                        "title": "Short Title",
                                        "content": "This Act shall be cited as..."
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
