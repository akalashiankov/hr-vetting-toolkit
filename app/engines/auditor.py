import re
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AuditResult:
    platform: str
    handle: str
    flagged_posts: List[Dict[str, str]] = field(default_factory=list)
    risk_score: int = 0

class SocialMediaAuditor:
    def __init__(self, risk_keywords: List[str] = None):
        self.risk_keywords = risk_keywords or [
            "hate speech", "confidential", "insider", "violence", 
            "illegal", "threat", "leak", "proprietary"
        ]

    def analyze_text(self, text: str) -> bool:
        pattern = re.compile(r'\b(' + '|'.join(self.risk_keywords) + r')\b', re.IGNORECASE)
        return bool(pattern.search(text))

    def audit_profile(self, platform: str, handle: str, public_posts: List[str]) -> AuditResult:
        result = AuditResult(platform=platform, handle=handle)
        
        for post in public_posts:
            if self.analyze_text(post):
                result.flagged_posts.append({
                    "content": post,
                    "reason": "Matched policy risk keyword"
                })
                result.risk_score += 10
                
        return result
