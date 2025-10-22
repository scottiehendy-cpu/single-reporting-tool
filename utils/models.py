from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Reporter(BaseModel):
    first_name: str
    surname: str
    title: Optional[str] = None
    email: EmailStr
    phone: str

class Organisation(BaseModel):
    name: str
    abn_status: str  # has_abn | not_applicable
    abn: Optional[str] = None
    abn_reason: Optional[str] = None
    jurisdiction: str
    postcode: Optional[str] = None
    country: Optional[str] = None
    address: str
    secondary_email: Optional[str] = None
    website: Optional[str] = None

class Purpose(BaseModel):
    purposes: List[str]
    cybersecurity_reason: List[str] = []
    ci_member: Optional[str] = None
    ci_sectors: List[str] = []
    consent_home_affairs: Optional[str] = None

class Incident(BaseModel):
    type: str
    other_type_text: Optional[str] = None
    infra_impacted: str
    infra_impact_details: Optional[str] = None
    customers_impacted: str
    occurrence_date: str
    occurrence_time: str
    identified_date: str
    identified_time: str
    ongoing: str
    identified_by: str
    narrative: str
    additional_details: Optional[str] = None

class Ransomware(BaseModel):
    variants: List[str] = []
    exploited_vulns: Optional[str] = None
    payment_demanded: Optional[str] = None
    payment_provided: Optional[str] = None
    communicated_with_extorter: Optional[str] = None

class Report(BaseModel):
    reporter: dict
    organisation: dict
    purpose: dict
    incident: dict
    ransomware: Optional[dict] = None
