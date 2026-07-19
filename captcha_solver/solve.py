import os
import io

import numpy as np
from PIL import Image
import onnxruntime

_MODEL_FILE = os.path.join(os.path.dirname(__file__), "best.onnx")
_CANVAS = 384
_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
_MIN_SCORE = 0.3
_PAD = (114, 114, 114)


class _Detector:
    def __init__(self):
        self._engine = None
        self._feed = None

    def _ensure_loaded(self):
        if self._engine is None:
            self._engine = onnxruntime.InferenceSession(
                _MODEL_FILE, providers=["CPUExecutionProvider"]
            )
            self._feed = self._engine.get_inputs()[0].name

    @staticmethod
    def _fit_square(frame):
        pic = Image.fromarray(frame)
        width, height = pic.size
        ratio = min(_CANVAS / width, _CANVAS / height)
        target = (max(1, int(width * ratio)), max(1, int(height * ratio)))
        shrunk = pic.resize(target, Image.BILINEAR)

        canvas = Image.new("RGB", (_CANVAS, _CANVAS), _PAD)
        offset = ((_CANVAS - target[0]) // 2, (_CANVAS - target[1]) // 2)
        canvas.paste(shrunk, offset)
        return np.asarray(canvas)

    def _to_tensor(self, frame):
        tensor = self._fit_square(frame).astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))
        return tensor[np.newaxis, ...]

    def predict(self, frame, expected=None):
        self._ensure_loaded()
        tensor = self._to_tensor(frame)
        raw = self._engine.run(None, {self._feed: tensor})[0][0]

        found = []
        for row in raw:
            ax, ay, bx, by, score, label = row
            if score < _MIN_SCORE:
                continue
            found.append((float((ax + bx) / 2), float(score), _ALPHABET[int(label)]))

        if expected and len(found) > expected:
            found.sort(key=lambda item: item[1], reverse=True)
            found = found[:expected]

        found.sort(key=lambda item: item[0])
        return "".join(item[2] for item in found)


_detector = _Detector()


def get_strategy_count():
    return 1


def _read_frame(source):
    if isinstance(source, (bytes, bytearray)):
        handle = Image.open(io.BytesIO(source))
    else:
        handle = Image.open(source)
    handle.load()
    return np.asarray(handle.convert("RGB"))


def solve_captcha(img_path, strategy_index=0, letter_count=None):
    return _detector.predict(_read_frame(img_path), expected=letter_count)
