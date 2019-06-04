function getRandomColor() {
    var colours = ['red', 'orange', 'yellow', 'olive', 'green',
		   'teal', 'blue', 'violet', 'purple', 'pink',
		   'brown', 'black'];
    var colorIndex = Math.floor(Math.random() * ((colours.length -1) - 0 + 1)) + 0;
    return colours[colorIndex];
}


Vue.component('contributer-item',{
    props:['contributer'],
    template:`<ul>
	<li class="contributer">
	<a ref="myPoint" href="#" class="contributer-text" style="margin-left:16px;" v-on:click="showPoints(contributer.id,contributer.subcategory)">
	<span v-bind:style="{color: color}">
	{{contributer.subcategory}}
	</span>
	<span class="dot" v-bind:style="{'background-color':color}">
	</span>
	</a>
	</span>
	</li>
	</ul>`,
    data: function(){
	return {
	    color: '#bbb'
	}
    },
     methods:{
	 showPoints: function(contribID, category){
	     var deleted = false;
	      var self = this;
	    //show points or remove them
	    dataset.map.eachLayer(function(layer){
		if (layer.myTag == category){
		    dataset.map.removeLayer(layer);
		    self.color = '#bbb';
		    console.log(this.color);
		    deleted = true;
		    return;
		}
	    });
	     if (deleted == false){
		 $.ajax({
		dataType:'json',
		url: '/api/v1/dataset/contributer/'+contribID,
		method: 'GET',
		success: function(result){
		    console.log("Fetched the data from api");
		    //change color of dot background-color:
		    var new_color = getRandomColor();
		    self.color = new_color;
		    L.geoJson(result.features,{
			onEachFeature: function(feature,layer){
			    layer.myTag = category;
			    contact.name = feature.properties.name;
			    contact.longitude = feature.geometry.coordinates[0];
			    contact.latitude = feature.geometry.coordinates[1];
			    contact.email = feature.properties.email;
			    contact.address = feature.properties.address;
			    contact.website = feature.properties.website;
			    contact.phone = feature.properties['phone_number'];
			    layer.on('click', function(){
				console.log('We clicked on the button');
				self.$set(contact.contactDisplay,
					  'display', 'block');
				//contact.show = 'block';
			    });
			},
			pointToLayer: function(feature, latlng){
			    return L.circleMarker(latlng,{
				radius:5,
				fillColor: self.color,
				color: "#000",
				weight: 1,
				opacity: 1,
				fillOpacity: 1
			    });
			}
		    }).addTo(dataset.map);
		    
		}
	    });
	     }
	    
	    
	}
    },
});

Vue.component('dataset-item',{
    props:['dataset'],
    template: '<li>'+
    	'<div class="collapsible-header collapsible-text">'+
    	'{{dataset.name}}' +
    	'<i class="fa fa-caret-down" style="float:right;top:50px" aria-hidden="true"></i>'+
    	'</div>'+
    	'<div class="collapsible-body">'+
    	'<contributer-item v-for="contrib in dataset.contributer_set" v-bind:contributer="contrib"></contributer-item>'+
    	'</div>'+
    	'</li>',
});

var dataset = new Vue({
    el:'#dataset-category',
    delimiters: ["[[","]]"],
    data: {
	category:[],
    },
    created: function(){
	var self = this;
	$.ajax({
		dataType: 'json',
		url: '/api/v1/dataset/category',
		method: 'GET',
		success: function(result){
		    self.category = result.data;
		    console.log(self.category);
		},
		error: function(error){
		    console.log(error);
		}
	    });
    }
    
});

var contact = new Vue({
    el:'#contact',
    delimiters:["[[", "]]"],
    data:{
	name:'',
	address:'',
	email:'',
	website:'',
	phone:'',
	latitude:'',
	longitude:'',
	contactDisplay:{
	    display: 'none'
	}
    }
});
