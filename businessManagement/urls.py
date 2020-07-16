from django.urls import path


from .views import (
    create_receipt,
    add_product_info_to_receipt,
    get_all_receipt,
    get_all_draft_receipt,
    customize_receipt,
    create_business,
    get_business,
    upload_receipt_signature,
    update_business,
    update_draft_receipt,
    get_receipt_id,
    get_user_business,
    add_data_to_inventory, get_all_categories, get_items_inventory)


urlpatterns = [
    path("receipt/create", create_receipt),
    path("receipt/product", add_product_info_to_receipt),
    path("receipt/issued", get_all_receipt),
    path("receipt/draft", get_all_draft_receipt),
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
    path('category/all',get_all_categories)
]
