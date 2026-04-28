# パスとファイル名: wiwa/core/i18n.py
# Path and filename: wiwa/core/i18n.py

# i18nユーティリティ
# Internationalization utilities
#
# 概要
# Summary
#   翻訳辞書からメッセージを取得し、言語を正規化する
#   Retrieve translated messages and normalize language codes
#
# 処理の流れ
# Flow
#   1. 言語コード正規化
#      Normalize language code
#   2. 翻訳辞書取得
#      Fetch translation dictionary
#   3. メッセージ取得
#      Get message by key
#   4. 変数埋め込み
#      Format message with variables

from wiwa.config import DEFAULT_LANG, SUPPORTED_LANGS

from wiwa.locales.ja import TRANSLATIONS as JA_TRANSLATIONS
from wiwa.locales.en import TRANSLATIONS as EN_TRANSLATIONS


# 言語ごとの翻訳辞書
# Translation dictionaries by language
TRANSLATIONS = {
    "ja": JA_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}


def normalize_lang(lang: str | None = None) -> str:
    """
    言語コードを正規化
    Normalize language code
    """
    current_lang = lang or DEFAULT_LANG

    if current_lang not in SUPPORTED_LANGS:
        return DEFAULT_LANG

    if current_lang not in TRANSLATIONS:
        return DEFAULT_LANG

    return current_lang


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """
    翻訳メッセージを取得
    Get translated message
    """
    current_lang = normalize_lang(lang)

    message = TRANSLATIONS[current_lang].get(key, key)

    if kwargs:
        try:
            return message.format(**kwargs)
        except Exception:
            return message

    return message