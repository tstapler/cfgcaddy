import logging
from typing import Collection

import cfgcaddy.utils as utils
from cfgcaddy.link import create_links, find_absences
from cfgcaddy.link_spec import LinkSpec, LinkingResult
from cfgcaddy.utils import create_dirs

logger = logging.getLogger()


class Linker:
    """Tyler Stapler's Config Linker"""

    custom_links: Collection[LinkSpec]

    def __init__(self, linker_config, interactive=True) -> None:

        if not linker_config:
            raise Exception("Linker requires Config!")

        self.config = linker_config
        self.interactive = interactive

        self.custom_links = self.config.links
        self.ignored_patterns = self.config.ignore_patterns

    def create_links(self) -> None:
        """Symlinks configuration files to the destination directory

        Parses the ignore file for regexes and then generates a list of files
        which need to be symlinked"""

        # TODO: Rewrite find_absences
        absent_files, absent_dirs = find_absences(
            self.config.linker_src, self.config.linker_dest, self.ignored_patterns
        )

        if not absent_files and not absent_dirs:
            logger.info("Nothing to do")
            return

        logger.info("Preparing to symlink the following files")
        logger.info("\n".join(str(link.dest) for link in absent_files))
        if not self.interactive or utils.user_confirm("Are these the correct files?"):
            create_dirs(dirs=absent_dirs)
            create_links(links=absent_files)

    def create_custom_links(self) -> None:
        """Link all the files in the customlink file

        Returns:
            None
        """
        modified = LinkingResult.SKIPPED

        for link in self.custom_links:
            modified = link.create(interactive=self.interactive)

        if not modified:
            logger.info("No folders to link")
