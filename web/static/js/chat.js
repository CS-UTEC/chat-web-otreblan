var my_id = 0
var other_users = []

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
					other_users.push(data[i])

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
	my_id = user
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
			$("#messages").empty()
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

$(function() {
	$("#text-box").dxTextArea({
		placeholder: "Mensaje"
	})

	$("#user-list").dxLookup({
		dropDownOptions: {
			showTitle: false
		},
		dataSource: other_users,
		valueExpr: 'id',
		displayExpr: 'username'
	})

});

function send() {
	var text_box = $("#text-box").dxTextArea("instance")
	var user_list = $("#user-list").dxLookup("instance")

	console.log(text_box.option("text"))

	var message = {
		'content': text_box.option("text"),
		'user_from_id': my_id,
		'user_to_id': user_list.option("value")
	}
	$.post({
		url: '/messages',
		type: 'post',
		dataType: 'json',
		contentType: 'application/json',
		data: JSON.stringify(message),
		success: function(data)
		{
			console.log(data.msg)
			update_table()
		},
		error: function(data)
		{
			console.error("Error")
		}
	});
}
