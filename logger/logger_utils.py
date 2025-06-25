from logger.logger_manager import LoggerManager


def shutdown_logger():
    """
    Gracefully shuts down all active loggers and closes their handlers.
    Required before deleting log files on Windows.
    """
    logger = LoggerManager.get_logger()

    handlers = logger.handlers[:]
    for handler in handlers:
        try:
            handler.close()
            logger.removeHandler(handler)
        except Exception as e:
            print(f"[LOGGER WARNING] Failed to close handler: {e}")
