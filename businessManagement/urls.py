from django.urls import path

from .views import (
    create_receipt,
    add_product_info_to_receipt,
    get_all_receipt,
    get_all_draft_receipt,
    customize_receipt,
    upload_receipt_signature)

urlpatterns = [
    path("receipt/create", create_receipt),
    path("receipt/product", add_product_info_to_receipt),
    path("receipt/issued", get_all_receipt),
    path("receipt/draft", get_all_draft_receipt),
    path("receipt/customize", customize_receipt),
    path("receipt/upload/signature", upload_receipt_signature),
]
