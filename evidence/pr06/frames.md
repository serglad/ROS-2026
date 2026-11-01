# ПР06 · Кадровое дерево course_ackermann

Репозиторий: `src/course_description/urdf/vehicle.urdf.xacro`; развёртывается
`xacro … > /tmp/vehicle.urdf`, проверяется `check_urdf`. Единицы СИ, оси REP-103
(x вперёд, y влево, z вверх), `base_link` — в плоскости колёс (центр оси).
Размеры взяты из SDF kit: колёсная база 0.8, колея 0.62, радиус колеса 0.12,
ширина 0.07, корпус 1.05×0.52×0.22 (центр z=0.12), сенсоры (0.28, 0, 0.38).

## Связи дерева (joint → parent/child)

| Joint | Parent | Child | Тип | Преобразование parent→child |
|---|---|---|---|---|
| front_left_wheel_joint | base_link | front_left_wheel_link | continuous (ось Y) | (0.40, 0.31, 0) |
| front_right_wheel_joint | base_link | front_right_wheel_link | continuous (ось Y) | (0.40, −0.31, 0) |
| rear_left_wheel_joint | base_link | rear_left_wheel_link | continuous (ось Y) | (−0.40, 0.31, 0) |
| rear_right_wheel_joint | base_link | rear_right_wheel_link | continuous (ось Y) | (−0.40, −0.31, 0) |
| lidar_joint | **base_link** | lidar_link | fixed | (0.28, 0, 0.38) |
| camera_joint | base_link | camera_link | fixed | (0.28, 0, 0.38) |
| imu_joint | base_link | imu_link | fixed | (0.28, 0, 0.38) |

Владелец публикации: единственный `robot_state_publisher` (launch
`course_description/description.launch.py`). Фиксированные звенья он публикует в
`/tf_static` (reliable + transient local) сразу; подвижные колёса появятся в `/tf`
только при публикациях `/joint_states` — для зачёта не требуется.

## Дефект и исправление

- Коммит `a9531f8` — зелёная реализация: `test_lidar_parent_is_base` проходит,
  `tf2_echo base_link lidar_link` = `[0.280, 0.000, 0.380]`.
- Коммит `0d89724` (стадия «Сломать»): parent `lidar_joint` изменён на `camera_link`
  с прежним offset. check_urdf всё ещё «успешно» разбирает дерево (структурная
  корректность не доказывает геометрию), но положение лидара в базе стало
  `[0.560, 0.000, 0.760]` (сумма двух offset), а `test_lidar_parent_is_base` упал.
- Коммит `ae1aab6` (стадия «Доказать»): parent возвращён на `base_link`; тот же тест
  зелёный (10 passed), `tf2_echo` снова `[0.280, 0.000, 0.380]`, `view_frames`
  показывает `lidar_link: parent: 'base_link'` (см. model-check.txt).

Каждое меняющееся преобразование публикует ровно один участник — два одновременных
robot_state_publisher дают случайный ответ (проверено: `ros2 node list` предупреждает
о дублях), поэтому перед новым запуском прежний launch останавливался.
