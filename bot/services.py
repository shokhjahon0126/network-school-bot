import logging
import requests
from decouple import config

logger = logging.getLogger(__name__)

MARKAZ_URL = config("MARKAZ_URL", default="https://demo.corely.uz/api/v1/crm/public/form")
LEAD_SUBMIT_URL = config("LEAD_SUBMIT_URL", default="https://demo.corely.uz/api/v1/crm/public/leads")


def fetch_markaz_data() -> dict:
    """O'quv markazi ma'lumotlarini (filiallar va kurslar) API dan olish."""
    try:
        response = requests.get(MARKAZ_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        logger.error(f"Failed to fetch markaz data. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching markaz data: {e}")
    return {}


def get_all_courses(context=None) -> list:
    """Kurslar ro'yxatini olish (avval context'dan, yo'q bo'lsa API dan)."""
    if context and context.bot_data.get("courses"):
        return context.bot_data["courses"]

    data = fetch_markaz_data()
    courses = data.get("courses", [])
    if context and courses:
        context.bot_data["courses"] = courses
        if "branches" in data:
            context.bot_data["branches"] = data.get("branches", [])
    return courses


def get_course_by_id(course_id: str, context=None) -> dict | None:
    """Berilgan ID bo'yicha kursni topish."""
    courses = get_all_courses(context)
    for c in courses:
        if str(c.get("id")) == str(course_id):
            return c
    return None


def submit_lead(name: str, phone: str, branch_id: str | None = None, course_ids: list | None = None, note: str = "") -> tuple[bool, str]:
    """
    Foydalanuvchi ma'lumotlarini belgilangan URL ga POST qilish.
    Qaytaradi: (success: bool, message: str)
    """
    payload = {
        "name": name,
        "phone": phone,
        "source_code": "telegram",
    }
    if branch_id:
        payload["branch_id"] = branch_id
    if course_ids:
        payload["course_ids"] = course_ids
    if note:
        payload["note"] = note

    try:
        response = requests.post(LEAD_SUBMIT_URL, json=payload, timeout=10)
        if response.status_code in [200, 201, 202]:
            return True, "Success"
        else:
            logger.error(f"Lead submission failed. Status: {response.status_code}, Body: {response.text}")
            return False, f"Xatolik kodi: {response.status_code}"
    except Exception as e:
        logger.error(f"Lead submission exception: {e}")
        return False, str(e)
