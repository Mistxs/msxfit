"""OCR через нативный Apple Vision (VNRecognizeTextRequest) — движок Live Text.

Первичный путь на macOS: точнее tesseract, особенно на русском. Фото с iPhone
уходит на backend (на Маке), где и распознаётся Vision-ом — облако не участвует.
Доступно только на macOS; на других ОС available() → False и api откатывается
на tesseract / ручной ввод.
"""
import logging

log = logging.getLogger(__name__)

_VISION = None
_TRIED = False


def _vision():
    global _VISION, _TRIED
    if _TRIED:
        return _VISION
    _TRIED = True
    try:
        from Foundation import NSData
        from Vision import VNImageRequestHandler, VNRecognizeTextRequest

        _VISION = (NSData, VNImageRequestHandler, VNRecognizeTextRequest)
        log.info("Apple Vision available")
    except Exception as e:  # не macOS или нет фреймворка
        log.info("Apple Vision unavailable: %s", e)
        _VISION = None
    return _VISION


def available():
    return _vision() is not None


def recognize(image_bytes, languages=("ru-RU", "en-US")):
    """Возвращает распознанный текст (строки через \\n)."""
    mods = _vision()
    if not mods:
        raise RuntimeError("Apple Vision not available on this host")
    NSData, VNImageRequestHandler, VNRecognizeTextRequest = mods

    data = NSData.dataWithBytes_length_(image_bytes, len(image_bytes))
    handler = VNImageRequestHandler.alloc().initWithData_options_(data, None)
    request = VNRecognizeTextRequest.alloc().init()
    try:
        request.setRecognitionLanguages_(list(languages))
    except Exception as e:  # язык может быть недоступен — оставим дефолт
        log.debug("setRecognitionLanguages failed: %s", e)
    try:
        request.setUsesLanguageCorrection_(True)
    except Exception:
        pass

    try:
        ok = handler.performRequests_error_([request], None)
    except Exception as e:  # PyObjC поднимает исключение при ошибке распознавания
        log.warning("Vision performRequests error: %s", e)
        return ""
    if not ok:
        return ""

    lines = []
    for obs in (request.results() or []):
        try:
            cands = obs.topCandidates_(1)
            if cands:
                lines.append(cands[0].string())
        except Exception:
            continue
    return "\n".join(lines)
