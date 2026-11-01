# ПР04 · Команды демонстрации

Запуск в двух терминалах (`ros2 run turtlesim turtlesim_node` + patrol). Полное описание
стадий и замеров — в `parameters.md`.

```bash
# 1 · Собрать
colcon build --symlink-install --packages-select patrol
source install/setup.bash
python3 -m pytest src/patrol/test
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel \
  -p period:=0.2 -p initial_speed:=0.4 -p turn_speed:=0.3

# 2 · Сломать (реализация до исправления): частота не меняется
ros2 param set /patrol period 0.5            # set successful
ros2 param dump /patrol                      # period: 0.5
timeout -s INT 10 ros2 topic hz /turtle1/cmd_vel   # average rate: 5.000 (старая)

# 3 · Доказать (после пересоздания таймера в callback)
ros2 param set /patrol period 0.05
timeout -s INT 10 ros2 topic hz /turtle1/cmd_vel   # average rate: 20.000
ros2 param set /patrol period 0.2
timeout -s INT 6 ros2 topic hz /turtle1/cmd_vel    # average rate: 5.000
ros2 param set /patrol period 0.0            # rejected: out of range Min 0.01, Max 10.0
```

Пересоздание таймера обязательно: rclpy Timer фиксирует период в момент создания,
изменение поля `period` на него не влияет. Callback сначала обновляет числовое поле,
затем останавливает старый таймер и создаёт новый — так между timer callback нельзя
получить команду со старым периодом и новыми скоростями вразнобой.
