import datetime

import class_mssql
import class_request
import class_settings


class OfdCashList:
    def __init__(self, settings_class):
        if type(settings_class) == class_settings.Settings:
            self.__login = settings_class.param("ofd_login")
            self.__password = settings_class.param("ofd_password")
            self.__token = settings_class.param("ofd_token")
        else:
            Exception("Некорректный класс настроек!")
        self.__date_out_pattern = "%Y%m%d"
        self.__settings_class = settings_class
        self.__cashes_list = []
        self.__initial_date = datetime.date(datetime.date.today().year, datetime.date.today().month - 1,
                                            datetime.date.today().day)
        self.__initial_date_str = self.__initial_date.strftime(self.__date_out_pattern)

    def write_data_to_sql(self):
        try:
            sql = class_mssql.MSSQLConnection(self.__settings_class)
            if sql.connected:
                file_name = class_settings.Settings.random_file_name()
                class_request.HttpRequest.write_data_to_xml(self.__cashes_list, file_name, "cashes")
                binary_data = class_mssql.MSSQLConnection.file_to_binary_data(file_name)
                sql.execute("exec [ofd_process_import] %s, %s", ("import_cashlist", binary_data))
                return sql.select("select * from [ofd_get_task] () order by id", "")
                # return sql.select("select * from [ofd_get_task_2] ('0000030591007160') order by id", "")
        except Exception as E:
            print(f"Исключительная ситуация при записи списка касс в БД: {E}.")
            return ()

    def process_shifts(self):
        try:
            sql = class_mssql.MSSQLConnection(self.__settings_class)
            if sql.connected:
                print('Подключение установлено. Обработка полученных данных.')
                sql.execute("exec [ofd_process_shifts]")
        except Exception as E:
            print(f"Исключительная ситуация при обработке данных по сменам: {E}.")

    def update_cashes_list(self):
        try:
            self.__initial_date_str = self.__initial_date.strftime(self.__date_out_pattern)
            req = class_request.HttpRequest()
            req.load_default_headers(self.__settings_class)
            __reply = req.get_data("https://ofv-api-v0-1-1.evotor.ru/v1/client/kkts")
            if __reply.status_code == 200:
                data = __reply.json()
                self.__cashes_list = []
                for i1, x in enumerate(data["kktList"]["orgBranches"]):
                    for i2, y in enumerate(x["branches"]):
                        for i3, z in enumerate(y["kkts"]):
                            d = {"main_branch": x["branchId"], "main_branch_name": x["branchName"],
                                 "child_branch": y["branchId"],
                                 "child_branch_name": y["branchName"], "kkt_number": z["kktNumber"],
                                 "kkt_reg_number": z["kktRegNumber"], "kkt_fiscal_number": z["kktFN"],
                                 "kkt_name": z["kktName"], "updated": self.__initial_date_str}
                            self.__cashes_list.append(d)
                return True
            else:
                return False
        except Exception as E:
            self.__cashes_list = []
            print(f"Исключительная ситуация при получении списка касс: {E}.")
            return False

    def __str__(self):
        return f"Данных касс: {len(self.__cashes_list)} шт."

    @property
    def date_pattern(self):
        return self.__date_out_pattern

    @date_pattern.setter
    def date_pattern(self, data):
        self.__date_out_pattern = data

    @property
    def cashes_list(self):
        return (rec for rec in self.__cashes_list)
