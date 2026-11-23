
import psutil


def get_cpu_usage():
    cpu = psutil.cpu_percent(interval=0.5)
    return f"CPU usage is {cpu:.0f} percent, sir."


def get_ram_usage():
    ram = psutil.virtual_memory()

    used = ram.used / (1024 ** 3)
    total = ram.total / (1024 ** 3)

    return (
        f"Memory usage is {ram.percent:.0f} percent. "
        f"{used:.1f} gigabytes used out of "
        f"{total:.1f} gigabytes, sir."
    )


def get_battery_status():
    battery = psutil.sensors_battery()

    if battery is None:
        return "Battery information is unavailable, sir."

    percentage = battery.percent

    if battery.power_plugged:
        return (
            f"Battery is at {percentage:.0f} percent "
            "and the charger is connected, sir."
        )

    return (
        f"Battery is at {percentage:.0f} percent "
        "and running on battery power, sir."
    )


def get_disk_usage():
    disk = psutil.disk_usage("C:\\")

    return (
        f"Your C drive is {disk.percent:.0f} percent full, sir."
    )


def get_system_status():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    battery = psutil.sensors_battery()

    report = (
        f"System status report, sir. "
        f"CPU usage is {cpu:.0f} percent. "
        f"Memory usage is {ram.percent:.0f} percent. "
    )

    if battery:
        report += (
            f"Battery level is {battery.percent:.0f} percent. "
        )

        if battery.power_plugged:
            report += "The charger is connected. "
        else:
            report += "Running on battery power. "

    if cpu > 90 or ram.percent > 90:
        report += "System load is high, sir."
    else:
        report += "System load is within normal limits, sir."

    return report

# -----------------------------------------
# MARK IX - LIVE HUD SYSTEM STATISTICS
# -----------------------------------------

def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    battery = psutil.sensors_battery()

    return {
        "cpu": round(cpu, 1),
        "ram": round(ram.percent, 1),
        "disk": round(disk.percent, 1),

        "battery": (
            round(battery.percent, 1)
            if battery is not None
            else None
        ),

        "charging": (
            battery.power_plugged
            if battery is not None
            else None
        )
    }


if __name__ == "__main__":
    print(get_system_status())
