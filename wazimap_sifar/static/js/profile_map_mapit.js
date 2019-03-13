// extend the default Wazimap ProfileMaps object to add mapit support

var BaseProfileMaps = ProfileMaps;
ProfileMaps = function() {
    var self = this;
    this.mapit_url = GeometryLoader.mapit_url;

    _.extend(this, new BaseProfileMaps());

    this.drawAllFeatures = function() {
        var self = this;
        var geo = this.geo;
        var geo_level = geo.this.geo_level;
        var geo_code = geo.this.geo_code;
        var geo_version = geo.this.version;

        // add demarcation boundaries
        if (geo_level == 'country') {
            this.map.setView({lat: -28.4796, lng: 10.698445}, 5);
        } else {
            // draw this geometry
            GeometryLoader.loadGeometryForGeo(geo_level, geo_code, geo_version, function(feature) {
                self.drawFocusFeature(feature);
            });
        }

	if (geo_level == 'municipality' || geo_level == 'subplace'){
	    function getIcon(icon, colour) {
		return L.AwesomeMarkers.icon({
		    prefix: 'fa',
		    icon: icon,
		    markerColor: colour,
		});
	    }

	    function showPoints(dataset, geo_code, colour, group) {
		GeometryLoader.loadPoints(dataset, geo_code, function(data){
		    var map = self.map;
		    data['data'].forEach(function(facility){
			L.circleMarker(
			    [facility['latitude'], facility['longitude']],
			    {color: colour, radius:4})
			    .addTo(group)
			    .bindPopup(facility['name']).on(
				'mouseover', function(e){
				    this.openPopup();
				});
		    });
		});
	    }
	    
	    
	    L.control.scale().addTo(this.map);
	    var healthGroup = new L.LayerGroup();
	    var pharmaGroup = new L.LayerGroup();
	    var professionalGroup = new L.LayerGroup();
	    var libraryGroup = new L.LayerGroup();
	    var communityParksGroup = new L.LayerGroup();
	    var districtParksGroup = new L.LayerGroup();

	    // var healthIcon = getIcon('ambulance', 'blue');
	    // var pharmacyIcon = getIcon('medkit', 'orange');
	    // var professionalIcon = getIcon('user-md', 'purple');
	    // var libraryIcon = getIcon('book', 'red');
	    // var commParksIcon = getIcon('tree', 'green');
	    // var distParksIcon = getIcon('tree', 'green');
	    showPoints('health_services', geo_code, '#0000A0', healthGroup);
	    showPoints('pharmacies', geo_code, '#cb8325', pharmaGroup);
	    showPoints('professional_services', geo_code, '#9823c9', professionalGroup);
	    showPoints('libraries', geo_code, 'red', libraryGroup);
	    showPoints('community_parks', geo_code, '#24ac20', communityParksGroup);
	    showPoints('district_parks', geo_code, '#24ac20', districtParksGroup);

	    var overlayMap = {
		"<span style='color:#0000A0'>Health Facilities</span>": healthGroup,
		"<span style='color:#cb8325'>Private Pharmacies</span>": pharmaGroup,
		"<span style='color:#9823c9'>Professional Services</span>": professionalGroup,
		"<span style='color:red'>Libraries</span>": libraryGroup,
		"<span style='color:#24ac20'>Community Parks</span>": communityParksGroup,
		"<span style='color:#24ac20'>District Parks</span>": districtParksGroup
	    };
	    L.control.layers(null,overlayMap, {collapsed:false}).addTo(this.map);
	}


        // peers
        var parents = _.keys(geo.parents);
        if (parents.length > 0) {
          self.drawSurroundingFeatures(geo_level, parents[0], null, geo_version);
        }

        // every ancestor up to just before the root geo
        for (var i = 0; i < parents.length-1; i++) {
          self.drawSurroundingFeatures(parents[i], parents[i+1], null, geo_version);
        }

        // children
        if (geo.this.child_level) {
          self.drawSurroundingFeatures(geo.this.child_level, geo_level, geo_code, geo_version);
        }
    };

    // Add map shapes for a level, limited to within the parent level (eg.
    // wards within a municipality).
    this.drawSurroundingFeatures = function(level, parent_level, parent_code, parent_version) {
        var code,
            parent,
            self = this,
            url;

        parent_code = parent_code || this.geo.parents[parent_level].geo_code;
        parent_version = parent_version || this.geo.parents[parent_level].geo_version;
        parent = MAPIT.level_codes[parent_level] + '-' + parent_code;

        // code of 'level', if any?
        if (this.geo.this.geo_level == level) {
            code = this.geo.this.geo_code;
        } else if (this.geo.parents[level]) {
            code = this.geo.parents[level].geo_code;
        }

        GeometryLoader.loadGeometrySet(parent + '|' + MAPIT.level_codes[level], level, parent_version, function(geojson) {
            // don't include this smaller geo, we already have a shape for that
            geojson.features = _.filter(geojson.features, function(f) {
                return f.properties.code != code;
            });

            self.drawFeatures(geojson);
        });

        // if we're loading districts, we also want to load metros, because
        // districts don't give us full coverage
	// We also need to load the point that
        if (level == 'district') {
            GeometryLoader.loadGeometrySet(parent + '|' + MAPIT.level_codes.municipality, 'municipality', parent_version, function(geojson) {
                // only keep metros
                geojson.features = _.filter(geojson.features, function(f) {
                    // only metro codes are three letters
                    return f.properties.code.length == 3;
                });

                self.drawFeatures(geojson);
            });
        }
    };
};
