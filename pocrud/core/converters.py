class IntListConverter:
    regex = r'\d+(?:,\d+)*'

    def to_python(self, value):
        return [int(item) for item in value.split(',')]

    def to_url(self, value):
        return ','.join(str(item) for item in value)