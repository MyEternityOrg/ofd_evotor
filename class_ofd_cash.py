import json
import re

import class_mssql
import class_request
import class_settings


# Автор модуля - Коржов С. (с) 2021
class OfdCash:

    def __init__(self, param, settings_cls):
        self.__reg_number = param['rn']
        self.__date_start = param['df']
        self.__date_stop = param['dt']
        self.__settings_cls = settings_cls
        if len(self.__reg_number) <= 0:
            Exception("Не переданы данные по ККТ!")

    @staticmethod
    def create_date_time(m):
        return m.group(1).replace(' ', 'T').replace('.000', '').replace('.', '-')

    def get_checks(self):
        req = class_request.HttpRequest(
            f'https://ofv-api-v0-1-1.evotor.ru/v1/client/{self.__reg_number}/all-documents?dateFrom={self.__date_start}'
            f'%2000:00:00&dateTo={self.__date_stop}%2023:59:59')
        req.load_default_headers(self.__settings_cls)
        data = req.get_data()
        dump = class_settings.Settings.random_file_name_local()
        if data.status_code == 200:
            try:
                data_list = data.text
                regex = re.compile(r'\s*(\d{4}[.]\d{2}[.]\d{2} (?:\d{2}[:]){2}\d{2}[/.]\d{3})\s*')
                data_list = regex.sub(OfdCash.create_date_time, data_list)
                data_list = json.loads(data_list).get('documents')
                print(
                    f"Для ККТ {self.__reg_number} ({self.__date_start} 00:00:00 - {self.__date_stop} 23:59:59): "
                    f"получено чеков: {len(data_list)} шт.")
                file_name = class_settings.Settings.random_file_name()
                class_request.HttpRequest.write_data_to_xml(data_list, file_name)
                # Пишем в SQL
                sql = class_mssql.MSSQLConnection(self.__settings_cls)
                if sql.connected:
                    if len(data_list) > 0:
                        binary_data = class_mssql.MSSQLConnection.file_to_binary_data(file_name)
                        # пишем данные.
                        try:
                            # sql.execute("insert into [import] ([packet_name], [packet_data]) values (%s, %s)",
                            #             ("import_cashdata_" + self.__reg_number, binary_data))
                            sql.execute("exec [ofd_process_import] %s, %s", ("import_cashdata", binary_data))
                        except Exception as E:
                            print(f'Исключительная ситуация (import_cashdata): {E},'
                                  f' ошибка будет сохранена в файл: {dump}')
                            with open(dump, 'wb') as f:
                                f.write(binary_data)
                    else:
                        # для пустых смен - можно смело двигать "метку времени".
                        sql.execute("update [cashes] set [last_updated] = %s where [kkt_reg_number] = %s",
                                    (self.__date_stop, self.__reg_number))
            except Exception as E:
                print(f'Ошибка записи данных по ККТ: {E}, содержимое буфера будет сохранено в файл: {dump}')
                with open(dump, 'wb') as f:
                    f.write(data.text)
        else:
            try:
                t = (data.json())
            except Exception as E:
                t = {'error': f'{E}'}
            print(
                f'Ошибка запроса данных по ККТ {self.__reg_number}, ответ сервера {data.status_code}: {data.reason} '
                f'({t.get("error", "No details")})')
