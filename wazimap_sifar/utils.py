from geojson import FeatureCollection, Feature, Point


def to_geojson(model, contrib_id):
    """
    Convert django model to geojson
    """
    feature_collection = []
    for record in model.objects.filter(contributer_id=contrib_id):
        try:
            properies = {
                "name": record.name,
                "address": record.address,
                "email": record.email,
                "website": record.website,
                "phone_number": record.phone_number,
            }
            my_point = Point((record.longitude, record.latitude))
            my_feature = Feature(geometry=my_point, properties=properies)
            feature_collection.append(my_feature)
        except ValueError:
            pass
    return FeatureCollection(feature_collection)
