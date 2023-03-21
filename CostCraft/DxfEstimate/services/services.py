import ezdxf
import xlsxwriter
import tempfile
import os
import requests
from math import ceil
from dotenv import load_dotenv, find_dotenv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .utils import get_item_entity
from ..models import *
from ..forms import *


load_dotenv(find_dotenv())


class MainServices():

    @staticmethod
    def get_context_data():
        pricelist = BasePrice.objects.all().select_related()
        rate_obj = ExchangeRate.objects.values_list('rate', 'date').last()
        form_price = AddPrice()
        context = {
            'pricelist': pricelist,
            'form_price': form_price,
            'rate': rate_obj[0],
            'ratedate': rate_obj[1],
        }
        return context

    @staticmethod
    def del_pricelist_rec(id):
        record = get_object_or_404(BasePrice, pk=id)
        record.delete()




class EstimateServices():

    @staticmethod
    def get_context_data():
        dxfupload = CollectEstimateUpload()
        estimate_objects = Estimate.objects.all()
        form_estimate = AddEstimate()
        sum_price = estimate_objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        context = {
            'estimate': estimate_objects,
            'form_estimate': form_estimate,
            'sum_price': sum_price,
            # TODO: можно загружать только dxf
            'dxfupload': dxfupload,
        }
        return context

    @staticmethod
    def del_estimate_rec(id):
        record = get_object_or_404(Estimate, pk=id)
        record.delete()

    @staticmethod
    def del_estimate():
        estimate = Estimate.objects.all()
        estimate.delete()


class XlsServices():

    @staticmethod
    def get_estimate():

        estimate = Estimate.objects.select_related('name').all()

        file_name = 'estimate.xlsx'

        with xlsxwriter.Workbook(file_name) as workbook:

            worksheet = workbook.add_worksheet()

            header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
            float_cell_format = workbook.add_format(
                {'align': 'center', 'border': True, 'text_wrap': True, 'num_format': '#,##0.00'})
            cell_format = workbook.add_format({'align': 'center', 'border': True, 'text_wrap': True})
            align_right_cell_format = workbook.add_format({'align': 'right', 'border': True, 'text_wrap': True})

            worksheet.set_column(0, 1, width=50)
            worksheet.set_column(1, 5, width=12)

            header_row = ['Наименование', 'Количество', 'Ед.изм.', 'Цена', 'Общая цена']

            def quantity_cell_format(row_unit):
                if 'шт' == row_unit:
                    return cell_format
                else:
                    return float_cell_format

            for col_num, header in enumerate(header_row):
                worksheet.write(0, col_num, header, header_format)

            for row_num, row in enumerate(estimate):
                worksheet.write_string((row_num + 1), 0, row.name.name, cell_format)
                worksheet.write_number((row_num + 1), 1, row.quantity, quantity_cell_format(row.units))
                worksheet.write_string((row_num + 1), 2, row.units, cell_format)
                worksheet.write_number((row_num + 1), 3, row.price_dol, float_cell_format)
                worksheet.write_formula((row_num + 1), 4, f"=B{row_num + 2}*D{row_num + 2}", float_cell_format)

            worksheet.merge_range(f"A{len(estimate) + 2}:D{len(estimate) + 2}", "Общая цена:", align_right_cell_format)

            worksheet.write_formula((len(estimate) + 1), 4, f"=СУММ(E2:E{len(estimate) + 1})", float_cell_format)

        with open(file_name, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Lenght'] = os.path.getsize(file_name)
            response['Content-Disposition'] = 'attachment; filename=estimate.xlsx'

        os.unlink(file_name)

        return response



class DxfServices():

    @staticmethod
    def get_dxf():
        product_data = BasePrice.objects.all().values('id', 'name', 'units')
        #TODO: использовать select_related или prefetch
        units = Units.objects.all()
        dxf_templ = ezdxf.new()
        msp = dxf_templ.modelspace()
        ref_coord_y = 0
        indent = 20
        for record in product_data:
            if len(record['name']) >= 10:
                # '0CC' is selected to identify layers when adding to an estimate.
                # '0' - to display in AutoCAD at the top of the layer list, 'CC' - CostCraft

                layer_name = '0CC' + '_' + str(record['id']) + '_' + str(record['name'][:10])
            else:
                layer_name = '0CC' + '_' + str(record['id']) + '_' + str(record['name'])
            layer_name = layer_name.replace(' ', '_')
            dxf_templ.layers.new(name=(layer_name))
            if str(units.get(pk=record['units'])) == 'м²':
                point_0 = (0, ref_coord_y)
                point_2 = (indent * 3, ref_coord_y + indent)
                point_1 = (point_0[0], point_2[1])
                point_3 = (point_2[0], point_0[1])
                msp.add_lwpolyline((
                    point_0,
                    point_1,
                    point_2,
                    point_3,
                    point_0,
                ),
                    dxfattribs={'layer': layer_name})
                msp.add_text(text=record['name'], height=indent, dxfattribs={
                    'layer': layer_name}).set_placement((indent * 4, ref_coord_y))
            if str(units.get(pk=record['units'])) == 'м':
                point_0 = (0, ref_coord_y)
                point_1 = (indent * 3, ref_coord_y)
                msp.add_lwpolyline((tuple(point_0), tuple(point_1)), dxfattribs={'layer': layer_name})
                msp.add_text(text=record['name'], height=indent, dxfattribs={
                    'layer': layer_name
                }).set_placement((indent * 4, ref_coord_y))
            if str(units.get(pk=record['units'])) == 'шт':
                point_0 = (0, ref_coord_y)
                point_2 = (indent * 3, ref_coord_y + indent)
                point_1 = (point_0[0], point_2[1])
                point_3 = (point_2[0], point_0[1])
                msp.add_lwpolyline((
                    point_0,
                    point_1,
                    point_2,
                    point_3,
                    point_0,
                ),
                    dxfattribs={'layer': layer_name})
                msp.add_text(text=record['name'], height=indent, dxfattribs={
                    'layer': layer_name}).set_placement((indent * 4, ref_coord_y))

            ref_coord_y += indent * 6
        # TODO: make the file temporary
        dxf_path = 'DxfEstimate/dxf/pricelist.dxf'
        dxf_templ.saveas(dxf_path)

        with open(dxf_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/dxf')
            response['Content-Lenght'] = os.path.getsize(dxf_path)
            response['Content-Disposition'] = 'attachment; filename=materials.dxf'

        return response

    @staticmethod
    def collect_estimate(dxf_req):
        #TODO: Оптимизировать кол-во запросов в БД
        dxf_file = tempfile.NamedTemporaryFile(suffix='.dxf', delete=False)
        dxf_file.write(dxf_req.read())
        dxf_file.close()

        dxf_scheme = ezdxf.readfile(dxf_file.name)

        entities_with_pricelist_ids = []
        for object in dxf_scheme.modelspace():
            if isinstance(object,
                          ezdxf.entities.lwpolyline.LWPolyline) or isinstance(object,
                          ezdxf.entities.circle.Circle) or isinstance(object,
                          ezdxf.entities.line.Line) or isinstance(object,
                          ezdxf.entities.line.Line):
                layer_name = object.dxfattribs()['layer']

                # if the layer was created with get_dxf():

                if '0CC_' in layer_name:
                    id = ''
                    for char in layer_name[4:]:
                        if '_' in char:
                            break
                        else:
                            id += char

                    entities_with_pricelist_ids.append({
                        'id': int(id),
                        'entity': object,
                    })

        os.unlink(dxf_file.name)

        layer_ids = {obj['id'] for obj in entities_with_pricelist_ids}

        pricelist = BasePrice.objects.filter(id__in=layer_ids)

        entities_with_pricelist_ids.sort(key=lambda obj: obj['id'])
        entities_with_pricelist_ids.append(None)

        item_id = None
        item_quantity = 0.0
        for obj in entities_with_pricelist_ids:
            if obj == None:
                record_in_estimate = Estimate(name=item_name, quantity=item_quantity, units=item_unit,
                                              types=item_types, price_dol=item_price)
                record_in_estimate.save()
            elif obj['id'] != item_id:
                if item_id != None:
                    record_in_estimate = Estimate(name=item_name, quantity=item_quantity, units=item_unit,
                                                  types=item_types, price_dol=item_price)
                    record_in_estimate.save()
                    item_quantity = 0.0
                item_id = obj['id']
                resource_data = pricelist.get(id=item_id)
                item_name = resource_data
                item_unit = resource_data.units
                item_types = resource_data.types
                item_price = resource_data.price_dol
                item_quantity += get_item_entity(obj, str(item_unit))
            elif obj['id'] == item_id:
                item_quantity += get_item_entity(obj, str(item_unit))


class CurrencyServices():

    @staticmethod
    def convertto_dol():
        conversion_prods = BasePrice.objects.filter(price_dol__isnull=True)
        rate = ExchangeRate.objects.values_list('rate').last()
        for prod in conversion_prods:
            prod.price_dol = prod.price_sum / (rate[0] * Decimal(1.01))
            prod.save()

    @staticmethod
    def get_rate():
        url = 'https://api.apilayer.com/exchangerates_data/convert'
        params = {'to': 'UZS', 'from': 'USD', 'amount': 1}
        headers = {'apikey': os.environ.get('APILAYER_KEY')}
        response = requests.get(url, headers=headers, params=params)
        rate = ceil(response.json()['result'])
        rate_obj, create = ExchangeRate.objects.update_or_create(defaults={'rate': rate})
        rate_obj.save()

