import logging


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='{"level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
    )
