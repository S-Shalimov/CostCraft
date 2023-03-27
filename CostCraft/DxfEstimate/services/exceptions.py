class UnknownUnitError(Exception):
    def __init__(self, unit):
        self.message = f'Unknown unit: {unit}'
        super().__init__(self.message)


class UnknownObjectError(Exception):
    def __init__(self, obj):
        self.message = f'Неправильный объект: {obj}.\nВозможно загрузить только:\nПолилинию, Отрезок, Дугу и Круг.'
        super().__init__(self.message)