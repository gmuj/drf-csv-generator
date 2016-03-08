import csv
import os
import tempfile
from collections import OrderedDict

class CSVGenerator:
    serializer = None
    extra_header_lines = []
    csv_writer_params = {}

    def __init__(self):
        self.csv_file_path = None
        self.validation_errors = []

    def _get_header_mapping(self):
        return OrderedDict([(field.label, key)
                            for key, field in self.serializer._declared_fields.items()])

    def write_csv(self, product_list):
        header_mapping = self._get_header_mapping()
        with tempfile.NamedTemporaryFile('w+', delete=False) as csv_file:
            self.csv_file_path = csv_file.name
            csv_writer = csv.DictWriter(csv_file, fieldnames=header_mapping.keys(), **self.csv_writer_params)

            for line in self.extra_header_lines:
                csv_writer.writer.writerow(line)

            csv_writer.writeheader()

            for product in product_list:
                product_serializer = self.serializer(data=product)
                product_serializer.is_valid()
                if product_serializer.errors:
                    self.validation_errors.append(product_serializer.errors)
                else:
                    csv_row = {header: product[map_key] for header, map_key in header_mapping.items()}
                    csv_writer.writerow(csv_row)

    def __del__(self):
        if self.csv_file_path and os.path.exists(self.csv_file_path):
            try:
                os.remove(self.csv_file_path)
            except OSError:
                # Better do something in this case
                pass
