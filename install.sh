#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "    Acer Nitro Control & Smart Fan Installer for Linux   "
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check root permissions for system components
if [ "$EUID" -ne 0 ]; then
    echo "[!] Для установки драйвера ядра и правил udev требуются права sudo."
    exec sudo bash "$0" "$@"
fi

CURRENT_USER="${SUDO_USER:-$USER}"
USER_HOME=$(getent passwd "$CURRENT_USER" | cut -d: -f6)

echo "[1/4] Установка DKMS-драйвера acer-nitro-ec..."
mkdir -p /usr/src/acer-nitro-ec-1.0.0
cp -r "$SCRIPT_DIR/driver/"* /usr/src/acer-nitro-ec-1.0.0/

if ! dkms status | grep -q "acer-nitro-ec"; then
    dkms add acer-nitro-ec/1.0.0 || true
fi
dkms build acer-nitro-ec/1.0.0 --force
dkms install acer-nitro-ec/1.0.0 --force

echo "acer_nitro_ec" > /etc/modules-load.d/acer_nitro_ec.conf
modprobe acer_nitro_ec || true

echo "[2/4] Настройка прав udev для управления без root..."
cat << 'EOF' > /etc/udev/rules.d/85-acer-nitro-fan.rules
ACTION=="add|change", SUBSYSTEM=="hwmon", ATTR{name}=="acer_nitro_ec", RUN+="/bin/sh -c 'chmod 0666 /sys%p/pwm*'"
EOF
udevadm control --reload
udevadm trigger

echo "[3/4] Установка утилит и графического интерфейса..."
mkdir -p /usr/local/bin
install -m 755 "$SCRIPT_DIR/bin/nitro-control" /usr/local/bin/nitro-control
install -m 755 "$SCRIPT_DIR/bin/nitro-autofan.py" /usr/local/bin/nitro-autofan.py

mkdir -p /usr/share/applications
install -m 644 "$SCRIPT_DIR/desktop/nitro-control.desktop" /usr/share/applications/nitro-control.desktop
update-desktop-database /usr/share/applications 2>/dev/null || true

echo "[4/4] Настройка автозапуска сервиса охлаждения..."
mkdir -p "$USER_HOME/.config/systemd/user"
cp "$SCRIPT_DIR/systemd/nitro-autofan.service" "$USER_HOME/.config/systemd/user/"
chown -R "$CURRENT_USER:$CURRENT_USER" "$USER_HOME/.config/systemd/user/nitro-autofan.service"

sudo -u "$CURRENT_USER" systemctl --user daemon-reload
sudo -u "$CURRENT_USER" systemctl --user enable --now nitro-autofan.service

echo "=========================================================="
echo "[+] Установка завершена успешно!"
echo "    - Запустить панель управления: nitro-control"
echo "    - Демон умного охлаждения запущен и работает в фоне."
echo "=========================================================="
