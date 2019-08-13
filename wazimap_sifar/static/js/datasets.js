function getRandomColor() {
    var colours = [
	'#4E6CeF', '#3949AB', '#5E35B1', '#8E24AA', '#D81B60', '#E00032',
	'#039BE5', '#00ACC1', '#00897B', '#0A8F08', '#7CB342', '#C0CA33',
	'#FDD835', '#FB8C00', '#F4511E'
    ];
    var colorIndex = Math.floor(Math.random() * ((colours.length -1) - 0 + 1)) + 0;
    return colours[colorIndex];
}


Vue.component('contributer-item',{
    props:['contributer'],
    template:`<div v-bind:class="{selected: isSelected}" class="accordion-radio-item" v-on:click="showPoints(contributer.id,contributer.subcategory)" v-bind:style="{color: color}">
					    <div class="accordion-item-heading">{{contributer.subcategory}}</div>
					</div>`,
    data: function(){
	return {
	    isSelected: false,
	    color: ''
	}
    },
     methods:{
	 showPoints: function(contribID, category){
	     var deleted = false;
	     var self = this;
	     contact.display = 'none';
	    //show points or remove them
	    dataset.map.eachLayer(function(layer){
		if (layer.myTag == category){
		    dataset.map.removeLayer(layer);
		    self.color = '';
		    self.isSelected = false;
		    deleted = true;
		    contact.display = 'none';
		    return;
		}
	    });
	     if (deleted == false){
		 $.ajax({
		dataType:'json',
		url: '/api/v1/dataset/contributer/'+contribID,
		method: 'GET',
		success: function(result){
		    //change color of dot background-color:
		    var new_color = getRandomColor();
		    self.isSelected = true;
		    self.color = new_color;
		    L.geoJson(result.features,{
			onEachFeature: function(feature,layer){
			    layer.myTag = category;
			    layer.on('click', function(){
				contact.name = feature.properties.name;
			    contact.email = feature.properties.email ? feature.properties.email :'Unavailable';
			    contact.address = feature.properties.address ? feature.properties.address :'Unavailable';
			    contact.website = feature.properties.website ? feature.properties.website :'Unavailable';
			    contact.phone = feature.properties['phone_number'] ? feature.properties['phone_number'] :'Unavailable';
				console.log('We clicked on the button');
				contact.display = 'block';
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
    template:`<div class="accordion-item">
				<div class="accordion-item-trigger" v-on:click="showCategory()">
				    <div class="dropdown-heading-wrapper">
                                        <img src="/static/img/baseline-work-24px.svg" alt="" class="grey-icon-left">
					<h5 class="card-heading-3 indent">{{dataset.name}}</h5>
				    </div><img src="/static/img/baseline-arrow_drop_down-24px.svg" style="-webkit-transform:translate3d(0, 0, 0) scale3d(1, 1, 1) rotateX(0) rotateY(0) rotateZ(0DEG) skew(0, 0);-moz-transform:translate3d(0, 0, 0) scale3d(1, 1, 1) rotateX(0) rotateY(0) rotateZ(0DEG) skew(0, 0);-ms-transform:translate3d(0, 0, 0) scale3d(1, 1, 1) rotateX(0) rotateY(0) rotateZ(0DEG) skew(0, 0);transform:translate3d(0, 0, 0) scale3d(1, 1, 1) rotateX(0) rotateY(0) rotateZ(0DEG) skew(0, 0)" alt="" class="icon-right"></div>
                                      <div v-bind:style="{display: display}" class="accordion-item-content">
                                     <contributer-item v-for="contrib in dataset.contributer_set" v-bind:contributer="contrib" v-bind:key="contrib.id"></contributer-item>
                                    </div>
			    </div>`,
    data: function(){
	return {
	    display: 'none'
	}
    },
    methods:{
	showCategory: function(){
	    contact.display = 'none';
	    if (this.display == 'none'){
		this.display = 'block';
	    }else{
		this.display = 'none';
	    }
	}
    } 
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
	display: 'none'
    },
    methods:{
	closePoint: function(event){
	    console.log('Hiding the point menu');
	    this.display = 'none';
	}
    }
});

