# Одометрия: нормализация frames и владение tf

## Исходные и нормализованные frames

Исходное сообщение с Gazebo-моста `/vehicle/odom_gz` (зафиксировано
`ros2 topic echo /vehicle/odom_gz --once`):

| Поле | Исходное | После адаптера |
|---|---|---|
| `header.frame_id` | `course_ackermann/odom` | `odom` |
| `child_frame_id` | `course_ackermann/base_link` | `base_link` |

Адаптер `odom_adapter` снимает ровно префикс `course_ackermann/`. Сообщения с
другими исходными frames или нечисловыми pose/twist отклоняются (не публикуются).
`stamp`, `pose`, `twist` и обе `covariance` сохраняются без изменений.

## Владение tf

- динамическое ребро `odom -> base_link` публикует только `odom_adapter`
  (единственный владелец, `tf2_ros.TransformBroadcaster`, `use_sim_time:=true`);
- статические связи сенсоров и колёс публикует `robot_state_publisher`
  (`/tf_static`, transient local) из ПР06 — адаптер их не дублирует;
- в записи `fixtures/pr07-sensors` `/tf` = 1723 сообщения за 34,5 с (~50 Гц),
  `/tf_static` = 1 сообщение.

## Тест сохранения метки времени

`src/course_simulation/test/test_adapters.py`:

- `test_odometry_frames_normalized_and_stamp_preserved` — `stamp.sec=7`,
  `stamp.nanosec=250` проходят через нормализацию неизменными;
- `test_odometry_pose_twist_and_covariance_preserved` — равенство pose, twist и
  обеих covariance (сравнение списков);
- `test_odometry_with_unexpected_frames_rejected`,
  `test_odometry_with_non_finite_values_rejected` — отклонение.

## Проверка живым запуском

`ros2 topic echo /vehicle/odom --once` при прямой команде показывает рост
положения; `ros2 run tf2_ros tf2_echo odom base_link --ros-args -p
use_sim_time:=true` возвращает то же положение, что и одометрия.
