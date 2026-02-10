"""Email Send Skill — Send emails via SMTP."""
import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class EmailSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="email-send", description="Send email via SMTP",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"to": {"type": "string", "required": True}, "subject": {"type": "string", "required": True},
                          "body": {"type": "string", "required": True}},
            output_schema={"sent": "boolean", "message_id": "string"},
            tags=["email", "send", "mail", "smtp", "notify"],
            trigger_patterns=[r"send\s+email", r"email\s+to", r"mail\s+"],
            combo_compatible=["deep-research", "data-analyzer", "news-search"],
            combo_position="end")

    def _execute(self, inputs, context=None):
        to_addr = inputs.get("to", "")
        subject = inputs.get("subject", "Dive AI Notification")
        body = inputs.get("body") or inputs.get("data", {}).get("summary", "No content")
        
        smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_pass = os.environ.get("SMTP_PASS", "")
        
        if not smtp_user:
            return AlgorithmResult("success", {
                "sent": False, "simulated": True,
                "to": to_addr, "subject": subject, "body_preview": body[:200],
                "note": "SMTP not configured. Set SMTP_USER/SMTP_PASS env vars.",
            }, {"skill": "email-send"})
        
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = to_addr
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            return AlgorithmResult("success", {"sent": True, "to": to_addr, "subject": subject},
                                   {"skill": "email-send"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
