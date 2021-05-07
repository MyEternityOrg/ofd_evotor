from xml.dom import minidom

import certifi
import requests

import class_settings


class HttpRequest:
    def __init__(self, addr=""):
        self.__req = requests.Session()
        self.__req.trust_env = False
        self.__addr = addr

    def load_default_headers(self, settings_class):
        try:
            if type(settings_class) == class_settings.Settings:
                if not settings_class.errors:
                    self.write_header("login", settings_class.param("ofd_login"))
                    self.write_header("password", settings_class.param("ofd_password"))
                    self.write_header("Token", settings_class.param("ofd_token"))
            else:
                print("Ошибка обработки файла настроек.")
        except Exception as E:
            print(f"Ошибка загрузки шаблона настроек: {E}.")

    def write_header(self, name, value):
        if len(str(name)) > 0 and len(str(value)) > 0:
            h = {name: value}
            self.__req.headers.update(h)

    def get_data(self, address=""):
        try:
            self.__req.cookies.clear_session_cookies()
            if len(str(address)) > 0:
                reply = self.__req.get(address, verify=certifi.where())
            else:
                reply = self.__req.get(self.__addr, verify=certifi.where())
            return reply
        except Exception as E:
            print(f"Ошибка получения данных: {E}.")
            return None

    @property
    def request(self):
        return self.__req

    @property
    def addr(self):
        return self.__addr

    @addr.setter
    def addr(self, value):
        self.__addr = value

    @classmethod
    def write_data_to_xml(cls, data, filename, header="root"):
        """
        :param data: Объект - список или генератор. Можно передать словари внутри списков, или списки списков.
        :param filename: Имя файла в который требуется записать данные.
        :param header: Имя корневого элемента xml
        :return: Вернет истину, если все отработает корректно.
        """
        g = (n for n in [0, 1])
        try:
            # Умеем сохранять списки или генераторы.
            if type(data) in (list, type(g)):
                with open(filename, "w", encoding="UTF8") as f:
                    root = minidom.Document()
                    xml = root.createElement(header)
                    root.appendChild(xml)
                    for i, dd in enumerate(data):
                        row = root.createElement("row")
                        row.setAttribute("id", str(i + 1))
                        if type(dd) == list:
                            for z, vl in enumerate(list(dd)):
                                val = root.createElement("row")
                                val.setAttribute("id", str(z + 1))
                                val.setAttribute("data", str(vl))
                                row.appendChild(val)
                            xml.appendChild(row)
                        elif type(dd) == dict:
                            for x in dd.keys():
                                row.setAttribute(x, str(dd.get(x)))
                            xml.appendChild(row)
                        else:
                            row.setAttribute("data", str(dd))
                            xml.appendChild(row)
                    xml_str = root.toprettyxml(indent="\t")
                    f.write(xml_str)
                    return True
            else:
                print("Записывать в xml данные можно только генераторы или списки!")
                return False
        except Exception as E:
            print(f"Исключительная ситуация при преобразовании в XML: {E}.")
            return False
