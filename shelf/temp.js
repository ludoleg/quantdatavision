var $select = $("#leftValues");
$.getJSON("/phaselist.json", function(data){
	$select.html('');
	var listitems;
	$.each(data, function(key, value){
		listitems += '<option value=' + key + '>' + key + '</option>';
	});
	$select.append(listitems);
});
