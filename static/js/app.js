$(function(){
	var select,
		selectItem,
		deleteBtn,
		tips,
		attributes,
		attribute,
		tip,
		actualizarBtn,
		sqLink;

	select = $('#places_list');
	tips = $("#tips");
	attributes = $("#attributes");

	sqLink = $('#sqlink');
	deleteBtn = $('#delete-btn');
	actualizarBtn = $('#actualizar-btn');

	selectItem = $("<option />");

	attribute = $("<td/><td/>");
	tip = $("<td />");

	select.on('change', function(e){
		var that = $(this);
		var id = that.val();
		var selectedItem = getSelectedElement(that);
		var fourId = selectedItem.data('fourId');
		
		if(fourId){
			var link = 'https://foursquare.com/v/' + fourId;
			sqLink.attr('href', link).text(link)
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

	actualizarBtn.on('click', function(e){
		e.preventDefault();
		var attrSerialized = serializeAttributes();
		var place = getSelectedElement(select);

		if(place.data('attributeId')){
			var url = 'Attribute/' + place.data('attributeId');

			$.parse.put(url, attrSerialized, function(d){
				alert('Actualizado');
			});
		}else{
			alert('Error!')
		}

	});


	$.parse.init({
		app_id : "pjDqEx0JZwcC6mWcycXAQ6lIWaldcGtynfLIkR0B",
    	rest_key : "m62wRFWC1JQ2fbFoNYmAPt6nmtOrRmXeUCJY49P1"
	})

	Parse.initialize("pjDqEx0JZwcC6mWcycXAQ6lIWaldcGtynfLIkR0B", "pdl4Xqgj3OYNoCBt7NOqe3jeLpjRs2R21jhgwvok");
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


		var selectedItem = getSelectedElement(select);
		$.parse.get('Attribute', {where: {
			place: {
				__type: 'Pointer',
				className: 'Place',
				objectId: id
			},
		}}, function(d){

			var placeId = select.val();
			if(d.results.length === 0){
				$.parse.post('Attribute', {place: {
					__type: 'Pointer',
					className: 'Place',
					objectId: placeId
				}}, function(data){
					getAttributes(placeId);
				});

				return;
			}

			selectedItem.data('attributeId', d.results[0].objectId)

			var clone = attribute.clone();
			var attr = d.results[0];
			var column;
			for(column in attr){
				if(!isInIgnoredColumns(column)){
					// console.log(column, attr[column]);
					var clone = $('<tr />');
					clone.append($('<td />').append($('<span>'+ column.toUpperCase() +'</span>')))
					clone.append($('<td />').append(
						$('<input type="checkbox" name="'+ column +'" />')
						.prop('checked', attr[column])
						.addClass('attr')
					));
					attributes.append(clone);
				}
			}
		});
	}

	function getSelectedElement(select){
		var selectedIndex = select[0].selectedIndex;
		var selectedItem = select.find('option').eq(selectedIndex);
		return selectedItem;
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

	function serializeAttributes(){
		var attrs = $('.attr');
		var attrsJson = {};

		attrs.each(function(ix, el){
			var attr = $(el);
			attrsJson[attr.attr('name')] = attr.prop('checked');
		});

		return attrsJson;
	}

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