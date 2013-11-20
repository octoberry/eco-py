var global_quest_list = {}

function quest_accept_click(key){
var val = global_quest_list.data[key];
console.log('quest_accept_click',key);
console.log('quest_accept_click',val);
      $.ajax({
        type: "POST",
        url: "/quest/accept",
        data: JSON.stringify({ 'quest_id': val._id }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            console.log('success',data);
        },
        failure: function(errMsg) {
            console.log('failure',errMsg);
        }
      });

  $( "#all_quest_item-form" ).dialog( "close" );

}

function photo_upload_click(key){
var val = global_quest_list.data[key];
console.log('photo_upload_click',key);
console.log('photo_upload_click',val);
$.ajax({
        type: "POST",
        url: "/quest/photo/upload",
        data: JSON.stringify({ 'quest_id': val._id }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            console.log('success',data);
        },
        failure: function(errMsg) {
            console.log('failure',errMsg);
        }
      });
  $( "#my_quest_item-form" ).dialog( "close" );
}


function quest_item_click( index, key){
  var val = global_quest_list.data[key];
  console.log('quest_item_click', prefix, val);

	var prefix = "";

   if (index == 0)
	  prefix = "all_";
  else
	  prefix = "my_";


		var strItem = "" +

		'<section id="main">'+
		'<div class="container_16 clearfix">' + 


		'<h2 class="luck grid_16">' + val.title + '</h2>' +
		'<div class="clear"></div><div class="big_sep"></div><div class="clear"></div>' +
		'<div class="grid_16 about_text">' +
			'<p>' + val.desc + '</p>' +
		'</div>' +
		'<div class="clear"></div><div class="big_sep"></div><div class="clear"></div>' +

		'<div class="grid_8 game_box osans-s">' +
		  '<h4 class="luck">Награда</h4>' +
		'</div>'+

		'<div class="grid_16 about_text">'+
		'<p><img src="/img/crystal.png">' + val.price + '</p>'+
		'</div>'+
			'</div><!--container_16-->'+
		'<div class="container_16 clearfix">' + 
		'';

		if ( index == 0 )
			strItem += '<a href="#" class="cta_btn" onclick="javascript:quest_accept_click('+key+')">Принять вызов</a>';
		else
			strItem += '<a href="#" class="cta_btn" onclick="javascript:photo_upload_click('+key+')">Загрузить фото</a>';

		strItem += "" +
		'<div class="container_16 clearfix">' + 
		'</section>';


		$( "#" + prefix + "quest_item_descr" ).text( "" );
		$( "#" + prefix + "quest_item_descr" ).append( strItem );

	
  $( "#" + prefix + "quest_item-form" ).dialog( "open" );

}

$(function() {

    $( "#all_quest_list-form" ).dialog({
      autoOpen: false,  height: 600,  width: 660,   modal: true, //dialogClass: 'noTitleStuff',
      close: function() {
      }
    });

    $( "#my_quest_list-form" ).dialog({
      autoOpen: false,  height: 600,  width: 660,   modal: true, //dialogClass: 'noTitleStuff',
      close: function() {
      }
    });

    $( "#all_quest_item-form" ).dialog({
      autoOpen: false,  height: 600,  width: 660,   modal: true, 
      close: function() {
      }
    });

    $( "#my_quest_item-form" ).dialog({
      autoOpen: false,  height: 600,  width: 660,   modal: true, 
      close: function() {
      }
    });
	


    $( "#all_quest_list" ).click(function() 
	{
        $.getJSON("/quests", function( data ) 
		{
          global_quest_list.data = data;
		  $( "#all_quest_item" ).text( "" );
          $.each( data, function( key, val ) 
		  {
			
			  var strItem = "" +
				'<article>' +
				'<div class="article_date luck grid_2 alpha omega">' + val.type + '</div>' +
				'<div class="grid_9 alpha">' +
				  '<h1>' + val.title + '</h1>' +
				  '<p>'+val.short_descr+'</p>' +
				  '<p>'+'<a href="#" onclick="javascript:quest_item_click( 0, ' + key  + ')">Перейти...<a/>'+'</p>' +
				  '<div class="small_sep"></div>' +
				'</div>' +
			  '</article>' +
			  '<div class="clear">';


			  $( "#all_quest_item" ).append( strItem );
          }); // $.each
          $( "#all_quest_list-form" ).dialog( "open" );
        }); // $.getJSON              
    }); // click

    $( "#my_quest_list" ).click(function(){
      console.log("#my_quest_list.click");
      $( "#my_quest_list-form" ).dialog( "open" );
    }); // click


    $( "#my_quest_list" ).click(function() 
	{
        $.getJSON("/my_quests", function( data ) 
		{
          global_quest_list.data = data;
		  $( "#my_quest_item" ).text( "" );
          $.each( data, function( key, val ) 
		  {
			
			  var strItem = "" +
				'<article>' +
				'<div class="article_date luck grid_2 alpha omega">' + val.type + '</div>' +
				'<div class="grid_9 alpha">' +
				  '<h1>' + val.title + '</h1>' +
				  '<p>'+val.short_descr+'</p>' +
				  '<p>'+'<a href="#" onclick="javascript:quest_item_click( 1,' + key  + ')">Перейти...<a/>'+'</p>' +
				  '<div class="small_sep"></div>' +
				'</div>' +
			  '</article>' +
			  '<div class="clear">';


			  $( "#my_quest_item" ).append( strItem );
          }); // $.each
          $( "#my_quest_list-form" ).dialog( "open" );
        }); // $.getJSON              
    }); // click

});

$(':file').change(function(){
    var file = this.files[0];
    name = file.name;
    size = file.size;
    type = file.type;
    //Your validation
    console.log('validation')

    var formData = new FormData($('form')[0]);
    $.ajax({
        url: '/quest/photo/upload',  //Server script to process data
        type: 'POST',
        xhr: function() {  // Custom XMLHttpRequest
            var myXhr = $.ajaxSettings.xhr();
            if(myXhr.upload){ // Check if upload property exists
                myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
            }
            return myXhr;
        },
        //Ajax events
        //beforeSend: beforeSendHandler,
        success: completeHandler,
        error: errorHandler,
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
    });
    console.log('uploading')
});

function progressHandlingFunction(e){
    if(e.lengthComputable){
        $('progress').attr({value:e.loaded,max:e.total});
    }
}

function completeHandler(e){
    console.log('done')
}

function errorHandler(e){
    console.log(e)
}
