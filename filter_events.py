#!/usr/bin/env python3
"""Фильтр шума: печатает только critical-события и итог «критичных N».

Запуск: python3 filter_events.py [файл]   (по умолчанию events.json рядом со скриптом)
"""
import json
import sys
from pathlib import Path

path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("events.json")
events = json.loads(Path(path).read_text(encoding="utf-8"))

critical = [e for e in events if e["level"] == "critical"]
for e in critical:
    print(f"[critical] {e['event']}")
print(f"критичных {len(critical)}")
