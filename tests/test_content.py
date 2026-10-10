import json
import unittest
from pathlib import Path

import server

BASE = Path(__file__).resolve().parent.parent
LAB_PATHS = ("/fragile", "/durci", "/absent", "/erreur")
# Les identifiants de mission sont enregistrés dans la progression : les renommer la casserait.
COURSE_ORDER = ["socle", "portpilot", "headerscope", "fileguard", "toolwrap", "reconwrap"]
STEP_IDS = {f"{course}-mr{n}" for course in COURSE_ORDER for n in (1, 2, 3)}


class CourseContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((BASE / "content" / "courses.json").read_text(encoding="utf-8"))
        cls.courses = {course["id"]: course for course in cls.data["courses"]}

    def test_courses_match_server_and_keep_progression_ids(self):
        self.assertEqual([c["id"] for c in self.data["courses"]], COURSE_ORDER)
        self.assertEqual(set(self.courses), server.COURSES)
        step_ids = [step["id"] for course in self.courses.values() for step in course["steps"]]
        self.assertEqual(len(step_ids), len(set(step_ids)))
        self.assertEqual(set(step_ids), STEP_IDS)

    def test_every_course_is_five_hours_and_total_is_the_sum(self):
        self.assertEqual(self.data["totalMinutes"], 300 * len(COURSE_ORDER))
        for course in self.courses.values():
            with self.subTest(course=course["id"]):
                self.assertEqual(course["durationMinutes"], 300)
                self.assertEqual(sum(item["minutes"] for item in course["timeline"]), 300)
                self.assertEqual(len(course["steps"]), 3)

    def test_cases_are_complete_and_identifiers_unique(self):
        for course in self.courses.values():
            seen = set()
            for step in course["steps"]:
                for case in step.get("tests", []) + step.get("demos", []):
                    with self.subTest(course=course["id"], case=case.get("id")):
                        self.assertTrue(all(case.get(k) for k in ("id", "title", "input", "expected")))
                        self.assertNotIn(case["id"], seen)
                        seen.add(case["id"])

    def test_automated_tests_never_depend_on_the_lab(self):
        # Le runner GitLab n'a pas accès au laboratoire : ces cas relèvent de la démonstration.
        for course in self.courses.values():
            for step in course["steps"]:
                for case in step.get("tests", []):
                    text = " ".join(str(case[k]) for k in ("title", "input", "expected"))
                    with self.subTest(case=case["id"]):
                        self.assertFalse(any(path in text for path in LAB_PATHS), text)

    def test_paliers_are_well_formed(self):
        for course in self.courses.values():
            for step in course["steps"]:
                paliers = step.get("paliers")
                if not paliers:
                    continue
                with self.subTest(step=step["id"]):
                    ids = [p["id"] for p in paliers]
                    self.assertEqual(len(ids), len(set(ids)))
                    self.assertTrue(all(i.startswith(step["id"] + "-p") for i in ids))
                    self.assertEqual(sum(p["minutes"] for p in paliers), step["minutes"])
                    known = {t["id"] for t in step.get("tests", [])}
                    used = [t for p in paliers for t in p.get("tests", [])]
                    self.assertEqual(set(used), known, "chaque test est demandé dans un palier")
                    for p in paliers:
                        self.assertTrue(all(p.get(k) for k in ("title", "goal", "do", "check", "hint")), p["id"])

    def test_local_links_and_documents_exist(self):
        for course in self.courses.values():
            self.assertTrue((BASE / "content" / f"{course['id']}.md").is_file())
            for link in course.get("references", []) + course.get("resources", []):
                url = link["url"]
                if url.startswith("/content/"):
                    self.assertTrue((BASE / "content" / url[len("/content/"):]).is_file(), url)
                elif url.startswith("/downloads/"):
                    self.assertTrue((BASE / "web" / "downloads" / url[len("/downloads/"):]).is_file(), url)
                else:
                    self.assertTrue(url.startswith("https://"), url)

    def test_fileguard_fixtures_are_where_the_setup_says(self):
        commands = " ".join(item.get("command", "") for item in self.courses["fileguard"]["setup"])
        self.assertIn("/app/fixtures/integrity", commands)
        names = {p.name for p in (BASE / "fixtures" / "integrity").iterdir()}
        self.assertEqual(names, {"README.txt", "message.txt", "settings.ini"})

    def test_setup_steps_are_well_formed(self):
        for course in self.courses.values():
            for item in course["setup"]:
                with self.subTest(course=course["id"], step=item["label"]):
                    self.assertTrue(item["label"].strip())
                    self.assertIsInstance(item.get("interactive", False), bool)


if __name__ == "__main__":
    unittest.main()
