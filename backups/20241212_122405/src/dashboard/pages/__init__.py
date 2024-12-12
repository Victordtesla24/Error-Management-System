"""Dashboard pages package."""

from .Agents import main as agents_page
from .ErrorList import main as error_list_page
from .Monitoring import main as monitoring_page
from .Projects import main as projects_page
from .Settings import main as settings_page

__all__ = [
    "agents_page",
    "error_list_page",
    "monitoring_page",
    "projects_page",
    "settings_page",
]
