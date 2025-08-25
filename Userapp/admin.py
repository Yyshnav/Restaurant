from django.contrib import admin

from Accountapp.models import *


admin.site.register(ProfileTable, )
admin.site.register(RatingTable, )
admin.site.register(CartTable, )
admin.site.register(WishlistTable, )
admin.site.register(ItemTable, )
admin.site.register(OrderTable, )
admin.site.register(OrderItemTable, )
admin.site.register(UserRole)
admin.site.register(PaymentTable)
admin.site.register(BillTable)
admin.site.register(DiningTable)
admin.site.register(DeliveryTable)
# admin.site.register(LoginTable)
admin.site.register(DeliveryBoyTable)
admin.site.register(FloorTable)
admin.site.register(FeedbackTable)

admin.site.register( CategoryTable   )
admin.site.register(SubCategoryTable)
admin.site.register(SubSubCategoryTable)

admin.site.register(AddonTable)
# admin.site.register(OfferTable)
admin.site.register(AddressTable)


admin.site.register(CouponTable)
admin.site.register(VoucherTable)
admin.site.register(PrinterTable)
admin.site.register(ItemVariantTable)
admin.site.register(VoiceDescriptionTable)
admin.site.register(ManagerTable) 
admin.site.register(WaiterTable)
admin.site.register(BranchTable)
admin.site.register(CarouselTable)
admin.site.register(SpotlightTable)
admin.site.register(ItemImageTable)
admin.site.register(ChatMessage)
admin.site.register(DeliveryBoyLocation)
admin.site.register(OfflineOrders)
admin.site.register(OfflineOrderItems)