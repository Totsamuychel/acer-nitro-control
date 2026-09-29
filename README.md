# Acer Nitro Control & Smart Fan for Linux 🚀

A full-featured system monitoring and hardware fan control utility with dynamic smart cooling for **Acer Nitro 5 (including AN515-45, AN515-46, AN515-55/57/58)** laptops on Linux (Arch, Fedora, Ubuntu, Debian).

Built specifically for **AMD Ryzen + NVIDIA GeForce RTX** hybrid graphics laptops and modern Wayland (Hyprland, GNOME, Sway) & X11 desktop environments.

---

## 🌟 Key Features

### 1. Fan Control & Smart Cooling
- **Real-time Fan Speeds (RPM)**: Independent live hardware RPM readings for both CPU Fan and GPU Fan directly from the Embedded Controller (EC).
- **Cooling Modes**:
  - 🔘 **Factory (Quiet)** — standard quiet firmware curve from the laptop EC;
  - ⚡ **Smart Autofan** — continuous background monitoring daemon: proactively increases fan speeds when temperatures rise above 72°C, and automatically triggers maximum TURBO mode at 82°C+ to suppress thermal spikes;
  - 🚀 **TURBO (100%)** — full-blast maximum cooling purge (~5500+ RPM);
  - 🎛 **Manual Control** — dedicated manual toggle switch that disables automatic mode buttons and locks control to independent CPU & GPU sliders (20% – 100%) with real-time percentage indicators.

### 2. Memory (RAM) Monitoring
- Dedicated breakdown of Physical RAM (16 GB), compressed ZRAM swap, and hardware-reserved VRAM for the AMD Radeon iGPU;
- **Live Top-8 RAM Processes**: sorted by memory consumption with PID, RAM in MB, and usage percentage.

### 3. CPU & GPU Load Distribution
- **Live Top-8 CPU Processes**: sorted by CPU load percentage (%CPU);
- **Graphics Card Status**:
  - *AMD Radeon Vega (iGPU)*: displays active rendering of the Hyprland desktop and 144 Hz display;
  - *NVIDIA GeForce RTX (dGPU)*: live power state verification (e.g. **D3cold / 0W** runtime power saving) and list of processes running on the dedicated GPU.

---

## 📦 Quick Installation

```bash
git clone https://github.com/Totsamuychel/acer-nitro-control.git
cd acer-nitro-control
sudo ./install.sh
```

---

## 🖥 Usage

- **From terminal:**
  ```bash
  nitro-control
  ```
- **From application menu:** search for **Acer Nitro Control**.

---

## 🛠 Project Architecture

- `bin/nitro-control` — modern GUI application written in **Python + GTK4 / Libadwaita** with dark mode support.
- `bin/nitro-autofan.py` — lightweight background daemon for dynamic thermal management and mode overrides.
- `systemd/nitro-autofan.service` — systemd user service managing the background autofan daemon.
- `driver/` — `acer-nitro-ec` DKMS Linux kernel driver with added support for the AN515-45 model.
- `desktop/` — XDG `.desktop` launcher entry.

---

## 📄 License

GPL-3.0 License
