from django.urls import path


from .views import (
    create_receipt,
    add_product_info_to_receipt,
    get_all_receipt,
    get_all_draft_receipt,
    delete_draft,
    customize_receipt,
    create_business,
    get_business,
    upload_receipt_signature,
    update_business,
    update_draft_receipt,
    get_receipt_id,
    get_user_business,
    add_data_to_inventory, get_all_categories, get_items_inventory, delete_inventory, promotions, delete_receipt,
    get_part_payment, update_part_payment)


urlpatterns = [
    path("receipt/<uuid:id>", delete_receipt),
    path("receipt/create", create_receipt),
    path("receipt/product", add_product_info_to_receipt),
    path("receipt/issued", get_all_receipt),
    path("receipt/draft", get_all_draft_receipt),
    path("reciept/draft/<uuid:id>", delete_draft),
    path("receipt/draft/update", update_draft_receipt),
    path("receipt/customize", customize_receipt),
    path("receipt/one", get_receipt_id),
    path("receipt/upload/signature", upload_receipt_signature),
    path("info/create", create_business),
    path("info/all", get_business),
    path("info/update", update_business),
    path("user/all", get_user_business),
    path("inventory/add", add_data_to_inventory),
    path('inventory/all',get_items_inventory),
    path('category/all',get_all_categories),
    path('inventory/<uuid:id>',delete_inventory),
    path('promotions',promotions),
    path('receipt/partpayment',get_part_payment),
    path('receipt/partpayment/<uuid:id>', update_part_payment)
]
