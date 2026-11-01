# ПР04 · Динамические параметры patrol

ROS 2 Jazzy. Параметры ноды `patrol`: `initial_speed` (0.5), `turn_speed` (0.3),
`period` (0.1). Для `period` объявлен `ParameterDescriptor` с диапазоном
`FloatingPointRange(from_value=0.01, to_value=10.0)`. Расчёт команды — чистая функция
`compute_command(pose, params)`; поведение ПР03 с фиксированными константами сохранено
отдельно в `choose_command`.

## 1 · Собрать

Значения читаются при создании ноды и попадают в `self.params`; таймер создаётся
с `self.params.period`. Запуск с параметрами из командной строки и из файла:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel \
  -p period:=0.2 -p initial_speed:=0.4 -p turn_speed:=0.3
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel \
  --params-file evidence/pr04/params.yaml
```

```text
$ ros2 param dump /patrol
/patrol:
  ros__parameters:
    initial_speed: 0.4
    period: 0.2
    turn_speed: 0.3

$ timeout -s INT 10 ros2 topic hz /turtle1/cmd_vel
average rate: 5.000   (min 0.199s, max 0.201s)
```

Обе команды запуска (CLI и params-file) дают 5 Гц — период со старта читается из параметров.

## 2 · Сломать

Callback принимает новое значение периода и обновляет только числовое поле
`self.params.period`. Период публикуется из параметра, а частота — из объекта таймера,
который хранит период внутри себя и не следит за полем.

```text
$ ros2 param set /patrol period 0.5
Set parameter successful
$ ros2 param dump /patrol | grep period
    period: 0.5
$ timeout -s INT 10 ros2 topic hz /turtle1/cmd_vel
average rate: 5.000   ← частота осталась старой
```

Диапазон descriptor работает уже здесь:

```text
$ ros2 param set /patrol period 0.0
Setting parameter failed: Parameter period out of range Min: 0.01, Max: 10.0, value: 0.0
```

## 3 · Доказать

Callback пересоздаёт таймер: сначала обновляется числовое поле, затем старый таймер
останавливается (`cancel`) и создаётся новый — иначе старый продолжал бы публиковать
с прежним периодом. Замер после исправления:

```text
$ ros2 param dump /patrol | grep period
    period: 0.2                      # запуск с period:=0.2
$ timeout -s INT 6 ros2 topic hz /turtle1/cmd_vel
average rate: 5.000

$ ros2 param set /patrol period 0.05
Set parameter successful
$ timeout -s INT 10 ros2 topic hz /turtle1/cmd_vel
average rate: 20.000  (min 0.049s, max 0.051s)   ← старый таймер остановлен, иначе было бы ~25
$ ros2 param dump /patrol | grep period
    period: 0.05

$ ros2 param set /patrol period 0.2
Set parameter successful
$ timeout -s INT 6 ros2 topic hz /turtle1/cmd_vel
average rate: 5.000
```

Точные 20 Гц (а не 5+20) подтверждают, что старый таймер остановлен и публикует только
новый. `ros2 param dump` показывает фактические значения узла до и после изменения.
Недопустимые значения (`0.0`, `-1.0`) отклоняются диапазоном descriptor, состояние
остается прежним.

## Тесты

`python3 -m pytest src/patrol/test` — 8 passed (см. tests.txt): нулевая команда без позы;
скорости из стартовых параметров; скорости после изменения callback; override при создании
узла доходят до состояния и таймера; `set_parameters` пересоздаёт таймер (новый период
400 мс, старый `is_canceled`); недопустимый период отклоняется.
