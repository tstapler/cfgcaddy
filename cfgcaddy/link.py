from __future__ import annotations

import logging
import os
import shutil
from os import path
from pathlib import Path
from typing import NoReturn, Union, Optional, List, Tuple, Sequence

import pathspec  # type: ignore

import cfgcaddy
from cfgcaddy.file_state import FileState
from cfgcaddy.link_spec import LinkSpec, LinkingResult
from cfgcaddy.utils import (
    user_confirm,
    make_parent_dirs,
    create_dirs,
    convert_to_path,
    Pathlike,
)

logger = logging.getLogger()


# MyPy based exhaustiveness check
def assert_never(value: NoReturn) -> NoReturn:
    assert False, f"Unhandled value: {value} ({type(value).__name__})"


def create_symlink(location: Path, target: Path) -> None:
    make_parent_dirs(location)
    location.symlink_to(target, target_is_directory=target.is_dir())


class Link(LinkSpec):
    src: Path
    dest: Path

    def __init__(self, src: Union[str, Path], dest: Union[str, Path]):
        self.src = convert_to_path(src)
        self.dest = convert_to_path(dest)

    def create(self, interactive: bool = False) -> LinkingResult:
        dest_state = FileState.from_pathlike(self.dest)
        src_state = FileState.from_pathlike(self.src)
        if dest_state is FileState.UNKNOWN:
            logger.debug(
                f"Link destination {self.dest} is an unrecognized filetype, skipping"
            )
            return LinkingResult.SKIPPED

        if src_state is FileState.UNKNOWN:
            logger.debug(
                f"Link target {self.src} is an unrecognized filetype, skipping"
            )
            return LinkingResult.SKIPPED

        if dest_state in [FileState.LINK_FILE, FileState.LINK_DIRECTORY]:
            if self.dest.samefile(self.src):
                logger.debug(f"Skipping {self.dest}, already linked")
                return LinkingResult.SKIPPED
            else:
                logger.info(
                    f"{self.dest} is a symlink, please remove it if you want to link {self.src}"
                )
        if dest_state is FileState.BROKEN_LINK:
            if src_state in [
                FileState.FILE,
                FileState.DIRECTORY,
                FileState.LINK_FILE,
                FileState.LINK_DIRECTORY,
            ]:
                self.dest.unlink()
                create_symlink(self.dest, self.src)
            elif src_state in [FileState.MISSING, FileState.BROKEN_LINK]:
                return LinkingResult.SKIPPED
            else:
                assert_never(src_state)
        elif dest_state is FileState.FILE:
            if src_state in [FileState.FILE, FileState.DIRECTORY, FileState.LINK]:
                logger.info(
                    f"{self.dest} is a file, move/rename it if you want a link to {self.src}."
                )
                return LinkingResult.SKIPPED
            elif src_state is FileState.MISSING:
                logger.info(f"Copying {self.dest} to {self.src} and symlinking")
                shutil.move(self.dest, self.src)
                create_symlink(self.dest, self.src)
                return LinkingResult.CREATED
            elif src_state is FileState.BROKEN_LINK:
                self.src.unlink()
                logger.info(f"Copying {self.dest} to {self.src} and symlinking")
                shutil.move(self.dest, self.src)
                create_symlink(self.dest, self.src)
                return LinkingResult.CREATED
            else:
                assert_never(src_state)
        elif dest_state is FileState.DIRECTORY:
            logger.debug(f"Link destination {self.dest} does not exist")
            if src_state in [FileState.FILE, FileState.LINK_FILE]:
                logger.info(
                    f"{self.dest} is a file and the link src {self.src} is a file, skipping"
                )
                return LinkingResult.SKIPPED
            elif src_state is FileState.BROKEN_LINK:
                self.src.unlink()
                return link_folder(self.src, self.dest, interactive=interactive)
            elif src_state in [
                FileState.DIRECTORY,
                FileState.LINK_DIRECTORY,
                FileState.MISSING,
            ]:
                return link_folder(self.src, self.dest, interactive=interactive)
            else:
                assert_never(src_state)
        elif dest_state is FileState.MISSING:
            logger.debug(f"Link destination {self.dest} does not exist")
            if src_state in [FileState.FILE, FileState.LINK_FILE]:
                logger.debug(f"Link target {self.src} is a file, linking")
                create_symlink(self.dest, self.src)
                return LinkingResult.CREATED
            elif src_state in [FileState.DIRECTORY, FileState.LINK_DIRECTORY]:
                logger.debug(f"Link target {self.src} is a directory, linking")
                return link_folder(self.src, self.dest, interactive=interactive)
            elif src_state in [FileState.MISSING, FileState.BROKEN_LINK]:
                logger.error(
                    f"Trying to link {self.dest} to {self.src} both files do not exist"
                )
                return LinkingResult.SKIPPED
            else:
                assert_never(src_state)
        assert_never(dest_state)


def link_folder(src: Path, dest: Path, interactive: bool = False) -> LinkingResult:
    """Link the folder src to the destination dest

    Args:
        src (path) - The path to link from
        dest (path) - The path to link to

    Returns:
        True if an operation was performed, else False
    """
    folder_name = path.basename(src).strip(".")

    try:
        # Both Folders Exist
        if path.exists(dest) and path.exists(src) and not path.islink(dest):
            if not interactive or user_confirm(
                "Link and merge {} to {}".format(src, dest)
            ):
                absent_files, absent_dirs = find_absences(dest, src)
                zip_file = shutil.make_archive(
                    path.join(src, "{}_backup".format(folder_name)),
                    "zip",
                    root_dir=dest,
                )
                logger.info("Backing up {} to {}".format(folder_name, zip_file))
                create_dirs(absent_dirs)
                logger.info("Created {}".format(absent_dirs))
                move_files(links=absent_files)
                logger.info("Moving files {}".format(absent_files))
                shutil.rmtree(dest)
                logger.info("Removed {}".format(dest))
                create_symlink(dest, src)
                logger.info("Symlinked {} to {}".format(src, dest))
                return LinkingResult.CREATED

        # Only the source exists
        elif not path.exists(dest) and not path.islink(dest) and path.exists(src):
            try:
                os.makedirs(path.dirname(dest), exist_ok=True)
            except Exception as e:
                logger.error("Failed to make dir {} - {}".format(dest, e))
                return LinkingResult.FAILED
            create_symlink(dest, src)
            logger.info("Symlinked {} to {}".format(src, dest))
            return LinkingResult.CREATED

        # Only the destination exists
        elif path.exists(dest) and not path.exists(src):
            if not interactive or user_confirm(
                "Delete, Move to {} and" " Link back to {}?".format(src, dest)
            ):
                shutil.move(dest, src)
                logger.info("Moving {} to {}".format(dest, src))
                os.symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src, dest))
                return LinkingResult.CREATED

        # Nothing to do
        logger.info(f"Skipping linking {src} to {dest}, not a supported usecase")
        return LinkingResult.SKIPPED

    except OSError as e:
        logger.error("Failed to link {} to {} - {}".format(src, dest, e))
        return LinkingResult.FAILED


def create_links(links: Optional[Sequence[LinkSpec]] = None) -> None:
    """Create symlinks for each item in links

    Args:
        links([Link]): a list of paths to link
    Returns:
        None: Does not return anything
    """
    if links:
        for link in links:
            try:
                make_parent_dirs(link.dest)
                os.symlink(link.src, link.dest)
            except OSError as err:
                # If the file exists and isn't a link
                if err.errno == 17 and not os.path.islink(link.dest):
                    logger.error(
                        "Can't make link from {} to {} because {}".format(
                            link.src, link.dest, err.strerror
                        )
                    )


def move_files(links: Sequence[LinkSpec]) -> None:
    """Move the files in the list from src to dest

    Args:
        links([Link])

    Returns:
        None: Does not return anything
    """
    if links:
        for link in links:
            try:
                shutil.move(link.src, link.dest)
            except OSError:
                logger.error("Can't move from {} to {}".format(link.src, link.dest))


def find_absences(
    src: Pathlike, dest: Pathlike, ignored_patterns: Optional[List[str]] = None
) -> Tuple[List[Link], List[str]]:
    """Walk the source directory and return a lists of files and dirs absent
        from the destination directory

    Args:
        src: The path to copy from (Default is the script's location)
        dest The path to copy to (Defaults to home directory)

    Returns:
        absent_files: a list of Links
        absent_dirs: a list of paths to directories
    """
    if not ignored_patterns:
        ignored_patterns = []
    absent_dirs = []
    absent_files = []

    default_ignore = ["!.*", cfgcaddy.DEFAULT_CONFIG_NAME, ".git"]

    ignored = pathspec.PathSpec.from_lines(
        "gitwildmatch", default_ignore + ignored_patterns
    )

    for root, dirs, files in os.walk(src, topdown=True):
        rel_path = path.relpath(root, src)
        if rel_path == ".":
            rel_path = ""

        # Remove ignored directories from the walk
        dirs[:] = [
            dir_name
            for dir_name in dirs
            if not ignored.match_file(path.join(root, dir_name))
        ]
        files[:] = [f for f in files if not ignored.match_file(path.join(root, f))]

        # Create list of dirs that don't exist
        for dir_name in dirs:
            pathname = path.join(dest, rel_path, dir_name)
            if not path.exists(pathname):
                if path.islink(pathname):
                    os.unlink(pathname)  # Fix Broken Links
                absent_dirs.append(pathname)

        # Create a list of files to be symlinked
        for f in files:
            pathname = path.join(dest, rel_path, f)
            if not path.exists(pathname):
                if path.islink(pathname):
                    os.unlink(pathname)  # Fix Broken Links
                # Add the source and destination for the symlink
                absent_files.append(Link(path.join(root, f), pathname))

    return absent_files, absent_dirs
