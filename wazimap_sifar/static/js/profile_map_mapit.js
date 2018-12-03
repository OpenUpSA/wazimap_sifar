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

	if (geo_level == 'municipality'){
    function getIcon(iconUrl) {
      return new L.Icon({
        iconUrl: iconUrl,
        shadowUrl: '/static/js/vendor/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });
    }
    function showPoints(dataset, geo_code, icon, group) {
      GeometryLoader.loadPoints(dataset, geo_code, function(data){
        var map = self.map;
        data['data'].forEach(function(facility){
          L.marker(
            [facility['latitude'], facility['longitude']],
            {icon: icon})
          .addTo(group)
          .bindPopup(facility['name']).on(
            'mouseover', function(e){
              this.openPopup();
            });
        });
      });
    }
    L.control.scale().addTo(this.map);
    var healthGroup = new L.LayerGroup().addTo(this.map);
    var pharmaGroup = new L.LayerGroup().addTo(this.map);
    var professionalGroup = new L.LayerGroup().addTo(this.map);
    var libraryGroup = new L.LayerGroup().addTo(this.map);
    var communityParksGroup = new L.LayerGroup().addTo(this.map);
    var districtParksGroup = new L.LayerGroup().addTo(this.map);
    var greenIcon = getIcon('/static/js/vendor/images/marker-icon-green.png');
    var orangeIcon = getIcon('/static/js/vendor/images/marker-icon-orange.png');
    var violetIcon = getIcon('/static/js/vendor/images/marker-icon-violet.png');
    var blueIcon = getIcon('/static/js/vendor/images/marker-icon-blue.png');
    var yellowIcon = getIcon('/static/js/vendor/images/marker-icon-yellow.png');
    var redIcon = getIcon('/static/js/vendor/images/marker-icon-red.png');
    showPoints('health_services', geo_code, greenIcon, healthGroup);
    showPoints('pharmacies', geo_code, orangeIcon, pharmaGroup);
    showPoints('professional_services', geo_code, violetIcon, professionalGroup);
    showPoints('libraries', geo_code, blueIcon, libraryGroup);
    showPoints('community_parks', geo_code, yellowIcon, communityParksGroup);
    showPoints('district_parks', geo_code, redIcon, districtParksGroup);

    var overlayMap = {
        "<span style='color:#24ac20'>Health Facilities</span>": healthGroup,
        "<span style='color:#cb8325'>Private Pharmacies</span>": pharmaGroup,
        "<span style='color:#9823c9'>Professional Services</span>": professionalGroup,
        "<span style='color:#2387c9'>Libraries</span>": libraryGroup,
        "<span style='color:#d3bf19'>Community Parks</span>": communityParksGroup,
        "<span style='color:#c42238'>District Parks</span>": districtParksGroup
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
