import copy
import json
import random
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def get_ability_file_path() -> Path:
    """Return the absolute path to abilitiy.json."""
    try:
        from django.conf import settings
        base_dir = Path(settings.BASE_DIR)
        if (base_dir / "abilitiy.json").exists():
            return base_dir / "abilitiy.json"
    except Exception:
        pass

    candidates = [
        Path("abilitiy.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "abilitiy.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return Path("abilitiy.json")


def load_ability_data() -> dict:
    """Load JSON data from abilitiy.json."""
    file_path = get_ability_file_path()
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_max_scores(questions: list) -> dict:
    """Calculate the maximum possible score for each category."""
    categories = ["frontend", "backend", "data_science", "cybersecurity", "mobile"]
    max_scores = {cat: 0 for cat in categories}
    for q in questions:
        for cat in categories:
            max_scores[cat] += max(
                (opt.get("weights", {}).get(cat, 0) for opt in q.get("options", [])),
                default=0
            )
    return max_scores


def start_new_quiz(context: ContextTypes.DEFAULT_TYPE) -> tuple[str, InlineKeyboardMarkup]:
    """Initialize a new quiz session with randomized questions and options."""
    data = load_ability_data()
    raw_questions = data.get("test", {}).get("questions", [])

    # Savollarni va har bir savol variantlarini chuqur nusxa qilib aralashtiramiz
    questions = copy.deepcopy(raw_questions)
    random.shuffle(questions)
    for q in questions:
        random.shuffle(q["options"])

    context.user_data["ability_quiz"] = {
        "questions": questions,
        "current_index": 0,
        "scores": {
            "frontend": 0,
            "backend": 0,
            "data_science": 0,
            "cybersecurity": 0,
            "mobile": 0,
        },
    }

    return build_question_view(context.user_data["ability_quiz"], 0)


def build_question_view(quiz: dict, index: int) -> tuple[str, InlineKeyboardMarkup]:
    """Build the text and inline keyboard for a specific question."""
    questions = quiz["questions"]
    total = len(questions)
    current_q = questions[index]
    options = current_q.get("options", [])

    text = (
        f"🧠 <b>Qobiliyatingizni aniqlash testi</b>\n\n"
        f"❓ <b>{index + 1}/{total}-savol:</b>\n"
        f"<b>{current_q['question']}</b>\n\n"
        f"<i>Quyidagi javoblardan birini tanlang:</i>"
    )

    keyboard = []
    for opt_idx, opt in enumerate(options):
        keyboard.append([
            InlineKeyboardButton(
                text=opt["text"],
                callback_data=f"quiz_{index}_{opt_idx}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="❌ Testni to‘xtatish",
            callback_data="quiz_cancel"
        )
    ])

    return text, InlineKeyboardMarkup(keyboard)


def format_results(scores: dict, data: dict) -> tuple[str, InlineKeyboardMarkup]:
    """Format the final quiz results with percentages and top recommendations."""
    questions = data.get("test", {}).get("questions", [])
    max_scores = calculate_max_scores(questions)

    direction_info = {
        "frontend": {"title": "Frontend Development", "icon": "💻"},
        "backend": {"title": "Backend Development", "icon": "⚙️"},
        "data_science": {"title": "Data Science", "icon": "📊"},
        "cybersecurity": {"title": "Cybersecurity", "icon": "🛡"},
        "mobile": {"title": "Mobile Development", "icon": "📱"},
    }

    results = []
    for slug, info in direction_info.items():
        user_score = scores.get(slug, 0)
        max_val = max_scores.get(slug, 1)
        percentage = min(100, max(0, round((user_score / max_val) * 100)))
        results.append({
            "slug": slug,
            "title": info["title"],
            "icon": info["icon"],
            "score": user_score,
            "max_score": max_val,
            "percentage": percentage,
        })

    # Foiz va ball bo‘yicha kamayish tartibida saralaymiz
    results.sort(key=lambda x: (x["percentage"], x["score"]), reverse=True)

    top_1 = results[0]
    show_top_count = data.get("test", {}).get("result", {}).get("show_top", 3)
    top_courses = results[:show_top_count]

    text = (
        "🎉 <b>Test muvaffaqiyatli yakunlandi!</b>\n\n"
        "Qobiliyatingiz va javoblaringiz tahlili natijasi:\n\n"
        f"🎯 <b>Sizga eng ko‘p mos keladigan asosiy yo‘nalish:</b>\n"
        f"👉 <b>{top_1['icon']} {top_1['title']} ({top_1['percentage']}%)</b>\n\n"
        "💡 <i>Sizning qiziqishingiz va fikrlash uslubingiz ushbu sohada yuqori natijalarga erishishingiz mumkinligini ko‘rsatmoqda!</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 <b>Sizga ko‘proq mos keladigan TOP yo‘nalishlar:</b>\n"
    )

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, item in enumerate(top_courses):
        medal = medals[i] if i < len(medals) else "🔹"
        text += f"{medal} <b>{item['icon']} {item['title']}</b> — <b>{item['percentage']}%</b>\n"

    text += "\n📊 <b>Barcha yo‘nalishlar bo‘yicha to‘liq natija:</b>\n"
    for item in results:
        filled = round(item["percentage"] / 10)
        bar = "🟩" * filled + "⬜️" * (10 - filled)
        text += f"{item['icon']} {item['title']}:\n<code>{bar}</code> {item['percentage']}%\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Testni qayta topshirish", callback_data="quiz_restart")]
    ])

    return text, keyboard


async def qobilyat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle clicking the '🧠 Qobiliyatimni aniqlash' button to start quiz."""
    text, reply_markup = start_new_quiz(context)
    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries for quiz options, cancel, and restart."""
    query = update.callback_query
    await query.answer()

    data_val = query.data

    if data_val == "quiz_cancel":
        context.user_data.pop("ability_quiz", None)
        try:
            await query.edit_message_text(
                "❌ <b>Test to‘xtatildi.</b>\n\n"
                "Qachon xohlasangiz menyudagi <b>🧠 Qobiliyatimni aniqlash</b> tugmasi orqali qaytadan boshlashingiz mumkin!",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    if data_val == "quiz_restart":
        text, reply_markup = start_new_quiz(context)
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    # Option tanlanganda format: quiz_<question_index>_<option_index>
    parts = data_val.split("_")
    if len(parts) != 3:
        return

    q_idx = int(parts[1])
    opt_idx = int(parts[2])

    quiz = context.user_data.get("ability_quiz")
    if not quiz:
        try:
            await query.edit_message_text(
                "⚠️ <b>Test muddati tugagan yoki topilmadi.</b>\n\n"
                "Iltimos, pastdagi menyudan <b>🧠 Qobiliyatimni aniqlash</b> tugmasini bosib qaytadan boshlang.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    # Eski yoki takroriy bosishlarni tekshiramiz
    if q_idx != quiz.get("current_index", -1):
        return

    current_q = quiz["questions"][q_idx]
    chosen_opt = current_q["options"][opt_idx]

    # Ballarni qo'shib boramiz
    for cat, weight in chosen_opt.get("weights", {}).items():
        quiz["scores"][cat] = quiz["scores"].get(cat, 0) + weight

    quiz["current_index"] += 1

    # Agar hali savollar qolgan bo'lsa
    if quiz["current_index"] < len(quiz["questions"]):
        next_text, next_markup = build_question_view(quiz, quiz["current_index"])
        try:
            await query.edit_message_text(
                text=next_text,
                reply_markup=next_markup,
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        # Barcha savollar tugadi - natijani hisoblash
        data = load_ability_data()
        result_text, result_markup = format_results(quiz["scores"], data)

        try:
            await query.edit_message_text(
                text=result_text,
                reply_markup=result_markup,
                parse_mode="HTML"
            )
        except Exception:
            pass

        # Natija yuborilgach, qobiliyat testiga oid barcha ma'lumotlarni context'dan tozalaymiz
        context.user_data.pop("ability_quiz", None)
        context.user_data.pop("last_quiz_scores", None)