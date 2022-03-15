import dataclasses
import filecmp
from pathlib import Path
from typing import List

import pytest
from _pytest.mark.structures import ParameterSet

from cfgcaddy.link import Link, LinkingResult


def create_directory_of_fixtures(prefix: Path, fixtures: List[str]):
    """Create a directory of test fixtures from a list of strings

    Slashes at the end of a string indicate a directory
    Slashes in the middle of a string will be interpreted as a directory/file relationship
    """
    for f in fixtures:
        p = Path(prefix, f)
        if f.endswith("/"):
            p.mkdir(parents=True, exist_ok=True)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()


@dataclasses.dataclass
class LinkTestCase:
    description: str
    src_tree: List[str]
    dest_tree: List[str]
    link_src: str
    link_dest: str
    expected_src_tree: List[str]
    expected_dest_tree: List[str]
    link_result: LinkingResult

    def initialize_fixture_directories(
        self,
        src_dir: Path,
        dest_dir: Path,
        expected_src_dir: Path,
        expected_dest_dir: Path,
    ):
        src_dir.mkdir(exist_ok=True, parents=True)
        create_directory_of_fixtures(src_dir, self.src_tree)
        dest_dir.mkdir(exist_ok=True, parents=True)
        create_directory_of_fixtures(dest_dir, self.dest_tree)
        expected_src_dir.mkdir(exist_ok=True, parents=True)
        create_directory_of_fixtures(expected_src_dir, self.src_tree)
        expected_dest_dir.mkdir(exist_ok=True, parents=True)
        create_directory_of_fixtures(expected_dest_dir, self.dest_tree)

    def to_pytest_param(self) -> ParameterSet:
        return pytest.param(self, id=self.description)


@pytest.mark.parametrize(
    "test_case",
    [
        LinkTestCase(
            description="src dir exists, dest directory missing",
            src_tree=["file1", "dir1/file2"],
            dest_tree=[],
            link_src="dir1",
            link_dest="dir1",
            expected_src_tree=["file1", "dir1/file2"],
            expected_dest_tree=["file1", "dir1/file2"],
            link_result=LinkingResult.CREATED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src dir exists, dest dir exists",
            src_tree=["dir1/file2"],
            dest_tree=["dir1/file3"],
            link_src="dir1",
            link_dest="dir1",
            expected_src_tree=["dir1/file2", "dir1/file3"],
            expected_dest_tree=["dir1/file2", "dir1/file3"],
            link_result=LinkingResult.CREATED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src dir missing, dest dir exists",
            src_tree=[],
            dest_tree=["dir1/file3"],
            link_src="dir1",
            link_dest="dir1",
            expected_src_tree=["dir1/file3"],
            expected_dest_tree=["dir1/file3"],
            link_result=LinkingResult.CREATED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src dir missing, dest dir missing",
            src_tree=[],
            dest_tree=[],
            link_src="dir1",
            link_dest="dir1",
            expected_src_tree=[],
            expected_dest_tree=[],
            link_result=LinkingResult.SKIPPED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src file exists, dest file missing",
            src_tree=["file1"],
            dest_tree=[],
            link_src="file1",
            link_dest="file1",
            expected_src_tree=["file1"],
            expected_dest_tree=["file1"],
            link_result=LinkingResult.CREATED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src file missing, dest file exists",
            src_tree=[],
            dest_tree=["file1"],
            link_src="file1",
            link_dest="file1",
            expected_src_tree=["file1"],
            expected_dest_tree=["file1"],
            link_result=LinkingResult.CREATED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src exists, dest file exists",
            src_tree=["file1"],
            dest_tree=["file1"],
            link_src="file1",
            link_dest="file1",
            expected_src_tree=["file1"],
            expected_dest_tree=["file1"],
            link_result=LinkingResult.SKIPPED,
        ).to_pytest_param(),
        LinkTestCase(
            description="src missing, dest file missing",
            src_tree=[""],
            dest_tree=[""],
            link_src="file1",
            link_dest="file1",
            expected_src_tree=["file1"],
            expected_dest_tree=["file1"],
            link_result=LinkingResult.SKIPPED,
        ).to_pytest_param(),
    ],
)
def test_link_create(tmp_path: Path, test_case: LinkTestCase):
    src_dir = Path(tmp_path, "src")
    dest_dir = Path(tmp_path, "dest")
    expected_src_dir = Path(tmp_path, "expected_src")
    expected_dest_dir = Path(tmp_path, "expected_dest")
    test_case.initialize_fixture_directories(
        src_dir, dest_dir, expected_src_dir, expected_dest_dir
    )
    link = Link(Path(src_dir, test_case.link_src), Path(dest_dir, test_case.link_dest))
    assert link.create() == test_case.link_result
    for expected, actual in [
        (expected_src_dir, src_dir),
        (expected_dest_dir, dest_dir),
    ]:
        comp = filecmp.dircmp(expected, actual)
        try:
            assert not comp.diff_files
        except AssertionError as e:
            comp.report_full_closure()
            raise e
