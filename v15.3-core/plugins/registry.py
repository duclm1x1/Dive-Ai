from __future__ import annotations

from typing import List

from .base import StackPlugin
from .nextjs import NextJsPlugin
from .nestjs import NestJsPlugin
from .tailwind import TailwindPlugin


def default_plugins() -> List[StackPlugin]:
    return [NextJsPlugin(), NestJsPlugin(), TailwindPlugin()]
