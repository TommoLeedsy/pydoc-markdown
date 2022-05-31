import dataclasses
import docspec
import logging
import os

from typing import List

from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.util.pages import Page, Pages

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MarkdownWikiRenderer(MarkdownRenderer):
    """
        Produces Markdown files in a layout compatible with [markdown wikis][0]

        Example configuration:

        ```yaml
        renderer:
          type: mkdocs
          pages:
            - title: Home
              name: index
              source: README.md
            - title: API Documentation
              contents:
                - '*'
        ```

        ### Options
        """

    #: The output directory for the generated Markdown files. Defaults to `docs`.
    output_directory: str = "docs"

    #: Remove files generated in a previous pass by the Mkdocs renderer before rendering
    #: again. Defaults to `True`.
    clean_render: bool = True

    #: If enabled, inserts anchors before Markdown headers to ensure that
    #: links to the header work. Defaults to `False`.
    insert_header_anchors: bool = False

    #: Render type hints for data elements in the header. Defaults to `True`
    render_typehint_in_data_header: bool = True

    #: The pages to render into the output directory.
    pages: Pages[Page] = dataclasses.field(default_factory=Pages)

    # Renderer

    def render(self, modules: List[docspec.Module]) -> None:
        assert self._context

        if self.clean_render:
            for sub_dir, dirs, files in os.walk(self.output_directory):
                for file in files:
                    os.remove(os.path.join(sub_dir, file))

        for item in self.pages.iter_hierarchy():
            filename = item.filename(self.output_directory, ".md", f"../{item.page.name}")
            if not filename:
                continue
            if not item.page.has_content():
                continue

            item.page.render(filename, modules, self, self._context.directory)
