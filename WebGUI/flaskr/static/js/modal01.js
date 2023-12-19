$(document).ready(function(){
 $('#insert_form').on("submit", function(event){  
  event.preventDefault();  
  if($('#name').val() == "")  
  {  
   alert("Name is required");  
  }  
  else if($('#address').val() == '')  
  {  
   alert("Address is required");  
  }  
  else if($('#designation').val() == '')
  {  
   alert("Designation is required");  
  }
    
  else 
  {  
   $.ajax({  
    url:"/insert",  
    method:"POST",  
    data:$('#insert_form').serialize(),  
    beforeSend:function(){  
     $('#insert').val("Inserting");  
    },  
    success:function(data){  
     $('#add_data_Modal').modal('hide'); 
      if (data=='success')  {
       window.location.href = "/";   
     }
    }  
   });  
  }  
 });
 
 $(document).on('click', '.view_data', function(){
  var employee_id = $(this).attr("id");
  $.ajax({
   url:"/select",
   method:"POST",
   data:{employee_id:employee_id},
   success:function(data){
    $('#dataModal').modal('show');
    var data_rs = JSON.parse(data);
    $('#view_name').val(data_rs[0]['emp_name']);
    $('#view_address').val(data_rs[0]['address']);
    $('#view_gender').val(data_rs[0]['gender']);
    $('#view_designation').val(data_rs[0]['designation']);
    $('#view_age').val(data_rs[0]['age']);
   }
  });
 });
});
