function link_user(user){
	return '<div><span><a href="users/'+user.id+'">@'+user.username+'</a></span></div>'
}

function me(){
	var id = 'null'
	$.get({
		url: '/users/-1',
		type: 'get',
		dataType: 'json',
		contentType: 'application/json',
		async: false,
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
	return id
}

function others(id){
	$.get({
		url: '/users',
		type: 'get',
		dataType: 'json',
		contentType: 'application/json',
		success: function(data)
		{
			console.log(id)
			for(var i = 0; i < data.length; i++){
				if(data[i].id === id){
					//$("#contacts").append("aaaaaa");
				}else{
					console.log(data[i].id)
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
	var user = me()
	others(user)
	get_messages(user)
}

function get_messages(user){
	$.get({
		url: '/messages',
		type: 'get',
		dataType: 'json',
		contentType: 'application/json',
		success: function(data)
		{
			for(var i = 0; i < data.length; i++){
				$("#messages").append(data[i].content + "<br>");
			}
		},
		error: function(data)
		{
			console.error("Error")
		}
	});
}
