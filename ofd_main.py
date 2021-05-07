import class_ofd
import class_ofd_cash
import class_settings

# Прочитаем настройки для работы и ОФД и Базой данных.
print(f'Чтение настроек...')
settings = class_settings.Settings()
# Получим список ККТ из ОФД.
print(f'Подключение к ОФД...')
evt = class_ofd.OfdCashList(settings)

# Если получено обновление ККТ
print(f'Получение списка ККТ...')
if evt.update_cashes_list():
    # Запрос списка касс - запишет данные в БД, и вернет нам набор для обработки в виде генератора.
    print(f'Получено задание на проверку чеков.')
    task = evt.write_data_to_sql()
    # Обходим результат - где элементом является список.
    for n, t in task:
        # Вторая колонка списка - данные для отправки в дочерний класс.
        dd = dict(x.split(': ') for x in t.split(', '))
        # Создаем и получаем чеки.
        cash = class_ofd_cash.OfdCash(dd, settings)
        cash.get_checks()
    print(f'Агрегация данных по сменам.')
    evt.process_shifts()
