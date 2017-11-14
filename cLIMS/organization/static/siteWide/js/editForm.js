$(function() {
	$('.jsonForm select').on('change', function() {
	  var jsonObjPK = this.value;
	  $.ajax({
		    url: "/constructForm/",
		    type: "POST",
		    data: { 
                'pk': jsonObjPK,
            }, 
		    cache:false,
		    dataType: "json",
		    success: function(obj){
		    	jsObj = obj.field_set;
		    	model = obj.model;
		    	form = constructForm(jsObj);
//		    	$("."+model).empty();
//		    	$("."+model).append( form );
		    	$(".inner").empty();
		    	$(".inner").append( form );
		    	var valuesJson = eval('(' + $( "#jsonForm").val() + ')');
		    	//console.log(valuesJson);
				for (var k in valuesJson) {
					$( "select[name='"+k+"']" ).val(""+valuesJson[k]+"");
					$( "input[name='"+k+"']" ).val(""+valuesJson[k]+"");
					$( "textarea[name='"+k+"']" ).val(""+valuesJson[k]+"");
				}
				
		    },
		    error: function(ts) { 
               
            }
		});
});
	
	function constructForm(jsObj) {
		form = ""
		for (var key in jsObj) {
			form +=  "<a style='cursor: pointer;'><i class='fa fa-question-circle' title='"+jsObj[key].help+"'></i></a>"
    		 form += "<label>"+key+"</label>";
    		 text = jsObj[key].data;
    		 if (text == "choices"){
    			 choices = jsObj[key].choices;
    			 len = Object.keys(choices).length;
    			 form += "<select name="+key+">";
    			 if(jsObj[key].required == "yes"){
        			 form += "class='makeRequire' >";
        		 }
        		 else{
        			 form += ">";
        		 }
    			 for (i = 1; i <= len; i++) {
    				 optionValue = jsObj[key].choices[i]
    				 form += "<option value='"+optionValue+"'>"+optionValue+"</option>";
    			 }
    			 form += "</select>";
    		 }
    		 else {
    			 if(jsObj[key].data  == "float"){
    				 form += "<input maxlength='1000' name="+key+" type=number step=0.01 " ;
    			 }
    			 else if(jsObj[key].data  == "textarea"){
    				 form += "<textarea name="+key+" rows='5' cols='30'> </textarea" ;
    			 }
    			 else{
    				 form += "<input maxlength='1000' name="+key+" type='"+jsObj[key].data+"'"
    			 }
    			 if(jsObj[key].required == "yes"){
        			 form += "class='makeRequire' >";
        		 }
        		 else{
        			 form += ">";
        		 }
    		 }
    		 
    		}
	    return form;
	}
	

	$( "input[name*='date']" ).attr({'type':'date'});
	
	$( ".jsonForm select" ).change();
	
	
	if ( $( ".jsonAnalysis" ).length ) {
		var jsonObjPK = $( ".jsonAnalysis select" ).val();
		console.log(jsonObjPK)
		  $.ajax({
			    url: "/constructForm/",
			    type: "POST",
			    data: { 
	                'pk': jsonObjPK,
	            }, 
			    cache:false,
			    dataType: "json",
			    success: function(obj){
			    	jsObj = obj.field_set;
			    	model = obj.model;
			    	form = constructForm(jsObj);
//			    	$("."+model).empty();
//			    	$("."+model).append( form );
			    	$(".inner").empty();
			    	$(".inner").append( form );
			    	var valuesJson = eval('(' +$( "#jsonForm").val() + ')');
					for (var k in valuesJson) {
						$( "select[name='"+k+"']" ).val(""+valuesJson[k]+"");
						$( "input[name='"+k+"']" ).val(""+valuesJson[k]+"");
						$( "textarea[name='"+k+"']" ).val(""+valuesJson[k]+"");
					}
					
			    },
			    error: function(ts) { 
//	                alert("Incorrect Choice");
	            }
			});
		
	}
	
		
});