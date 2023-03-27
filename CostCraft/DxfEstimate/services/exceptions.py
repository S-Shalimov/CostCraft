class UnknownUnitError(Exception):
    def __init__(self, unit):
        self.message = f'Unknown unit: {unit}'
        super().__init__(self.message)