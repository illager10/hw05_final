from django.core.paginator import Paginator
from django.conf import settings


def paginate_page(request, object_list):
    """Постраничное разбиение материалов"""
    paginator = Paginator(object_list, settings.PAGE_CONST)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
