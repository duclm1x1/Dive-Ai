"""PDF Skill — Extract text and structure from PDF files."""
import os
import subprocess
from typing import Dict, Any, Optional
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class PdfSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(
            name="pdf-extract", description="Extract text and structure from PDF files",
            category=SkillCategory.BROWSER, version="1.0.0",
            input_schema={"file_path": {"type": "string", "required": True}},
            output_schema={"text": "string", "pages": "integer"},
            tags=["pdf", "extract", "document", "text"],
            trigger_patterns=[r"pdf", r"extract\s+pdf", r"read\s+pdf"],
            combo_compatible=["data-analyzer", "note-taker", "deep-research"],
            combo_position="start", cost_per_call=0.0,
        )

    def _execute(self, inputs, context=None):
        file_path = inputs.get("file_path") or inputs.get("path", "")
        if not file_path or not os.path.exists(file_path):
            return AlgorithmResult("failure", None, {"error": f"File not found: {file_path}"})
        
        # Try PyPDF2 / pypdf
        try:
            try:
                from pypdf import PdfReader
            except ImportError:
                from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            pages = len(reader.pages)
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text_parts.append(f"--- Page {i+1} ---\n{page_text}")
            
            full_text = "\n\n".join(text_parts)
            return AlgorithmResult("success", {
                "text": full_text[:50000], "pages": pages,
                "file": os.path.basename(file_path),
                "size_bytes": os.path.getsize(file_path),
            }, {"skill": "pdf-extract", "pages": pages})
        
        except ImportError:
            # Fallback: try pdftotext command
            try:
                result = subprocess.run(
                    ["pdftotext", file_path, "-"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return AlgorithmResult("success", {
                        "text": result.stdout[:50000], "pages": -1,
                        "method": "pdftotext",
                    }, {"skill": "pdf-extract"})
            except FileNotFoundError:
                pass
            
            return AlgorithmResult("failure", None, {
                "error": "No PDF library available. Install: pip install pypdf",
                "skill": "pdf-extract",
            })
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "skill": "pdf-extract"})
