"""Plugin system for DJ Press."""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


# Hook definitions
class Hooks(Enum):
    """Available hook points in DJ Press."""

    PRE_RENDER_CONTENT = "pre_render_content"
    POST_RENDER_CONTENT = "post_render_content"
    POST_SAVE_POST = "post_save_post"
    DJ_HEADER = "dj_header"
    DJ_FOOTER = "dj_footer"
