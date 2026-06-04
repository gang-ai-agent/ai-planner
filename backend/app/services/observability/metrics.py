class Metrics:
    def increment(self, name: str, labels: dict[str, str] | None = None) -> None:
        _ = (name, labels)

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        _ = (name, value, labels)


metrics = Metrics()
