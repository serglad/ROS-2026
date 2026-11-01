# ПР05 · Launch, QoS и повтор записи

ROS 2 Jazzy. Пакет `course_bringup`: `launch/patrol.launch.py` (аргументы
`namespace`, `record`, `bag_dir`, `subscriber_reliability`), ноды `pose_relay`
(издатель `sensor_pose`, best effort) и `pose_probe` (подписчик с настраиваемой
надёжностью). turtlesim — глобально, остальное в namespace. Запись — MCAP,
условие `IfCondition(record)`; для записи тема подаётся абсолютным именем
`/<namespace>/sensor_pose`, иначе относительное имя без namespace не находится.

## 1 · Собрать

```bash
colcon build --symlink-install --packages-select course_bringup
source install/setup.bash
python3 -m pytest src/course_bringup/test          # 6 passed, см. tests
ros2 launch course_bringup patrol.launch.py namespace:=robot_a record:=true \
  bag_dir:=evidence/pr05/bag subscriber_reliability:=best_effort
```

```text
$ ros2 node list
/robot_a/patrol  /robot_a/pose_probe  /robot_a/pose_relay  /turtlesim
```

`record:=false` в дефектном прогоне ниже — recorder не запускался (IfCondition).

## 2 · Сломать

```bash
ros2 launch course_bringup patrol.launch.py namespace:=robot_a \
  subscriber_reliability:=reliable record:=false
timeout 3s ros2 topic echo /robot_a/sensor_pose --qos-reliability reliable --once
```

Топик виден в `ros2 topic list`, но echo не получает сообщений (exit 124), в логах
`offering incompatible QoS ... RELIABILITY`, `pose_probe received 0 poses`.
`ros2 topic info --verbose` показывает BEST_EFFORT издатель против RELIABLE подписчика.
Полная диагностика — в `qos-before.txt`.

## 3 · Доказать

Причина — правила совместимости QoS: best effort издатель не может обслуживать
reliable подписчика. Перезапуск с `subscriber_reliability:=best_effort` восстанавливает
поток: живой echo получил позу, `pose_probe` насчитал 598 поз, recorder записал 22 с
(449 сообщений, один поток). Тот же профиль проверен на повторе:

```bash
ros2 bag play evidence/pr05/bag --qos-profile-overrides-path config/qos-overrides.yaml
timeout 3s ros2 topic echo /robot_a/sensor_pose --qos-reliability best_effort --once   # exit 0
```

`qos-after.txt` содержит живой echo, echo с повтора и `ros2 bag info` (один поток
`/robot_a/sensor_pose`, 449 сообщений); `bag-metadata.yaml` скопирован из каталога
записи. «До» и «после» — один и тот же набор входных сообщений записи.
