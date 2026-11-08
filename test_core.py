import os
import tempfile
import unittest
from pathlib import Path

from renamekit import Options, apply_renames, plan_renames, undo_renames
from renamekit.core import to_kebab, to_snake


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self._cwd = os.getcwd()
        os.chdir(self.dir)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def make(self, *names):
        for n in names:
            (self.dir / n).write_text(n)
        return [self.dir / n for n in names]


class TestCases(unittest.TestCase):
    def test_snake(self):
        self.assertEqual(to_snake("My Cool-File"), "my_cool_file")
        self.assertEqual(to_snake("camelCaseName"), "camel_case_name")

    def test_kebab(self):
        self.assertEqual(to_kebab("My Cool_File"), "my-cool-file")


class TestPlan(Base):
    def test_replace(self):
        files = self.make("a_old.txt", "b_old.txt")
        plan = plan_renames(files, Options(replace=("old", "new")))
        self.assertEqual([d.name for _, d in plan], ["a_new.txt", "b_new.txt"])

    def test_number_and_ext(self):
        files = self.make("x.JPG", "y.JPG")
        plan = plan_renames(files, Options(number=True, lower_ext=True, width=2))
        self.assertEqual([d.name for _, d in plan], ["x_01.jpg", "y_02.jpg"])

    def test_duplicate_targets_rejected(self):
        files = self.make("a1.txt", "a2.txt")
        with self.assertRaises(ValueError):
            plan_renames(files, Options(regex=(r"\d", "")))

    def test_existing_target_rejected(self):
        files = self.make("a.txt", "b.txt")
        with self.assertRaises(ValueError):
            plan_renames(files[:1], Options(replace=("a", "b")))


class TestApplyUndo(Base):
    def test_apply_and_undo(self):
        files = self.make("one.txt", "two.txt")
        plan = plan_renames(files, Options(prefix="x_"))
        apply_renames(plan)
        self.assertTrue((self.dir / "x_one.txt").exists())
        self.assertEqual(undo_renames(), 2)
        self.assertTrue((self.dir / "one.txt").exists())
        self.assertFalse((self.dir / "x_one.txt").exists())

    def test_swap_works(self):
        files = self.make("a.txt", "b.txt")
        (self.dir / "a.txt").write_text("A")
        (self.dir / "b.txt").write_text("B")
        plan = [(files[0], self.dir / "b.txt"), (files[1], self.dir / "a.txt")]
        apply_renames(plan)
        self.assertEqual((self.dir / "b.txt").read_text(), "A")
        self.assertEqual((self.dir / "a.txt").read_text(), "B")


if __name__ == "__main__":
    unittest.main()
