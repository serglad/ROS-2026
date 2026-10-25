# ПР03 · Первая нода: поза и команда

ROS 2 Jazzy (тип позы — `turtlesim/msg/Pose`). Пакет `src/patrol`, команда запуска `patrol`.

## 1 · Собрать

```bash
colcon build --symlink-install --packages-select patrol
source install/setup.bash
python3 -m pytest src/patrol/test   # 4 passed, 1 skipped (см. tests.txt)
```

Нода `patrol`:

- подписка на `/turtle1/pose` сохранена в поле `self.pose_sub`, callback только сохраняет
  последнее сообщение в `self.latest_pose`;
- издатель `geometry_msgs/msg/Twist` создан на относительное имя `cmd_vel`;
- таймер `create_timer(0.1, ...)` публикует команду, выбранную чистой функцией
  `choose_command(pose)`: до первой позы — нулевой Twist, после — `linear.x=0.5`, `angular.z=0.3`.

Запуск (отдельный терминал):

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

## 2 · Сломать

Запуск без remap: `ros2 run patrol patrol`. Относительное имя `cmd_vel` resolving в
`/cmd_vel`, который с `/turtle1/cmd_vel` не соединён.

```text
$ ros2 topic info /cmd_vel
Publisher count: 1
Subscription count: 0

$ ros2 topic info /turtle1/cmd_vel
Publisher count: 0
Subscription count: 1

$ timeout -s INT 6 ros2 topic hz /turtle1/cmd_vel
(нет сообщений, выход по таймауту, код 124)
```

Черепашка стоит: `ros2 topic echo /turtle1/pose --once` даёт постоянные `linear_velocity: 0.0`.

## 3 · Доказать

Причина — разрыв имени темы, а не QoS или домен: издатель и подписчик видят разные имена.
Remap `-r cmd_vel:=/turtle1/cmd_vel` связывает их:

```text
$ ros2 topic info /turtle1/cmd_vel
Publisher count: 1
Subscription count: 1

$ timeout -s INT 10 ros2 topic hz /turtle1/cmd_vel
average rate: 10.001 ... average rate: 10.000 (min 0.099s, max 10.001s, std dev ~0.0003s)
```

Реальная частота команд за 10 секунд — 10 Гц (период таймера 0,1 с). Поза поступает:
координаты меняются между двумя снимками `ros2 topic echo /turtle1/pose --once`
(5.43, 5.55 → 6.79, 6.11), то есть callback подписки вызывается и команда зависит от позы.

## Роли init, spin, callback, Ctrl+C

- `rclpy.init()` — инициализация контекста ROS (создаёт DDS-окружение, параметризация);
- `rclpy.spin(node)` — крутит исполнитель: берёт готовые события и по очереди вызывает
  callbacks подписок и таймеров, сам callback ничего не ждёт;
- callback подписки `on_pose` — короткий обработчик: только сохраняет последнее сообщение,
  всю остальную работу делает таймер;
- `Ctrl+C` — SIGINT прерывает spin (`KeyboardInterrupt`), в `finally` выполняются
  `destroy_node()` и `try_shutdown()`.

## Остановка

После остановки ноды turtlesim останавливается не мгновенно: исчезновение процесса patrol
— это не команда торможения. У turtlesim есть собственный `~command_timeout` (1 с), и
черепашка замирает через секунду после последнего Twist; явная нулевая команда
`ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0}, angular: {z: 0.0}}'`
останавливает её гарантированно.
