$(function(){
	var select,
		selectItem,
		deleteBtn,
		tips,
		attributes,
		attribute,
		tip,
		actualizarBtn;

	select = $('#places_list');
	tips = $("#tips");
	attributes = $("#attributes");

	deleteBtn = $('#delete-btn');
	actualizarBtn = $('#actualizar-btn');

	selectItem = $("<option />");

	attribute = $("<td/><td/>");
	tip = $("<td />");

	select.on('change', function(e){
		var that = $(this);
		var id = that.val();
		var selectedIndex = that[0].selectedIndex;
		var selectedItem = that.find('option').eq(selectedIndex);
		var fourId = selectedItem.data('fourId');
		
		if(fourId){
			getTips(fourId);
			getAttributes(id);
		}else{
			cleanTips();
			cleanAttributes();
		}
		// TODO: Get attributes of places
	});


	deleteBtn.on('click', function(e){
		e.preventDefault();
		var placeId = select.val();
		if(placeId){
			var URI = 'Place/'+placeId;
			$.parse.delete(URI, function(d){
				getPlaces();
				cleanTips();
				cleanAttributes();
			});
		}
	});

	$.parse.init({
		app_id : "pjDqEx0JZwcC6mWcycXAQ6lIWaldcGtynfLIkR0B",
    	rest_key : "m62wRFWC1JQ2fbFoNYmAPt6nmtOrRmXeUCJY49P1"
	})

	getPlaces();


	function getAttributes(id){
		cleanAttributes();

		function isInIgnoredColumns(columnName){
			var ignored = ['updatedAt', 'objectId', 'createdAt', 'place']
			for(var i=0; i<ignored.length; i++){
				if(columnName === ignored[i]){
					return true;
				}
			}
			return false;
		}

		$.parse.get('Attribute', {where: {
			place: {
				__type: 'Pointer',
				className: 'Place',
				objectId: id
			}
		}}, function(d){
			var clone = attribute.clone();
			if(d.results.length === 0){ return; }
			var attr = d.results[0];
			var column;
			for(column in attr){
				if(!isInIgnoredColumns(column)){
					// console.log(column, attr[column]);
					var clone = $('<tr />').addClass('attr');
					clone.append($('<td />').append($('<span>'+ column.toUpperCase() +'</span>')))
					clone.append($('<td />').append($('<input type="checkbox" name="'+ column +'" />').prop('checked', attr[column])))

					attributes.append(clone);
				}
			}
		});
	}

	function cleanAttributes(){
		attributes.text('');
	}

	function getPlaces(){
		cleanPlacesList();
		$.parse.get('Place', {
			'limit': 1000,
			'order': 'name',
		}, function(data){
			var places = data.results;
			for(var i=0; i < places.length; i++){
				var place = places[i];
				var clone = selectItem.clone();
				clone.val(place.objectId);
				clone.text(place.name);
				clone.data('fourId', place.sq_id);
				clone.appendTo(select);
			}
		});
	};

	function getTips(id){
		cleanTips();
		var sq_c = 'AXCOUAILVTQS2FO4CQAQWYMQMPVJD5XHCCXTRCH3BEWFZAQE';
		var sq_cs = 'YANAVI5G5B2G3BEDDUWM1ETCWCYZLCZUHKJF0HQJZJLOBVQ5';
		var accessData = '?client_id='+ sq_c +'&client_secret='+ sq_cs +'&v=20141120&locale=es'
		var controlData = '&limit=500'
		var url = 'https://api.foursquare.com/v2/venues/'+ id +'/tips/' + accessData + controlData;

		$.get(url, function(d){
			var typs = d.response.tips.items;
			for(var t=0; t<typs.length; t++){
				var typ = typs[t];
				var clone = tip.clone();
				clone.text(typ.text);
				tips.append($('<tr />').append(clone));
			}
		});

	}

	function cleanTips(){
		tips.text('');
	}

	function cleanPlacesList(){
		select.html('<option value="">-------</option>');
	};
});