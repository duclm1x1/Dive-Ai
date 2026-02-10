"""Email Reader Skill — Read emails via IMAP."""
import imaplib, email, os
from email.header import decode_header
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class EmailReaderSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="email-read", description="Read emails via IMAP",
            category=SkillCategory.COMMUNICATION, version="1.0.0",
            input_schema={"folder": {"type": "string"}, "limit": {"type": "integer"}, "unread_only": {"type": "boolean"}},
            output_schema={"emails": "list", "total": "integer"},
            tags=["email", "read", "inbox", "mail", "imap"],
            trigger_patterns=[r"read\s+email", r"check\s+inbox", r"new\s+mail"],
            combo_compatible=["deep-research", "note-taker", "task-manager"],
            combo_position="start")

    def _execute(self, inputs, context=None):
        imap_host = os.environ.get("IMAP_HOST", "imap.gmail.com")
        imap_user = os.environ.get("IMAP_USER", "") or os.environ.get("SMTP_USER", "")
        imap_pass = os.environ.get("IMAP_PASS", "") or os.environ.get("SMTP_PASS", "")
        folder = inputs.get("folder", "INBOX")
        limit = inputs.get("limit", 10)
        unread = inputs.get("unread_only", True)
        
        if not imap_user:
            return AlgorithmResult("success", {
                "emails": [], "total": 0, "simulated": True,
                "note": "IMAP not configured. Set IMAP_USER/IMAP_PASS env vars.",
            }, {"skill": "email-read"})
        
        try:
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(imap_user, imap_pass)
            mail.select(folder)
            
            criteria = "UNSEEN" if unread else "ALL"
            _, msg_nums = mail.search(None, criteria)
            msg_ids = msg_nums[0].split()[-limit:]
            
            emails = []
            for mid in msg_ids:
                _, data = mail.fetch(mid, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                subject = str(decode_header(msg["Subject"])[0][0] or "")
                if isinstance(subject, bytes): subject = subject.decode()
                from_addr = msg["From"]
                date = msg["Date"]
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="replace")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="replace")
                
                emails.append({"subject": subject, "from": from_addr, "date": date, "body": body[:500]})
            
            mail.logout()
            return AlgorithmResult("success", {"emails": emails, "total": len(emails)}, {"skill": "email-read"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
