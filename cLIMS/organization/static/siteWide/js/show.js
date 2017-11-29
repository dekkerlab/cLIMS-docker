
$(document).ready(function(){
	
	 $('.paginationTable').dataTable({
		 "ordering": false
	 });
	
    $(".divison").hover(function(){
        $(this).css("background-color", "yellow");
        }, function(){
        $(this).css("background-color", "pink");
    });
    
    $(".edit").click(function(){
    	$('.show').toggleClass("hidden");
    	if ($(this).text() == "Edit")
    	       $(this).text("Done")
    	    else
    	       $(this).text("Edit");
    });
    
    $(".del").click(function(){
    	$('.show').toggleClass("hidden");
    	if ($(this).text() == "Delete")
    	       $(this).text("Done")
    	    else
    	       $(this).text("Delete");
    });
    
    $(".combine").click(function(){
    	$('.show').toggleClass("hidden");
    });
    
    $('.combination').change(function() {
    	var checkedVals = $('.combination:checkbox:checked').map(function() {
    	    return this.value;
    	}).get();
    	lenCheck = checkedVals.length;
    	if(lenCheck>1){
    		$('.add').removeClass('disabled');
    	}
    	else{
    		$('.add').addClass('disabled');
    	}
    });
    
    $(".add").click(function(){
    	var checkedVals = $('.combination:checkbox:checked').map(function() {
    	    return this.value;
    	}).get();
    	joinedVals = checkedVals.join(",");
    	window.location.href = "/combineSamples/"+joinedVals;
    });
    
//	$(".divison").mouseover(function(){
//	    $(".divison").css("background-color", "red");
//	});
//    $(".divison").mouseout(function(){
//        $(".divison").css("background-color", "lightgray");
//    });
//    

        $('[data-toggle="tooltip"]').tooltip();
    
//        $( ".jsonObj" ).load( "ajax/test.html", function() {
//        	val =  $( ".jsonObj" ).html();
//        	  alert( val);
//        	});
        
        $(".expand").click(function(){
        	 $(this).toggleClass("hidden");
        	 $(this).parent().parent().find('.collapse').toggleClass("hidden");
        	 $(this).parent().parent().find('.divData').toggleClass("hidden");
        	
        });
        $(".collapse").click(function(){
        	 $(this).toggleClass("hidden");
        	 $(this).parent().parent().find('.expand').toggleClass("hidden");
        	 $(this).parent().parent().find('.divData').toggleClass("hidden");
        });
        
        $(".expandAll").click(function(){
        	if ($(this).text() == "Expand All"){
        		$(this).text("Collapse All")
       	       $(".expand").addClass("hidden");
          		$('.collapse').removeClass("hidden");
          		$('.divData').removeClass("hidden");
        	}
     	      
     	    else{
     	    	$(this).text("Expand All");
     	    	$(".expand").removeClass("hidden");
          		$('.collapse').addClass("hidden");
          		$('.divData').addClass("hidden");
     	    }
     	       
         
       	
       });
        $("#unselect").click(function(){
            alert("If nothing selected all experiments will be considered.")
            $('input:checkbox[name=dcic]').attr('checked',false);
        });
        $("#checkAll").change(function () {
            $("input:checkbox").prop('checked', $(this).prop("checked"));
        });
});
