function link_user(user){
	return '<div><span><a href="users/'+user.id+'">@'+user.username+'</a></span></div>'
}

function me(){
	$.get({
		url: '/users/-1',
		type: 'get',
		dataType: 'json',
		contentType: 'application/json',
		success: function(data)
		{
			$("#contacts").html(link_user(data));
			id = data.id;
		},
		error: function(data)
		{
			console.error("Error")
		}
	});
}

function others(id){
	$.get({
		url: '/users',
		type: 'get',
		dataType: 'json',
		contentType: 'application/json',
		success: function(data)
		{
			for(var i = 0; i < data.length; i++){
				console.log(data[i].id)
				console.log(Cookies.get('id'))
				if(data[i].id != id){
					$("#contacts").append(link_user(data[i]));
				}
			}
		},
		error: function(data)
		{
			console.error("Error")
		}
	});
}

function update_table(){
	me()
	others(Cookies.get("id"))
}
