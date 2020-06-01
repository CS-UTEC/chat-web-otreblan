$(function(){
	var url = '/messages'

	var users = []

	$.get({
		url: '/users',
		type: 'get',
		dataType: 'json',
		contentType: 'application/json',
		async: false,
		success: function(data)
		{
			users = data
		},
		error: function(data)
		{
			console.error("Error")
		}
	});


	$("#grid").dxDataGrid({
		dataSource: DevExpress.data.AspNet.createStore({
			key: "id",
			loadUrl: url,
			insertUrl: url,
			updateUrl: url,
			deleteUrl: url,
			onBeforeSend: function(method, ajaxOptions) {
				ajaxOptions.xhrFields = { withCredentials: true };
			}
		}),

		editing: {
			allowUpdating: true,
			allowDeleting: true,
			allowAdding: true
		},

		paging: {
			pageSize: 12
		},

		pager: {
			showPageSizeSelector: false,
			allowedPageSizes: [8, 12, 20]
		},

		columns: [{
			dataField: "id",
			dataType: "number",
			allowEditing: false
		}, {
			dataField: "content"
		}, {
			dataField: "sent_on",
			dataType: "datetime"
		}, {
			dataField: "user_from_id",
			lookup: {
				dataSource: users,
				valueExpr: "id",
				displayExpr: "username"
			}
		}, {
			dataField: "user_to_id",
			lookup: {
				dataSource: users,
				valueExpr: "id",
				displayExpr: "username"
			}
		}, ],
	}).dxDataGrid("instance");
});
