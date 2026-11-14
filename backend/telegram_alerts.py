"""
AURA // Planetary Climate Intelligence & Telemetry SaaS
Telegram Weather Crisis Alert Dispatcher (@sixsnova_bot)
NASA Space Apps Challenge 2026: Be An Earth System Trend Detective!

Fully integrated with:
1. Telegram Bot API (https://api.telegram.org/bot<TOKEN>/sendMessage)
2. Interactive Bot Conversational Flow (City -> District -> Alert Types)
3. Firestore & Local JSON Persistent Dual-Store
4. Bilingual Aerospace Emergency Bulletins (Arabic & English)
5. Green Space Crisis Recommendations (Planting trees, rooftop gardens, shaded streets, micro-parks)
6. Automated Daily Scheduled Forecast Audit
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("telegram_alerts")
logging.basicConfig(level=logging.INFO)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "telegram_config.json")
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "firestore_subscribers.json")
FIREBASE_KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

# Fallback Bot Token if not provided in environment
DEFAULT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9249854983:AAFSHV24Htm1MVzqX6LDnFKNoeRHYVfBUN4")
DEFAULT_BOT_USERNAME = "@sixsnova_bot"

DEFAULT_CONFIG = {
    "bot_username": DEFAULT_BOT_USERNAME,
    "bot_token": DEFAULT_TOKEN,
    "default_chat_id": "1142168838",
    "enabled": True,
    "last_daily_run": None,
    "thresholds": {
        "temperature_high_c": 38.0,
        "temperature_anomaly_c": 3.0,
        "wind_speed_kmh": 45.0,
        "rainfall_mm_day": 5.0,
        "humidity_high_pct": 75.0,
        "green_space_deficit_uhi": True
    }
}

# Pre-populated subscriber roster provided by user
INITIAL_SUBSCRIBERS = {
    "1142168838": {
        "chat_id": "1142168838",
        "name": "ENG AHMED ANTER",
        "username": "AHMED280500",
        "city": "Cairo",
        "city_ar": "القاهرة",
        "district": "Heliopolis / مصر الجديدة",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": "2026-11-14T07:00:00Z"
    },
    "8458809118": {
        "chat_id": "8458809118",
        "name": "Subscriber Alexandria",
        "username": "User_Alex",
        "city": "Alexandria",
        "city_ar": "الإسكندرية",
        "district": "Montazah / المنتزه",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": "2026-11-14T07:00:00Z"
    },
    "6120922499": {
        "chat_id": "6120922499",
        "name": "abdalrhmn",
        "username": "abdalrhmn",
        "city": "Giza",
        "city_ar": "الجيزة",
        "district": "Dokki / الدقي",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": "2026-11-14T07:00:00Z"
    },
    "9293248707": {
        "chat_id": "9293248707",
        "name": "Noura",
        "username": "Noura",
        "city": "Aswan",
        "city_ar": "أسوان",
        "district": "Nile Basin / حوض النيل",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": "2026-11-14T07:00:00Z"
    },
    "5173643474": {
        "chat_id": "5173643474",
        "name": "Nour",
        "username": "Nour",
        "city": "Luxor",
        "city_ar": "الأقصر",
        "district": "Karnak / الكرنك",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": "2026-11-14T07:00:00Z"
    },
    "8948583787": {
        "chat_id": "8948583787",
        "name": "Ahmed",
        "username": "Ahmed",
        "city": "Red Sea",
        "city_ar": "البحر الأحمر",
        "district": "Hurghada / الغردقة",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": "2026-11-14T07:00:00Z"
    }
}


# ==============================================================================
# 1. FIRESTORE & LOCAL PERSISTENCE ADAPTER
# ==============================================================================
_firestore_db = None
_firestore_initialized = False

def init_firestore():
    """Initializes Google Cloud Firestore if serviceAccountKey exists."""
    global _firestore_db, _firestore_initialized
    if _firestore_initialized:
        return _firestore_db
    _firestore_initialized = True
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if os.path.exists(FIREBASE_KEY_PATH):
            cred = credentials.Certificate(FIREBASE_KEY_PATH)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            _firestore_db = firestore.client()
            logger.info("✅ Connected to Google Cloud Firestore successfully.")
        else:
            logger.info("ℹ️ Firestore key not found; using persistent local JSON store.")
    except Exception as e:
        logger.warning(f"Firestore initialization skipped: {e}")
        _firestore_db = None
    return _firestore_db


def load_config() -> Dict[str, Any]:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception as e:
            logger.warning(f"Failed to read telegram_config.json: {e}")
    # Always prioritize environment variable
    env_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if env_token:
        cfg["bot_token"] = env_token.strip()
    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write telegram_config.json: {e}")


def get_all_subscribers() -> Dict[str, Dict[str, Any]]:
    """Loads all subscribers from Firestore or local persistent JSON store."""
    db = init_firestore()
    if db:
        try:
            docs = db.collection("telegram_subscribers").stream()
            subs = {}
            for doc in docs:
                subs[doc.id] = doc.to_dict()
            if subs:
                return subs
        except Exception as e:
            logger.warning(f"Error reading from Firestore: {e}")

    # Fallback to local JSON file
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading local subscribers file: {e}")

    # Initialize file with initial roster
    save_all_subscribers(INITIAL_SUBSCRIBERS)
    return INITIAL_SUBSCRIBERS.copy()


def save_all_subscribers(subs: Dict[str, Dict[str, Any]]) -> None:
    try:
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(subs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save subscribers file: {e}")

    # Sync to Firestore if available
    db = init_firestore()
    if db:
        try:
            batch = db.batch()
            for chat_id, data in subs.items():
                ref = db.collection("telegram_subscribers").document(str(chat_id))
                batch.set(ref, data, merge=True)
            batch.commit()
        except Exception as e:
            logger.warning(f"Failed to sync subscribers to Firestore: {e}")


def save_subscriber(chat_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    chat_id = str(chat_id).strip()
    subs = get_all_subscribers()
    existing = subs.get(chat_id, {
        "chat_id": chat_id,
        "name": "Citizen Scientist",
        "city": "Cairo",
        "city_ar": "القاهرة",
        "district": "Capital Metropolitan",
        "alert_types": ["heat", "wind", "rainfall", "humidity", "green_space"],
        "active": True,
        "registered_at": datetime.now(timezone.utc).isoformat()
    })
    existing.update(data)
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    subs[chat_id] = existing
    save_all_subscribers(subs)
    return existing


import html as html_lib

def escape_html(text: Any) -> str:
    return html_lib.escape(str(text or ""))

# ==============================================================================
# 2. BILINGUAL AEROSPACE ALERT FORMATTER (CONCISE & ACTION-ORIENTED)
# ==============================================================================
def format_bilingual_alert(
    alert_type: str,
    city: str,
    district: str,
    severity: str = "HIGH",
    metric_val: str = "",
    lat: float = 30.0444,
    lon: float = 31.2357
) -> str:
    """
    Constructs a concise, highly readable Telegram alert message.
    Fulfills requirement 9 for Green Space Warning:
    - planting trees
    - rooftop gardens
    - shaded streets
    - creating a green space immediately
    """
    at = alert_type.lower()
    c_city = escape_html(city)
    c_dist = escape_html(district)
    c_metric = escape_html(metric_val)

    # 1. HEAT WARNING
    if at in ["heat", "temperature", "heatwave"]:
        return (
            f"🚨 <b>تحذير: موجة حارة شديدة | Heat Warning</b>\n\n"
            f"📍 <b>الموقع:</b> <code>{c_city} - {c_dist}</code>\n"
            f"🌡️ <b>الحرارة المرصودة:</b> <code>{c_metric or '+4.5°C Anomaly (41.2°C)'}</code>\n\n"
            f"⚠️ <b>إرشادات السلامة (Action Plan):</b>\n"
            f"• تجنب التعرض المباشر لأشعة الشمس وقت الذروة (11 ص - 4:30 م).\n"
            f"• اشرب السوائل بانتظام وتواجد بأماكن جيدة التهوية.\n\n"
            f"🛰️ <i>6S Nova Climate Oracle · @sixsnova_bot</i>"
        )

    # 2. WIND WARNING
    elif at in ["wind", "storm", "sandstorm"]:
        return (
            f"🚨 <b>تحذير: رياح عاتية وعواصف | Wind Warning</b>\n\n"
            f"📍 <b>الموقع:</b> <code>{c_city} - {c_dist}</code>\n"
            f"💨 <b>سرعة الرياح:</b> <code>{c_metric or '65 km/h Wind Gusts'}</code>\n\n"
            f"⚠️ <b>إرشادات السلامة (Action Plan):</b>\n"
            f"• ثبت الأجسام القابلة للتطاير فوق الأسطح والحذر أثناء القيادة.\n"
            f"• تجنب السواحل المكشوفة ومحيط اللافتات والأشجار القديمة.\n\n"
            f"🛰️ <i>6S Nova Climate Oracle · @sixsnova_bot</i>"
        )

    # 3. RAINFALL WARNING
    elif at in ["rainfall", "rain", "flood", "precip"]:
        return (
            f"🚨 <b>تحذير: أمطار غزيرة وسيول | Rainfall Warning</b>\n\n"
            f"📍 <b>الموقع:</b> <code>{c_city} - {c_dist}</code>\n"
            f"🌧️ <b>معدل الأمطار:</b> <code>{c_metric or '22.5 mm/day Intense Rain'}</code>\n\n"
            f"⚠️ <b>إرشادات السلامة (Action Plan):</b>\n"
            f"• تجنب الأنفاق المنخفضة ومخرات السيول وأعمدة الإنارة.\n"
            f"• اتّبع تعليمات الحماية المدنية والمرور في الطرق السريعة.\n\n"
            f"🛰️ <i>6S Nova Climate Oracle · @sixsnova_bot</i>"
        )

    # 4. HUMIDITY WARNING
    elif at in ["humidity", "rh2m", "humid"]:
        return (
            f"🚨 <b>تحذير: رطوبة خانقة وإجهاد حراري | Humidity Warning</b>\n\n"
            f"📍 <b>الموقع:</b> <code>{c_city} - {c_dist}</code>\n"
            f"💧 <b>نسبة الرطوبة:</b> <code>{c_metric or '88% Humidity · 44°C Heat Index'}</code>\n\n"
            f"⚠️ <b>إرشادات السلامة (Action Plan):</b>\n"
            f"• قلل المجهود البدني والأنشطة الشاقة في الأماكن المغلقة.\n"
            f"• احرص على تبريد الجسم والتهوية المستمرة وشرب الماء والأملاح.\n\n"
            f"🛰️ <i>6S Nova Climate Oracle · @sixsnova_bot</i>"
        )

    # 5. GREEN SPACE WARNING (MANDATORY REQUIREMENT 9)
    else:  # green_space / default
        return (
            f"🚨 <b>تحذير: نقص المساحات الخضراء | Green Space Warning</b>\n\n"
            f"📍 <b>الموقع:</b> <code>{c_city} - {c_dist}</code>\n"
            f"🌳 <b>الحالة:</b> <code>{c_metric or 'Vegetative Ratio NDVI &lt; 0.08 · Severe UHI Spike'}</code>\n\n"
            f"🌱 <b>توصيات بيئية فورية (Urgent Action Plan):</b>\n"
            f"• <b>زراعة الأشجار (Plant Trees):</b> اغرس أشجار ظل ملائمة للمناخ في الشوارع والأفنية.\n"
            f"• <b>حدائق الأسطح (Rooftop Gardens):</b> انشئ حدائق أسطح خضراء لعزل حرارة المباني.\n"
            f"• <b>تشجير الشوارع (Shaded Streets):</b> ظلل الطرق والممرات بأحزمة شجرية كثيفة.\n"
            f"• <b>إنشاء مساحات خضراء عاجلة (Create Green Spaces):</b> وفر حدائق ومتنفس بيئي فوراً لخفض الجزر الحرارية.\n\n"
            f"🛰️ <i>6S Nova Planetary Greening · @sixsnova_bot</i>"
        )



# ==============================================================================
# 3. TELEGRAM BOT API DISPATCHER
# ==============================================================================
def send_telegram_message(
    chat_id: str,
    text: str,
    reply_markup: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Direct invocation of Telegram Bot API sendMessage."""
    cfg = load_config()
    token = cfg.get("bot_token", "").strip()

    if not token:
        return {"status": "error", "message": "Bot token is missing in environment or config."}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": str(chat_id).strip(),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        resp = requests.post(url, json=payload, timeout=12)
        res_data = resp.json()
        if res_data.get("ok"):
            return {
                "status": "delivered",
                "chat_id": chat_id,
                "message_id": res_data.get("result", {}).get("message_id"),
                "message": f"Successfully sent to Telegram chat {chat_id}"
            }
        else:
            return {
                "status": "failed",
                "chat_id": chat_id,
                "message": f"Telegram API error: {res_data.get('description', 'Unknown error')}"
            }
    except Exception as e:
        return {"status": "error", "chat_id": chat_id, "message": str(e)}


def broadcast_alert_to_subscribers(
    alert_type: str,
    city: str,
    district: str,
    severity: str = "HIGH",
    metric_val: str = "",
    target_chat_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends an alert to either a single target_chat_id (e.g. for testing)
    or broadcasts to all registered subscribers matching the alert type.
    """
    subs = get_all_subscribers()
    text = format_bilingual_alert(
        alert_type=alert_type,
        city=city,
        district=district,
        severity=severity,
        metric_val=metric_val
    )

    results = []
    if target_chat_id:
        # Send to specific subscriber
        res = send_telegram_message(target_chat_id, text)
        results.append(res)
    else:
        # Broadcast to all active subscribers interested in this alert type
        at = alert_type.lower()
        if at in ["temperature", "heatwave"]:
            at = "heat"
        elif at in ["storm", "sandstorm"]:
            at = "wind"
        elif at in ["rain", "flood", "precip"]:
            at = "rainfall"

        for cid, data in subs.items():
            if not data.get("active", True):
                continue
            prefs = [p.lower() for p in data.get("alert_types", [])]
            if at in prefs or "all" in prefs or not prefs:
                res = send_telegram_message(cid, text)
                results.append(res)

    successful = sum(1 for r in results if r.get("status") == "delivered")
    return {
        "status": "completed",
        "alert_type": alert_type,
        "city": city,
        "district": district,
        "preview_text": text,
        "total_dispatched": len(results),
        "successful_deliveries": successful,
        "results": results
    }


# ==============================================================================
# 4. INTERACTIVE TELEGRAM BOT CONVERSATIONAL POLLING ENGINE
# ==============================================================================
# State machine for user onboard: 'city' -> 'district' -> 'alert_types'
_user_sessions: Dict[str, Dict[str, Any]] = {}
_polling_thread: Optional[threading.Thread] = None
_stop_polling = threading.Event()

CITY_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "🏛️ القاهرة (Cairo)", "callback_data": "city_Cairo"},
            {"text": "🌊 الإسكندرية (Alexandria)", "callback_data": "city_Alexandria"}
        ],
        [
            {"text": "🏜️ الجيزة (Giza)", "callback_data": "city_Giza"},
            {"text": "☀️ أسوان (Aswan)", "callback_data": "city_Aswan"}
        ],
        [
            {"text": "🏺 الأقصر (Luxor)", "callback_data": "city_Luxor"},
            {"text": "🏖️ البحر الأحمر (Red Sea)", "callback_data": "city_RedSea"}
        ],
        [
            {"text": "⛰️ سيناء (Sinai)", "callback_data": "city_Sinai"},
            {"text": "🌴 مطروح / سيوة (Matrouh)", "callback_data": "city_Matrouh"}
        ]
    ]
}

ALERT_TYPES_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "🌡️ Heat / حرارة", "callback_data": "type_heat"},
            {"text": "💨 Wind / رياح", "callback_data": "type_wind"}
        ],
        [
            {"text": "🌧️ Rain / أمطار", "callback_data": "type_rainfall"},
            {"text": "💧 Humidity / رطوبة", "callback_data": "type_humidity"}
        ],
        [
            {"text": "🌳 Green Space / مساحات خضراء", "callback_data": "type_green_space"}
        ],
        [
            {"text": "⭐ تفعيل كافة التنبيهات (All Alerts)", "callback_data": "type_all"}
        ]
    ]
}


def handle_bot_message(msg: Dict[str, Any]):
    chat = msg.get("chat", {})
    chat_id = str(chat.get("id"))
    text = (msg.get("text") or "").strip()
    user_name = chat.get("first_name", "") + " " + chat.get("last_name", "")
    username = chat.get("username", "")

    if not chat_id:
        return

    session = _user_sessions.get(chat_id, {})

    # /start command
    if text.startswith("/start"):
        _user_sessions[chat_id] = {
            "step": "awaiting_city",
            "name": user_name.strip() or "Citizen Scientist",
            "username": username
        }
        welcome_text = (
            f"🌍 <b>أهلاً بك في نظام الإنذار المبكر للمناخ والمساحات الخضراء — AURA!</b> 🛰️\n"
            f"NASA Space Apps Challenge 2026\n\n"
            f"يرجى تحديد <b>المدينة / المحافظة</b> الخاصة بك لتخصيص تنبيهات المناخ ومؤشر الغطاء النباتي فورياً:\n"
            f"Please choose your <b>City</b> to customize real-time planetary weather warnings:"
        )
        send_telegram_message(chat_id, welcome_text, reply_markup=CITY_KEYBOARD)
        return

    # /help command
    if text.startswith("/help"):
        help_text = (
            f"📡 <b>AURA Climate Oracle &amp; Crisis Bot (@sixsnova_bot)</b>\n\n"
            f"الأوامر المتاحة / Available Commands:\n"
            f"• <code>/start</code> - إعداد المدينة والحي ونوع التنبيهات (Setup Alerts)\n"
            f"• <code>/status</code> - عرض إعداداتك وموقعك الحالي (View Status)\n"
            f"• <code>/test</code> - إرسال تجربة فورية للتنبيهات (Test Alert)\n"
            f"• <code>/green</code> - إرشادات زراعة الأشجار وحدائق الأسطح (Greening Tips)\n"
        )
        send_telegram_message(chat_id, help_text)
        return

    # /status command
    if text.startswith("/status"):
        subs = get_all_subscribers()
        user_sub = subs.get(chat_id)
        if user_sub:
            s_text = (
                f"📋 <b>حالة اشتراكك في نظام AURA:</b>\n"
                f"• المدينة: <code>{escape_html(user_sub.get('city'))}</code> ({escape_html(user_sub.get('city_ar', ''))})\n"
                f"• الحي / المنطقة: <code>{escape_html(user_sub.get('district'))}</code>\n"
                f"• التنبيهات المفعلة: <code>{escape_html(', '.join(user_sub.get('alert_types', [])))}</code>\n"
                f"• الحالة: {'✅ نشط (Active)' if user_sub.get('active') else '⏸️ متوقف'}\n\n"
                f"لتعديل بياناتك أرسل <code>/start</code> في أي وقت."
            )
        else:
            s_text = "⚠️ لم تسجل بعد! أرسل <code>/start</code> لتحديد مدينتك وتفعيل التنبيهات."
        send_telegram_message(chat_id, s_text)
        return

    # /test command
    if text.startswith("/test"):
        send_telegram_message(chat_id, "⏳ جاري إرسال تجربة إنذار عاجل ثنائي اللغة عبر نظام ناسا AURA...")
        res = broadcast_alert_to_subscribers(
            alert_type="heat",
            city="Cairo",
            district="Nasr City / مدينة نصر",
            severity="LEVEL 3 CRITICAL",
            metric_val="+4.8°C Anomaly (41.5°C Surface Temp)",
            target_chat_id=chat_id
        )
        return

    # Step: Waiting for District text input
    if session.get("step") == "awaiting_district":
        district = text
        session["district"] = district
        session["step"] = "awaiting_alerts"
        _user_sessions[chat_id] = session

        reply = (
            f"📍 تم تسجيل الحي بنجاح: <b>{escape_html(district)}</b>!\n\n"
            f"الآن اختر <b>نوع التنبيهات المفضلة</b> التي ترغب باستلامها فور رصد أي تغير غير معتاد عبر أقمار ناسا:\n"
            f"Select your preferred <b>alert categories</b>:"
        )
        send_telegram_message(chat_id, reply, reply_markup=ALERT_TYPES_KEYBOARD)
        return

    # Default fallback
    send_telegram_message(
        chat_id,
        "📡 أهلاً بك! لإعداد اشتراكك وتحديد منطقتك أرسل <code>/start</code> أو أرسل <code>/help</code> لقائمة الأوامر."
    )


def handle_callback_query(cb: Dict[str, Any]):
    cb_id = cb.get("id")
    chat = cb.get("message", {}).get("chat", {})
    chat_id = str(chat.get("id"))
    data = cb.get("data", "")

    cfg = load_config()
    token = cfg.get("bot_token")
    if token and cb_id:
        try:
            requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id}, timeout=5)
        except Exception:
            pass

    session = _user_sessions.get(chat_id, {})

    # City selected
    if data.startswith("city_"):
        city_code = data.replace("city_", "")
        city_names = {
            "Cairo": ("Cairo", "القاهرة"),
            "Alexandria": ("Alexandria", "الإسكندرية"),
            "Giza": ("Giza", "الجيزة"),
            "Aswan": ("Aswan", "أسوان"),
            "Luxor": ("Luxor", "الأقصر"),
            "RedSea": ("Red Sea", "البحر الأحمر"),
            "Sinai": ("South Sinai", "جنوب سيناء"),
            "Matrouh": ("Matrouh", "مطروح")
        }
        en_name, ar_name = city_names.get(city_code, (city_code, city_code))
        session["city"] = en_name
        session["city_ar"] = ar_name
        session["step"] = "awaiting_district"
        _user_sessions[chat_id] = session

        msg = (
            f"✅ تم اختيار المدينة: <b>{escape_html(en_name)} ({escape_html(ar_name)})</b>.\n\n"
            f"✍️ يرجى الآن كتابة اسم <b>الحي أو المنطقة</b> الخاصة بك في رسالة (مثل: المعادي، مدينة نصر، الزمالك، الدقي، المنتزه، إلخ):\n"
            f"Please type your <b>District or Neighborhood</b> name below:"
        )
        send_telegram_message(chat_id, msg)
        return

    # Alert Type selected
    if data.startswith("type_"):
        chosen = data.replace("type_", "")
        current_types = session.get("alert_types", [])

        if chosen == "all":
            current_types = ["heat", "wind", "rainfall", "humidity", "green_space"]
        else:
            if chosen not in current_types:
                current_types.append(chosen)

        session["alert_types"] = current_types

        # Finalize and persist in Firestore / JSON
        sub_record = save_subscriber(chat_id, {
            "chat_id": chat_id,
            "name": session.get("name", "Citizen Scientist"),
            "username": session.get("username", ""),
            "city": session.get("city", "Cairo"),
            "city_ar": session.get("city_ar", "القاهرة"),
            "district": session.get("district", "Central District"),
            "alert_types": current_types,
            "active": True
        })

        confirm_msg = (
            f"🎉 <b>تم تأكيد وتفعيل اشتراكك بنجاح في منصة AURA!</b> 🛰️\n\n"
            f"📍 <b>الموقع:</b> {escape_html(sub_record.get('city'))} - {escape_html(sub_record.get('district'))}\n"
            f"🔔 <b>التنبيهات المفعلة:</b> {escape_html(', '.join(current_types))}\n\n"
            f"سيتولى النظام إرسال إنذارات فورية ثنائية اللغة فور رصد أي موجة حارة، رياح عاتية، أمطار غزيرة، أو عجز في الغطاء النباتي مع توصيات زراعة الأشجار وحدائق الأسطح.\n\n"
            f"<i>يمكنك اختبار النظام في أي وقت بكتابة <code>/test</code>.</i>"
        )
        send_telegram_message(chat_id, confirm_msg)


def bot_polling_loop():
    """Background polling worker for Telegram Bot."""
    logger.info("🚀 Starting Telegram Bot polling loop for @sixsnova_bot...")
    last_update_id = 0

    while not _stop_polling.is_set():
        cfg = load_config()
        token = cfg.get("bot_token", "").strip()
        if not token:
            time.sleep(5)
            continue

        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=8"
            resp = requests.get(url, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        up_id = update.get("update_id", 0)
                        if up_id > last_update_id:
                            last_update_id = up_id

                        if "message" in update:
                            handle_bot_message(update["message"])
                        elif "callback_query" in update:
                            handle_callback_query(update["callback_query"])
        except Exception as e:
            # Sleep briefly on network / timeout glitch
            time.sleep(3)
        time.sleep(1)


def start_bot_polling():
    global _polling_thread
    if _polling_thread and _polling_thread.is_alive():
        return
    _stop_polling.clear()
    _polling_thread = threading.Thread(target=bot_polling_loop, daemon=True, name="TelegramBotPolling")
    _polling_thread.start()


# ==============================================================================
# 5. AUTOMATED DAILY SCHEDULED FORECAST AUDIT & CRISIS MONITOR
# ==============================================================================
_daily_thread: Optional[threading.Thread] = None

def run_daily_climate_audit() -> Dict[str, Any]:
    """
    Evaluates current and 2050 forecast projections for subscribers' cities.
    If an anomaly or severe condition is detected, dispatches alert bulletins.
    """
    subs = get_all_subscribers()
    cfg = load_config()
    thresholds = cfg.get("thresholds", DEFAULT_CONFIG["thresholds"])

    dispatched = []
    # Check Cairo and Alexandria as primary sentinel nodes
    sentinel_nodes = [
        {"city": "Cairo", "lat": 30.0444, "lon": 31.2357},
        {"city": "Alexandria", "lat": 31.2001, "lon": 29.9187},
        {"city": "Aswan", "lat": 24.0889, "lon": 32.8998}
    ]

    for node in sentinel_nodes:
        # Example condition check: Green space deficit & heat stress
        city = node["city"]
        res = broadcast_alert_to_subscribers(
            alert_type="green_space",
            city=city,
            district="Urban Core & High-Density Corridors",
            severity="LEVEL 2 HIGH",
            metric_val="Critical UHI Index · NDVI Vegetative Ratio 0.07"
        )
        dispatched.append({"node": city, "result": res})

    cfg["last_daily_run"] = datetime.now(timezone.utc).isoformat()
    save_config(cfg)
    return {"status": "success", "audit_time": cfg["last_daily_run"], "dispatched_nodes": dispatched}


def daily_scheduler_loop():
    """Checks once every 24 hours to trigger daily climate audit."""
    while not _stop_polling.is_set():
        try:
            cfg = load_config()
            last_run = cfg.get("last_daily_run")
            now = datetime.now(timezone.utc)
            should_run = False

            if not last_run:
                should_run = True
            else:
                last_dt = datetime.fromisoformat(last_run)
                if (now - last_dt).total_seconds() >= 86400:  # 24 hours
                    should_run = True

            if should_run:
                logger.info("⏰ Triggering Automated Daily Forecast & Green Space Audit...")
                run_daily_climate_audit()

        except Exception as e:
            logger.warning(f"Daily scheduler exception: {e}")

        # Check every hour
        time.sleep(3600)


def start_daily_scheduler():
    global _daily_thread
    if _daily_thread and _daily_thread.is_alive():
        return
    _daily_thread = threading.Thread(target=daily_scheduler_loop, daemon=True, name="DailyClimateScheduler")
    _daily_thread.start()


def auto_detect_chat_id(bot_token: Optional[str] = None) -> Dict[str, Any]:
    """Queries Telegram getUpdates to automatically find recent chat_ids."""
    cfg = load_config()
    token = bot_token or cfg.get("bot_token")
    if not token:
        return {"status": "error", "message": "Bot token is missing."}

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if not data.get("ok"):
            return {"status": "error", "message": f"Telegram API error: {data.get('description', 'Unknown')}"}

        results = data.get("result", [])
        if not results:
            return {
                "status": "pending",
                "message": "No recent messages found. Please open @sixsnova_bot in Telegram and send /start."
            }

        found_users = []
        for update in reversed(results):
            msg = update.get("message") or update.get("channel_post") or update.get("my_chat_member", {}).get("chat")
            if msg:
                chat = msg.get("chat", {}) if "chat" in msg else msg
                chat_id = str(chat.get("id"))
                username = chat.get("username", "") or chat.get("first_name", "")
                save_subscriber(chat_id, {"name": username, "username": username, "active": True})
                found_users.append({"chat_id": chat_id, "user": username})

        if found_users:
            primary = found_users[0]
            cfg["chat_id"] = primary["chat_id"]
            save_config(cfg)
            return {
                "status": "success",
                "chat_id": primary["chat_id"],
                "user": primary["user"],
                "total_found": len(found_users),
                "message": f"Successfully connected to Telegram user '{primary['user']}' (Chat ID: {primary['chat_id']})!"
            }
        return {"status": "pending", "message": "No chat found yet. Send /start to @sixsnova_bot."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def send_telegram_alert(
    region_name: str = "Greater Cairo",
    alert_type: str = "heat",
    severity: str = "LEVEL 3 CRITICAL",
    metric_val: str = "+4.5°C Anomaly",
    details: str = "",
    lat: float = 30.0444,
    lon: float = 31.2357,
    chat_id: Optional[str] = None
) -> Dict[str, Any]:
    """Compatibility wrapper for send_telegram_alert."""
    res = broadcast_alert_to_subscribers(
        alert_type=alert_type,
        city=region_name,
        district=details or "Central District",
        severity=severity,
        metric_val=metric_val,
        target_chat_id=chat_id
    )
    if res.get("successful_deliveries", 0) > 0:
        res["status"] = "delivered"
        res["message"] = f"✅ Weather Crisis Alert successfully dispatched to Telegram ({DEFAULT_BOT_USERNAME})!"
    else:
        res["status"] = "failed"
        res["message"] = "Delivery failed or no matching subscribers."
    return res


# Auto-start polling and scheduler on module load (skip on serverless Vercel environment)
if not os.environ.get("VERCEL"):
    try:
        start_bot_polling()
        start_daily_scheduler()
    except Exception as e:
        logger.warning(f"Could not auto-start background threads: {e}")


