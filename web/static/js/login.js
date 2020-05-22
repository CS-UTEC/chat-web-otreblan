async function login()
{
	var credentials = {
		'username': $('#username').val(),
		'password': $('#password').val()
	}
	console.log("loading")
	//await new Promise(r => setTimeout(r, 1000));
	$.post({
		url: '/authenticate',
		type: 'post',
		dataType: 'json',
		contentType: 'application/json',
		data: JSON.stringify(credentials),
		success: function(data)
		{
			console.log(data.msg)
			//Cookies.set('id', data.id)
			document.getElementById("ok").style.display = "block"
		},
		error: function(data)
		{
			console.error("Error")
			document.getElementById("no").style.display = "block"
		}
	});
}
