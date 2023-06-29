var bus_count_info
var bus_current_page = 0
var bus_next = null
var bus_prev = null
var bus_first_included=true
var bus_last_included=true
var bus_total_page = 0
var bus_pages = []
var bus_id = ''
var del_id = ''
var a = NaN
var file_upload = true
var file_list = []
var endYear = new Date(new Date().getFullYear(), 11, 31)
var updatefile = false
var bus_images = []
var most = []
//schedule_service').datepicker({ dateFormat: 'mm-dd-yy' }).val();
$(function() {

    $('#schedule_service').datepicker({
        format: 'mm/dd/yyyy', // Notice the Extra space at the beginning
    });
    var endYear = new Date(new Date().getFullYear(), 11, 31);
    $('#date').datepicker({
        format: " yyyy", // Notice the Extra space at the beginning
        startDate: "1980",
        endDate: endYear,
        viewMode: "years",
        minViewMode: "years",
         autoclose: true
    });
})

function submit_form(){

    if ($("#add_bus_form").valid() && file_upload){
     $('#bus_photos')[0].files = FileListItems(file_list)
        var data = $("#add_bus_form")[0]
        var form_data = new FormData(data)
        loader();
        $.ajax({
            url : '/api/v1/bus/',
            type : 'POST',
            data : form_data,
            cache: false,
            processData: false,
            contentType: false,

            success : function(data) {
                hideloader();
                $('.alert-success').show().delay(1500)
                window.setTimeout(function(){
                    location.href = '/list/bus'
                }, 1000);
                $('#succ-msg').text('Bus added successfully.')
            },
            error: function(data) {
                hideloader();
                 var i = 0
               for (var key in data.responseJSON) {
                   if (i ==0){
                    $('.alert-danger').show().delay(1000)
                    if (data.responseJSON[key][0] =="bus management with this bus id already exists."){
                        $('#error_txt').text("Bus Id already exists in the system.")
                    }
                    else{
                        $('#error_txt').text(data.responseJSON[key][0])
                    }
                    setTimeout(function(){ $('.alert-danger').hide() }, 3000);
                   }
                   i = i +1

                }
            }
        });
    }
 }


function  get_manufacturer_list(){
    loader();
    $.ajax({
            url : '/api/v1/manufacturer',
            type : 'get',
            dataType:'json',
            success : function(data) {
                hideloader()
               for (item in data){
                 $('#manufacturer_list').append('<option value="'+data[item].id+'">'+data[item].name+'</option>');}
                 a = parseInt(location.pathname.split('/')[2])
                let b =location.pathname.split('/')[3]
                if (isNaN(a) == false){
                get_bus_detail(a, b)
                }
            },
             error: function(error) {
                 hideloader();
            }
        });
}

function patch_form(data){
hideloader()
 $("input[name='bus_id']").val(data.bus_id)
 $("select[name='manufacturer']").val(data.manufacturer)
 $("input[name='make_year']").val(data.make_year)
 $("input[name='history']").val(data.history)
 $("input[name='chassis_number']").val(data.chassis_number)
 $("input[name='body_construction']").val(data.body_construction)
 $("select[name='status']").val(data.status)
 if (data.schedule_service){
    $("input[name='schedule_service']").val(get_date(data.schedule_service))
 }
 if (data.schedule_repair){
    $("input[name='schedule_repair']").val(get_date(data.schedule_repair))
 }
 if (data.vehicle_licensing){
    $("input[name='vehicle_licensing']").val(get_date(data.vehicle_licensing))
 }
 $("select[name='bus_category']").val(data.bus_category)
 $("input[name='odo_reading']").val(data.odo_reading)
 $("input[name='bus_price']").val(data.bus_price)
 $("select[name='fuel_input']").val(data.fuel_type_id)
 $("input[name='average_fuel_cost']").val(data.average_fuel_cost)
 $("input[name='labor_cost']").val(data.labor_cost)
 bus_images = data.bus_images
 bus_image()
}

function bus_image(){
    $(".images").empty()
    result_len = bus_images.length
    for(i=0; i<result_len; i++){
        stri='<div class="small-blk"><a href="javascript:void(0);" onclick="remove_images('+ bus_images[i].id+','+ i +')"><i class="fas fa-times-circle close-icon"></i></a><div class="round-circle">'+
            '<img src="/media/'+ bus_images[i].image+'" width="25" height="25" alt="User-Profile"></div></div>'
        $(".images").append(stri)
    }
}

function remove_images(id, i){
    loader();
    $.ajax({
    url: '/api/v1/bus/photo/'+id+'/',
    type: 'DELETE',
    success: function(data){
        hideloader();
        if (i > -1) {
            bus_images.splice(i, 1);
        }
        bus_image()
    },
    error: function(data) {
        hideloader();
    }
    });

}
function remove_bus(){
    loader();
    $.ajax({
    url: '/api/v1/bus/'+del_id+'/',
    type: 'DELETE',
    success: function(data){
        hideloader();
        $('#myModal').modal('hide')
        window.setTimeout(function(){
            location.href = '/list/bus'
        }, 1000);
         $('.alert-success').show().delay(1500)
        $('#succ-msg').text('Bus deleted successfully.')
    },
    error: function(data) {
        hideloader();
        var i = 0
        $('#myModal').modal('hide')
        for (var key in data.responseJSON) {
           if (i ==0){
            $('.alert-danger').show().delay(1500)
            $('#error_txt').text(data.responseJSON[key])
            setTimeout(function(){ $('.alert-danger').hide() }, 3000);
           }
           i = i +1

        }
    }
    });

}


$(window).on('load', function(){
    hideloader();

    $(".listview").hide()
    if (window.location.pathname == "/list/bus/"){
        get_bus_details()
    }
     a = parseInt(location.pathname.split('/')[2])
    let b =location.pathname.split('/')[3]
    if (isNaN(a) == false){
   }
   get_chart_data()
  get_manufacturer_list()
//  $(".tooltiptext").hide()
   getBusLogs()


});


function edit_form(){


    if ($("#add_bus_form").valid() && file_upload){

     $('#bus_photos')[0].files = FileListItems(file_list)

        var data = $("#add_bus_form")[0]
        var form_data = new FormData(data)
        var id = 1
        loader();
        $.ajax({
            url : '/api/v1/bus/'+a+'/',
            type : 'put',
            data : form_data,
//            dataType:'json',
            cache: false,
            processData: false,
            contentType: false,
            success : function(data) {
                hideloader();
                window.setTimeout(function(){
                    location.href = '/list/bus'
                }, 1000);
                 $('.alert-success').show().delay(1500)
                $('#succ-msg').text('Bus edited successfully.')
            },
            error: function(data) {
                hideloader();
                 var i = 0
               for (var key in data.responseJSON) {
                   if (i ==0){
                    $('.alert-danger').show().delay(1500)
                    if (data.responseJSON[key][0] =="bus management with this bus id already exists."){
                        $('#error_txt').text("Bus Id already exists in the system.")
                    }
                    else{
                        $('#error_txt').text(data.responseJSON[key][0])
                    }
                    setTimeout(function(){ $('.alert-danger').hide() }, 3000);
                   }
                   i = i +1

                }
            }
        });
    }
    }

$(".previous-icon").click(function(){ get_bus_data(bus_current_page - 1); });
$(".next-icon").click(function(){ get_bus_data(bus_current_page + 1); });

function get_bus_detail(id, b) {
    loader();
    $.ajax({
        url: '/api/v1/bus/' + id + '/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            if (b != '') {
                hideloader()
                patch_details(data)
            }
            else {
                hideloader()
                setTimeout(patch_form(data), 5000)

            }
        },
        error: function (error) {
            hideloader();
        }
    });
}

//$('#schedule_service').datepicker({ dateFormat: 'mm-dd-yy' }).val();
function patch_details(data){
    hideloader()
    result_len = data.bus_images.length
    $("#demo").hide()
    if (result_len > 0){
        $("#dummy-img").empty()
        $("#demo").show()

        $(".carousel-inner").empty()
        for (i=0;i<result_len;i++){
            if (i === 0){
                stri = '<div class="carousel-item active"><img class="img-size" src="/media/'+ data.bus_images[i].image +'" width="1309" height="357" alt="Banner"></div>'
            }
            else{
                stri = '<div class="carousel-item"><img class="img-size" src="/media/'+ data.bus_images[i].image +'"    width="1309" height="357" alt="Banner"></div>'
            }
            $(".carousel-inner").append(stri)
        }
    }
    else{
        $("#bus-details").show()
    }
     $("#bus_id").html(data.bus_id)
     $("#manufacturer").text((data.manufacturer != '' && data.manufacturer != null) ? (data.manufacturer_name) :  'NA')
     $("#production_year").text((data.make_year != '' && data.make_year != null) ? data.make_year :  'NA')
     $("#bus_history").text((data.history != '' && data.history != null) ? data.history :  'NA' )
     $("#chassis").text(data.chassis_number)
     $("#body_type").text((data.body_construction != '' && data.body_construction != null) ? data.body_construction :  'NA')
     $("#bus_status").text( (data.status != '' && data.status != null) ? check_status(data.status) :  'NA')
     $("#service_date").text( (data.schedule_service != null && data.schedule_service != null) ? get_date(data.schedule_service):  'NA' )
     $("#vehicle_licensing").text( (data.vehicle_licensing != null && data.vehicle_licensing != null) ? get_date(data.vehicle_licensing):  'NA' )
     $("#repair_date").text(  (data.schedule_repair != null && data.schedule_repair != null) ? get_date(data.schedule_repair):  'NA' )
     $("#bus_category").text((data.bus_category != '' && data.bus_category != null) ? category_class(data.bus_category) :  'NA')
     $("#odo_km").text( (data.odo_reading != '' && data.odo_reading != null) ? data.odo_reading +' KMs' :  'NA')
     $("#bus_cost").text((data.bus_price!= '' && data.bus_price != null) ? ('$ '+data.bus_price) :  'NA')
     $("#fuel_in").text((data.fuel_type != '' && data.fuel_type != null) ? (data.fuel_type) :  'NA')
     $("#avg_fuel_cost").text((data.average_fuel_cost != '' && data.average_fuel_cost != null) ? ('$ '+data.average_fuel_cost) :  'NA')
     $("#labor_cost").text((data.labor_cost != '' && data.labor_cost != null) ? ('$ '+data.labor_cost) :  'NA')
     $('#edit_button').attr("href", '/bus/'+data.id)
    del_id = data.id

}
function get_date(date){
    return  moment(date).format('DD/MM/YYYY');
}

function manufactuer(status){
    if (status == "1"){
        return "Honda"
    }
    else if(status == "2"){
        return 'Hyundai'
    }
    else if(status == "3"){
        return 'Tata'
    }
    else if(status == "4"){
        return "Any other"
    }
}
function fuel_input(status){
    if (status == "1"){
        return "Diesal"
    }
    else if(status == "2"){
        return 'Petrol'
    }
    else if(status == "3"){
        return 'ECV'
    }
    else if(status == "4"){
        return "Any other"
    }
}

function get_bus_data(page){
    loader();
    $.ajax({
        url : '/api/v1/bus/?page='+page,
        type : 'get',
        dataType:'json',
        success : function(data) {
        hideloader();
        $(".no-bus").empty()
        if (data.count == 0){
            $(".no-bus").empty()
            stri='<h3 class="center-txt">No data found</h3>'
            $(".no-bus").append(stri);
        }
        else{
            if (window.location.pathname == "/bus/dashboard"){
                dashboard_listtable(data)
            }
            if (window.location.pathname == "/list/bus/"){
                bus_listtable(data)
            }
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
            bus_pages = []

            for (var i=bus_current_page-2; i<=bus_current_page+2; i++) {
              if(i>0 && i<=bus_total_page){
                bus_pages.push(i);
              }
            }
            if(bus_current_page-2>1){
              bus_first_included=false
            }
            if(bus_current_page+2<bus_total_page){
              bus_last_included=false
            }
            $(".next-icon-list").empty();
            for(var item of bus_pages){
                $(".next-icon-list").append('<li><a class="element" href="javascript:get_bus_data('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
                if (bus_current_page == item){
                    $("#"+item)[0].parentNode.classList.add("active")
                }
            }

        }
        },
        error: function(error) {
            hideloader();
        }
    });
}

function bus_listtable(data){
    $(".table-block").empty();
    stri = ''
    result_len= (data.results.length)
    for (i=result_len-1;i>=0;i--){
       var body = (  data.results[i].body_construction != '' && data.results[i].body_construction != null) ?  data.results[i].body_construction:  'NA'
       var service = (  data.results[i].schedule_service != '' && data.results[i].schedule_service != null) ?  data.results[i].schedule_service:  'NA'
       var average_fuel_cost = (  data.results[i].average_fuel_cost != '' && data.results[i].average_fuel_cost != null) ?  data.results[i].average_fuel_cost:  'NA'
       var labor_cost = (  data.results[i].labor_cost != '' && data.results[i].labor_cost != null) ?  data.results[i].labor_cost:  'NA'
       stri_des = data.results[i].request['description']
       if (data.results[i].request['description'].length >= 35) {
            stri_des = data.results[i].request['description'].substring(0, 32) +'...'
        }
        var order_link = data.results[i].request['order_no']
        if (data.results[i].request['order_id'] != ''){
            var order_link = '<a href="/order/'+data.results[i].request['order_id']+'/detail">'+data.results[i].request['order_no']+'</a>'
        }
        editable = ''
        if (data.results[i].editable){
            editable = '<a href="/bus/'+data.results[i].id+'/"  title="Edit" class="blue-block icon-blk"><i class="fas fa-pen"></i></a>'
            }
       stri='<tr class="table-block">'+
            '<td><div class="cus-tooltip">'+data.results[i].bus_id+'<div class="tooltiptext"><table><tr><td>'+
            '<div class="tb-heading">Odometer</div><div class="tb-desc">'+data.results[i].odo_reading+'</div></td><td>'+
            '<div class="tb-heading">Fuel Input</div><div class="tb-desc">'+fuel_input(data.results[i].fuel_input)+'</div></td></tr>'+
            '<tr><td><div class="tb-heading">Fuel Cost</div><div class="tb-desc">'+average_fuel_cost+'</div>'+
            '</td><td><div class="tb-heading">Labour Cost</div><div class="tb-desc">'+labor_cost+'</div>'+
			'</td></tr></table><div class="text-left"><div class="btn-sec mr-2">'+
			'<a href="/repair/?bus='+data.results[i].id+'" class="blue-btn">Add Repair Request</a></div><div class="btn-sec"><a href="/service/?bus='+data.results[i].id+'" class="blue-btn">Add Service Request</a></div></div></div>'+
			'</div></td>'+
            '<td>'+data.results[i].out_of_service+'</td><td>'+data.results[i].back_in_service+'</td>'+
            '<td>'+ data.results[i].request['bus_system'] +'</td><td>'+ stri_des +'</td><td><a href="'+data.results[i].request['id']+'">'+data.results[i].request['request_no']+'</a></td><td>'+ order_link +'</td>'+
            '<td><span class="cus-badge '+ get_class(data.results[i].status) +'">'+ check_status(data.results[i].status) +'</span></td><td class="actions"><a href="/bus/'+data.results[i].id+'/detail/" onclick="myFunction()"  title="View" class="icon-blk green-block"><i class="fas fa-eye"></i></a>'+editable+'</td></tr>'
            $(".header-row").after(stri);
    }
//        $( ".cus-tooltip" ).mouseout(function() {
//          $("#purpose").addClass("overflow-cus");
//        });
//        $( ".cus-tooltip" ).mouseover(function() {
//          $("#purpose").removeClass("overflow-cus");
//        });

}

function check_status(status){
    if (status == "1"){
        return "IS"
    }
    else if(status == "2"){
        return 'OOS'
    }
    else if(status == "3"){
        return 'SS'
    }
    else if(status == "4"){
        return "WP"
    }
}
function category_class(status){
    if (status == "1"){
        return "Public Transport"
    }
    else if(status == "2"){
        return 'School Transport'
    }
    else if(status == "3"){
        return 'Private Transport'
    }
    else if(status == "4"){
        return "Any other"
    }
}

if (location.pathname == "/list/bus/"){
    $(document).ready(function () {
        $("select").each(function () {
            $('#sorting').val($(this).find('option[selected]').val())
            sort_buses()
        });
    })
}
function dashboard_listtable(data){
    console.log(data)
    $(".table-block").empty();
    stri = ''
    result_len= (data.results.length)
    if (data.results.length > 1){
        for (i=0;i<result_len;i++){
          stri='<tr class="table-block"><td><a href="/bus/'+data.results[i].id+'/detail/" class="icon-blk green-block" title="View Detail">'+
                '<i class="fas fa-eye"></i></a><a href="/bus/'+data.results[i].id+'/" class="blue-block icon-blk" title="Edit">'+
                '<i class="fas fa-pen"></i></a></td><td>'+data.results[i].bus_id+'</td><td>'+data.results[i].chassis_number+'</td><td>'+data.results[i].bus_category+'</td><td class="text-center"><span class="cus-badge red-badge">'+data.results[i].status+'</span></td><td>'+data.results[i].schedule_service+'</td></tr>'
                $(".header-row").after(stri);
        }
    }
    else{
        stri='<h3 class="center-txt">No data found</h3>'
        $(".header-row").after(stri);
    }
}
function getBusLogs(){
    loader();
    $.ajax({
        url: '/api/v1/bus/log/logs/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            console.log(22222222222222)
            console.log(data)
            hideloader();
            if (data.length !=0){
            $('#last_date').text(data.created_at.date)
            $('#last_time').text(data.created_at.time)
            $('#last_by').text(data.user)
            }
        },
        error: function (error) {
            hideloader();
        }
    });
}
function get_bus_details() {
    $("#sorting").prop('selectedIndex',0);
    loader();
    $.ajax({
        url: '/api/v1/dashboard/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            if (window.location.pathname == "/list/bus/") {
                hideloader()
                most = data
                sort_buses()
                bus_gridtable(data)
                $('.dynamic-loader').hide()
                $('.overlay').hide()
            }
        },
        error: function (error) {
            hideloader();
        }
    });
}
$('#sorting').on('change', function(){
    sort_buses()
})
function sort_buses(){
    if ($('#sorting').val() === '1'){
        data = most.sort(function(a,b){return new Date(a.make_year) - new Date(b.make_year)})
        bus_gridtable(data)
    }if ($('#sorting').val() === '2'){
        data = most.sort(function(a,b){return new Date(b.make_year) - new Date(a.make_year)})
        bus_gridtable(data)
    }
}
function bus_gridtable(data){
    $('.bus-no').empty()
    if (data.length == 0){
        stri = '<h3 class="record center-txt">No record found</h3>'
        $('.bus-no').append(stri);
    }
    else{
        $(".cus-height").empty();
        stri = ''
        var a = 0

        for (i=0;i<Math.ceil(data.length/5);i++){
            var stri1 = '', stri2 = '', stri3 = '', stri4 = '', stri5 = '', stri = ''
            if (check(a,data)== true){
                stri1='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a].status)+'" href="/bus/'+data[a].id+'/detail/" title="View Detail">'+ check_bus_id(data[a].bus_id, data[a].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a href=/repair?bus='+data[a].id+' class="blue-btn">Add Repair Request</button></div><div class="btn-sec"><a href=/service/?bus=' + data[a].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+1,data)== true){
                stri2 = '<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+1].status)+'" href="/bus/'+data[a+1].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+1].bus_id, data[a+1].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a href=/repair?bus='+data[a+1].id+' class="blue-btn">Add Repair Request</button></div><div class="btn-sec"><a href=/service/?bus=' + data[a+1].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+2,data)== true){
                stri3 ='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+2].status)+'" href="/bus/'+data[a+2].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+2].bus_id, data[a+2].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a href=/repair?bus='+data[a+2].id+' class="blue-btn">Add Repair Request</button></div><div class="btn-sec"><a href=/service/?bus=' + data[a+2].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+3,data)== true){
                stri4 ='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+3].status)+'" href="/bus/'+data[a+3].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+3].bus_id, data[a+3].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a href=/repair?bus='+data[a+3].id+' class="blue-btn">Add Repair Request</button></div><div class="btn-sec"><a href=/service/?bus=' + data[a+3].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            if (check(a+4,data)== true){
                stri5 ='<div class="grid-box"><div class="cus-tooltip"><a class="detail-btn '+get_class(data[a+4].status)+'" href="/bus/'+data[a+4].id+'/detail/" title="View Detail">'+ check_bus_id(data[a+4].bus_id, data[a+4].status) +'</a>'+
                '<div class="tooltiptext"><div class="btn-sec"><a href=/repair?bus='+data[a+4].id+' class="blue-btn">Add Repair Request</button></div><div class="btn-sec"><a href=/service/?bus=' + data[a+4].id + ' class="blue-btn">Add Service Request</a></div></div></div></div>'
            }
            stri = '<div class="grid-row">'+stri1+stri2+stri3+stri4+stri5+'</div>'
            $(".cus-height").append(stri);
            a = a + 5;
        }
    }

}

function check_bus_id(bus_id, status){
    if (status == "3" ){
        return bus_id+'(SS)'
    }
    else if(status == "4"){
        return bus_id+'(WP)'
    }
    return bus_id
}
if (document.getElementById('bus_photos')){
$('#bus_photos').on("change",function() {
  if (this.files.length > 0){
      for (var i = 0; i < this.files.length; i++){
        file_list.push(this.files[i])
        append_file()
      }
  }
});
}
function FileListItems (files) {
  var b = new ClipboardEvent("").clipboardData || new DataTransfer()
  for (var i = 0, len = files.length; i<len; i++) b.items.add(files[i])
  return b.files
}
function remove_file(id) {


    for (i = 0; i < file_list.length; i++) {
        if (i == id) {
            file_list.splice(id, 1);
            append_file()
            break;
        }


    }

    for (i = 0; i < file_list.length; i++) {
    const validImageTypes = ['image/jpg', 'image/jpeg', 'image/png'];
        if (!validImageTypes.includes(file_list[i].type)){
            $("#bus_photos1").text("Please select Only .jpg, .png and .jpeg format.")
             file_upload = false
             break;
         }
         else{
            file_upload = true
         }
    }

    if (file_upload == true){
        $("#bus_photos1").text('')
    }
     if (file_list.length == 0)
     {
     $("#bus_photos1").text('')
     }

     $('#bus_photos')[0].files = FileListItems(file_list)

}


function append_file(){
    $('.select-image').empty()
    for (var i = 0; i < file_list.length; i++){

        const validImageTypes = ['image/jpg', 'image/jpeg', 'image/png'];
        if (!validImageTypes.includes(file_list[i].type)){
            $("#bus_photos1").text("Please select Only .jpg, .png and .jpeg format.")
             file_upload = false

         }
         else{
            file_upload = true
         }
         stri = '<span class="small-blk">'+ file_list[i].name +'<a href="javascript:void(0);" id='+ i +' onclick="remove_file(this.id)" class="fas fa-times" title="close"></a></span>'
         $('.select-image').append(stri)
     }

     file_upload = check_meme_type(file_list)

     if ( file_upload == undefined)
     {
     file_upload = true
     }

}

function check_meme_type(files){
 for (var i = 0; i < files.length; i++){

        const validImageTypes = ['image/jpg', 'image/jpeg', 'image/png'];
        if (!validImageTypes.includes(file_list[i].type)){
             return false
         }


}
}


//function check_status
function check(index, data){

    if(typeof data[index] === 'undefined') {
        return false;
    }
    else {
        return true
    }
}

function get_class(status){
    if (status == "1"){
        return "green-badge"
    }
    else if(status == "2"){
        return 'red-badge'
    }
    else if(status == "3"){
        return 'green-badge yelow-txt'
    }
    else if(status == "4"){
        return "red-badge"
    }
}
function gridview(){

      get_bus_details()
      $(".gridview").show()
      $(".listview").hide()
      $(".select-blk").show()

        var element = document.getElementById("gridview");
        element.classList.add("type-active");
        var element = document.getElementById("listview");
        element.classList.remove("type-active");
}
function listview(){
    $('.dynamic-loader').show()
    $('.overlay').show()
    $(".select-blk").hide()
    get_bus_data(1)
    $(".listview").show()
    $(".gridview").hide()
    var element = document.getElementById("gridview");
    element.classList.remove("type-active");
    var element = document.getElementById("listview");
    element.classList.add("type-active");
}
jQuery.validator.addMethod("regexs", function(value, element) {
  return this.optional(element) || /\.pn?g$/i.test(value) || /\.jp?g$/i.test(value) || /\.jpe?g$/i.test(value);
}, "Letters only please");
$.validator.addMethod(
    "regex",
    function(value, element, regexp) {
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    "Please enter valid number."
);

 $("#add_bus_form").validate({
    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        bus_id: {
            required: true,
            maxlength : 7,
            minlength: 4,
        },
        chassis_number: {
            required: true,
             maxlength : 18,
            minlength: 16,
            regex:/^(?=\S*[a-zA-Z])(?=\S*\d)\S{16,}$/
        },
        make_year: {
            required: true,
            maxlength: endYear,
        },
        odo_reading: {
            required: true,
            digits: true
        },
        bus_price: {
            required: true,
            digits: true
        },
        fuel_input: {
            required: true,
            digits: true
        },
        status: {
            required: true,
        },
        manufacturer: {
            required: true,
        },
        bus_category: {
            required: true,
        },
        bus_photos:{
            regexs: true,
        },
        average_cost:{
            digits: true,
        },
        labor_cost:{
            digits: true,
        },
        average_fuel_cost:{
            digits: true,
        }
    },
        messages: {
        bus_id: {
            required: 'Please enter bus id. ',
            minlength: 'Bus id should be of at least 4 characters.',
            maxlength: 'Bus id should be less than equal to 7 characters.',
        },
        chassis_number: {
            required: 'Please enter chassis number.',
            minlength: 'Chassis number should be of at least 16 characters.',
            maxlength: 'Chassis number should be less than equal to 18 characters.',
            regex: 'Please enter valid chassis number.'
        },
        make_year: {
            required: 'Please  enter Production year.',
            maxlength: 'Please enter a valid Year of Production.'
        },
        odo_reading: {
            required: 'Please enter Odo meter reading .',

        },
        bus_price: {
            required: 'Please enter bus price.',
            digits: ' Please enter the valid digits.',
        },
        fuel_input: {
            required: 'Please select fuel input.',
        },
        status: {
            required: 'Please select bus status',
        },
        manufacturer: {
            required: 'Please select manufacturer.',
        },
        bus_category: {
            required: 'Please select bus category.',
        },
        bus_photos: {
            regexs: 'Please select Only .jpg, .png and .jpeg format are allowed.'
        }
    },
});

function get_chart_data() {
    loader();
    $.ajax({
        url: '/api/v1/bus/bus_data/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            set_label_data(data)
        },
        error: function (error) {
            hideloader();
        }
    });
}
function set_label_data(data){
$('#is_bus').text(data.in_service)
$('#ss_bus').text(data.ss)
$('#os_bus').text(data.os)
$('#wp_bus').text(data.wp)
$('#tot_is_bus').text(data.in_service + data.ss)
$('#tot_oos_bus').text(data.os + data.wp)
}

function export_data(email=false, file_type='pdf') {
    var url ='/api/v1/export/buses?file_type='+file_type
    window.setTimeout(function(){
        $(".alert").hide()
    }, 2000);
    if (email) {

        url=url+'&email'
        loader();
        $.ajax({
            url : url,
            type : 'get',
            dataType:'json',
            success : function(data) {
                hideloader();
                $('.alert-success').show().delay(1500)
                $('#succ-msg').text('Email has been sent successfully.')

                 window.setTimeout(function(){
                    $('.alert').hide()
                }, 2000);

            },
            error: function(data) {
                hideloader();
            }
        });
    }
    else {
        window.open(url)
    }
    
}

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}
