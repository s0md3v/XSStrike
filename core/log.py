import logging
from rich.logging import RichHandler
from rich.console import Console
from typing import Optional, Any

console = Console()

# Define custom log levels (Modernized)
VULN_LEVEL_NUM = 60
RUN_LEVEL_NUM = 22
GOOD_LEVEL_NUM = 25

logging.addLevelName(VULN_LEVEL_NUM, 'VULN')
logging.addLevelName(RUN_LEVEL_NUM, 'RUN')
logging.addLevelName(GOOD_LEVEL_NUM, 'GOOD')

# Global configurations (for legacy modules compatibility)
console_log_level = 'INFO'
file_log_level: Optional[str] = None
log_file = 'xsstrike.log'

class XSStrikeLogger(logging.Logger):
    def vuln(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(VULN_LEVEL_NUM):
            self._log(VULN_LEVEL_NUM, msg, args, **kwargs)

    def run(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(RUN_LEVEL_NUM):
            self._log(RUN_LEVEL_NUM, msg, args, **kwargs)

    def good(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(GOOD_LEVEL_NUM):
            self._log(GOOD_LEVEL_NUM, msg, args, **kwargs)

    def no_format(self, msg: str = '', level: str = 'INFO') -> None:
        """Legacy support for logging without format using Rich console."""
        console.print(msg)

    def red_line(self, amount: int = 60, level: str = 'INFO') -> None:
        """Legacy support for printing a separator line."""
        console.print("-" * amount, style="bold red")

    def debug_json(self, msg: str = '', data: Any = None) -> None:
        if self.isEnabledFor(logging.DEBUG):
            import json
            try:
                formatted_data = json.dumps(data, indent=2)
                self.debug(f"{msg} {formatted_data}")
            except (TypeError, ValueError):
                self.debug(f"{msg} {data}")

def setup_logger(name: str = 'xsstrike') -> XSStrikeLogger:
    logging.setLoggerClass(XSStrikeLogger)
    logger = logging.getLogger(name)
    logger.handlers = [] # Clear existing handlers
    
    # Rich handler for console
    level = getattr(logging, console_log_level.upper(), logging.INFO)
    rich_handler = RichHandler(
        console=console,
        show_path=False,
        omit_repeated_times=False,
        rich_tracebacks=True,
        markup=True
    )
    rich_handler.setLevel(level)
    logger.addHandler(rich_handler)

    # File handler if requested
    if file_log_level:
        file_level = getattr(logging, file_log_level.upper(), logging.INFO)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)
    return logger # type: ignore
