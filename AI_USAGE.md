report.ai_used=false

## PR03

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Qwen3.8-flash-next (ID `deepcode/qwen3.8-flash-next`).
- Среда или интерфейс агента: Kilo CLI в VS Code.
- Затронутые компоненты: пакет `src/patrol` (нода, чистая функция, тесты), `evidence/pr03/*`, `.github/workflows/PR03.yml`.
- Характер помощи: генерация каркаса и кода ноды по условию ПР, оформление evidence и workflow; локальные запуски выполнялись в терминале окружения.
- Как результат был проверен независимо: `colcon build --packages-select patrol`, `python3 -m pytest src/patrol/test`, проверка графа `ros2 topic info` и замер `ros2 topic hz` (10 Гц за 10 с), движение черепашки по `/turtle1/pose`, `check_practice.py PR03`.

## PR04

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Qwen3.8-flash-next (ID `deepcode/qwen3.8-flash-next`).
- Среда или интерфейс агента: Kilo CLI в VS Code.
- Затронутые компоненты: пакет `src/patrol` (параметры, descriptor, callback с пересозданием таймера, тесты), `evidence/pr04/*`, `.github/workflows/PR04.yml`.
- Характер помощи: реализация по условию ПР, отладка импортов и имени полей descriptor, оформление evidence и workflow; локальные запуски выполнялись в терминале окружения.
- Как результат был проверен независимо: `python3 -m pytest src/patrol/test` (8 passed), живые замеры `ros2 param dump`/`ros2 param set`/`ros2 topic hz` (5→20→5 Гц, отклонение значений вне диапазона), `check_practice.py PR04`.

## PR05

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Qwen3.8-flash-next (ID `deepcode/qwen3.8-flash-next`).
- Среда или интерфейс агента: Kilo CLI в VS Code.
- Затронутые компоненты: пакет `src/course_bringup` (pose_relay, launch с аргументами), `config/qos-overrides.yaml`, `evidence/pr05/*`, `.github/workflows/PR05.yml`.
- Характер помощи: реализация по актуальному условию с сайта (манифест kit v1-w08), отладка имени темы записи и финализации bag, оформление evidence и workflow; локальные запуски выполнялись в терминале окружения.
- Как результат был проверен независимо: `colcon test-result` (19 тестов, 0 failures), живой опыт QoS incompatible → переход на совместимый профиль (echo exit 124 → exit 0, probe 0 → 598 поз), запись MCAP (449 сообщений, один поток) и повтор с overrides, `check_practice.py PR05`.

## PR06

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Qwen3.8-flash-next (ID `deepcode/qwen3.8-flash-next`).
- Среда или интерфейс агента: Kilo CLI в VS Code.
- Затронутые компоненты: пакет `src/course_description` (Xacro-модель, launch, структурные тесты), `evidence/pr06/*`, `.github/workflows/PR06.yml`.
- Характер помощи: Xacro по размерам из kit-SDF, тесты и evidence, отладка launch-подстановок; локальные запуски (robot_state_publisher, RViz, tf2-инструменты) выполнялись в терминале окружения.
- Как результат был проверен независимо: `check_urdf` развёрнутого URDF, `pytest src/course_description/test` (10 passed), живой `tf2_echo` (0.280/0/0.380; при дефектном родителе 0.560/0/0.760), `view_frames`, `tf-qos.txt` (transient_local exit=0 против volatile exit=124), `check_practice.py PR06`.
