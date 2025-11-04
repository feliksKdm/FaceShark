# Python 3.12 Compatibility Notes

## Обновленные зависимости для Python 3.12

Проект FaceSharp обновлен для работы с Python 3.12. Основные изменения:

### Ключевые обновления:

1. **NumPy 2.1.3** - поддерживает Python 3.12, использует Meson вместо distutils
2. **scikit-learn 1.5.2** - совместим с NumPy 2.x и Python 3.12
3. **scipy 1.14.1** - требуется для scikit-learn, поддерживает Python 3.12
4. **OpenCV 4.10.0** - обновлена для лучшей совместимости
5. **FastAPI 0.115.0** - последняя стабильная версия с поддержкой Python 3.12

### Изменения в коде:

- Использование `np.fft` вместо `scipy.fft` в `quality_metrics.py` (совместимость с NumPy 2.x)
- Все зависимости обновлены до версий, поддерживающих Python 3.12

### Установка:

```bash
# Создать виртуальное окружение с Python 3.12
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### Проверка совместимости:

```bash
python --version  # Должно быть Python 3.12.x
pip check  # Проверить конфликты зависимостей
```

### Известные проблемы:

- MediaPipe 0.10.13 может требовать дополнительные системные зависимости на некоторых платформах
- ONNX Runtime 1.20.0 может требовать установку дополнительных пакетов для GPU поддержки

### Разработка:

Для разработки установите также dev-зависимости:

```bash
pip install -r requirements-dev.txt
```

