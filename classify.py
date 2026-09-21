#!/usr/bin/env python3
"""Классификатор обращений: категория (справка / жалоба / другое) + черновик ответа.

Работает на правилах, без LLM и внешних зависимостей.
Запуск: python3 classify.py [файл]   (по умолчанию messages.txt рядом со скриптом)
"""
import re
import sys
from collections import Counter
from pathlib import Path

# Тематические правила: первое совпадение задаёт категорию и черновик ответа.
# Жалобы стоят первыми, чтобы «Почему опять нет Wi-Fi?» не ушло в справку
# только из-за вопросительной формы.
TOPICS = [
    ("жалоба", ("столов", "очеред", "холодн", "еда", "еды"),
     "Спасибо, что сообщили. Мы передали замечание администрации столовой: "
     "проверим температуру блюд и организацию раздачи в часы пик."),
    ("жалоба", ("wi-fi", "wifi", "вайфай", "интернет"),
     "Спасибо за сигнал! Заявка передана в IT-службу, специалисты уже проверяют "
     "сеть. Сообщим, как только связь восстановится."),
    ("справка", ("справк",),
     "Справку о месте учёбы можно заказать в личном кабинете студента или в деканате. "
     "Обычно она готова в течение 1–3 рабочих дней."),
    ("справка", ("парковк",),
     "Гостевая парковка находится у главного входа. Сообщите, пожалуйста, номер "
     "автомобиля и время визита — оформим гостевой пропуск."),
    ("другое", ("консультац", "запис"),
     "Здравствуйте! Уточните, пожалуйста, предмет или преподавателя и удобное время — "
     "подтвердим запись на завтра."),
]

# Общие признаки — для обращений, которые не подошли ни под одну тему.
COMPLAINT_MARKERS = ("не работ", "нет ", "пропал", "сломал", "плох", "грязн", "шумн", "жалоб")
QUESTION_MARKERS = ("как", "где", "когда", "куда", "сколько", "можно ли")

FALLBACK_REPLIES = {
    "справка": "Здравствуйте! Уточняем информацию и ответим в ближайшее время.",
    "жалоба": "Спасибо, что сообщили о проблеме. Обращение передано ответственной службе, "
              "вернёмся с ответом в ближайшее время.",
    "другое": "Здравствуйте! Обращение получено и передано профильному специалисту.",
}


def normalize(text):
    text = text.lower().replace("ё", "е")
    return re.sub(r"[‐-―]", "-", text)  # «Wi‑Fi» пишут с разными дефисами


def has(text, stems):
    return any(re.search(r"\b" + re.escape(stem), text) for stem in stems)


def classify(text):
    t = normalize(text)
    for category, stems, reply in TOPICS:
        if has(t, stems):
            return category, reply
    if has(t, COMPLAINT_MARKERS):
        category = "жалоба"
    elif "?" in t or has(t, QUESTION_MARKERS):
        category = "справка"
    else:
        category = "другое"
    return category, FALLBACK_REPLIES[category]


def read_messages(path):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            yield re.sub(r"^\d+[).]\s*", "", line)  # убираем нумерацию «1) »


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("messages.txt")
    stats = Counter()
    for i, message in enumerate(read_messages(path), 1):
        category, reply = classify(message)
        stats[category] += 1
        print(f"{i}) {message}")
        print(f"   Категория: {category}")
        print(f"   Черновик:  {reply}\n")
    print("Итого: " + ", ".join(f"{cat} — {stats[cat]}" for cat in FALLBACK_REPLIES))


if __name__ == "__main__":
    main()
