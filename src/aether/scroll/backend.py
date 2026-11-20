from evdev import UInput, ecodes


class EvdevScrollBackend:
    """Emits vertical and horizontal scroll events."""

    def __init__(self) -> None:
        self.device = UInput(
            {
                ecodes.EV_REL: [
                    ecodes.REL_WHEEL,
                    ecodes.REL_HWHEEL,
                ],
            },
            name="AETHER Virtual Touchpad",
            bustype=ecodes.BUS_USB,
        )

    def scroll(self, vertical: int = 0, horizontal: int = 0) -> None:
        if not isinstance(vertical, int) or isinstance(vertical, bool):
            raise TypeError("vertical must be an integer")

        if not isinstance(horizontal, int) or isinstance(horizontal, bool):
            raise TypeError("horizontal must be an integer")

        if vertical:
            self.device.write(
                ecodes.EV_REL,
                ecodes.REL_WHEEL,
                vertical,
            )

        if horizontal:
            self.device.write(
                ecodes.EV_REL,
                ecodes.REL_HWHEEL,
                horizontal,
            )

        if vertical or horizontal:
            self.device.syn()

    def close(self) -> None:
        self.device.close()