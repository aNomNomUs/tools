import json
import unittest
from datetime import date
from http.server import HTTPServer
from threading import Thread
from urllib.request import urlopen

from astrology.compatibility import compatibility_report, compatibility_score
from astrology.constants import ZODIAC_SIGNS
from astrology.horoscope import HoroscopeEngine
from astrology.profile import profile_payload, sign_from_birthday
from astrology.server import AstroRequestHandler
from astrology.utils import derive_seed, pick_deterministic, sanitize_sign_name


class UtilsTests(unittest.TestCase):
    def test_sanitize_sign_name_rejects_bad_chars(self):
        with self.assertRaises(ValueError):
            sanitize_sign_name("Virgo!!!")

    def test_pick_deterministic_raises_on_empty(self):
        with self.assertRaises(ValueError):
            pick_deterministic([], 1)

    def test_derive_seed_stable(self):
        self.assertEqual(derive_seed("Aries", "2024-01-01"), derive_seed("Aries", "2024-01-01"))


class ProfileTests(unittest.TestCase):
    def test_sign_from_birthday_maps(self):
        self.assertEqual(sign_from_birthday(date(2024, 4, 5)), "Aries")

    def test_profile_payload_validation(self):
        with self.assertRaises(ValueError):
            profile_payload(" ", date(2024, 4, 5))


class HoroscopeTests(unittest.TestCase):
    def test_generate_known_template(self):
        engine = HoroscopeEngine()
        text = engine.generate("Aries", date(2024, 3, 22))
        self.assertTrue(text)
        self.assertNotIn("Aries", text)

    def test_invalid_sign_raises(self):
        engine = HoroscopeEngine()
        with self.assertRaises(ValueError):
            engine.generate("NotASign", date.today())


class CompatibilityTests(unittest.TestCase):
    def test_score_symmetric(self):
        for sign in ZODIAC_SIGNS:
            self.assertGreaterEqual(compatibility_score(sign, sign), 80)

    def test_report_fields(self):
        report = compatibility_report("Aries", "Gemini")
        self.assertTrue({"primary", "partner", "score", "vibe"}.issubset(report.keys()))


class ServerTests(unittest.TestCase):
    def test_healthz(self):
        server = HTTPServer(("127.0.0.1", 0), AstroRequestHandler)
        host, port = server.server_address
        thread = Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        try:
            with urlopen(f"http://{host}:{port}/healthz") as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(payload["ok"])
        finally:
            server.shutdown()
            thread.join()
            server.server_close()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
