from .models import Feature

def export_features(request):
    features = Feature.objects.all()
    feature_dict = {}

    for feature in features:
        feature_name=feature.name.lower().replace(" ","_")
        feature_dict[feature_name] = feature.production_enabled

    return {
        'features': feature_dict
    }