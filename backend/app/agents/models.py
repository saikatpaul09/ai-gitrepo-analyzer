from typing import Literal

from pydantic import BaseModel


class Finding(BaseModel):
    category: str
    severity: Literal[
        "critical",
        "high",
        "medium",
        "low",
        "info",
    ]
    title: str
    file: str | None = None
    line: int | None = None
    description: str
    recommendation: str


class AnalysisResult(BaseModel):
    findings: list[Finding]


class ReportSummary(BaseModel):
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    info: int


class AnalysisReport(BaseModel):
    summary: ReportSummary
    executive_summary: str
    findings: list[Finding]
    recommendations: list[str]