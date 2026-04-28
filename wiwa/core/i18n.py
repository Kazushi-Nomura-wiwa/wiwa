# パスとファイル名: wiwa/core/i18n.py

from wiwa.config import DEFAULT_LANG

from wiwa.locales.ja import MESSAGES as JA_MESSAGES
from wiwa.locales.en import MESSAGES as EN_MESSAGES


MESSAGES = {
    "ja": JA_MESSAGES,
    "en": EN_MESSAGES,
}


def t(key: str, lang: str | None = None) -> str:
    """
    翻訳メッセージを取得する
    Get translated message
    """

    current_lang = lang or DEFAULT_LANG

    return (
        MESSAGES
        .get(current_lang, MESSAGES["ja"])
        .get(key, key)
    )