from modeltranslation.translator import translator, TranslationOptions
from .models import VehicleType, Feature, Location, Vehicle, Review, RentalPolicy


class VehicleTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


class FeatureTranslationOptions(TranslationOptions):
    fields = ('name',)


class LocationTranslationOptions(TranslationOptions):
    fields = ('city', 'address',)


class VehicleTranslationOptions(TranslationOptions):
    fields = ('title',)


class ReviewTranslationOptions(TranslationOptions):
    fields = ('text',)


class RentalPolicyTranslationOptions(TranslationOptions):
    fields = ('title', 'rules',)


# регистрация
translator.register(VehicleType, VehicleTypeTranslationOptions)
translator.register(Feature, FeatureTranslationOptions)
translator.register(Location, LocationTranslationOptions)
translator.register(Vehicle, VehicleTranslationOptions)
translator.register(Review, ReviewTranslationOptions)
translator.register(RentalPolicy, RentalPolicyTranslationOptions)
