import time

from evdev import UInput, ecodes

capabilities = {
    ecodes.EV_REL: [
        ecodes.REL_X,
        ecodes.REL_Y,
        ecodes.REL_WHEEL,
        ecodes.REL_HWHEEL,
    ],
}

with UInput(
    capabilities,
    name="AETHER Virtual Mouse",
    bustype=ecodes.BUS_USB,
) as device:
    print("Dispositivo virtual criado.")
    input("Posicione o cursor sobre uma página e pressione Enter...")

    print("Rolando verticalmente...")

    for _ in range(30):
        device.write(ecodes.EV_REL, ecodes.REL_WHEEL, -1)
        device.syn()
        time.sleep(0.05)

    print("Teste concluído.")
